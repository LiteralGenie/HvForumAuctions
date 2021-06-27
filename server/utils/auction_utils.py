from .scraper_utils import get_html, get_soup
from . import misc_utils
from .template_utils import render
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Generator
from classes import AuctionContext
import re, json, time


def int_to_price(x):
	unit= 'c'
	if x > 10**6:
		x= x / 10**6
		unit= 'm'
	elif x > 10**3:
		x= x / 10**3
		unit= 'k'

	if int(x) == float(x):
		x= int(x)

	return str(x) + unit


async def update_thread(ctx):
	# inits
	await ctx.do_forum_login()

	# get highest bids for each item
	max_bids= ctx.get_max_bids()

	md5= ctx.CONFIG['post_key']

	# todo: "".join(f"%u{ord(x):04x}.upper()" for x in text)
	cln= lambda x: re.sub(r'\\u(\w{4})', lambda m: rf'%u{m.group(1).upper()}', json.dumps(x)).replace(r"\n", "\n")[1:-1]
	payload_template= dict(
		f=ctx.CONFIG['forum_number'],
		t=ctx.META['thread_id'],
		md5check= md5,
		act='xmlout',
		do='post-edit-save',
		std_used=1
	)

	# edit post with items
	tmp= payload_template.copy()
	tmp['Post']= cln(render(ctx.TEMPLATES['main_post'], max_bids=max_bids, **ctx.__dict__))
	tmp['p']= ctx.META['main_post_id']
	resp= await ctx.session.post('https://forums.e-hentai.org/index.php', data=tmp)
	debug= await resp.text()

	# edit post with warning log
	tmp= payload_template.copy()
	tmp['Post']= cln(render(ctx.TEMPLATES['warning_post'], max_bids=max_bids, **ctx.__dict__))
	tmp['p']= ctx.META['warning_post_id']
	resp= await ctx.session.post('https://forums.e-hentai.org/index.php', data=tmp)
	debug= await resp.text()

	pass

async def scan_updates(ctx):
	# type: (AuctionContext) -> bool

	# get unread posts
	has_new= False
	posts= get_new_posts(ctx)
	async for p in posts:
		if p['index'] < int(ctx.CONFIG['ignore_first_n']):
			continue
		has_new= True

		# parse post text for bid-code (item##)
		lst= parse_bid_text(p['text'])

		# match bid-code with items for sale
		for b in lst:
			b.update(dict(
				is_proxy=False,
				source=p,
			))
			ctx.BIDS= update_bid_cache(b, ctx)

	# return
	misc_utils.dump_json(ctx.BIDS, ctx.BID_FILE)
	return has_new


def update_bid_cache(bid, ctx):
	class Error(Exception):
		pass

	def update():
		# get category
		for group in ctx.META['equips']:
			if bid['item_type'].lower() == group['abbreviation'].lower():
				cat= group['abbreviation']
				lst= group['items']
				break
		else:
			if bid['item_type'].lower() == ctx.META['materials']['abbreviation'].lower():
				cat= ctx.META['materials']['abbreviation'].lower()
				lst= ctx.META['materials']['items']
			else:
				raise Error(1) # bad category

		# get id
		for item_id,item in lst.items():
			code= bid['item_code']
			if int(item_id) == int(code):
				ctx.BIDS['items'].setdefault(cat, {}).\
					setdefault(str(item_id), []).\
					append(bid)
				break
		else:
			raise Error(2) # bad item number

	try:
		update()
	except Error as e:
		bid['fail_code']= str(e)
		ctx.BIDS['warnings'].append(bid)

	return ctx.BIDS


def parse_bid_text(text):
	# inits
	regex=  "(?:\[|\s)*" # leading bracket -->  [
	regex+= "([a-z]+)(?:\s|_)*(\d+)" # item code -->  item00
	regex+= "(?:\]|\s)+" # closing bracket -->  ]
	regex+= "(\d+\.?\d*)(b|m|k|c)?" # bid  -->  50k

	matches= re.findall(regex, text, flags=re.IGNORECASE)

	for x in matches:
		item_type, item_code, val, unit= x

		# get price
		mult= 10**0
		unit= unit.lower()
		if unit == 'k': mult= 10**3
		elif unit == 'm': mult= 10**6
		elif unit == 'b': mult= 10**9

		price= float(val) * mult

		yield dict(
			item_type=item_type,
			item_code=item_code,
			max=price
		)

def parse_page(html, seen):
	# inits
	soup= BeautifulSoup(html, 'html.parser')
	posts= soup.select(':not(#topicoptionsjs) > div.borderwrap > table:nth-child(1)')

	page_time= soup.select_one('#gfooter > tbody > tr > td:nth-child(3)')
	page_time= _parse_page_time(page_time.text.strip())

	for p in posts: # type: BeautifulSoup
		body= p.select('.postcolor')

		# parse id / content
		p_id= body.parent['id'].replace("post-main-", "")

		for lb in body.find_all("br"):
			lb.replace_with("\n")
		text= body.get_text()

		# check if seen
		if p_id in seen:
			continue

		# parse user info
		tmp= body.parent.parent.find(class_='bigusername').find('a')
		user= dict(
			name= tmp.get_text(),
			id= re.search(r'showuser=(\d+)', tmp['href']).groups()[0]
		)

		# parse time
		post_time= p.select('.subtitle > div > span').text.strip()
		post_time= parse_post_time(post_time, page_time)

		# post index
		index= p.select('.postdetails > a').text
		index= int(index[1:])

		# return
		yield dict(
			index=index,
			id=p_id,
			text=text,
			user=user,
			time=post_time
		)


async def get_new_posts(ctx):
	# type: (AuctionContext) -> Generator[dict]
	thread_link= f"https://forums.e-hentai.org/index.php?showtopic={ctx.thread_id}"

	flag= True
	while flag:
		# inits
		page_link= f"{thread_link}&st={ctx.SEEN_POSTS['next_index']}"
		html= await get_html(page_link, ctx.session)
		flag= True

		for post in parse_page(html, ctx.SEEN_POSTS['seen']):
			yield post

			flag= False
			ctx.SEEN_POSTS['next_index']+= 1
			ctx.SEEN_POSTS['seen'].append(post['id'])

	# dont immediately update file because other steps (parsing / update / etc) may fail inbetween yields
	misc_utils.dump_json(ctx.SEEN_POSTS, ctx.SEEN_FILE)


# calculate difference btwn page time (the assumed "now") and the post time to get timestamp
def parse_post_time(text, page_time):
	# type: (str, datetime) -> float

	post_time= _parse_post_time(text, page_time)
	diff= (page_time - post_time).seconds
	assert diff > 0

	return (time.time() - diff)

def _parse_page_time(text):
	# Time is now: 26th June 2021 - 22:58

	MONTHS= ["January", "February", "March", "April", "May", "June",
			 "July", "August", "September", "October", "November", "December"]

	tmp= re.fullmatch(r'Time is now: (\d+)\w* (\w+) (\d+) - (\d+):(\d+)', text)
	assert tmp, text

	(day,month,year,hour,minute)= tmp.groups()
	month= 1 + MONTHS.index(month)

	return datetime(year, month, day, hour, minute)

def _parse_post_time(text, page_time):
	# type: (str, datetime) -> datetime

	# Jun 24 2021, 21:01
	# Yesterday, 01:50
	# Today, 04:11
	MONTHS= "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

	if "Today" in text:
		(hour,min) = re.fullmatch("Today, (\d+):(\d+)", text).groups()
		return page_time.replace(hour=hour, minute=min)
	elif "Yesterday" in text:
		day= page_time.day
		(hour,min) = re.fullmatch("Yesterday, (\d+):(\d+)", text).groups()
		return page_time.replace(day=day, hour=hour, minute=min)
	else:
		(month, day, year, hour, min)= re.fullmatch("(\w+) (\d+) (\d+), (\d+):(\d+)", text)
		month= 1 + MONTHS.index(month)
		return datetime(year, month, day, hour, min)
