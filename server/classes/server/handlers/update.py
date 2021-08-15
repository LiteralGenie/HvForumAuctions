from .cors_handler import CorsHandler
from classes.auction import AuctionContext
import time


def get_check(ctx):
    # type: (AuctionContext) -> type
    class CheckHandler(CorsHandler):
        def get(self):
            self.write(dict(cooldown=ctx.get_cooldown()))

    return CheckHandler

def get_update(ctx, force=False):
    # type: (AuctionContext, bool) -> type
    class UpdateHandler(CorsHandler):
        async def get(self):
            if time.time() < ctx.META['end'] or force:
                await ctx.do_thread_update()
            if not int(self.get_argument('no_redirect', "0")):
                self.redirect(ctx.thread_link)

    return UpdateHandler