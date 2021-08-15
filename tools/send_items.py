from utils.auction_utils import int_to_price, get_equip_info
from classes import AuctionContext
from chromote import Chromote, ChromeTab
from tools.tool_utils import TabGenerator, Tab, strip_para
import asyncio, time




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
        ret['seller']= ctx.META['materials'].get('sellers', {}).get(item['item_code'], '프레이')
    else:
        info= get_equip_info(item['item_type'], item['item_code'], ctx.META, ctx.EQUIPS)
        ret['text']= f"{abbrv} {info['name']}"
        ret['name']= info['name']
        ret['eid']= info['eid']
        ret['seller']= info['seller']

    return ret

def get_tab(chrome):
    # type: (Chromote) -> ChromeTab

    tabs= chrome.tabs
    for i,x in enumerate(tabs):
        print(f"{i} - {x}")
    ind= int(input("tab index? "))

    return tabs[ind]

def do_isekai(item, tab, ctx):
    # type: (dict, Tab, AuctionContext) -> None

    # inits
    info= get_info(item, ctx)
    tab.to_isk()

    # set user / subject / body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:
    ........................
    item: {info['text']}
    price: {int_to_price(item['visible_bid'])}
    seller: {info['seller']}
    ........................
    Thanks for choosing my auction and please check your mailbox in persistent HV~
    {ctx.thread_link}
    {ctx.log_link}
    """).replace("'", "\\'")

    # message
    cmds= tab.set_main(user=item['user'],
                       subject="Auction Purchase",
                       body=msg,
                       execute=False)

    # attach
    if info['is_mat']:
        cmds+= tab.set_item(info['name'], info['quant'],
                            execute=False)
    else:
        cmds+= tab.set_equip(info['eid'],
                             execute=False)

    # execute
    tab.execute(cmds)
    return

def do_persistent(item, tab, ctx):
    # inits
    info= get_info(item, ctx)
    tab.to_pers()

    # set body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:
    ........................
    item: {info['text']}
    price: {int_to_price(item['visible_bid'])}
    seller: {info['seller']}
    ........................
    {ctx.thread_link}
    {ctx.log_link}
    """, appos=False)

    # message
    cmds= tab.set_main(user=item['user'],
                       subject='Auction Items',
                       body=msg,
                       execute=False)

    # CoD
    cmds+= tab.set_item(item='Binding of Friendship',
                        quant=1,
                        price=item['visible_bid'],
                        execute=False)

    # execute
    tab.execute(cmds)
    return

def do_seller(item, tab, ctx):
    # type: (dict, Tab, AuctionContext) -> None

    # inits
    info= get_info(item, ctx)
    if info['seller'] is None:
        return

    tab.to_pers()

    # message
    msg= strip_para(f"""
    Your auction item has been sold!
    ........................
    item: {info['text']}
    price: {int_to_price(item['visible_bid'])}
    buyer: {item['user']}
    ........................
    {ctx.thread_link}
    {ctx.log_link}
    """)

    cmds= tab.set_main(
        user=info['seller'],
        subject='Auction Earnings',
        body=msg,
        execute=False
    )

    # credits payment
    cmds+= tab.set_currency(credits=item['visible_bid'], execute=False)

    # execute
    tab.execute(cmds)
    return


async def main():
    chrome= Chromote()
    ctx= await AuctionContext.create()
    tab_gen= TabGenerator(chrome, n=9)

    max_bids= ctx.get_max_bids()
    for cat in max_bids.values():
        lst= sorted(list(cat.values()), key=lambda item: int(item['item_code']))
        for item in lst:
            if item['item_type'] in ['Arm'] and int(item['item_code']) < 999: continue
            if item['item_type'] in ['Wep'] and int(item['item_code']) < 999: continue
            if item['item_type'] in ['Mat'] and int(item['item_code']) < 101: continue
            # if item['item_type'] in ['Arm'] and int(item['item_code']) not in []: continue
            # if item['item_type'] in ['Wep'] and int(item['item_code']) not in []: continue
            # if item['item_type'] in ['Mat'] and int(item['item_code']) not in []: continue

            print("\n" + str(item))

            # inp= input("Skip? ")
            inp= "0"
            if inp.lower() in "1 y".split():
                continue

            do_persistent(item, tab_gen.get_tab(), ctx)
            do_isekai(item, tab_gen.get_tab(), ctx)
            do_seller(item, tab_gen.get_tab(), ctx)

    await ctx.close()




asyncio.run(main())