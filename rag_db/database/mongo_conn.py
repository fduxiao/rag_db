from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.operations import SearchIndexModel


class MongoConn:
    def __init__(self, url="mongodb://localhost:27017?directConnection=true"):
        self.client = AsyncMongoClient(url)

    async def connect(self):
        await self.client.aconnect()

    async def get_database(self, name: str = None):
        return MongoDB(self.client.get_database(name))

    async def close(self):
        await self.client.aclose()


class MongoDB:
    def __init__(self, database: AsyncDatabase):
        self.database = database

    async def get_collection(self, name: str):
        return MongoColl(self.database.get_collection(name))


class MongoColl:
    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def insert(self, data):
        obj = await self.collection.insert_one(data)
        return obj.inserted_id

    async def update(self, query, update, upsert=False):
        return await self.collection.update_one(query, update, upsert=upsert)

    async def delete(self, query):
        return await self.collection.delete_one(query)

    async def find_one(self, query):
        return await self.collection.find_one(query)

    async def find(self, query, projection, sort, skip, limit):
        async for one in self.collection.find(query, projection, skip, limit).sort(sort):
            yield one

    async def count(self, query):
        return self.collection.count_documents(query)

    async def ensure_vector_index(self, field, n_dim, name="vector_index", similarity="dotProduct"):
        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": field,
                        "similarity": similarity,
                        "numDimensions": n_dim
                    },
                ]
            },
            name=name,
            type="vectorSearch"
        )
        await self.collection.create_search_index(model=search_index_model)

    async def vector_query(self, field, query_vector, index="vector_index", limit=5, exact=True,
                           projection: dict =None, score_field="score"):
        if projection is None:
            projection =  {
                "_id": 1,
                "text": 1,
            }
        if score_field is not None:
            projection[score_field] = {
                "$meta": "vectorSearchScore"
            }

        pipeline = [
            {
                "$vectorSearch": {
                    "index": index,
                    "queryVector": query_vector,
                    "path": field,
                    "exact": exact,
                    "limit": limit
                }
            },
            {
                "$project": projection
            }
        ]
        # Execute the search
        async for one in await self.collection.aggregate(pipeline):
            yield one
