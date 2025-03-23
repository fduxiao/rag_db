import datetime


class Field:
    def __init__(self, name=None):
        self.name = name

    @classmethod
    def default(cls):
        return None

    def __set_name__(self, owner, name):
        if self.name is None:
            self.name = name
        owner.default_dict[name] = self.default()
        owner.fields[name] = self

    def to_data(self, value):
        return value

    def from_data(self, data):
        return data

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.from_data(instance.data[self.name])

    def __set__(self, instance, value):
        instance.data[self.name] = self.to_data(value)


class DatetimeField(Field):
    @classmethod
    def default(cls):
        return datetime.datetime.now(datetime.UTC)

    def to_data(self, value: datetime.datetime):
        if value is None:
            return value
        return value.timestamp()

    def from_data(self, data):
        if data is None:
            return data
        return datetime.datetime.fromtimestamp(data, datetime.UTC)
