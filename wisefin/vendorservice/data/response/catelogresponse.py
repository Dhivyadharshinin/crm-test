import json


class CatelogResponse:
    id = None
    activitydetail_id = None
    detailname = None
    productname = None
    category = None
    subcategory = None
    name = None
    specification = None
    size = None
    remarks = None
    uom = None
    unitprice = None
    fromdate = None
    todate = None
    packing_price = None
    delivery_date = None
    capacity = None
    direct_to = None
    modify_ref_id = None
    modify_status = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_activitydetail_id(self, activitydetail_id):
        self.activitydetail_id = activitydetail_id

    def set_detailname(self, detailname):
        self.detailname = detailname

    def set_productname(self, productname):
        self.productname = productname

    def set_category(self, category):
        self.category = category

    def set_subcategory(self, subcategory):
        self.subcategory = subcategory

    def set_name(self,name):
        self.name=name

    def set_specification(self,specification):
        self.specification=specification

    def set_size(self,size):
        self.size=size

    def set_remarks(self,remarks):
        self.remarks=remarks

    def set_uom(self,uom):
        self.uom=uom

    def set_unitprice(self,unitprice):
        self.unitprice=unitprice

    def set_fromdate(self, fromdate):
        if fromdate == None or fromdate == 'None':
            self.fromdate = None
        else:
            fromdate=str(fromdate)
            self.fromdate=fromdate

    def set_todate(self, todate):
        if todate == None or todate == 'None':
            self.todate = None
        else:
            todate=str(todate)
            self.todate=todate

    def set_packing_price(self,packing_price):
        self.packing_price=packing_price

    def set_delivery_date(self,delivery_date):
        self.delivery_date=delivery_date

    def set_capacity(self,capacity):
        self.capacity=capacity

    def set_direct_to(self,direct_to):
        self.direct_to=direct_to

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status



    def get_id(self):
        return self.id

    def get_activitydetail_id(self):
        return self.activitydetail_id

    def get_detailname(self):
        return self.detailname

    def get_productname(self):
        return self.productname

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

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

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

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag
