from classes import Server, AuctionContext
import asyncio


async def main():
    ctx= await AuctionContext.create()
    server= Server(ctx)

    async def auto_update():
        while True:
            print('auto updating')
            await asyncio.sleep(ctx.CONFIG['auto_update_interval'])
            await ctx.do_thread_update()

    asyncio.create_task(auto_update())


if __name__ == "__main__":
    loop= asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
