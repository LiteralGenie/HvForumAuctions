from dataclasses import dataclass

from classes import AuctionContext
from utils.auction_utils import get_equip_info


@dataclass
class ItemInfo:
    is_mat: bool
    text: str
    name: str
    seller: str

    quant: int = 0
    eid: int = None

    def __post_init__(self):
        self.eid = int(self.eid) if self.eid else self.eid

@dataclass
class BidInfo:
    item_type: str
    item_code: int
    max: int
    is_proxy: bool
    user: str
    time: float
    source: dict
    visible_bid: int

    def __post_init__(self):
        self.item_code = int(self.item_code)

class AucItem(BidInfo, ItemInfo):
    def __init__(self, bid: BidInfo, item: ItemInfo):
        self.__dict__ = { **bid.__dict__, **item.__dict__ }


def get_info(item_type: str, item_code: str, ctx: AuctionContext) -> ItemInfo:
    abbrv= f"[{item_type}_{item_code}]"

    if item_type == "Mat":
        [quant,name]= ctx.META['materials']['items'][item_code]
        return ItemInfo(
            is_mat=True,
            text= f"{abbrv} {quant}x {name}",
            quant=quant,
            name=name,
            seller=ctx.META['materials'].get('sellers', {}).get(item_code, '프레이')
        )
    else:
        info= get_equip_info(item_type, item_code, ctx.META, ctx.EQUIPS)
        return ItemInfo(
            is_mat=False,
            text= f"{abbrv} {info['name']}",
            name=info['name'],
            eid=info['eid'],
            seller=info['seller'],
        )