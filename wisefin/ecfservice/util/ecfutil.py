from utilityservice.data.response.nwisefinlist import NWisefinList
from django.db.models import Q
import json

from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList



class ECFModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2


class ECFStatus:
    DRAFT = 1
    PENDING_FOR_APPROVAL = 2
    APPROVED = 3
    REJECT = 4
    PENDING_FOR_APPROVAL_MODIFICATION = 5
    DELETE = 6

    DRAFT_ECFStatus = "DRAFT"
    PENDING_FOR_APPROVAL_ECFStatus = "PENDING_FOR_APPROVAL"
    APPROVED_ECFStatus = "APPROVED"
    REJECT_ECFStatus = "REJECT"
    Pending_For_Approval_Modification = "PENDING_FOR_APPROVAL_MODIFICATION"
    Delete = "DELETE"


class ddl_status:
    ECF_CREATED_BY_ME = 1
    PENDING_FOR_APPROVAL = 2
    ECF_REJECTED_BY_ME = 4
    ECF_RE_AUDIT_BY_ME = 5
    ECF_APPROVED_BY_ME = 3
    DELETE = 6

    ECF_CREATED_BY_ME_VAL = 'ECF CREATED BY ME'
    PENDING_FOR_APPROVAL_VAL = 'PENDING FOR APPROVAL'
    ECF_REJECTED_BY_ME_VAL = 'ECF REJECTED BY ME'
    ECF_APPROVED_BY_ME_VAL = 'ECF APPROVED BY ME'
    DELETE_VAL = 'DELETE'
    ECF_RE_AUDIT_BY_ME_VAL = 'ECF RE-AUDIT BY ME'


def get_status(number):
    if (number == ECFStatus.DRAFT):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'DRAFT'
        return vyslite

    elif (number == ECFStatus.PENDING_FOR_APPROVAL):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PENDING_FOR_APPROVAL'
        return vyslite
    elif (number == ECFStatus.APPROVED):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'APPROVED'
        return vyslite
    elif (number == ECFStatus.REJECT):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'REJECT'
        return vyslite
    elif (number == ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PENDING_FOR_APPROVAL_MODIFICATION'
        return vyslite
    elif (number == ECFStatus.DELETE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'DELETE'
        return vyslite

#test
def get_ddl_ecf_list():
    idarr = [ddl_status.ECF_CREATED_BY_ME, ddl_status.PENDING_FOR_APPROVAL, ddl_status.ECF_REJECTED_BY_ME,
             ddl_status.ECF_APPROVED_BY_ME,
             ddl_status.DELETE]
    statusarr = [ddl_status.ECF_CREATED_BY_ME_VAL, ddl_status.PENDING_FOR_APPROVAL_VAL,
                 ddl_status.ECF_REJECTED_BY_ME_VAL,
                 ddl_status.ECF_APPROVED_BY_ME_VAL, ECFStatus.Delete]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = statusarr[x]
        vyslist.append(vyslite)
    return vyslist


def get_status_list():
    idarr = [ECFStatus.DRAFT, ECFStatus.PENDING_FOR_APPROVAL, ECFStatus.APPROVED, ECFStatus.REJECT,
             ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION, ECFStatus.DELETE]
    statusarr = [ECFStatus.DRAFT_ECFStatus, ECFStatus.PENDING_FOR_APPROVAL_ECFStatus, ECFStatus.APPROVED_ECFStatus,
                 ECFStatus.REJECT_ECFStatus, ECFStatus.Pending_For_Approval_Modification, ECFStatus.Delete]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = statusarr[x]
        vyslist.append(vyslite)
    return vyslist


class ECFRefType:
    ECFHEADER = 1
    INVOICEHEADER = 2
    INVOICEPO = 3
    INVOICEDETAIL = 4
    DEBIT = 5
    CREDIT = 6
    ECFFILES = 7
    PPXLIQUIDATION = 8


class ECFDocUtil:
    REF_TYPE_REQUEST = 1
    REF_TYPE_TRANSACTION = 2
    REF_TYPE_COMMENT = 3


def get_fileextension_val(extension):
    if extension in ['txt','doc','pdf','ppt','pot','pps','pptx','odt','odg','odp','ods','docx','docm','dotx','dotm','docb',
                     'xlsx','xls','xlt','xlm','xlsm','xltx','xltm','jpg', 'jpeg','tiff', 'tif','png','TXT','DOC','PDF','PPT',
                     'POT','PPS','PPTX','ODT','ODG','ODP','ODS','DOCX','DOCM','DOTX','DOTM','DOCB','XLSX','XLS','XLT','XLM',
                     'XLSM','XLTX','XLTM','JPG', 'JPEG','TIFF', 'TIF','PNG']:
        return True
    else:
        return False


# ECFTYPE
class Type:
    PO = 1
    NON_PO = 2
    ERA = 3
    ADVANCE = 4
    TCF = 8

    PO_Type = "PO"
    NON_PO_Type = "NON PO"
    ERA_Type = "EMP REIMP"
    ADVANCE_Type = "ADVANCE"
    TCF_Type = "TCF"

def get_Type(number):
    if (number == Type.PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PO'
        return vyslite

    elif (number == Type.NON_PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO'
        return vyslite
    elif (number == Type.ERA):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'EMP REIMP'
        return vyslite
    elif (number == Type.ADVANCE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ADVANCE'
        return vyslite
    elif (number == Type.TCF):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'TCF'
        return vyslite
    else:
        return NWisefinList()


def get_Type_list():
    idarr = [Type.PO, Type.NON_PO, Type.ERA, Type.ADVANCE,Type.TCF]
    typearr = [Type.PO_Type, Type.NON_PO_Type, Type.ERA_Type, Type.ADVANCE_Type,Type.TCF_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist


# PPXDROPDOWN
class PPX:
    EMPLOYEE = 'E'
    SUPPLIER = 'S'
    EMPLOYEE_PPX = "EMPLOYEE"
    SUPPLIER_PPX = "SUPPLIER"


def get_Ppx(string):
    if (string == PPX.EMPLOYEE):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = 'EMPLOYEE'
        return vyslite

    elif (string == PPX.SUPPLIER):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = 'SUPPLIER'
        return vyslite


def get_Ppx_list():
    idarr = [PPX.EMPLOYEE, PPX.SUPPLIER]
    PPXarr = [PPX.EMPLOYEE_PPX, PPX.SUPPLIER_PPX]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = PPXarr[x]
        vyslist.append(vyslite)
    return vyslist


# PayDROPDOWN
class Pay:
    EMPLOYEE = 'E'
    SUPPLIER = 'S'
    BRANCH_PETTYCASH = 'B'
    TOUR = 'T'

    EMPLOYEE_Pay = "EMPLOYEE"
    SUPPLIER_Pay = "SUPPLIER"
    BRANCH_Pay = "BRANCH PETTYCASH"
    TOUR_Pay = "TOUR"

def get_Pay(string):
    if (string == Pay.EMPLOYEE):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = 'EMPLOYEE'
        return vyslite

    elif (string == Pay.SUPPLIER):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = 'SUPPLIER'
        return vyslite

    elif (string == Pay.BRANCH_PETTYCASH):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = 'BRANCH PETTYCASH'
        return vyslite


def get_Pay_list(typeid):
    if (int(typeid) == 3):
        idarr = [Pay.EMPLOYEE, Pay.BRANCH_PETTYCASH,Pay.SUPPLIER]
        Payarr = [Pay.EMPLOYEE_Pay, Pay.BRANCH_Pay,Pay.SUPPLIER_Pay]
    elif (int(typeid) == 4):
        idarr = [Pay.EMPLOYEE, Pay.SUPPLIER]
        Payarr = [Pay.EMPLOYEE_Pay, Pay.SUPPLIER_Pay]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = Payarr[x]
        vyslist.append(vyslite)
    return vyslist


class SupplierType:
    SINGLE = 1
    MULTIPLE = 2

    SINGLE_Type = "SINGLE"
    MULTIPLE_Type = "MULTIPLE"


def get_suppliertype(number):
    if (number == SupplierType.SINGLE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'SINGLE'
        return vyslite

    elif (number == SupplierType.MULTIPLE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'MULTIPLE'
        return vyslite


def get_supplier_list():
    idarr = [SupplierType.SINGLE, SupplierType.MULTIPLE]
    suptypearr = [SupplierType.SINGLE_Type, SupplierType.MULTIPLE_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = suptypearr[x]
        vyslist.append(vyslite)
    return vyslist


class TDS:
    NA = 0
    NOT_KNOWN = 1
    YES = 2

    NA_TDS = "NA"
    NOT_KNOWN_TDS = "NOT_KNOWN"
    YES_TDS = "YES"


def get_tds(number):
    if (number == TDS.NA):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NA'
        return vyslite

    elif (number == TDS.NOT_KNOWN):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NOT_KNOWN'
        return vyslite
    elif (number == TDS.YES):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'YES'
        return vyslite
    else:
        return NWisefinList()


def get_tds_list():
    idarr = [TDS.NA, TDS.NOT_KNOWN, TDS.YES]
    suptdsarr = [TDS.NA_TDS, TDS.NOT_KNOWN_TDS, TDS.YES_TDS]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = suptdsarr[x]
        vyslist.append(vyslite)
    return vyslist


# ECF Query Handling
class ECFQuery:
    def supp_taxdtl(self, vendor_id):
        from vendorservice.models.vendormodels import SupplierSubTax
        condition = Q(suppliertax__vendor_id=vendor_id) & Q(suppliertax__status=1)
        vendor_obj = SupplierSubTax.objects.filter(condition).values('id', 'suppliertax__subtax_id', 'rate_id')
        return vendor_obj

    def supp_taxratedtl(self, vendor_id, subtax_id):
        from vendorservice.models.vendormodels import SupplierSubTax
        condition = Q(suppliertax__subtax_id=subtax_id) & Q(suppliertax__vendor_id=vendor_id) & Q(suppliertax__status=1)
        vendor_obj = SupplierSubTax.objects.filter(condition).values('id', 'suppliertax__subtax_id', 'rate_id',
                                                                     'isexcempted', 'excemfrom', 'excemto',
                                                                     'excemthrosold', 'excemrate')
        return vendor_obj

    def tax_type_get(self, subtax_id):
        from masterservice.models.mastermodels import SubTax
        condition = Q(id__in=subtax_id)
        obj = SubTax.objects.filter(condition).values('id', 'name', 'glno')
        tax_typ_list_data = NWisefinList()
        for i in obj:
            supp_tax_dtl = {"id": i['id'], "subtax_type": i['name'], "glno": i['glno'], 'dflag':'M',
                            'subtax_name_glno' : str(i['name'])+ "-" + str(i['glno'])}

            supp_tax_dtl = {"id": i['id'], "subtax_type": i['name'], "glno": i['glno'], 'dflag': 'M'}

            tax_typ_list_data.append(supp_tax_dtl)

        from masterservice.models.mastermodels import SubTax
        condition = ~Q(id__in=subtax_id)
        obj = SubTax.objects.filter(condition).values('id', 'name', 'glno')
        for i in obj:
            supp_tax_dtl = {"id": i['id'], "subtax_type": i['name'], "glno": i['glno'], 'dflag': 'O'}
            tax_typ_list_data.append(supp_tax_dtl)

        return tax_typ_list_data.get()

    def tax_mst_get(self, subtax_id, rate_id):
        from masterservice.models.mastermodels import SubTax, TaxRate

        condition = Q(subtax__id=subtax_id) & Q(id=rate_id) & Q(subtax__status=1)
        obj = TaxRate.objects.filter(condition).values('id', 'subtax__name', 'name', 'rate', 'subtax__glno')
        print(obj.query)
        tax_dtl_list_data = NWisefinList()
        for i in obj:
            supp_tax_dtl = {"id": i['id'], "subtax_type": i['subtax__name'], "rate_name": i['name'],
                            "rate": i['rate'], "glno": i['subtax__glno'], "dflag": "M"}
            tax_dtl_list_data.append(supp_tax_dtl)

        condition = Q(subtax__id=subtax_id) & Q(status=1)
        obj = TaxRate.objects.filter(condition).values('id', 'subtax__name', 'name', 'rate', 'subtax__glno')
        # tax_dtl_list_data = NWisefinList()
        for i in obj:
            supp_tax_dtl = {"id": i['id'], "subtax_type": i['subtax__name'], "rate_name": i['name'],
                            "rate": i['rate'], "glno": i['subtax__glno'], "dflag": "O"}
            tax_dtl_list_data.append(supp_tax_dtl)

        return tax_dtl_list_data.get()


class AdvanceType:
    Vendor_Capital_Advance = 1
    Vendor_Revenue_advance = 2
    Employee_advance_And_Deposits = 3

    Vendor_Capital_Advance_Type = "Vendor Capital Advance"
    Vendor_Revenue_advance_Type = "Vendor Revenue advance"
    Employee_advance_And_Deposits_Type = "Employee advance & Deposits"


def get_advancetype(number):
    if (number == AdvanceType.Vendor_Capital_Advance):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Vendor Capital Advance'
        return vyslite

    elif (number == AdvanceType.Vendor_Revenue_advance):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Vendor Revenue advance'
        return vyslite
    elif (number == AdvanceType.Employee_advance_And_Deposits):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Employee advance & Deposits'
        return vyslite


def getadvance_list():
    idarr = [AdvanceType.Vendor_Capital_Advance, AdvanceType.Vendor_Revenue_advance,
             AdvanceType.Employee_advance_And_Deposits]
    advtypearr = [AdvanceType.Vendor_Capital_Advance_Type, AdvanceType.Vendor_Revenue_advance_Type,
                  AdvanceType.Employee_advance_And_Deposits_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = advtypearr[x]
        vyslist.append(vyslite)
    return vyslist


class Role:
    Manager = "S5"
   

#ECFTYPE
class APType:
    PO = 1
    NON_PO = 2
    ERA = 3
    ADVANCE = 4

    PO_Type = "PO"
    NON_PO_Type = "NON PO"
    ERA_Type = "ERA"
    ADVANCE_Type = "ADVANCE"

def get_ECF_type(number):
    if (number == Type.PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PO'
        return vyslite

    elif (number == Type.NON_PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO'
        return vyslite
    elif (number == Type.ERA):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ERA'
        return vyslite
    elif (number == Type.ADVANCE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ADVANCE'
        return vyslite
    else:
        vyslite = NWisefinList()
        vyslite.data=[]
        return  vyslite

def get_APType_list():
    idarr = [Type.PO, Type.NON_PO, Type.ERA, Type.ADVANCE]
    typearr = [Type.PO_Type, Type.NON_PO_Type,Type.ERA_Type, Type.ADVANCE_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist
