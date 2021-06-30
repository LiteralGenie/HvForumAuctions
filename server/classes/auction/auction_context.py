from utils.scraper_utils import get_session, do_hv_login, do_forum_login
from utils.config_utils import load_config
from utils.auction_utils import get_new_posts, parse_proxy_code, parse_forum_bid, update_bid_cache, rand_string, rand_phrase
from utils.template_utils import render
import utils, time, re, json, copy

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

    # ensure string keys
    def load_META(self):
        meta= utils.load_yaml(self.META_FILE, default=False, as_dict=True)

        dcts= [*meta.get('equips', []), meta.get('materials', {})]
        for d in dcts:
            if d == {}:
                return
            d['items']= { str(x):y for x,y in d['items'].items() }

        self.META= meta
        return meta


    def __init__(self):
        # paths
        self.CONFIG= load_config()
        self.FOLDER= str(self.CONFIG['current_auction'])
        self.load_paths()

        # files
        self.META= self.load_META()

        self.BIDS= utils.load_json(self.BID_FILE,
                                   default=dict(items={}, warnings=[]))

        self.SEEN_POSTS= utils.load_json(self.SEEN_FILE,
                                         default=dict(next_index=0, seen=[]))

        self.PROXIES= utils.load_json(self.PROXY_FILE,
                                      default=dict(bids=[], codes=[], keys=[]))

        self.TEMPLATES= utils.load_yaml(utils.AUCTION_TEMPLATES)
        self.FORMAT_SETTINGS= utils.load_yaml(utils.AUCTION_FORMAT_CONFIG)
        self.EQUIPS= None # load later

        # others
        self.last_check= 0
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
                bid_log= copy.deepcopy(bid_log)

                # remove bids that don't satisfy the min increment
                prev_bid=0
                while True:
                    for i,x in enumerate(bid_log):
                        if x['max'] < prev_bid + min_inc:
                            bad= i
                            break
                    else:
                        break

                    del bid_log[i]

                if not bid_log:
                    continue

                # sort
                bid_log.sort(key=lambda x: (x['max'], -1*x['time']),
                             reverse=True)
                max_bid= bid_log[0]

                # get runner-up in case highest bid is proxy
                try:
                    tmp= (x for x in bid_log
                          if x['user'] != max_bid['user'] or not x['is_proxy'])
                    second_max= next(tmp)

                    if second_max['user'] == max_bid['user']:
                        next_bid= second_max['max']
                    else:
                        next_bid= second_max['max'] + min_inc

                    next_bid= max(next_bid, 0)
                except StopIteration:
                    next_bid= 0

                # get bid value to display
                # @todo: warning for insufficient bid increment
                if max_bid['is_proxy']:
                    max_bid['visible_bid']= min(next_bid, max_bid['max'])
                else:
                    max_bid['visible_bid']= max_bid['max']

                if max_bid['max'] >= min_inc:
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
        link_key= rand_string(data['keys'])
        data['keys'].append(link_key)

        # time info
        start= time.time()
        end= start + self.CONFIG['proxy_ttl']

        # save
        ret= dict(code=code, key=link_key,
                  user=bid_data['user'], items=bid_data['items'],
                  start=start, end=end, confirmed=False)
        data['bids'].append(ret)

        utils.dump_json(self.PROXIES, self.PROXY_FILE)
        return ret

    def get_cooldown(self):
        ret= time.time() - self.last_check # time elapsed
        ret= self.CONFIG['update_cooldown'] - ret # positive if cooldown present
        return max(ret,0) # lift negative cooldowns to 0s

    async def do_thread_update(self):
        if await self.do_thread_scan():
            await self._update_thread()

    async def do_thread_scan(self):
        if self.get_cooldown() <= 0:
            await self._scan_updates()
            return True
        return None

    async def _scan_updates(self):
        # type: (AuctionContext) -> bool
        # @todo: log

        # get unread posts
        has_new= False
        posts= get_new_posts(self)
        async for p in posts:
            if p['index'] < int(self.CONFIG['ignore_first_n']):
                continue
            has_new= True

            # parse post text for bid-code (item##)
            lst= parse_forum_bid(p['text'])

            # match bid-code with items for sale
            for b in lst:
                cpy= p.copy()
                tmp= dict(is_proxy=False, source=cpy)
                tmp['user']= cpy.pop('user')
                tmp['time']= cpy.pop('time')

                b.update(tmp)
                self.BIDS= update_bid_cache(b, self)

            # parse post text for proxy code --- 1 per post
            proxy_bid= parse_proxy_code(p['text'], p['user'], self.PROXIES)
            if proxy_bid:
                proxy_bid['confirmed']= True
                for it in proxy_bid['items']:
                    tmp= dict()
                    tmp['item_type']= it['cat']
                    tmp['item_code']= it['code']
                    tmp['max']= it['bid']
                    tmp['is_proxy']= True
                    tmp['user']= proxy_bid['user']
                    tmp['time']= proxy_bid['start']
                    tmp['source']= dict(
                        code=proxy_bid['code'],
                        key=proxy_bid['key'],
                    )

                    self.BIDS= update_bid_cache(tmp, self)

        # return
        self.last_check= time.time()
        utils.dump_json(self.BIDS, self.BID_FILE)
        utils.dump_json(self.PROXIES, self.PROXY_FILE)
        return has_new

    async def _update_thread(self):
        # inits
        await self.do_forum_login()

        # get highest bids for each item
        max_bids= self.get_max_bids()

        md5= self.CONFIG['post_key']

        # todo: "".join(f"%u{ord(x):04x}.upper()" for x in text)
        cln= lambda x: re.sub(r'\\u(\w{4})', lambda m: rf'%u{m.group(1).upper()}', json.dumps(x)).replace(r"\n", "\n")[1:-1]
        payload_template= dict(
            f=self.CONFIG['forum_number'],
            t=self.META['thread_id'],
            md5check= md5,
            act='xmlout',
            do='post-edit-save',
            std_used=1
        )

        # edit post with items
        tmp= payload_template.copy()
        tmp['Post']= cln(render(self.TEMPLATES['main_post'], max_bids=max_bids, **self.__dict__))
        tmp['p']= self.META['main_post_id']
        resp= await self.session.post('https://forums.e-hentai.org/index.php', data=tmp)
        assert resp.status == 200

        # edit post with warning log
        tmp= payload_template.copy()
        tmp['Post']= cln(render(self.TEMPLATES['warning_post'], max_bids=max_bids, **self.__dict__))
        tmp['p']= self.META['warning_post_id']
        resp= await self.session.post('https://forums.e-hentai.org/index.php', data=tmp)
        assert resp.status == 200