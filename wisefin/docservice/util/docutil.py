from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList


class DocModule:
    MEMO = 1
    INWARD = 2
    VENDOR = 3
    PROOFING = 4
    PD = 5
    PR = 6
    SG = 7
    TA = 8
    DTPC = 9
    FA = 10
    AP = 11
    ECF = 12
    REPORT = 13
    JV = 14
    MASTER = 15
    CMS = 16
    QUES = 17
    ATD = 18
    HRMS=19

    def get_prefix_modulenum_(self, module_prefix):
        if module_prefix == DocPrefix.MEMO:
            return self.MEMO
        elif module_prefix == DocPrefix.INWARD:
            return self.INWARD
        elif module_prefix == DocPrefix.VENDOR:
            return self.VENDOR
        elif module_prefix == DocPrefix.PROOFING:
            return self.PROOFING
        elif module_prefix == DocPrefix.PD:
            return self.PD
        elif module_prefix == DocPrefix.PR:
            return self.PR
        elif module_prefix == DocPrefix.SG:
            return self.SG
        elif module_prefix == DocPrefix.DTPC:
            return self.DTPC
        elif module_prefix == DocPrefix.TA:
            return self.TA
        elif module_prefix == DocPrefix.FA:
            return self.FA
        elif module_prefix == DocPrefix.AP:
            return self.AP
        elif module_prefix == DocPrefix.ECF:
            return self.ECF
        elif module_prefix == DocPrefix.REPORT:
            return self.REPORT
        elif module_prefix == DocPrefix.JV:
            return self.JV
        elif module_prefix == DocPrefix.MASTER:
            return self.MASTER
        elif module_prefix == DocPrefix.CMS:
            return self.CMS
        elif module_prefix == DocPrefix.QUES:
            return self.QUES
        elif module_prefix == DocPrefix.ATD:
            return self.ATD
        elif module_prefix == DocPrefix.HRMS:
            return self.HRMS



class DocPrefix:
    MEMO = 'Memo_'
    INWARD = 'Inwd_'
    VENDOR = 'Vndr_'
    PROOFING = 'Prf_'
    PD = 'Rems_'
    PR = 'Prpo_'
    SG = 'sg_'
    TA = 'ta_'
    DTPC = 'DTPC_'
    FA = 'FA_'
    AP = 'AP_'
    ECF = 'ECF_'
    REPORT = 'REPORT_'
    JV = 'JV_'
    MASTER = 'Master_'
    CMS = 'CMS_'
    QUES = 'QUS_'
    ATD = 'ATD_'
    HRMS ='HRMS_'

    def get_prefix(self, module):
        if module == DocModule.MEMO:
            return self.MEMO
        elif module == DocModule.INWARD:
            return self.INWARD
        elif module == DocModule.VENDOR:
            return self.VENDOR
        elif module == DocModule.PROOFING:
            return self.PROOFING
        elif module == DocModule.PD:
            return self.PD
        elif module == DocModule.PR:
            return self.PR
        elif module == DocModule.SG:
            return self.SG
        elif module == DocModule.DTPC:
            return self.DTPC
        elif module == DocModule.TA:
            return self.TA
        elif module == DocModule.FA:
            return self.FA
        elif module == DocModule.AP:
            return self.AP
        elif module == DocModule.ECF:
            return self.ECF
        elif module == DocModule.REPORT:
            return self.REPORT
        elif module == DocModule.JV:
            return self.JV
        elif module == DocModule.MASTER:
            return self.MASTER
        elif module == DocModule.CMS:
            return self.CMS
        elif module == DocModule.QUES:
            return self.QUES
        elif module == DocModule.ATD:
            return self.ATD
        elif module == DocModule.HRMS:
            return self.HRMS


def fileexe_validation(extension):
    if extension in ['txt', 'doc', 'pdf', 'ppt', 'pot', 'pps', 'pptx', 'odt', 'odg', 'odp', 'ods', 'docx', 'docm',
                     'dotx', 'dotm', 'docb',
                     'xlsx', 'xls', 'xlt', 'xlm', 'xlsm', 'xltx', 'xltm', 'jpg', 'jpeg', 'tiff', 'tif', 'png', 'JPG',
                     'JPEG', 'PNG', 'PDF']:
        return True
    else:
        return False


def file_validation(extension):
    if extension in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'JPG', 'JPEG', 'PNG', 'PDF', 'pdf']:
        return True
    else:
        return False


class DocModuleType:
    PR = 6
    TA = 8

    PR_Type = "PR"
    TA_Type = "TA"


def getDocModuleType(number):
    if (number == DocModuleType.PR):
        vyslite = dict()
        vyslite["id"] = number
        vyslite["text"] = DocModuleType.PR_Type
        vyslite["prefix"] = DocPrefix.PR
        return vyslite


def getDocModuleType_ta(request):
    if (int(request.GET.get('module')) == DocModuleType.TA):
        vyslite = dict()
        vyslite["id"] = request.GET.get('ta_id')
        vyslite["module"] = request.GET.get('module')
        vyslite["text"] = DocModuleType.TA_Type
        vyslite["prefix"] = DocPrefix.TA
        return vyslite


def get_docmodule_type_list():
    idarr = [DocModuleType.PR]
    typearr = [DocModuleType.PR_Type]
    prefixarr = [DocPrefix.PR]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslite.prefix = prefixarr[x]
        vyslist.append(vyslite)
    return vyslist


def exel_file_validation(extension):
    if extension in ['xlsx', 'xls', 'xlt', 'xlm', 'xlsm', 'xltx', 'xltm']:
        return True
    else:
        return False
