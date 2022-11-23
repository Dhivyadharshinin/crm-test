import json


class TaxRateResquest:
    id = None
    subtax_id = None
    code = None
    name = None
    rate = None


    def __init__(self, taxrate_obj):
        if 'id' in taxrate_obj:
            self.id = taxrate_obj['id']
        if 'subtax_id' in taxrate_obj:
            self.subtax_id = taxrate_obj['subtax_id']
        if 'code' in taxrate_obj:
            self.code = taxrate_obj['code']
        if 'name' in taxrate_obj:
            self.name = taxrate_obj['name']
        if 'rate' in taxrate_obj:
            self.rate = taxrate_obj['rate']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_subtax_id(self):
        return self.subtax_id

    def get_rate(self):
        return self.rate
