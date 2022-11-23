import json
import requests
from nwisefin import settings
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList

class Inward_Status:
    NEW = 1
    # PENDING = 2
    PARTIALCOMPLETED = 3
    COMPLETED = 4
    # APPROVED = 4

    NEW_VAL = 'New'
    # PENDING_VAL = 'Pending'
    PARTIALCOMPLETED_VAL = 'Partial Completed'
    COMPLETED_VAL = 'Completed'
    # APPROVED_VAL = 'APPROVED'


def get_inward_status(integer):
    if (integer == Inward_Status.NEW):
        vyslite = NWisefinLiteList()
        vyslite.id = Inward_Status.NEW
        vyslite.text = Inward_Status.NEW_VAL
        return vyslite

    # elif (integer == Inward_Status.PENDING):
    #     vyslite = NWisefinLiteList()
    #     vyslite.id = Inward_Status.PENDING
    #     vyslite.text = Inward_Status.PENDING_VAL
    #     return vyslite

    elif (integer == Inward_Status.PARTIALCOMPLETED):
        vyslite = NWisefinLiteList()
        vyslite.id = Inward_Status.PARTIALCOMPLETED
        vyslite.text = Inward_Status.PARTIALCOMPLETED_VAL
        return vyslite

    elif (integer == Inward_Status.COMPLETED):
        vyslite = NWisefinLiteList()
        vyslite.id = Inward_Status.COMPLETED
        vyslite.text = Inward_Status.COMPLETED_VAL
        return vyslite

    # elif (integer == Inward_Status.APPROVED):
    #     vyslite = NWisefinLiteList()
    #     vyslite.id = Inward_Status.APPROVED
    #     vyslite.text = Inward_Status.APPROVED_VAL
    #     return vyslite
    else:
        return None

def get_inward_status_list():
    idarr = [Inward_Status.NEW, Inward_Status.PARTIALCOMPLETED, Inward_Status.COMPLETED]
             # Inward_Status.APPROVED]
    text_arr = [Inward_Status.NEW_VAL, Inward_Status.PARTIALCOMPLETED_VAL, Inward_Status.COMPLETED_VAL]
            # Inward_Status.APPROVED_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = text_arr[x]
        vyslist.append(vyslite)
    return vyslist

class ModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2

class InwardRefType:
    INWARD_HEADRER = 1
    INWARD_DETAIL = 2
    INWARD_FILE = 3
    INWARD_TEMPLATE = 4
    INWARD_PRODUCTCAT = 5

class RequestStatusUtil:
    ONBORD=1

def get_api_caller(request,api_json) :
    serverport_ip = settings.SERVER_IP
    api_url=api_json['api_url']
    full_url = serverport_ip + api_url
    token_name = request.headers['Authorization']
    headers = {'Authorization': token_name}
    resp = requests.get(full_url, headers=headers, verify=False)
    api_resp = json.loads(resp.content)
    return api_resp


def post_api_caller(request,api_jsondata) :
    serverport_ip = settings.SERVER_IP
    api_url=api_jsondata['api_url']
    del api_jsondata['api_url']
    full_url = serverport_ip + api_url
    token_name = request.headers['Authorization']
    headers = {'Authorization': token_name}
    resp = requests.post(full_url, headers=headers,data=api_jsondata, verify=False)
    api_resp = json.loads(resp.content)
    return api_resp

class inward_doc_status:
    ALL = 1
    ASSIGNED = 2
    UNASSIGNED = 3

    ALL_Type = "All"
    ASSIGNED_Type = "Assigned"
    UNASSIGNED_Type = "UnAssigned"

def get_inward_docstatus():
    idarr = [inward_doc_status.ALL, inward_doc_status.ASSIGNED, inward_doc_status.UNASSIGNED]
    typearr = [inward_doc_status.ALL_Type, inward_doc_status.ASSIGNED_Type,
               inward_doc_status.UNASSIGNED_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

class inward_status:
    OPEN = 1
    CLOSED = 2
    REOPEN = 3

    OPEN_Type = "Open"
    CLOSED_Type = "Closed"
    REOPEN_Type = "Reopen"

def get_inwardstatus():
    idarr = [inward_status.OPEN, inward_status.CLOSED, inward_status.REOPEN]
    typearr = [inward_status.OPEN_Type, inward_status.CLOSED_Type, inward_status.REOPEN_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

class inward_action:
    INFORMATION_ONLY = 1
    REPLY_MUST = 2
    ACTION_MUST = 3

    INFORMATION_ONLY_Type = "Information Only"
    REPLY_MUST_Type = "Reply Must"
    ACTION_MUST_Type = "Action Must"

def get_inwardaction():
    idarr = [inward_action.INFORMATION_ONLY, inward_action.REPLY_MUST, inward_action.ACTION_MUST]
    typearr = [inward_action.INFORMATION_ONLY_Type, inward_action.REPLY_MUST_Type, inward_action.ACTION_MUST_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

class inward_docaction:
    RETAINED_AT_BRANCH = 1
    DISPATCHED_TO_BRANCH = 2

    RETAINED_AT_BRANCH_Type = "Retained At Branch"
    DISPATCHED_TO_BRANCH_Type = "Dispatched To Branch"

def get_inwarddocaction():
    idarr = [inward_docaction.RETAINED_AT_BRANCH, inward_docaction.DISPATCHED_TO_BRANCH]
    typearr = [inward_docaction.RETAINED_AT_BRANCH_Type, inward_docaction.DISPATCHED_TO_BRANCH_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

def get_fileextension_val(extension):
    if extension in ['txt','doc','pdf','ppt','pot','pps','pptx','odt','odg','odp','ods','docx','docm','dotx','dotm','docb',
                     'xlsx','xls','xlt','xlm','xlsm','xltx','xltm','jpg', 'jpeg','tiff', 'tif','png']:
        return True
    else:
        return False

class DocModule:
    INWARD = 2

class RefType:
    INWARDDETAIL = 1