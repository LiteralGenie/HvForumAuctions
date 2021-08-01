from classes import AuctionContext
from utils.auction_utils import get_equip_info
from tools.tool_utils import TabGenerator, Tab, strip_para
from chromote import Chromote
import asyncio


def get_info(cat, code, ctx):
    abbrv= f"[{cat}_{code}]"
    ret= dict(is_mat=False)

    if cat == "Mat":
        [quant,name]= ctx.META['materials']['items'][code]
        ret['text']= f"{abbrv} {quant}x {name}"
        ret['is_mat']= True
        ret['quant']= quant
        ret['name']= name
        ret['seller']= ctx.META['materials'].get('sellers', {}).get(code, '프레이')
    else:
        info= get_equip_info(cat, code, ctx.META, ctx.EQUIPS)
        ret['text']= f"{abbrv} {info['name']}"
        ret['name']= info['name']
        ret['eid']= info['eid']
        ret['seller']= info['seller']

    return ret


async def main():
    chrome= Chromote()
    ctx= await AuctionContext().create()

    header= f"Your auction items have been listed!\n\n{ctx.thread_link}\n\n............................"

    sellers= dict()
    for cat in ctx.META['equips'] + [ctx.META['materials']]:
        for code,name in cat.get('sellers', {}).items():
            info= get_info(cat['abbreviation'], code, ctx)
            sellers.setdefault(name, [])\
                   .append(info['text'])

    gen= TabGenerator(chrome, n=1)

    for name,items in sellers.items():
        item_str= '\n\n'.join(items)
        body= strip_para(f"""
        Your items have been listed in [{ctx.META['name']}] !
        
        {ctx.thread_link}
        
        ....................................
        
        {item_str}
        """, appos=False)

        tab= gen.get_tab()
        tab.to_isk()
        cmds= tab.set_main(user=name, subject="Auction Items", body=body)
        tab.execute(cmds)

asyncio.run(main())