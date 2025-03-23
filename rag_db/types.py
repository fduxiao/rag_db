from typing import TypeAlias
from sanic.app import Sanic
from .config import Config
from .context import Context

RagDBApp: TypeAlias = Sanic[Config, Context]
