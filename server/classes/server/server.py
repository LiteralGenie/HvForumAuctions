from tornado.web import Application, StaticFileHandler, RedirectHandler
from .handlers import proxy_view, proxy_form, timer, update, logs
import utils


class Server(Application):
    def __init__(self, ctx):
        # inits
        handlers= []
        self.ctx= ctx

        # routes
        handlers.append(('/logs', logs.get(ctx)))
        handlers.append(('/', RedirectHandler, {"url": f"/logs?id={ctx.FOLDER}"}))
        handlers.append(('/api/logs', logs.api_get(ctx)))

        handlers.append(('/update',           update.get_update(ctx)))
        handlers.append(('/api/update_check', update.get_check(ctx)))

        handlers.append(('/proxy/form',     proxy_form.get(ctx)))
        handlers.append(('/api/proxy/form', proxy_form.api(ctx)))

        handlers.append(('/proxy/view',     proxy_view.get_user_view(ctx)))
        handlers.append(('/api/proxy/view', proxy_view.get_api_view(ctx)))

        handlers.append(('/timer', timer.get(ctx)))

        handlers.append(('/((?:img|js|css|gif)/.*)', StaticFileHandler, dict(path=utils.PAGES_DIR)))

        # start server
        super().__init__(handlers)
        self.listen(self.ctx.CONFIG['port'])
        print(f'Running server at http://localhost:{self.ctx.CONFIG["port"]}')