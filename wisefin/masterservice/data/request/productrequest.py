import json
class ProductRequest:
    id = None
    code = None
    name = None
    weight = None
    unitprice = None
    uom_id = None
    hsn_id = None
    category_id = None
    subcategory_id = None
    productcategory_id = None
    producttype_id = None
    uom_code = None
    hsn_code = None
    category_code = None
    subcategory_code = None
    productcategory_code = None
    producttype_code = None
    product_details = None
    status = 1
    type=None
    productdisplayname=None
    producttradingitem=None
    product_isblocked=None
    product_isrcm=None
    def __init__(self, product_obj):
        if 'id' in product_obj:
            self.id = product_obj['id']
        if 'code' in product_obj:
            self.code = product_obj['code']
        if 'name' in product_obj:
            self.name = product_obj['name']
        if 'weight' in product_obj:
            self.weight = product_obj['weight']
        if 'unitprice' in product_obj:
            self.unitprice = product_obj['unitprice']
        if 'uom_id' in product_obj:
            self.uom_id = product_obj['uom_id']
        if 'hsn_id' in product_obj:
            self.hsn_id = product_obj['hsn_id']
        if 'category_id' in product_obj:
            self.category_id = product_obj['category_id']
        if 'subcategory_id' in product_obj:
            self.subcategory_id = product_obj['subcategory_id']
        if 'type' in product_obj:
            self.type=product_obj['type']
        if 'productcategory_id' in product_obj:
            self.productcategory_id = product_obj['productcategory_id']
        if 'producttype_id' in product_obj:
            self.producttype_id = product_obj['producttype_id']
        if 'uom_code' in product_obj:
            self.uom_code = product_obj['uom_code']
        if 'hsn_code' in product_obj:
            self.hsn_code = product_obj['hsn_code']
        if 'category_code' in product_obj:
            self.category_code = product_obj['category_code']
        if 'subcategory_code' in product_obj:
            self.subcategory_code = product_obj['subcategory_code']
        if 'productcategory_code' in product_obj:
            self.productcategory_code = product_obj['productcategory_code']
        if 'producttype_code' in product_obj:
            self.producttype_code = product_obj['producttype_code']
        if 'product_details' in product_obj:
            self.product_details = product_obj['product_details']
        if 'status' in product_obj:
            self.status = product_obj['status']
        if 'productdisplayname' in product_obj:
            self.productdisplayname=product_obj['productdisplayname']
        if 'producttradingitem' in product_obj:
            self.producttradingitem=product_obj['producttradingitem']
        if 'product_isblocked' in product_obj:
            self.product_isblocked=product_obj['product_isblocked']
        if 'product_isrcm' in product_obj:
            self.product_isrcm=product_obj['product_isrcm']
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_weight(self):
        return self.weight
    def get_unitprice(self):
        return self.unitprice
    def get_uomid(self):
        return self.uom_id
    def get_hsn_id(self):
        return self.hsn_id
    def get_categoryid(self):
        return self.category_id
    def get_subcategoryid(self):
        return self.subcategory_id
    def get_type(self):
        return self.type
    def get_productcategoryid(self):
        return self.productcategory_id
    def get_producttypeid(self):
        return self.producttype_id
    def get_uom_code(self):
        return self.uom_code
    def get_hsn_code(self):
        return self.hsn_code
    def get_category_code(self):
        return self.category_code
    def get_subcategory_code(self):
        return self.subcategory_code
    def get_productcategory_code(self):
        return self.productcategory_code
    def get_producttype_code(self):
        return self.producttype_code
    def get_product_details(self):
        return self.product_details
    def get_status(self):
        return self.status
    def get_productdisplayname(self):
        return self.productdisplayname
    def get_producttradingitem(self):
        return self.producttradingitem
    def get_product_isrcm(self):
        return self.product_isrcm
    def get_product_isblocked(self):
        return self.product_isblocked

# class productDevisionRequest:
#     id=None
#     type=None
#     created_by=None
#     created_date=None
#     updated_by=None
#     updated_date=None
#
#     def __init__(self, devision_obj):
#         if 'id' in devision_obj:
#             self.id = devision_obj['id']
#         if 'type' in devision_obj:
#             self.type=devision_obj['type']
#         if 'created_by'in devision_obj:
#             self.created_by=devision_obj['created_by']
#         if 'created_date' in devision_obj:
#             self.created_date = devision_obj['created_date']
#         if 'updated_by' in devision_obj:
#             self.updated_by=devision_obj['updated_by']
#         if 'updated_date' in devision_obj:
#             self.updated_date = devision_obj['updated_date']
#
#     # def get(self):
#         # return json.dumps(self, default=lambda o: o.__dict__,
#                           # sort_keys=True, indent=4)
#
#     def get_id(self):
#         return self.id
#
#     def get_type(self):
#         return self.type
#
#     def get_created_by(self):
#         return self.created_by
#
#     def get_created_date(self):
#
#         return self.created_date
#
#     def get_updated_by(self):
#         # updated_by=int(updated_by)
#         return self.updated_by
#
#     def get_updated_date(self):
#         return self.updated_date
