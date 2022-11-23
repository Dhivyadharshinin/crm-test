import json

class CommodityProductMapRequest:
    id = None
    product_id = None
    commodity_id = None

    def __init__(self, cpMap_obj):
        if 'id' in cpMap_obj:
            self.id = cpMap_obj['id']
        if 'product_id' in cpMap_obj:
            self.product_id = cpMap_obj['product_id']
        if 'commodity_id' in cpMap_obj:
            self.commodity_id = cpMap_obj['commodity_id']

    def get_id(self):
        return self.id

    def get_product_id(self):
        return self.product_id

    def get_commodity_id(self):
        return self.commodity_id
