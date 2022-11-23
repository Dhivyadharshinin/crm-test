import json

from productservice.util.product_util import SourceUtil, common_util_fetch


class SourceResponse:
    id,code,name,type=(None,)*4

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_type(self, type):
        type_name=common_util_fetch(SourceUtil.var,type)
        self.type = type_name

    def set_name(self, name):
        self.name = name