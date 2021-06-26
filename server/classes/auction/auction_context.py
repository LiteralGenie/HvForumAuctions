from utils.scraper_utils import get_session, do_hv_login, do_forum_login
from utils.config_utils import load_config
import utils

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

	def __init__(self):
		# paths
		self.CONFIG= load_config()
		self.folder= self.CONFIG['current_auction']

		self.CACHE_DIR= f"{utils.AUCTION_CACHE_DIR}{self.folder}/"

		self.META= utils.load_yaml(utils.AUCTION_DIR + f"{self.folder}.yaml",
								   default=False,
								   as_dict=True)
		self.BIDS= utils.load_json(self.CACHE_DIR + "bids.json",
												default=dict(items={}, warnings=[]))
		self.SEEN_POSTS= utils.load_json(self.CACHE_DIR + "seen_posts.json",
													  default=dict(next_index=0, seen=[]))
		self.SEEN_MMS= utils.load_json(self.CACHE_DIR + "seen_mms.json",
													default=dict(seen=[]))
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

