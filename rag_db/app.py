from sanic import Sanic
from sanic.response import text

from .config import Config
from .context import Context
from .request import Request
from .types import RagDBApp


def create_app() -> Sanic:
    config = Config()
    ctx = Context(config)

    app: RagDBApp = Sanic(config.app_name, config=config, ctx=ctx, request_class=Request)

    @app.listener("before_server_start")
    async def setup_db(_app: RagDBApp, loop):
        await _app.ctx.setup_db(loop)

    @app.listener("after_server_stop")
    async def setup_db(_app: RagDBApp):
        await _app.ctx.close_db()

    @app.get("/")
    async def hello_world(request: Request):
        return text(f"{request.context.hello_world}")

    return app
