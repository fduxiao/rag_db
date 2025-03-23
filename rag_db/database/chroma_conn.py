from functools import wraps
from urllib.parse import urlparse
import chromadb


def auto_async(func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        if self.is_async:
            return await func(self, *args, **kwargs)
        return func(self, *args, **kwargs)
    return wrapped


class ChromaConn:
    def __init__(self, url="file://./db/chroma", is_async=False):
        url = urlparse(url)
        self.url = url
        self.is_async = is_async
        self._client = None
        if url.scheme == "file":
            self._client = chromadb.PersistentClient(url[7:])
            self.is_async = False
        elif url.scheme == "memory":
            self._client = chromadb.Client()
            self.is_async = False
        else:
            if not is_async:
                self._client = chromadb.HttpClient(host=url.hostname, port=url.port)

    @property
    def client(self):
        if self._client is None:
            raise ConnectionError("Please connect")

    async def connect(self):
        self._client = await chromadb.AsyncHttpClient(host=self.url.hostname, port=self.url.port)

    async def get_or_create_collection(self, name):
        if self.is_async:
            coll = await self.client.get_or_create_collection(name=name)
        else:
            coll = self.client.get_or_create_collection(name=name)
        return ChromaColl(coll, is_async=self.is_async)


class ChromaColl:
    def __init__(self, coll, is_async):
        self.coll = coll
        self.is_async = is_async

    @auto_async
    async def count(self):
        return self.coll.count()

    @auto_async
    async def modify(self, name, metadata):
        return self.coll.modify(name=name, metadata=metadata)

    @auto_async
    async def add(self, ids, documents, embeddings, metadatas):
        return self.coll.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    @auto_async
    async def upsert(self, ids, documents, embeddings, metadatas):
        return self.coll.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    @auto_async
    async def delete(self, ids, where, where_document):
        return self.coll.delete(
            ids=ids,
            where=where,
            where_document=where_document
        )

    @auto_async
    async def query(self, query_embeddings, n_result, where, where_document):
        return self.query(
            query_embeddings=query_embeddings,
            n_result=n_result,
            where=where,
            where_document=where_document
        )
