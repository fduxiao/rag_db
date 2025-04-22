import copy
from uuid import uuid4
from .field import Field, DatetimeField


class Model:
    collection_name = "test"
    fields = {}
    default_dict = {}
    model_id = Field("_id")
    created_at = DatetimeField()
    updated_at = DatetimeField()
    deleted_at = DatetimeField()

    def from_dict(self, data):
        self.data = copy.deepcopy(data)
        return self

    @staticmethod
    def get_id():
        return str(uuid4())

    def __init__(self):
        self.data = copy.deepcopy(self.default_dict)
        self.model_id = self.get_id()
        self.created_at = DatetimeField.default()
        self.updated_at = None
        self.deleted_at = None


class EmbeddingModel(Model):
    embedding = Field("embedding")
    text = Field("text")
