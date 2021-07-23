import os.path

from .cors_handler import CorsHandler
from classes import AuctionContext, EquipScraper
from utils.auction_utils import get_equip_info
import utils, glob


LOG_HISTORY= dict()
async def load_ctx(folder, default_ctx):
    try:
        folder= str(folder)
        if default_ctx.FOLDER == folder:
            ctx= default_ctx
        else:
            ctx= LOG_HISTORY.get(folder, await AuctionContext.create(folder=folder, session=default_ctx.session))

        LOG_HISTORY[folder]= ctx
        return ctx
    except FileNotFoundError:
        raise

def api_get(current_ctx):
    # type: (AuctionContext) -> type
    global LOG_HISTORY


    class ApiGetHandler(CorsHandler):
        async def get(self):
            folder= self.get_argument("id", None)
            if folder:
                try:
                    ctx= await load_ctx(folder, current_ctx)
                    return await self._get(ctx)
                except FileNotFoundError:
                    print(f"WARNING: invalid id for api/logs: {folder}")

            self.write(list_logs(current_ctx))

        async def _get(self, ctx):
            is_current= (ctx is current_ctx)

            ret= dict()
            max_bids= ctx.get_max_bids()

            ret['auction_name']= ctx.META.get('name', "Genie's Bottle")
            ret['auction_link']= ctx.thread_link
            ret['start']= ctx.META.get('start', ctx.META['end'] - 3*86400)
            ret['end']= ctx.META['end']
            ret['last_update']= ctx.last_check
            ret['is_current']= is_current

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
                        tmp= ctx.META['materials']['items'][code]
                        item_info['name']= f"{tmp[0]}x {tmp[1]}"

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

def get(current_ctx):
    class LogHandler(CorsHandler):
        async def get(self):
            folder= self.get_argument("id", None)

            if folder:
                await load_ctx(folder, current_ctx)
                return self.render(utils.PAGES_DIR + "log.html")
            else:
                return self.render(utils.PAGES_DIR + "log_list.html")


    return LogHandler

def list_logs(ctx):
    folders= glob.glob(utils.AUCTION_DIR + "*")

    metas= []
    for x in folders:
        file= x + "/meta.yaml"
        if os.path.exists(file):
            metas.append(file)
    metas= [utils.load_yaml(x) for x in metas]
    metas.sort(key=lambda x: float(x['number']))

    ret= dict(info_link=ctx.CONFIG['info_link'])

    ret['logs']= []
    for data in metas:
        folder= os.path.basename(os.path.dirname(x))
        end= data['end']
        start= data.get('start', end - 3*86400)

        ret['logs'].append(dict(
            name=data.get('name', "Genie's Bottle"),
            link=f"/logs?id={folder}",
            start=start,
            end=end,
        ))

    return list(reversed(ret))