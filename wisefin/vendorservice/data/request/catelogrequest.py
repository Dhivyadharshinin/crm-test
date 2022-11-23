import json


class CatelogRequest:
    id = None
    activity_detail_id = None
    detail_name = None
    product_name = None
    category = None
    subcategory = None
    name = None
    specification = None
    size = None
    remarks = None
    uom = None
    unitprice = None
    from_date = None
    to_date = None
    packing_price = None
    delivery_date = None
    capacity = None
    direct_to = None
    portal_flag = 0

    def __init__(self, catlog_obj):
        if 'id' in catlog_obj:
            self.id = catlog_obj['id']
        if 'activity_detail_id' in catlog_obj:
            self.activity_detail_id = catlog_obj['activity_detail_id']
        if 'detail_name' in catlog_obj:
            self.detail_name = catlog_obj['detail_name']
        if 'product_name' in catlog_obj:
            self.product_name = catlog_obj['product_name']
        if 'subcategory' in catlog_obj:
            self.subcategory = catlog_obj['subcategory']
        if 'category' in catlog_obj:
            self.category = catlog_obj['category']
        if 'name' in catlog_obj:
            self.name = catlog_obj['name']
        if 'specification' in catlog_obj:
            self.specification = catlog_obj['specification']
        if 'size' in catlog_obj:
            self.size = catlog_obj['size']
        if 'remarks' in catlog_obj:
            self.remarks = catlog_obj['remarks']
        if 'uom' in catlog_obj:
            self.uom = catlog_obj['uom']
        if 'unitprice' in catlog_obj:
            self.unitprice = catlog_obj['unitprice']
        if 'from_date' in catlog_obj:
            self.from_date = catlog_obj['from_date']
        if 'to_date' in catlog_obj:
            self.to_date = catlog_obj['to_date']
        if 'packing_price' in catlog_obj:
            self.packing_price = catlog_obj['packing_price']
        if 'delivery_date' in catlog_obj:
            self.delivery_date = catlog_obj['delivery_date']
        if 'capacity' in catlog_obj:
            self.capacity = catlog_obj['capacity']
        if 'direct_to' in catlog_obj:
            self.direct_to = catlog_obj['direct_to']
        if 'portal_flag' in catlog_obj:
            self.portal_flag = catlog_obj['portal_flag']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    # def set_id(self, id):
    #     self.id = id
    #
    # def set_activity_detail_id(self, activity_detail_id):
    #     self.activity_detail_id = activity_detail_id
    #
    # def set_detail_name(self, detail_name):
    #     self.detail_name = detail_name
    #
    # def set_product_name(self, product_name):
    #     self.product_name = product_name
    #
    # def set_category(self, category):
    #     self.category = category
    #
    # def set_subcategory(self, subcategory):
    #     self.subcategory = subcategory
    #
    # def set_name(self,name):
    #     self.name=name
    #
    # def set_specification(self,specification):
    #     self.specification=specification
    #
    # def set_size(self,size):
    #     self.size=size
    #
    # def set_remarks(self,remarks):
    #     self.remarks=remarks
    #
    # def set_uom(self,uom):
    #     self.uom=uom
    #
    # def set_unitprice(self,unitprice):
    #     self.unitprice=unitprice
    #
    # def set_from_date(self,from_date):
    #     self.from_date=from_date
    #
    # def set_to_date(self,to_date):
    #     self.to_date=to_date
    #
    # def set_packing_price(self,packing_price):
    #     self.packing_price=packing_price
    #
    # def set_delivery_date(self,delivery_date):
    #     self.delivery_date=delivery_date
    #
    # def set_capacity(self,capacity):
    #     self.remarks=capacity
    #
    # def set_direct_to(self,direct_to):
    #     self.direct_to=direct_to

    def get_id(self):
        return self.id

    def get_activity_detail_id(self):
        return self.activity_detail_id

    def get_detail_name(self):
        return self.detail_name

    def get_product_name(self):
        return self.product_name

    def get_category(self):
        return self.category

    def get_subcategory(self):
        return self.subcategory

    def get_name(self):
        return self.name

    def get_specification(self):
        return self.specification

    def get_size(self):
        return self.size

    def get_remarks(self):
        return self.remarks

    def get_uom(self):
        return self.uom

    def get_unitprice(self):
        return self.unitprice

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.to_date

    def get_packing_price(self):
        return self.packing_price

    def get_delivery_date(self):
        return self.delivery_date

    def get_capacity(self):
        return self.capacity

    def get_direct_to(self):
        return self.direct_to

    def get_portal_flag(self):
        return self.portal_flag
