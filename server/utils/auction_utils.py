from .scraper_utils import get_html, get_soup
from . import misc_utils
from .template_utils import render
from bs4 import BeautifulSoup
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
				is_forum_post=True,
				is_proxy=False,
				source=p,
			))
			ctx.BIDS= update_bid_cache(b, ctx)

	# return
	misc_utils.dump_json(ctx.BIDS, ctx.CACHE_DIR + "bids.json")
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

async def get_new_posts(ctx):
	thread_link= f"https://forums.e-hentai.org/index.php?showtopic={ctx.thread_id}"
	# get new posts
	break_flag= False
	while not break_flag:
		# inits
		page_link= f"{thread_link}&st={ctx.SEEN_POSTS['next_index']}"
		break_flag= True

		# get page
		html= await get_html(page_link, ctx.session)
		soup= BeautifulSoup(html, 'html.parser')
		posts= soup.find_all(class_='postcolor')

		for x in posts:
			# parse id / content
			p_id= x.parent['id'].replace("post-main-", "")

			for lb in x.find_all("br"):
				lb.replace_with("\n")
			text= x.get_text()

			# check if seen
			if p_id in ctx.SEEN_POSTS['seen']:
				continue

			# parse user info
			tmp= x.parent.parent.find(class_='bigusername').find('a')
			user= dict(
				name= tmp.get_text(),
				id= re.search(r'showuser=(\d+)', tmp['href']).groups()[0]
			)

			# return
			break_flag= False
			yield dict(
				index= ctx.SEEN_POSTS['next_index'],
				id=p_id,
				text=text,
				user=user,
				time=time.time()
			)

			ctx.SEEN_POSTS['next_index']+= 1
			ctx.SEEN_POSTS['seen'].append(p_id)


	# dont immediately update file because other steps (parsing / update / etc) may fail inbetween yields
	misc_utils.dump_json(ctx.SEEN_POSTS, ctx.CACHE_DIR + "seen_posts.json")
