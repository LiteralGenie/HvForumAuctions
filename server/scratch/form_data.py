import asyncio
from utils.auction_utils import scan_updates, update_thread
from classes import AuctionContext

async def main():
    ctx= await AuctionContext.create()
    data= ctx.get_max_bids()
    print('done')

asyncio.run(main())