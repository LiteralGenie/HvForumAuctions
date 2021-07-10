from utils.auction_utils import int_to_price, get_equip_info
from classes import AuctionContext
from chromote import Chromote, ChromeTab
import asyncio, time


ISEKAI_URL= "https://hentaiverse.org/isekai/?s=Bazaar&ss=mm&filter=new"
PERS_URL= "https://hentaiverse.org/?s=Bazaar&ss=mm&filter=new"

USER_INPUT= "document.querySelector('input[list=hvut-mm-userlist]')"
SUBJECT_INPUT= """document.querySelector("#hvut-mm-userlist").previousSibling"""
BODY_INPUT= "document.querySelector('textarea[spellcheck=false]')"
ITEM_SEARCH_INPUT= """document.querySelector('#hvut-mm-item > div > input[placeholder=Search]')"""
EQUIP_SEARCH_INPUT= """document.querySelector('#hvut-mm-equip > div > input[placeholder=Search]')"""
EQUIP_BUTTON= """document.querySelector('input[value=Equipment]')"""


def execute(tab, *cmds):
    for x in cmds:
        print(f'executing -- ', x)
    tab.evaluate(';'.join(cmds))
    time.sleep(.25)

def strip_para(text):
    split= text.split("\n")
    split= [x.strip() for x in split]

    ret= "\n".join(split)
    ret= ret.strip().replace("\n", "\\n")
    return ret

def get_info(item, ctx):
    # type: (dict, AuctionContext) -> dict

    abbrv= f"[{item['item_type']}_{item['item_code']}]"
    ret= dict(is_mat=False)

    if item['item_type'] == "Mat":
        [quant,name]= ctx.META['materials']['items'][item['item_code']]
        ret['text']= f"{abbrv} {quant}x {name}"
        ret['is_mat']= True
        ret['quant']= quant
        ret['name']= name
    else:
        info= get_equip_info(item['item_type'], item['item_code'], ctx.META, ctx.EQUIPS)
        ret['text']= f"{abbrv} {info['name']}"
        ret['name']= info['name']
        ret['eid']= info['eid']

    return ret

def get_tab(chrome):
    # type: (Chromote) -> ChromeTab

    tabs= chrome.tabs
    for i,x in enumerate(tabs):
        print(f"{i} - {x}")
    ind= int(input("tab index? "))

    return tabs[ind]

def do_isekai(item, tab, ctx):
    # type: (dict, ChromeTab, AuctionContext) -> None

    # inits
    info= get_info(item, ctx)
    tab.set_url(ISEKAI_URL); time.sleep(1)

    # set user / subject / body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:

    ........................
    
    {int_to_price(item['visible_bid'])} -- {info['text']}
    
    ........................
    
    Thanks for choosing my auction and please check your mailbox in persistent HV~
    """).replace("'", "\\'")

    execute(tab, f"{USER_INPUT}.value='{item['user']}'",
                 f"{SUBJECT_INPUT}.value='Auction Items'",
                 f"{BODY_INPUT}.value='{msg}'")

    # set item
    if info['is_mat']:
        execute(tab, f"{ITEM_SEARCH_INPUT}.value=\"{info['name']}\"",
                     f"{ITEM_SEARCH_INPUT}.dispatchEvent(new Event('input'))")

        target_row= 'document.querySelector(".nosel.itemlist > tbody > tr:not(.hvut-none)")'
        execute(tab, f"{target_row}.querySelector('.hvut-mm-count').value= {info['quant']}",
                     f"{target_row}.querySelector('input[type=checkbox]').click()")
    else:
        execute(tab, f"{EQUIP_BUTTON}.click()")
        execute(tab, f"{EQUIP_SEARCH_INPUT}.value='{info['name']}'")
        execute(tab, f"{EQUIP_SEARCH_INPUT}.dispatchEvent(new Event('input'))")

        target_row= 'document.querySelector(".nosel.equiplist > div:not(.hvut-none)")'
        execute(tab, f"{target_row}.querySelector('input[type=checkbox]').click()")

    input('Waiting for send... ')
    return

def do_persistent(item, tab, ctx):
     # inits
    info= get_info(item, ctx)
    tab.set_url(PERS_URL); time.sleep(1)

    # set body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:

    ........................
    
    {int_to_price(item['visible_bid'])} -- {info['text']}
    """).replace("'", "\\'")


    target_row= 'document.querySelector(".nosel.itemlist > tbody > tr:not(.hvut-none)")'
    execute(tab,
            # set target
            f"{USER_INPUT}.value='{item['user']}'",
            f"{SUBJECT_INPUT}.value='Auction Items'",
            f"{BODY_INPUT}.value='{msg}'",
            # set CoD
            f"{target_row}.querySelector('.hvut-mm-count').value= 1",
            f"{target_row}.querySelector('.hvut-mm-price').value= {int(item['visible_bid'])}",
            f"{target_row}.querySelector('input[type=checkbox]').click()")

    input('Waiting for send... ')
    return

async def main():
    chrome= Chromote()
    tab= get_tab(chrome)
    ctx= await AuctionContext.create()

    max_bids= ctx.get_max_bids()
    for cat in max_bids.values():
        for item in cat.values():
            print("\n" + str(item))

            inp= input("Skip? ")
            if inp in "1 y".split():
                continue

            do_isekai(item, tab, ctx)
            do_persistent(item, tab, ctx)

    await ctx.close()

asyncio.run(main())