from .config import Config
from .database import Historian


class Context:
    hello_world = "Hello, world!"

    def __init__(self, config: Config):
        self.historian = Historian(
            mongo_url=config.mongodb_url,
            chroma_url=config.chromadb_url
        )

    async def setup_db(self, loop):
        await self.historian.connect()
        self.historian.schedule_heartbeat_task(loop)

    async def close_db(self):
        await self.historian.close()
