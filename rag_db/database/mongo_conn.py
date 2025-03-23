from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.operations import SearchIndexModel


class MongoConn:
    def __init__(self, url="mongodb://localhost:27017?directConnection=true"):
        self.client = AsyncMongoClient(url)

    async def connect(self):
        self.client = await self.client.aconnect()

    async def get_collection(self, database: str, collection: str):
        database = self.client.get_database(database)
        return database.get_collection(collection)

    async def close(self):
        await self.client.close()


class MongoColl:
    def __init__(self, collection: AsyncCollection):
        self.collection = collection

    async def insert(self, data):
        return await self.collection.insert_one(data)

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
