import decimal
import re
from datetime import datetime

from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.apsubcategoryresponse import ApsubcategoryResponse
from masterservice.data.response.productcategoryresponse import ProductcategoryResponse
from masterservice.data.response.productresponse import ProductResponse
from masterservice.data.response.producttyperesponse import ProducttypeResponse
from masterservice.data.response.uomresponse import UomResponse

from django.http import HttpResponse

from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList


class ModifyStatus:
    create = 1
    update = 2
    delete = 0

class MasterRefType:
    MASTER = 1
    CONTACTTYPE = 2
    DESIGNATION = 3
    COUNTRY = 4
    STATE = 5
    DISTRICT = 6
    CITY = 7
    PINCODE = 8
    TAX = 9
    SUBTX = 10
    TAX_RATE = 11
    BANK = 12
    BANK_BRANCH = 13
    PAYMODE = 14
    CATEGORY = 15
    SUBCATEGORY = 16
    UOM = 17
    PRODUCT = 18
    CUSTOMERCATEGORY=19
    DOCUMENT_GROUP =20
    ADDRESS =21
    PRODUCTCATEGORY =22
    PRODUCTTYPE =23
    HSN =24
    COMMODITY = 25
    Apexpense = 26
    PRODUCTSPECIFICATION = 27
    AUDITCHECKLIST=28

class RequestStatusUtil:
    ONBOARD = 1
    ONBOARD_VAL = "ONBOARD"
    MODIFICATION =2
    MODIFICATION_VAL = "MODIFICATION"

class MasterTypeUtil:
    Designation=1
    Country=2
    Bank=3
    PayMode=4
    Uom=5
    CustomerCategory=6

class CategoryType:
    OD = 1
    IT = 2

    OD_Type = "OD"
    IT_Type = "IT"

class CustomerType:
    ADHOC=1

    ADHOC_VAR='ADHOC'



def getCategoryType(number):
    if (number == CategoryType.OD):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'OD'
        return vyslite

    elif (number == CategoryType.IT):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'IT'
        return vyslite

def get_category_type_list():
    idarr = [CategoryType.OD, CategoryType.IT]
    typearr = [CategoryType.OD_Type, CategoryType.IT_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist
def get_fileextension_val(extension):
    if extension in ['xlsx']:
        return True
    else:
        return False
class SG_FileType:
    NOTE_PAD = 1
    EXCEL = 2

    NOTE_PAD_VAL = "NOTEPAD"
    EXCEL_VAL = "EXCEL"


class ZoneType:
    zone1 = "1"
    zone2 = "2"
    zone3 = "3"
    nozone = "0"

    zone1_val = 'Corporation'
    zone2_val = 'Municipality'
    zone3_val = 'Others'
    nozone_val = 'NO ZONE'

def get_zone_type_list():
    idarr = [ZoneType.zone1, ZoneType.zone2,ZoneType.zone3,ZoneType.nozone]
    typearr = [ZoneType.zone1_val, ZoneType.zone2_val,ZoneType.zone3_val,ZoneType.nozone_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

def getzoneType(number):

    if (number == ZoneType.zone1):
        data ={"id":ZoneType.zone1,"name":ZoneType.zone1_val}
    elif (number == ZoneType.zone2):
        data = {"id": ZoneType.zone2, "name": ZoneType.zone2_val}
    elif (number == ZoneType.zone3):
        data = {"id": ZoneType.zone3, "name": ZoneType.zone3_val}
    elif (number == ZoneType.nozone):
        data = {"id": ZoneType.nozone, "name": ZoneType.nozone_val}
    else:
        data = {"id":None, "name": None}
    return data



class ProductClassification:
    GOOD_AND_SERVICE = "1"
    GOODS = "2"
    SERVICE = "3"


    GOOD_AND_SERVICE_VALUE = 'Goods & Service'
    GOODS_VALUE = 'Goods'
    SERVICE_VALUE = 'Service'

# def get_product_classifivcation_list():
#     classification_array = [ProductClassification.GOOD_AND_SERVICE, ProductClassification.GOODS,ProductClassification.SERVICE]
#     typearr = [ProductClassification.GOOD_AND_SERVICE_VALUE, ProductClassification.GOODS_VALUE,ProductClassification.SERVICE_VALUE]
#     length = len(classification_array)
#     vyslist = NWisefinLiteList()
#     for x in range(length):
#         vyslite = NWisefinList()
#         vyslite.id = classification_array[x]
#         vyslite.text = typearr[x]
#         vyslist.append(vyslite)
#     return vyslist

    def getclassificationType(request):

        # if (number == ProductClassification.GOOD_AND_SERVICE):
        #     data ={"id":ProductClassification.GOOD_AND_SERVICE,"name":ProductClassification.GOOD_AND_SERVICE_VALUE}
        # elif (number == ProductClassification.GOODS):
        #     data = {"id": ProductClassification.GOODS, "name":  ProductClassification.GOODS_VALUE}
        # elif (number == ProductClassification.SERVICE):
        #     data = {"id":ProductClassification.SERVICE, "name": ProductClassification.SERVICE_VALUE}
        # else:
        #     data = {"id":None, "name": None}
        data=[{"id":ProductClassification.GOOD_AND_SERVICE,"name":ProductClassification.GOOD_AND_SERVICE_VALUE},{"id": ProductClassification.GOODS, "name":  ProductClassification.GOODS_VALUE},{"id":ProductClassification.SERVICE, "name": ProductClassification.SERVICE_VALUE}]
        print(data)
        return data


    def getclassificationType_one(request,number):

        if (number == ProductClassification.GOOD_AND_SERVICE):
            data ={"id":ProductClassification.GOOD_AND_SERVICE,"name":ProductClassification.GOOD_AND_SERVICE_VALUE}
        elif (number == ProductClassification.GOODS):
            data = {"id": ProductClassification.GOODS, "name":  ProductClassification.GOODS_VALUE}
        elif (number == ProductClassification.SERVICE):
            data = {"id":ProductClassification.SERVICE, "name": ProductClassification.SERVICE_VALUE}
        else:
            data = {"id":None, "name": None}
        return data


def dictdefault(data):
    from masterservice.models.mastermodels import APsubcategory
    if isinstance(data,ProductResponse):
        return data.__dict__
    if isinstance(data,ApcategoryResponse):
        return data.__dict__
    if isinstance(data,APsubcategory):
        return data.__dict__
    if isinstance(data,HsnResponse):
        return data.__dict__
    if isinstance(data,UomResponse):
        return data.__dict__
    if isinstance(data,datetime):
        return str(data)
    if isinstance(data,decimal.Decimal):
        return int(data)
    if isinstance(data,ApsubcategoryResponse):
        return data.__dict__
    if isinstance(data,ProducttypeResponse):
        return data.__dict__
    if isinstance(data,ProductcategoryResponse):
        return data.__dict__
    else:
        try:
            return data.__dict__
        except:
            return str(data)


class Code_Gen_Type:
    apcategory = 1
    apsubcategory = 2
    bank_branch = 3
    bank = 4
    Cost_centre = 5
    Bussiness_segment = 6
    ccbsmapping = 7
    channel = 8
    commodity = 9
    courier = 10
    customer_category = 11
    customer = 12
    document_type = 13
    hsn = 14
    master_businesssegment = 15
    designation = 16
    country = 17
    district = 18
    state = 19
    city = 20
    paymode = 21
    product_category = 22
    product = 23
    product_type = 24
    subtax = 25
    tax = 26
    taxrate = 27
    uom = 28
    ORG_IP = 29
    ORG_DETAILS = 30
    ATTENDANCE_CONFIG = 31
    LEAVE_TYPE = 32
    HOLIDAY = 33
    GRADE = 34

class Code_Gen_Value:
    apcategory = "CAT"
    apsubcategory = "SCAT"
    bank_branch = "BB"
    bank = "BK"
    Cost_centre = "CC"
    Bussiness_segment = "BS"
    ccbsmapping = "CCBS"
    channel = "ICNL"
    commodity = "COMD"
    courier = "ICOU"
    customer_category = "CCAT"
    customer = "CUST"
    document_type = "IDOC"
    hsn = "HSN"
    master_businesssegment = "BS"
    designation = "DESG"
    country = "CO"
    district = "DT"
    state = "SN"
    city = "CY"
    paymode = "PM"
    product_category = "PDCT"
    product = "VPDT"
    product_type = "PTYPE"
    subtax = "ST"
    tax = "TAX"
    taxrate = "TR"
    uom = "UOM"
    ORG_IP = 'IP'
    ORG_DETAILS = 'ORG'
    ATTENDANCE_CONFIG = 'AG'
    LEAVE_TYPE = 'LT'
    HOLIDAY = 'HD'
    GRADE = 'GR'
    
class DelmatType:
    PR = 1
    PO = 2
    ECF = 3
    BRANCH_EXP = 4

    PR_Type = "PR"
    PO_Type = "PO"
    ECF_Type = "ECF"
    BRANCH_EXP_Type = "BRANCH_EXP"

def getDelmateType(number):
    if (number == DelmatType.PR):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'PR'
        return vyslite

    elif (number == DelmatType.PO):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'PO'
        return vyslite
    elif (number == DelmatType.ECF):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'ECF'
        return vyslite
    elif (number == DelmatType.BRANCH_EXP):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'BRANCH_EXP'
        return vyslite

def get_delmat_type_list():
    idarr = [DelmatType.PR, DelmatType.PO,DelmatType.ECF,
             DelmatType.BRANCH_EXP]
    typearr = [DelmatType.PR_Type, DelmatType.PO_Type,
               DelmatType.ECF_Type,DelmatType.BRANCH_EXP_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

class PrModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2

class PrRefType:
    DELMAT = 1
    COMMODITYPRODUCTMAPING = 2
    PAR = 3
    PARDETAILS = 4
    MEP = 5
    MEPDETAILS= 6
    POHEADER = 7
    POCLOSE = 8
    POCANCEL = 9
    CONTIGENCY = 10
    PRHEADER = 11
    GRN = 12
    PRDETAILS = 13
    PRCCBS = 14
    PODETAILS = 15
    PRPOQTY = 16
    PODELIVERY = 17
    PO = 18
    POTERMS =19
    POTERMSTEMPLATE =20
    POTERMSTEMPLATEDETAIL =21
    POAMEND = 22
    REOPEN = 23
    RCN = 24
    HOLD = 25
    RELEASE = 26
    POPAYMENT = 27

class Expense_category:
    others='others'

class FA_client:
    client_name='NAC'
class MasterStatus:
    Active=1
    Inactive=0
    Active_VALUE = 'Active'
    Inactive_VALUE = 'Inactive'
    def masterstatus(request):
        data = [{"id": MasterStatus.Active, "name": MasterStatus.Active_VALUE},
                {"id": MasterStatus.Inactive, "name": MasterStatus.Inactive_VALUE}]
        return data

class Master_Drop_down:
    Yes=1
    No=0
    Yes_VALUE = 'Yes'
    No_VALUE = 'No'

class Delmat:
    REF_TYPE='DELMAT'
    REF_TYPE_VAL=1
    REF_TYPE_VAL_DELMAT=2
    def get_asset_details_type(self,ref_type):
        return self.REF_TYPE_VAL

    def get_PV_details_type(self,ref_type):
        return self.REF_TYPE_VAL_DELMAT


class QuestionHeader:
    SLNO = 'SLNO'


class VendorclassficationMapping:
    QUERTELY = 1
    HALFYEARLY = 2
    FULL_YEAR = 3
    ONE_TIME = 4
    # FIN_QUERTELY = 5
    # FIN_HALFYEARLY = 6
    # FIN_FULL_YEAR = 7
    # FIN_ONE_TIME = 8

    QUERTELY_VAL = 'QUERTERLY'
    HALFYEARLY_VAL = 'HALFYEARLY'
    FULL_YEAR_VAL = 'FULLYEAR'
    ONE_TIME_VAL = 'ONE TIME'
    # FIN_QUERTELY_VAL = 'fin_quarterly'
    # FIN_HALFYEARLY_VAL = 'fin_halfyearly'
    # FIN_FULL_YEAR_VAL = 'fin_full_year'
    # FIN_ONE_TIME_VAL = 'fin_one_time'

def Vendorclassfication_type(type):
    if (type == VendorclassficationMapping.QUERTELY):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'QUERTERLY'
        return vys_list
    elif (type == VendorclassficationMapping.HALFYEARLY):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'HALFYEARLY'
        return vys_list
    elif (type == VendorclassficationMapping.FULL_YEAR):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'FULLYEAR'
        return vys_list
    elif (type == VendorclassficationMapping.ONE_TIME):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'ONE TIME'
        return vys_list
    # elif (type == VendorclassficationMapping.FIN_QUERTELY):
    #     vys_list = NWisefinLiteList()
    #     vys_list.id = type
    #     vys_list.name = 'fin_quarterly'
    #     return vys_list
    # elif (type == VendorclassficationMapping.FIN_HALFYEARLY):
    #     vys_list = NWisefinLiteList()
    #     vys_list.id = type
    #     vys_list.name = 'fin_halfyearly'
    #     return vys_list
    # elif (type == VendorclassficationMapping.FIN_FULL_YEAR):
    #     vys_list = NWisefinLiteList()
    #     vys_list.id = type
    #     vys_list.name = 'fin_full_year'
    #     return vys_list
    # elif (type == VendorclassficationMapping.FIN_ONE_TIME):
    #     vys_list = NWisefinLiteList()
    #     vys_list.id = type
    #     vys_list.name = 'fin_one_time'
    #     return vys_list

def Vendor_classfiction_composite():
    idarr = [VendorclassficationMapping.QUERTELY, VendorclassficationMapping.HALFYEARLY, VendorclassficationMapping.FULL_YEAR, VendorclassficationMapping.ONE_TIME]
    typearr = [VendorclassficationMapping.QUERTELY_VAL, VendorclassficationMapping.HALFYEARLY_VAL, VendorclassficationMapping.FULL_YEAR_VAL, VendorclassficationMapping.ONE_TIME_VAL]

    length = len(idarr)
    list_data = NWisefinList()
    for y in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[y]
        vyslite.name = typearr[y]
        list_data.append(vyslite)
    return list_data

class Process:
    PARALLEL = 1
    SEQUENITAL = 2

    PARALLEL_VAL = 'PARALLEL'
    SEQUENITAL_VAL = 'SEQUENTIAL_VAL'

def process_type(type):
    if (type == Process.PARALLEL):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'PARALLEL'
        return vys_list
    elif (type == Process.SEQUENITAL):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = 'SEQUENTIAL'
        return vys_list

def process_composite_type():
    idarr = [Process.PARALLEL, Process.SEQUENITAL]
    typearr = [Process.PARALLEL_VAL, Process.SEQUENITAL_VAL]

    length = len(idarr)
    list_data = NWisefinList()
    for y in range(length):
        vyslist = NWisefinLiteList()
        vyslist.id = idarr[y]
        vyslist.name = typearr[y]
        list_data.append(vyslist)
    return list_data


class Input_type:
    CHECK_BOX = 1
    TEXT = 2
    RADIO_BUTTON = 3
    DROPDOWN = 4
    TEXT_AREA = 5
    NUMBER = 6
    YESNO = 7
    FILE = 8

    CHECK_BOX_VAL = 'CHECK_BOX'
    TEXT_VAL = 'TEXT'
    RADIO_BUTTON_VAL = 'RADIO_BUTTON'
    DROP_DOWN_VAL = 'DROP_DOWN'
    TEXT_AREA_VAL = 'TEXT_AREA'
    NUMBER_VAL = 'NUMBER'
    YESNO_VAL = 'YES/NO'
    FILE_VAL = 'FILE'


def input_type_val(type):
    if(type == Input_type.CHECK_BOX):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.CHECK_BOX_VAL
        return vys_list
    elif(type == Input_type.TEXT):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.TEXT_VAL
        return vys_list
    elif(type == Input_type.RADIO_BUTTON):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.RADIO_BUTTON_VAL
        return vys_list
    elif(type == Input_type.DROPDOWN):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.DROP_DOWN_VAL
        return vys_list
    elif(type == Input_type.TEXT_AREA):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.TEXT_AREA_VAL
        return vys_list
    elif(type == Input_type.NUMBER):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.NUMBER_VAL
        return vys_list
    elif(type == Input_type.YESNO):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.YESNO_VAL
        return vys_list
    elif(type == Input_type.FILE):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Input_type.FILE_VAL
        return vys_list

def input_composite_type():
    idarr = [Input_type.CHECK_BOX,Input_type.TEXT,Input_type.RADIO_BUTTON,Input_type.DROPDOWN,Input_type.TEXT_AREA,Input_type.NUMBER,Input_type.YESNO,Input_type.FILE]
    typearr = [Input_type.CHECK_BOX_VAL,Input_type.TEXT_VAL,Input_type.RADIO_BUTTON_VAL,Input_type.DROP_DOWN_VAL,Input_type.TEXT_AREA_VAL,Input_type.NUMBER_VAL,Input_type.YESNO_VAL,Input_type.FILE_VAL]
    length = len(idarr)
    list_data = NWisefinList()
    for x in range(length):
        vys_list = NWisefinLiteList()
        vys_list.id = idarr[x]
        vys_list.name = typearr[x]
        # search = re.search(query.lower(), vys_list.name.lower())
        # if search is not None:
        list_data.append(vys_list)
    return list_data


class Is_activity_level:
    vendor = 0
    activity = 1

class VendorMapping:
    relationship_category = 1
    vendor_type = 2
    criticality = 3
    
class VOWMasterTable:
    CITY = 1
    STATE = 2
    PINCODE = 3
    DISTRICT = 4
    TAX = 5
    SUB_TAX = 6
    TAX_RATE = 7
    PAY_MODE = 8
    BANK = 9
    BANK_BRANCH = 10
    PRODUCT = 11
    DOC_GROUP = 12
    IFSC = 13
    ENTITY = 14
class MasterDocUtil:
    DEPARTMENT = 1
    ORGANITATION = 2

class OrgArcUtil:
    org = 1
    org_branch = 2
    client =3