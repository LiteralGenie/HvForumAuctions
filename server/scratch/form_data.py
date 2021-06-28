import asyncio
from classes import AuctionContext

async def main():
    ctx= await AuctionContext.create()
    data= ctx.get_max_bids()
    print('done')

asyncio.run(main())