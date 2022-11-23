import json

from django.template.defaultfilters import length


class NWisefinList:
    data = []
    pagination = None
    count = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        self.data = []

    def set_list(self, list):
        self.data = list

    def get_list(self):
        return self.data

    def append(self, obj):
        self.data.append(obj)

    def set_listcount(self, count):
        self.count = count

    def get_listcount(self):
        return self.count

    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.data) > pagination.limit:
            self.data.pop()

    def get_pagination(self):
        return self.pagination