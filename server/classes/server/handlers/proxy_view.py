"""
Example GET response
{
  "view": {
        "user": "user_user",
        "confirmed": false,
        "key": "key_key",
        "code": "code_code",
        "start": 1624804494,
        "end": 1624805094,

        "thread": "https://forums.e-hentai.org/index.php?showtopic=249142",

        "items": [
            { "cat": "Wep",
                "code": "1",
                "bid": 25000,

                "name": "Legendary Ethereal Shortsword of Slaughter",
                "link": "https://hentaiverse.org/isekai/equip/45866/1f7cadc535",
                "winner": {
                    "user": "user that isnt you",
                    "bid": 1000000
                }},
            {
                "cat": "Arm",
                "code": "3",
                "bid": 125000,

                "name": "item 2",
                "link": "https://hentaiverse.org/isekai/equip/45866/1f7cadc535",
                "winner": {
                    "user": "user_user",
                    "bid": 12500
                }},
            {
                "cat": "Mat",
                "code": "5",
                "bid": 125000,

                "name": "mat 2",
                "winner": {
                    "user": "user_user",
                    "bid": 12500
                }}
        ]
    }
}

Example POST payload
{
    "user": blahblah
    "items": [
        { "cat": "Wep", "code": "1", "bid": 25000},
        { "cat": "Arm", "code": "3", "bid": 123458},
    ]
}
"""

import utils
from .cors_handler import CorsHandler
from classes.auction import AuctionContext, EquipScraper
import json


def get_user_view(ctx):
    # type: (AuctionContext) -> type
    class UserViewHandler(CorsHandler):
        # get landing page for viewing bids
        def get(self):
            self.render(utils.PAGES_DIR + "proxy_view.html")

    return UserViewHandler

def get_api_view(ctx):
    # type: (AuctionContext) -> type
    class ApiViewHandler(CorsHandler):
        # summarize and repackage meta / bid info for frontend
        def get(self):
            # inits
            max_bids= ctx.get_max_bids()

            # retrieve proxy bid
            key= self.get_argument('key', None)
            if key is None:
                return self.write('no key supplied')
            if key not in ctx.PROXIES['keys']:
                return self.write('invalid key')

            proxy_bid= next(x for x in ctx.PROXIES['bids'] if x['key'] == key)

            # add extra info
            ret= json.loads(json.dumps(proxy_bid))
            ret['thread']= ctx.thread_link

            for item in ret['items']:
                try:
                    mx= max_bids[item['cat']]
                    mx= mx[item['code']]

                    bid= mx['visible_bid']
                    user= mx['user']
                except KeyError:
                    bid= 0
                    user= ""

                item['winner']= dict(user=user, bid=bid)

                # concat if material
                cat= get_meta_cat(item['cat'])
                info= cat['items'][str(item['code'])]

                # if material...
                if isinstance(info, list):
                    item['name']= f"{info[0]}x {info[1]}"
                # else equip...
                else:
                    item['link']= info
                    eid= EquipScraper.extract_id_key(info)[0]
                    item['name']= ctx.EQUIPS[eid]['name']

            self.write(ret)

    def get_meta_cat(cat):
        for dct in [*ctx.META['equips'], ctx.META['materials']]:
            if dct['abbreviation'] == cat:
                return dct
        else:
            raise KeyError

    return ApiViewHandler