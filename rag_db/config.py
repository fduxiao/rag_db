import os
from sanic.config import Config as _Config


def get_config(name: str, value):
    return os.environ.get(name, value)


class Config(_Config):
    app_name = get_config("APP_NAME", 'rag_db')
    prefix = get_config("PREFIX", '')
    mongodb_url = get_config("MONGO_URL", 'mongodb://localhost:27017/?directConnection=true')
    chromadb_url = get_config("CHROMA_URL", 'chromadb://localhost:8000')
