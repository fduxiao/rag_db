from typing import Optional

from .chroma_conn import ChromaConn
from .mongo_conn import MongoConn, MongoDB
from .model import Model


class Historian:
    def __init__(self,mongo_url="mongodb://localhost:27017?directConnection=true",
                 chroma_url="file://./db/chroma"):
        self.mongo_conn = MongoConn(mongo_url)
        self.chroma_conn = ChromaConn(chroma_url, is_async=True)
        self.mongo_db: Optional[MongoDB] = None
        self.chroma_db = None

    def schedule_heartbeat_task(self, loop):
        self.chroma_conn.schedule_heartbeat_task(loop)

    async def connect(self):
        await self.mongo_conn.connect()
        await self.chroma_conn.connect()

    async def close(self):
        await self.mongo_conn.close()
        await self.chroma_conn.stop_heartbeat()

    async def set_database(self, mongo_db: str = None):
        self.mongo_db = self.mongo_conn.get_database(mongo_db)

    async def create_model(self, model: Model):
        coll = await self.mongo_db.get_collection(model.collection_name)
        model_id = await coll.insert(model.data)
        model.model_id = model_id
        return model_id

    async def find(self):
        pass
