from classes import Server, AuctionContext
import asyncio


async def main():
    ctx= await AuctionContext.create()
    server= Server(ctx)

if __name__ == "__main__":
    loop= asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
