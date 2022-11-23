import json
from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.apsubcategoryresponse import ApsubcategoryResponse
from masterservice.data.response.productcategoryresponse import ProductcategoryResponse
from masterservice.data.response.producttyperesponse import ProducttypeResponse
from masterservice.data.response.uomresponse import UomResponse


class ProductResponse:
    id = None
    code = None
    name = None
    weight = None
    unitprice = None
    uom = None
    hsn = None
    category = None
    subcategory = None
    type=None
    productcategory_id = None
    producttype_id = None
    product_details = None
    productdisplayname=None
    producttradingitem=None
    status=None
    product_isblocked = None
    product_isrcm = None
    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_name(self, name):
        self.name = name
    def set_weight(self, weight):
        weight = str(weight)
        self.weight = weight
    def set_unitprice(self, unitprice):
        unitprice = str(unitprice)
        self.unitprice = unitprice
    def set_status(self,status):
        self.status=status
    def set_uomid(self, uom):
        # print('uom',uom)
        if uom is not None:
            # p
            uom_data = UomResponse()
            uom_data.set_id(uom.id)
            uom_data.set_code(uom.code)
            uom_data.set_name(uom.name)
            self.uom_id = uom_data
        else:
            self.uom =uom
    def set_hsn_id(self, hsn):
        if hsn is not None:
            hsn_data = HsnResponse()
            hsn_data.set_id(hsn.id)
            hsn_data.set_code(hsn.code)
            hsn_data.set_igstrate(hsn.igstrate)
            hsn_data.set_hsn_code(str(hsn.code) +"-"+ str(hsn.igstrate))
            self.hsn_id = hsn_data
        else:
            self.hsn =hsn
        # self.hsn_id = hsn_id

    def set_categoryid(self, category):
        if category is not None:
            cat_data = ApcategoryResponse()
            cat_data.set_id(category.id)
            cat_data.set_code(category.code)
            cat_data.set_no(category.no)
            cat_data.set_name(category.name)
            cat_data.set_glno(category.glno)
            cat_data.set_isasset(category.isasset)
            self.category_id = cat_data
        else:
            self.category_id =category
    def set_subcategoryid(self, subcategory):
        if subcategory is not None:
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_no(subcategory.no)
            cat_data.set_name(subcategory.name)
            cat_data.set_status(subcategory.status)
            cat_data.set_category_id(subcategory.category_id)
            # cat_data.set_expense(subcategory.expense)
            cat_data.set_gstblocked(subcategory.gstblocked)
            cat_data.set_gstrcm(subcategory.gstrcm)
            cat_data.set_glno(subcategory.glno)
            self.subcategory_id = cat_data
        else:
            self.subcategory_id =subcategory
    def set_type(self,type):
        self.type=type
    def set_productcategoryid(self, productcategory_id):
        self.productcategory_id = productcategory_id
    def set_producttypeid(self, producttype_id):
        self.producttype_id = producttype_id
    def set_product_details(self, product_details):
        if isinstance(product_details,str):
            product_details=json.loads(product_details.replace("'", '"'))
        self.product_details = product_details
    def set_productdisplayname(self,productdisplayname):
        self.productdisplayname=productdisplayname
    def set_producttradingitem(self,producttradingitem):
        self.producttradingitem=producttradingitem
    def set_product_isrcm(self,product_isrcm):
         self.product_isrcm=product_isrcm
    def set_product_isblocked(self,product_isblocked):
         self.product_isblocked=product_isblocked

class ProducSearchResponse:
    id = None
    code = None
    name = None
    hsn_id = None
    category = None
    subcategory= None
    productcategory_id = None
    producttype_id = None
    weight = None
    unitprice = None
    # producttype_id = None
    product_details = None
    productdisplayname = None
    producttradingitem = None
    status=None
    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_name(self, name):
        self.name = name
    def set_status(self,status):
        self.status=status
    def set_hsn_id(self, hsn):
        if hsn is not None:
            hsn_data=HsnResponse()
            hsn_data.set_id(hsn.id)
            hsn_data.set_code(hsn.code)
            hsn_data.set_igstrate(hsn.igstrate)
            self.hsn_id=hsn_data
        else:
            self.hsn_id=hsn

        # self.hsn_id = hsn_id
    def set_category(self, category):
        if category is not None:
            cat_data = ApcategoryResponse()
            cat_data.set_id(category.id)
            cat_data.set_code(category.code)
            cat_data.set_name(category.name)
            self.category= cat_data
        else:
            self.category =category
    def set_subcategory(self, subcategory):
        if subcategory is not None:
            cat_data = ApsubcategoryResponse()
            cat_data.set_id(subcategory.id)
            cat_data.set_code(subcategory.code)
            cat_data.set_name(subcategory.name)
            self.subcategory = cat_data
        else:
            self.subcategory =subcategory
    def set_productcategoryid(self, productcategory):
        if productcategory is not None:
            productcategory_data = ProductcategoryResponse()
            productcategory_data.set_id(productcategory.id)
            productcategory_data.set_code(productcategory.code)
            productcategory_data.set_name(productcategory.name)
            self.productcategory_id = productcategory_data
        else:
            self.productcategory_id = productcategory


    def set_producttypeid(self, producttype):
        if producttype is not None:
            producttype_data = ProducttypeResponse()
            producttype_data.set_id(producttype.id)
            producttype_data.set_code(producttype.code)
            producttype_data.set_name(producttype.name)
            self.producttype_id = producttype_data
        else:
            self.producttype_id =producttype
        # self.producttype_id = producttype_id
    def set_weight(self, weight):
        weight = str(weight)
        self.weight = weight
    def set_unitprice(self, unitprice):
        unitprice = str(unitprice)
        self.unitprice = unitprice

    def set_product_details(self, product_details):
        self.product_details = product_details

    def set_productdisplayname(self, productdisplayname):
        self.productdisplayname = productdisplayname

    def set_producttradingitem(self, producttradingitem):
        self.producttradingitem = producttradingitem
    def set_uom_id(self,uom):
        if uom is not None:
            uom_data = UomResponse()
            uom_data.set_id(uom.id)
            uom_data.set_code(uom.code)
            uom_data.set_name(uom.name)
            self.uom_id = uom_data
        else:
            self.uom_id = uom



class productcat_type_list:

    data = []

    # # print(data)
    # #MYAPPRESPONSE get
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def __init__(self):
        self.data = []

    def get_list(self):
        # print(self.data)
        return self.data

    def append(self, object):
        self.data.append(object)

class ProductCategory_dev_Response:
    product_category=None
    id=None
    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_product_category(self,product_category):

        self.product_category=product_category
    def set_id(self,id):
        self.id=id

    def set_product_subcategory(self,product_subcategory):
        self.product_subcategory=product_subcategory

