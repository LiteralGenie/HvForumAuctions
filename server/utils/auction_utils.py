from .scraper_utils import get_html, get_soup
from . import misc_utils, global_utils
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Generator
import re, random, time


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


def update_bid_cache(bid, ctx):
    class UpdateError(Exception):
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
                cat= ctx.META['materials']['abbreviation']
                lst= ctx.META['materials']['items']
            else:
                raise UpdateError(1) # bad category

        # get id
        for item_id,item in lst.items():
            code= bid['item_code']
            if str(item_id) == str(code):
                ret= dict(cat=str(cat), id=str(item_id))
                break
        else:
            raise UpdateError(2) # bad item number

        # check min increment
        min_inc= ctx.CONFIG['min_bid_increment']
        if bid['max'] < min_inc:
            raise UpdateError(3)

        max_bids= ctx.get_max_bids()
        if (cat in max_bids) and (item_id in max_bids[cat]):
            mx= max_bids[cat][item_id]
            if bid['max'] < mx['visible_bid'] + min_inc:
                raise UpdateError(3)

        return ret


    try:
        result= update()
        cat= result['cat']
        item_id= result['id']

        ctx.BIDS['items'].setdefault(cat, {}).setdefault(item_id, [])
        ctx.BIDS['items'][cat][item_id].append(bid)
    except UpdateError as e:
        bid['fail_code']= str(e)
        ctx.BIDS['warnings'].append(bid)

    # return
    return ctx.BIDS


def parse_proxy_code(text, user, pending_bids):
    for pb in pending_bids['bids']:
        if pb['code'].lower() in text.lower():
            if pb['user'].lower() == user.lower():
                return pb


def parse_forum_bid(text):
    # inits
    regex=  "(?:\[|\s)*" # leading bracket -->  [
    regex+= "([a-z]+)(?:\s|_)*(\d+)" # item code -->  item00
    regex+= "(?:\]|\s)+" # closing bracket -->  ]
    regex+= "(\d+\.?\d*)\s*(b|m|k|c)?" # bid  -->  50k

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

    page_time= soup.select_one('#gfooter tr > td:nth-child(3)') # tbody is missing
    page_time= _parse_page_time(page_time.text.strip())

    for p in posts: # type: BeautifulSoup
        body= p.select_one('.postcolor')

        # parse id / content
        pid= body.parent['id'].replace("post-main-", "")

        for lb in body.find_all("br"):
            lb.replace_with("\n")
        text= body.get_text()

        # check if seen
        if pid in seen:
            continue

        # parse user info
        tmp= body.parent.parent.find(class_='bigusername').find('a')
        name= tmp.text
        uid= re.search(r'showuser=(\d+)', tmp['href']).groups()[0]

        # parse time
        post_time= p.select_one('.subtitle > div > span').text.strip()
        post_time= parse_post_time(post_time, page_time)

        # post index
        index= p.select_one('.postdetails > a').text
        index= int(index[1:])

        # return
        yield dict(
            index=index,
            uid=uid,
            pid=pid,
            text=text,
            user=name,
            time=post_time
        )


async def get_new_posts(ctx):
    # type: (AuctionContext) -> Generator[dict]

    thread_link= f"https://forums.e-hentai.org/index.php?showtopic={ctx.thread_id}"

    flag= True
    while flag:
        # inits
        page_link= f"{thread_link}&st={ctx.SEEN_POSTS['next_index']}"
        print('getting', page_link) #@todo log
        html= await get_html(page_link, ctx.session)
        flag= False

        for post in parse_page(html, ctx.SEEN_POSTS['seen']):
            yield post

            flag= True
            ctx.SEEN_POSTS['next_index']+= 1
            ctx.SEEN_POSTS['seen'].append(post['pid'])

    # dont immediately update file because other steps (parsing / update / etc) may fail inbetween yields
    misc_utils.dump_json(ctx.SEEN_POSTS, ctx.SEEN_FILE)


# calculate difference btwn page time (the assumed "now") and the post time to get timestamp
def parse_post_time(text, page_time):
    # type: (str, datetime) -> float

    post_time= _parse_post_time(text, page_time)
    diff= (page_time - post_time).total_seconds()
    assert diff > -10
    diff= max(diff,0)

    return (time.time() - diff)

def _parse_page_time(text):
    # Time is now: 26th June 2021 - 22:58

    MONTHS= ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]

    tmp= re.fullmatch(r'Time is now: (\d+)\w* (\w+) (\d+) - (\d+):(\d+)', text)
    assert tmp, text

    lst= list(tmp.groups())
    lst[1]= 1 + MONTHS.index(lst[1])
    [day,month,year,hour,minute]= [int(x) for x in lst]

    return datetime(year, month, day, hour, minute)

def _parse_post_time(text, page_time):
    # type: (str, datetime) -> datetime

    # Jun 24 2021, 21:01
    # Yesterday, 01:50
    # Today, 04:11
    MONTHS= "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

    if "Today" in text:
        [hour,min] = [int(x) for x in re.fullmatch("Today, (\d+):(\d+)", text).groups()]
        return page_time.replace(hour=hour, minute=min)
    elif "Yesterday" in text:
        day= int(page_time.day)
        [hour,min] = [int(x) for x in re.fullmatch("Yesterday, (\d+):(\d+)", text).groups()]
        return page_time.replace(day=day, hour=hour, minute=min)
    else:
        lst= list(re.fullmatch("(\w+) (\d+) (\d+), (\d+):(\d+)", text).groups())
        lst[0]= 1 + MONTHS.index(lst[0])
        (month, day, year, hour, min)= [int(x) for x in lst]

        return datetime(year, month, day, hour, min)

_dct= misc_utils.load_yaml(global_utils.DICTIONARY_FILE, False)
def rand_phrase(invalid=None):
    invalid= invalid or set()

    ret= None
    while (ret in invalid) or (ret is None):
        ret= [
            random.choice(_dct['adjectives']),
            random.choice(_dct['adjectives']),
            random.choice(_dct['nouns']),
        ]
        ret= "".join(x.capitalize() for x in ret)

    return ret

_alphabet= "abcdefghijklmnopqrstuvwxyz1234567890"
def rand_string(invalid, n=7, alphabet=_alphabet):
    invalid= invalid or set()

    ret= None
    while (ret in invalid) or (ret is None):
        ret= "".join(random.choice(alphabet) for i in range(n))
    return ret

def get_equip_info(cat, code, meta, equips):
    from classes import EquipScraper

    for dct in meta['equips']:
        if dct['abbreviation'] == cat:
            link= dct['items'][code]
            eid= EquipScraper.extract_id_key(link)[0]
            name= equips[eid]['name']

            return dict(name=name, link=link)
