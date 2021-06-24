import asyncio
from utils.auction_utils import scan_updates, update_thread
from classes import AuctionContext

async def main():
    ctx= await AuctionContext.create()
    await scan_updates(ctx)
    await update_thread(ctx)
    await ctx.close()
    print('done')

asyncio.run(main())