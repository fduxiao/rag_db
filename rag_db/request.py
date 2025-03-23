from sanic import Request as _Request
from .context import Context


class Request(_Request):
    @property
    def context(self) -> Context:
        return self.app.ctx
