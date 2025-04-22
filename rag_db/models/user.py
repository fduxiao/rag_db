from ..database import Model, Field


class User(Model):
    username = Field()
    password = Field()
