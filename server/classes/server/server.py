from tornado.web import Application, StaticFileHandler
from classes import AuctionContext
from .handlers import timer_handle
import utils


class Server(Application):
    def __init__(self):
        # inits
        handlers= []
        self.ctx= AuctionContext()

        # routes
        handlers.append(('/timer', timer_handle(self.ctx)))
        handlers.append(('/(bg_small_box.png)', StaticFileHandler, dict(path=utils.DATA_DIR)))
        handlers.append(('/((?:img|js|css)/.*)', StaticFileHandler, dict(path=utils.PAGES_DIR)))

        # start server
        super().__init__(handlers)
        self.listen(self.ctx.CONFIG['port'])
        print(f'Running server at http://localhost:{self.ctx.CONFIG["port"]}')