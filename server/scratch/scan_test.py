import asyncio
from classes import AuctionContext

async def main():
    # ctx= await AuctionContext.create()
    ctx= AuctionContext()
    max_bids= ctx.get_max_bids()
    await ctx.close()
    print('done')

asyncio.run(main())