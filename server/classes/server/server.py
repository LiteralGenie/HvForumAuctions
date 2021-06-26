from tornado.web import Application, StaticFileHandler
from classes import AuctionContext
from .proxy_form_handler import handle_proxy
from .timer_handler import handle_timer
import utils


class Server(Application):
    def __init__(self, ctx):
        # inits
        handlers= []
        self.ctx= ctx

        # routes
        handlers.append(('/proxy_form', handle_proxy(self.ctx)))
        handlers.append(('/timer', handle_timer(self.ctx)))

        handlers.append(('/((?:img|js|css)/.*)', StaticFileHandler, dict(path=utils.PAGES_DIR)))

        # start server
        super().__init__(handlers)
        self.listen(self.ctx.CONFIG['port'])
        print(f'Running server at http://localhost:{self.ctx.CONFIG["port"]}')