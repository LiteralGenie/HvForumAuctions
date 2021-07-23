from utils.auction_utils import int_to_price, get_equip_info
from classes import AuctionContext
from chromote import Chromote, ChromeTab
import asyncio, time

def executable(fn):
    def ret(self, *args, execute=True, **kwargs):
        cmds= fn(self, *args, **kwargs)

        if execute:
            self.execute(cmds)
            return []
        else:
            return cmds

    return ret

class Tab:
    ISEKAI_URL= "https://hentaiverse.org/isekai/?s=Bazaar&ss=mm&filter=new"
    PERS_URL= "https://hentaiverse.org/?s=Bazaar&ss=mm&filter=new"

    USER_INPUT= "document.querySelector('input[list=hvut-mm-userlist]')"
    SUBJECT_INPUT= """document.querySelector("#hvut-mm-userlist").previousSibling"""
    BODY_INPUT= "document.querySelector('textarea[spellcheck=false]')"
    ITEM_SEARCH_INPUT= """document.querySelector('#hvut-mm-item > div > input[placeholder=Search]')"""
    EQUIP_SEARCH_INPUT= """document.querySelector('#hvut-mm-equip > div > input[placeholder=Search]')"""
    EQUIP_BUTTON= """document.querySelector('input[value=Equipment]')"""
    CURRENCY_BUTTON= """document.querySelector('input[value="Credits / Hath"]')"""

    def __init__(self, tab):
        self.tab= tab

    def to_isk(self):
        self.tab.set_url(self.ISEKAI_URL)

    def to_pers(self):
        self.tab.set_url(self.PERS_URL)


    @executable
    def set_main(self, user=None, subject=None, body=None):
        cmds= []
        if user:    cmds.append(f"{self.USER_INPUT}.value='{user}'")
        if subject: cmds.append(f"{self.SUBJECT_INPUT}.value='{subject}'")
        if body:    cmds.append(f"{self.BODY_INPUT}.value='{body}'")

        return cmds

    @executable
    def set_item(self, item, quant, price=0):
        cmds= []
        target_row= 'document.querySelector(".nosel.itemlist > tbody > tr:not(.hvut-none)")'

        cmds+= [
            f"{self.ITEM_SEARCH_INPUT}.value=\"{item}\"",
            f"{self.ITEM_SEARCH_INPUT}.dispatchEvent(new Event('input'))",
        ]
        cmds.append([
            f"{target_row}.querySelector('.hvut-mm-count').value= {int(quant)}",
            f"{target_row}.querySelector('.hvut-mm-price').value= {int(price)}",
            f"{target_row}.querySelector('input[type=checkbox]').click()"
        ])

        return cmds

    @executable
    def set_equip(self, equip):
        cmds= []
        target_row= 'document.querySelector(".nosel.equiplist > div:not(.hvut-none)")'

        # add as string in case these commands are added to the back of the set_main list
        # (because set_main acts on the landing view, and this command can be executed from there as well)
        cmds+= [
            f"{self.EQUIP_BUTTON}.click()"
        ]
        cmds.append([
            f"{self.EQUIP_SEARCH_INPUT}.value='{equip}'",
            f"{self.EQUIP_SEARCH_INPUT}.dispatchEvent(new Event('input'))"
        ])
        cmds.append([
            f"{target_row}.querySelector('input[type=checkbox]').click()"
        ])

        return cmds

    @executable
    def set_currency(self, credits=None):
        # inits
        c_row= "document.querySelector('#hvut-mm-credits')"
        cmds= []

        # open currency section
        cmds+= [
            f"{self.CURRENCY_BUTTON}.click()"
        ]

        # attach credits
        if credits:
            cmds.append([
                f"{c_row}.querySelector('.hvut-mm-count').value={credits}",
                f"{c_row}.querySelector('[type=checkbox]').click()"
            ])

        # return
        return cmds

    # evaluates "groups" of JS strings, where each group is formed by joining consecutive strings in cmds
    # list instances within cmds are treated as their own group
    def execute(self, cmds):
        def exec(lst):
            if not lst: return
            tmp= ';\n'.join(lst)

            print(f'executing\n...\n{tmp}\n...')
            self.tab.evaluate(tmp)

        lst= []
        for x in cmds:
            if isinstance(x, list):
                exec(lst)
                lst= []

                exec(x)
                continue
            else:
                lst.append(x)
                if x is cmds[-1]:
                    exec(lst)
                    lst= []
                    continue

        assert lst == [], str(lst)

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
        ret['seller']= ctx.META['materials'].get('sellers', {}).get(item['item_code'])
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
    
    {int_to_price(item['visible_bid'])} -- {info['text']}
    
    ........................
    
    {ctx.thread_link}
    
    Thanks for choosing my auction and please check your mailbox in persistent HV~
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
        cmds+= tab.set_equip(info['name'],
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
    
    {int_to_price(item['visible_bid'])} -- {info['text']}
    """).replace("'", "\\'")

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
    item: {info['name']}
    price: {int_to_price(item['visible_bid'])}
    buyer: {item['user']}
    ........................
    {ctx.thread_link}
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

    max_bids= ctx.get_max_bids()
    for cat in max_bids.values():
        lst= sorted(list(cat.values()), key=lambda item: int(item['item_code']))
        for item in lst:
            print("\n" + str(item))

            # inp= input("Skip? ")
            inp= "0"
            if inp.lower() in "1 y".split():
                continue

            tabs= [Tab(chrome.add_tab()) for i in range(3)]
            do_isekai(item, tabs[0], ctx)
            do_persistent(item, tabs[1], ctx)
            do_seller(item, tabs[2], ctx)

    await ctx.close()

asyncio.run(main())