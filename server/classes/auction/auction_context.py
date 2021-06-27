from utils.scraper_utils import get_session, do_hv_login, do_forum_login
from utils.config_utils import load_config
import utils, random, time

# @todo: redo context -- more aggregated instead of separate META / EQUIP_DATA, etc -- its awk to repeatedly extract key to access eq data


# use with async
class AuctionContext:
    @classmethod
    async def create(cls):
        ctx= cls()
        await ctx.do_hv_login()
        await ctx.do_forum_login()

        ctx.EQUIPS= await ctx.get_eq_cache(ctx.session)
        return ctx

    def load_paths(self):
        self.CACHE_DIR= utils.AUCTION_CACHE_DIR + self.FOLDER + "/"
        self.DATA_DIR= utils.AUCTION_DIR + self.FOLDER + "/"

        self.META_FILE= self.DATA_DIR + "meta.yaml"
        self.PROXY_FILE= self.DATA_DIR + "proxies.json"

        self.BID_FILE= self.CACHE_DIR + "bids.json"
        self.SEEN_FILE= self.CACHE_DIR + "seen_posts.json"


    def __init__(self):
        # paths
        self.CONFIG= load_config()
        self.FOLDER= self.CONFIG['current_auction']
        self.load_paths()

        # files
        self.META= utils.load_yaml(self.META_FILE, default=False, as_dict=True)

        self.BIDS= utils.load_json(self.BID_FILE,
                                   default=dict(items={}, warnings=[]))

        self.SEEN_POSTS= utils.load_json(self.SEEN_FILE,
                                         default=dict(next_index=0, seen=[]))

        self.PROXIES= utils.load_json(self.PROXY_FILE,
                                      default=dict(bids=[], codes=[], links=[]))

        self.TEMPLATES= utils.load_yaml(utils.AUCTION_TEMPLATES)
        self.FORMAT_SETTINGS= utils.load_yaml(utils.AUCTION_FORMAT_CONFIG)
        self.EQUIPS= None # load later

        # others
        self.session= get_session()
        self.thread_id= self.META['thread_id']
        self.thread_link= f"https://forums.e-hentai.org/index.php?showtopic={self.thread_id}"

    async def close(self):
        await self.session.close()

    # adds winning bid info to the data loaded from bids.json
    def get_max_bids(self):
        # inits
        ret= {}
        bid_cache= self.BIDS
        min_inc= self.CONFIG['min_bid_increment']

        # loop item categories
        for cat,item_lst in bid_cache['items'].items():
            ret[cat]= {}

            # loop bids and get max --- assumed they're ordered chronologically
            for item_code,bid_log in item_lst.items():
                bid_log.sort(key=lambda x: (x['max'], -1*x['source']['time']),
                             reverse=True)
                max_bid= bid_log[0]

                second_max= [x for x in bid_log
                             if x['source']['user']['name'] != max_bid['source']['user']['name']]
                second_max= second_max[0]['max'] if second_max else 0
                second_max= max(0, second_max)

                if max_bid['is_proxy']:
                    max_bid['visible_bid']= second_max + min_inc
                else:
                    max_bid['visible_bid']= max_bid['max']
                ret[cat][item_code]= max_bid

        return ret

    async def do_hv_login(self):
        self.session= await do_hv_login(self.session)
    async def do_forum_login(self):
        self.session= await do_forum_login(self.session)

    async def get_eq_cache(self, session):
        from .equip_parser import EquipParser
        from .equip_scraper import EquipScraper

        DATA= utils.load_json(self.CACHE_DIR + "eq_cache.json")

        # parse equips
        for group in self.META['equips']:
            items= group['items'].items()
            for _,link in items:
                eq_id,_ = EquipScraper.extract_id_key(link)
                if eq_id in DATA:
                    continue

                eq= await EquipScraper.scrape_equip(link, session)

                parser= await EquipParser.create()
                percentiles= parser.raw_stat_to_percentile(
                    name= eq['name'],
                    raw_stats= eq['base_stats'],
                    only_legendary=True
                )
                eq['percentiles']= percentiles

                assert eq['level'] > 0, eq

                DATA[eq_id]= eq
                utils.dump_json(DATA, self.CACHE_DIR + "eq_cache.json")

        return DATA


    def create_proxy_bids(self, bid_data):
        data= self.PROXIES

        # for the bid itself
        code= rand_phrase(data['codes'])
        data['codes'].append(code)

        # link to view the proxy bid
        link_key= rand_string(data['links'])
        data['links'].append(link_key)

        # time info
        start= time.time()
        end= start + self.CONFIG['proxy_ttl']

        # save
        ret= dict(code=code, key=link_key, bids=bid_data,
                  start=start, end=end)
        data['bids'].append(ret)

        utils.dump_json(self.PROXIES, self.PROXY_FILE)
        return ret

        

_dct= utils.load_yaml(utils.DICTIONARY_FILE, False)
def rand_phrase(invalid=None):
    invalid= invalid or set()

    ret= None
    while (ret in invalid) or (ret is None):
        ret= [random.choice(_dct['adjectives']),
              random.choice(_dct['nouns'])]
        ret= "".join(x.capitalize() for x in ret)

    return ret

_alphabet= "abcdefghijklmnopqrstuvwxyz1234567890"
def rand_string(invalid, n=7, alphabet=_alphabet):
    invalid= invalid or set()

    ret= None
    while (ret in invalid) or (ret is None):
        ret= "".join(random.choice(alphabet) for i in range(n))
    return ret