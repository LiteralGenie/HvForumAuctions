from .cors_handler import CorsHandler
from classes.auction import AuctionContext


def get_check(ctx):
    # type: (AuctionContext) -> type
    class CheckHandler(CorsHandler):
        def get(self):
            self.write(dict(cooldown=ctx.get_cooldown()))

    return CheckHandler

def get_update(ctx):
    # type: (AuctionContext) -> type
    class UpdateHandler(CorsHandler):
        async def get(self):
            # @todo: redirect
            await ctx.do_thread_update()

    return UpdateHandler