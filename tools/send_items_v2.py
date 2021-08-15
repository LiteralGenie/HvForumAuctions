import sys
from dataclasses import dataclass
from typing import List

from tools.tool_utils.auc import AucItem, get_info, BidInfo
from tools.tool_utils.misc import strip_para
from tools.tool_utils.mm import MoogleMail, HvSession
from utils.auction_utils import int_to_price
from classes import AuctionContext
import asyncio, logging


# LOGGING ---

# noinspection PyArgumentList
logging.basicConfig(level=logging.WARNING,
                    handlers=[logging.FileHandler(filename="./unsold.log",
                                                 encoding='utf-8', mode='a+')])

# ---

def do_isekai(item: AucItem, ctx: AuctionContext, mm: MoogleMail) -> None:
    # attach
    if item.is_mat:
        mm.attach_item(item.name, item.quant)
    else:
        mm.attach_equip(item.eid)

    # set user / subject / body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:
    ........................
    item: {item.text}
    price: {int_to_price(item.visible_bid)}
    seller: {item.seller}
    ........................
    Thanks for choosing my auction and please check your mailbox in persistent HV~
    {ctx.thread_link}
    {ctx.log_link}
    """)

    # send
    mm.send(item.user, 'Auction Purchase (item)', msg)
    return

def do_persistent(item: AucItem, ctx: AuctionContext, mm: MoogleMail) -> None:
    # set body
    msg= strip_para(f"""
    Hello, you've purchased the following item from {ctx.META['name']}:
    ........................
    item: {item.text}
    price: {int_to_price(item.visible_bid)}
    seller: {item.seller}
    ........................
    {ctx.thread_link}
    {ctx.log_link}
    """)

    # send
    mm.attach_item('Binding of Friendship', 1)
    mm.set_cod(cod=item.visible_bid)
    mm.send(item.user, 'Auction Purchase (CoD)', msg)
    return

def do_seller(item: AucItem, ctx: AuctionContext, mm: MoogleMail) -> None:
    # inits
    if item.seller is None:
        return

    # message
    msg= strip_para(f"""
    Your auction item has been sold!
    ........................
    item: {item.text}
    price: {int_to_price(item.visible_bid)}
    buyer: {item.user}
    ........................
    {ctx.thread_link}
    {ctx.log_link}
    """)

    # send
    if mm.state.credits >= item.visible_bid:
        mm.set_credits(item.visible_bid)
        mm.send(item.seller, 'Auction Earnings', msg)
    else:
        msg = f'[{ctx.META["name"]}] [to {item.seller}] not enough credits for item\n{msg}'
        logging.warning(msg)
        print(msg, file=sys.stderr)

def check_valid(items: List[AucItem], mm_ps: MoogleMail, mm_isk: MoogleMail):
    # check equips
    for it in [x for x in items if x.item_type != "Mat"]:
        mm_isk.state.get_equip(it.eid, throw=True)

    # check mat quants
    counts = dict()
    for it in [x for x in items if x.item_type == "Mat"]:
        counts[it.name] = counts.get(it.name, 0) + it.quant
        mat = mm_isk.state.get_item(it.name, throw=True)
        assert mat.quant >= counts[it.name], f"not enough {it.name}, {mat.quant} / {counts[it.name]}"

    # check bindings for CoD
    n = len(items)
    dummies = mm_ps.state.get_item('binding of friendship', throw=True)
    assert dummies.quant >= n, f'not enough bindings for CoD [{dummies.quant}x / {n}x]'

    # check credits
    total = int(sum(it.visible_bid for it in items))
    if total > mm_ps.state.credits:
        print(f'warning: not enough credits [{mm_ps.state.credits:,}c / {total:,}c]', file=sys.stderr)

async def main():
    # inits
    ctx= await AuctionContext.create()

    session = HvSession(user=ctx.CONFIG['forum_name'], pw=ctx.CONFIG['forum_pass']).login()
    mm_ps = MoogleMail(session=session, isekai=False)
    mm_isk = MoogleMail(session=session, isekai=True)
    items = []

    # get items
    max_bids= ctx.get_max_bids()
    for cat in max_bids.values():
        lst= sorted(list(cat.values()), key=lambda item: int(item['item_code']))
        for item in lst:
            if item['item_type'] in ['Arm'] and int(item['item_code']) < 0: continue
            if item['item_type'] in ['Wep'] and int(item['item_code']) < 999: continue
            if item['item_type'] in ['Mat'] and int(item['item_code']) < 999: continue
            # if item['item_type'] in ['Arm'] and int(item['item_code']) not in []: continue
            # if item['item_type'] in ['Wep'] and int(item['item_code']) not in []: continue
            # if item['item_type'] in ['Mat'] and int(item['item_code']) not in []: continue

            # inp= input("Skip? ")
            inp= "0"
            if inp.lower() in "1 y".split():
                continue

            info = get_info(item['item_type'], item['item_code'], ctx)
            items.append(
                AucItem(BidInfo(**item), info)
            )

    # check validity
    check_valid(items, mm_ps, mm_isk)

    # send
    for item in items:
        print(f"{item.seller} -> {item.user} --- {item.visible_bid} --- {item.text}")
        print('sending CoD')
        do_persistent(item, ctx, mm_ps)
        print('sending item')
        do_isekai(item, ctx, mm_isk)
        print('sending credits')
        do_seller(item, ctx, mm_ps)


    await ctx.close()




asyncio.run(main())