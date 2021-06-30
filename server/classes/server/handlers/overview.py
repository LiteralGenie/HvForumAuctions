from .cors_handler import CorsHandler
from classes import AuctionContext, EquipScraper
from utils.auction_utils import get_equip_info
import utils


def get(ctx):
    # type: (AuctionContext) -> type
    class OverviewGetHandler(CorsHandler):
        def get(self):
            print('here')
            return self.render(utils.PAGES_DIR + "overview.html")

    return OverviewGetHandler


def api_get(ctx):
    # type: (AuctionContext) -> type
    class ApiGetHandler(CorsHandler):
        def get(self):
            print('here2')
            ret= dict()
            max_bids= ctx.get_max_bids()

            ret['auction_name']= ctx.META.get('name', "Genie's Bottle")
            ret['auction_link']= ctx.thread_link
            ret['start']= ctx.META.get('start', ctx.META['end'] - 3*86400)
            ret['end']= ctx.META['end']

            ret['items']= []
            lst= [*ctx.META['equips'], ctx.META['materials']]
            for x in lst:
                cat= x['abbreviation']
                for code,it in x['items'].items():
                    # basic item info
                    item_info= dict()
                    item_info['cat']= cat
                    item_info['code']= code

                    if info := get_equip_info(cat, code, ctx.META, ctx.EQUIPS):
                        item_info['name']= info['name']
                        item_info['link']= info['link']
                    else:
                        item_info['name']= ctx.META['materials']['items'][code]

                    # add bids
                    item_info['bids']= []
                    bid_lst= ctx.BIDS['items'].get(cat, {}).get(code, [])
                    for bid in bid_lst:
                        mx= max_bids[cat][code]
                        bid_dct= dict()

                        if bid['time'] == mx['time']:
                            bid_dct['bid']= mx['visible_bid']
                            bid_dct['is_winner']= True
                        else:
                            bid_dct['bid']= min(bid['max'], mx['visible_bid'])
                            bid_dct['is_winner']= False

                        bid_dct['user']= bid['user']
                        bid_dct['time']= bid['time']
                        bid_dct['is_proxy']= bid['is_proxy']

                        item_info['bids'].append(bid_dct)

                    ret['items'].append(item_info)

            self.write(ret)
    return ApiGetHandler