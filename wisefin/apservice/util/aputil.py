import json
import traceback
import requests
from nwisefin import settings
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList


class AP_Status:
    NEW = 1
    PENDING_FOR_APPROVAL= 2
    BOUNCE= 3
    RE_AUDIT= 4
    REJECTED= 5
    PAYMENT_INITIATE= 6
    APPROVED = 7
    PAID = 8
    FILE_INITIATE = 9
    AP_INITIATE = 10
    PAY_INITIATE = 11



    NEW_VAL ='NEW'
    PENDING_FOR_APPROVAL_VAL="PENDING FOR APPROVAL"
    BOUNCE_VAL="BOUNCE"
    APPROVED_VAL='APPROVED'
    RE_AUDIT_VAL='RE-AUDIT'
    REJECTED_VAL='REJECTED'
    PAYMENT_INITIATE_VAL='PAYMENT INITIATED'
    PAID_VAL = 'PAID'
    FILE_INITIATE_VAL = 'FILE INITIATED'
    AP_INITIATE_VAL = 'AP INITIATED'
    PAY_INITIATE_VAL = 'PAY INITIATED'

class dropdown_status:
    REVIEWED_BY_ME = 1
    APPROVED_BY_ME = 7
    REJECTED_BY_ME = 5


    REVIEWED_BY_ME_VAL = 'REVIEWED BY ME'
    APPROVED_BY_ME_VAL = 'APPROVED BY ME'
    REJECTED_BY_ME_VAL = 'REJECTED BY ME'



def get_AP_status(integer):
    if (integer == AP_Status.NEW):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.NEW
        vyslite.text = AP_Status.NEW_VAL
        return vyslite

    elif (integer == AP_Status.BOUNCE):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.BOUNCE
        vyslite.text = AP_Status.BOUNCE_VAL
        return vyslite

    elif (integer == AP_Status.PAYMENT_INITIATE):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.PAYMENT_INITIATE
        vyslite.text = AP_Status.PAYMENT_INITIATE_VAL
        return vyslite

    elif (integer == AP_Status.PENDING_FOR_APPROVAL):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.PENDING_FOR_APPROVAL
        vyslite.text = AP_Status.PENDING_FOR_APPROVAL_VAL
        return vyslite

    elif (integer == AP_Status.PAID):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.PAID
        vyslite.text = AP_Status.PAID_VAL
        return vyslite

    elif (integer == AP_Status.APPROVED):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.APPROVED
        vyslite.text = AP_Status.APPROVED_VAL
        return vyslite

    elif (integer == AP_Status.RE_AUDIT):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.RE_AUDIT
        vyslite.text = AP_Status.RE_AUDIT_VAL
        return vyslite

    elif (integer == AP_Status.REJECTED):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.REJECTED
        vyslite.text = AP_Status.REJECTED_VAL
        return vyslite

    elif (integer == AP_Status.FILE_INITIATE):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.FILE_INITIATE
        vyslite.text = AP_Status.FILE_INITIATE_VAL
        return vyslite

    elif (integer == AP_Status.AP_INITIATE):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.AP_INITIATE
        vyslite.text = AP_Status.AP_INITIATE_VAL
        return vyslite

    elif (integer == AP_Status.PAY_INITIATE):
        vyslite = NWisefinLiteList()
        vyslite.id = AP_Status.PAY_INITIATE
        vyslite.text = AP_Status.PAY_INITIATE_VAL
        return vyslite

    else:
        return None

def get_AP_status_list():
    idarr = [AP_Status.NEW,AP_Status.PAID,AP_Status.APPROVED,AP_Status.RE_AUDIT,
             AP_Status.REJECTED,AP_Status.PAYMENT_INITIATE,AP_Status.FILE_INITIATE]
    text_arr = [AP_Status.NEW_VAL,AP_Status.PAID_VAL,AP_Status.APPROVED_VAL,
                AP_Status.RE_AUDIT_VAL , AP_Status.REJECTED_VAL,AP_Status.PAYMENT_INITIATE_VAL,AP_Status.FILE_INITIATE_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = text_arr[x]
        vyslist.append(vyslite)
    return vyslist


def get_dropdown_list():
    idarr = [dropdown_status.REVIEWED_BY_ME,AP_Status.PENDING_FOR_APPROVAL,AP_Status.BOUNCE,
             dropdown_status.APPROVED_BY_ME,dropdown_status.REJECTED_BY_ME,
             AP_Status.PAYMENT_INITIATE,AP_Status.FILE_INITIATE]
    text_arr = [dropdown_status.REVIEWED_BY_ME_VAL,AP_Status.PENDING_FOR_APPROVAL_VAL,AP_Status.BOUNCE_VAL,
                dropdown_status.APPROVED_BY_ME_VAL , dropdown_status.REJECTED_BY_ME_VAL,
                AP_Status.PAYMENT_INITIATE_VAL,AP_Status.FILE_INITIATE_VAL]
    length = len(idarr)
    vyslist = NWisefinList()

    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = text_arr[x]
        vyslist.append(vyslite)
    return vyslist


def get_dropdown_payment_file_list():
    idarr = [AP_Status.PAID,AP_Status.PAYMENT_INITIATE,AP_Status.FILE_INITIATE]
    text_arr = [AP_Status.PAID_VAL,AP_Status.PAYMENT_INITIATE_VAL,AP_Status.FILE_INITIATE_VAL]
    length = len(idarr)
    vyslist = NWisefinList()

    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = text_arr[x]
        vyslist.append(vyslite)
    return vyslist



class APDocModule:
    AP=11


class audit_checklist_value:
    OK=1
    NOT_OK=2
    NOT_APPLICABLE=3

    OK_VAL = "OK"
    NOT_OK_VAL = "NOT_OK"
    NOT_APPLICABLE_VAL = "NOT_APPLICABLE"

def get_audit_checklist_value(number):
    if (number == audit_checklist_value.OK):
        vyslite = NWisefinLiteList()
        vyslite.id = audit_checklist_value.OK
        vyslite.text = audit_checklist_value.OK_VAL
        return vyslite
    elif (number == audit_checklist_value.NOT_OK):
        vyslite = NWisefinLiteList()
        vyslite.id = audit_checklist_value.NOT_OK
        vyslite.text = audit_checklist_value.NOT_OK_VAL
        return vyslite
    elif (number == audit_checklist_value.NOT_APPLICABLE):
        vyslite = NWisefinLiteList()
        vyslite.id = audit_checklist_value.NOT_APPLICABLE
        vyslite.text = audit_checklist_value.NOT_APPLICABLE_VAL
        return vyslite
    else:
        return None



class Yes_Or_No:
    YES=1
    NO=0
    YES_VAL="YES"
    NO_VAL="NO"

def get_yes_or_no(number):
    if (number == Yes_Or_No.YES):
        vyslite = NWisefinLiteList()
        vyslite.id = Yes_Or_No.YES
        vyslite.text = Yes_Or_No.YES_VAL
        return vyslite
    elif (number == Yes_Or_No.NO):
        vyslite = NWisefinLiteList()
        vyslite.id = Yes_Or_No.NO
        vyslite.text = Yes_Or_No.NO_VAL
        return vyslite

def get_yes_or_no_list():
    idarr = [Yes_Or_No.YES, Yes_Or_No.NO]
    textarr = [Yes_Or_No.YES_VAL, Yes_Or_No.NO_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = textarr[x]
        vyslist.append(vyslite)
    return vyslist


class APModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2


class APRefType:
    APHEADER = 1
    APINVOICEHEADER=2
    APINVOICEPO=3
    APINVOICEDETAIL=4
    APDEBIT=5
    APAUDITCHECKLIST=6
    APAUDITCHECKLIST_MAP=7
    PAYMENTHEADER=8
    PAYMENTDETAILS=9
    APINVOICEPOMAP=10
    APDEBITCCBS=11
    APCREDIT=12
    AP_PPXHeader=13
    AP_PPXDetails=14
    AP_File=15


class APRequestStatusUtil:
    ONBORD = 1

    ONBOARD_VAL = "ONBOARD"


#APTYPE
class APType:
    PO = 1
    NON_PO = 2
    PETTYCASH = 3
    ADVANCE = 4

    PO_VAL = "PO"
    NON_PO_VAL = "NON PO"
    PETTYCASH_VAL = "PETTYCASH"
    ADVANCE_VAL = "ADVANCE"



def get_APType(number):
    if (number == APType.PO):
        vyslite = NWisefinLiteList()
        vyslite.id = APType.PO
        vyslite.text = APType.PO_VAL
        return vyslite
    elif (number == APType.NON_PO):
        vyslite = NWisefinLiteList()
        vyslite.id = APType.NON_PO
        vyslite.text = APType.NON_PO_VAL
        return vyslite
    elif (number == APType.PETTYCASH):
        vyslite = NWisefinLiteList()
        vyslite.id = APType.PETTYCASH
        vyslite.text = APType.PETTYCASH_VAL
        return vyslite
    elif (number == APType.ADVANCE):
        vyslite = NWisefinLiteList()
        vyslite.id = APType.ADVANCE
        vyslite.text = APType.ADVANCE_VAL
        return vyslite

def get_aptype_list():
    idarr = [APType.PO, APType.NON_PO,APType.PETTYCASH,APType.ADVANCE]

    typearr = [APType.PO_VAL, APType.NON_PO_VAL,APType.PETTYCASH_VAL,APType.ADVANCE_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist

class APStatus:
    DRAFT=1
    PENDING_FOR_APPROVAL=2
    APPROVED=3
    REJECT=4
    PENDING_FOR_APPROVAL_MODIFICATION = 5
    DELETE = 6

    DRAFT_VAL= "DRAFT"
    PENDING_FOR_APPROVAL_VAL = "PENDING_FOR_APPROVAL"
    APPROVED_VAL = "APPROVED"
    REJECT_VAL = "REJECT"
    PENDING_FOR_APPROVAL_MODIFICATION_VAL = "PENDING_FOR_APPROVAL_MODIFICATION"
    DELETE_VAL = "DELETE"

def get_apstatus(number):
    if (number == APStatus.DRAFT):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.DRAFT
        vyslite.text = APStatus.DRAFT_VAL
        return vyslite
    elif (number == APStatus.PENDING_FOR_APPROVAL):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.PENDING_FOR_APPROVAL
        vyslite.text = APStatus.PENDING_FOR_APPROVAL_VAL
        return vyslite
    elif (number == APStatus.APPROVED):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.APPROVED
        vyslite.text = APStatus.APPROVED_VAL
        return vyslite
    elif (number == APStatus.REJECT):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.REJECT
        vyslite.text = APStatus.REJECT_VAL
        return vyslite
    elif (number == APStatus.PENDING_FOR_APPROVAL_MODIFICATION):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.PENDING_FOR_APPROVAL_MODIFICATION
        vyslite.text = APStatus.PENDING_FOR_APPROVAL_MODIFICATION_VAL
        return vyslite
    elif (number == APStatus.DELETE):
        vyslite = NWisefinLiteList()
        vyslite.id = APStatus.DELETE
        vyslite.text = APStatus.DELETE_VAL
        return vyslite


# PPX_TYPE
class PPX_TYPE:
    EMPLOYEE = 'E'
    SUPPLIER = 'S'
    EMPLOYEE_PPX_VAL = "EMPLOYEE"
    SUPPLIER_PPX_VAL = "SUPPLIER"

def get_ppxtype(string):
    if (string == PPX_TYPE.EMPLOYEE):
        vyslite = NWisefinLiteList()
        vyslite.id = PPX_TYPE.EMPLOYEE
        vyslite.text = PPX_TYPE.EMPLOYEE_PPX_VAL
        return vyslite
    elif (string == PPX_TYPE.SUPPLIER):
        vyslite = NWisefinLiteList()
        vyslite.id =  PPX_TYPE.SUPPLIER
        vyslite.text =  PPX_TYPE.SUPPLIER_PPX_VAL
        return vyslite

def get_ppxtype_list():
    idarr = [PPX_TYPE.EMPLOYEE, PPX_TYPE.SUPPLIER]
    PPXarr = [PPX_TYPE.EMPLOYEE_PPX_VAL, PPX_TYPE.SUPPLIER_PPX_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = PPXarr[x]
        vyslist.append(vyslite)
    return vyslist



# PAY_TO
class PAY_TO:
    EMPLOYEE = 'E'
    SUPPLIER = 'S'
    BRANCH = 'B'

    EMPLOYEE_VAL = "EMPLOYEE"
    SUPPLIER_VAL = "SUPPLIER"
    BRANCH_VAL = "BRANCH"


def get_pay_to(string):
    if (string == PAY_TO.EMPLOYEE):
        vyslite = NWisefinLiteList()
        vyslite.id = PAY_TO.EMPLOYEE
        vyslite.text = PAY_TO.EMPLOYEE_VAL
        return vyslite
    elif (string == PAY_TO.SUPPLIER):
        vyslite = NWisefinLiteList()
        vyslite.id = PAY_TO.SUPPLIER
        vyslite.text = PAY_TO.SUPPLIER_VAL
        return vyslite
    elif (string == PAY_TO.BRANCH):
        vyslite = NWisefinLiteList()
        vyslite.id = PAY_TO.BRANCH
        vyslite.text = PAY_TO.BRANCH_VAL
        return vyslite


def get_Pay_to_list(nurmber):
    if (int(nurmber) == 3):
        idarr = [PAY_TO.EMPLOYEE, PAY_TO.BRANCH]
        Payarr = [PAY_TO.EMPLOYEE_VAL, PAY_TO.BRANCH_VAL]
    elif (int(nurmber) == 4):
        idarr = [PAY_TO.EMPLOYEE, PAY_TO.SUPPLIER]
        Payarr = [PAY_TO.EMPLOYEE_VAL, PAY_TO.SUPPLIER_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = Payarr[x]
        vyslist.append(vyslite)
    return vyslist




def ap_post_api_caller(request,api_jsondata) :
    try:
        serverport_ip = settings.SERVER_IP
        api_url=api_jsondata.pop('api_url')
        full_url = serverport_ip + api_url
        token_name = request.headers['Authorization']
        headers = {'Authorization': token_name}
        logger.info("renewal started")
        logger.info('api_jsondatastr'+str(api_jsondata))
        api_jsondata = json.dumps(api_jsondata, indent=2)
        resp = requests.post(full_url, headers=headers,data=api_jsondata, verify=False)
        api_resp = json.loads(resp.content)
        return api_resp
    except Exception as excep:
        traceback.print_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.INVALID_DATA)
        error_obj.set_description(str(excep))
        return error_obj.get()


def ap_get_api_caller(request,api_json) :
    try:
        serverport_ip = settings.SERVER_IP
        api_url=api_json['api_url']
        full_url = serverport_ip + api_url
        logger.info('full_url '+str(full_url))
        logger.info('full_url '+str(full_url))
        token_name = request.headers['Authorization']
        headers = {'Authorization': token_name}
        resp = requests.get(full_url, headers=headers, verify=False)
        logger.info('resp.text '+str(resp.text))
        logger.info('resp '+str(resp))
        logger.info('status_code '+str(resp.status_code))
        logger.info('status_code '+str(resp.status_code))
        logger.info('resp.content '+str(resp.content))
        api_resp = json.loads(resp.content)
        logger.info('after_loads '+str(api_resp))
        return api_resp
    except Exception as excep:
        traceback.print_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.INVALID_DATA)
        error_obj.set_description(str(excep))
        return error_obj





def get_apfileextension_val(extension):
    if extension in ['txt','doc','pdf','ppt','pot','pps','pptx','odt','odg','odp','ods','docx','docm','dotx','dotm','docb',
                     'xlsx','xls','xlt','xlm','xlsm','xltx','xltm','jpg', 'jpeg','tiff', 'tif','png','TXT','DOC','PDF','PPT',
                     'POT','PPS','PPTX','ODT','ODG','ODP','ODS','DOCX','DOCM','DOTX','DOTM','DOCB','XLSX','XLS','XLT','XLM',
                     'XLSM','XLTX','XLTM','JPG', 'JPEG','TIFF', 'TIF','PNG']:
        return False
    else:
        return extension

