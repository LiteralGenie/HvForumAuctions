from classes import AuctionContext
import asyncio

from tools.tool_utils.auc import get_info
from tools.tool_utils.misc import strip_para
from tools.tool_utils.mm import HvSession, MoogleMail


async def main():
    ctx= await AuctionContext().create()
    session = HvSession(user=ctx.CONFIG['forum_name'], pw=ctx.CONFIG['forum_pass']).login()
    mm_isk = MoogleMail(session=session, isekai=True)

    sellers= dict()
    for cat in ctx.META['equips'] + [ctx.META['materials']]:
        for code,name in cat.get('sellers', {}).items():
            info = get_info(cat['abbreviation'], code, ctx)
            sellers.setdefault(name, []).append(info.text)

    for name,items in sellers.items():
        item_str= '\n\n'.join(items)
        body= strip_para(f"""
        Your items have been listed in [{ctx.META['name']}] !
        
        {ctx.thread_link}
        
        ....................................
        
        {item_str}
        """)

        print('Notifying', name)
        mm_isk.send(user=name, subject="Auction Start", body=body)

asyncio.run(main())