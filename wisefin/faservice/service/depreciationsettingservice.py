import traceback

from django.db import IntegrityError
from django.db.models import Q

from faservice.data.response.depreciationsettingresponse import DepreciationSettingResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.data.response.assetcatresponse import AssetCatResponse
from faservice.models.famodels import  DepSettings
from faservice.service.faauditservice import FaAuditService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
#from inwardservice.data.response.escalatontyperesponse import EscalationTypeResponse
#from inwardservice.models import EscalationType
from inwardservice.models import EscalationType
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DepreciationSettingService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_depsetting(self, depsettings_obj, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        if not depsettings_obj.get_id() is None:
            try:
                depsettings_var = DepSettings.objects.filter(id=depsettings_obj.get_id()).update(
                    doctype=depsettings_obj.get_doctype(),
                    depgl = depsettings_obj.get_depgl(),
                    depreservegl = depsettings_obj.get_depreservegl(),
                    updated_date=now(),
                    updated_by=emp_id)

                depsettings = DepSettings.objects.get(id=depsettings_obj.get_id())

                refid = ref_type = -1
                relrefid = depsettings.id
                self.audit_function(depsettings, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus)
            except IntegrityError as error:
                logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EscalationType.DoesNotExist:
                logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DEPSETTING_ID)
                error_obj.set_description(ErrorDescription.INVALID_DEPSETTING_ID)
                return error_obj
            except:
                logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                depsettings = DepSettings.objects.create(
                                            doctype=depsettings_obj.get_doctype(),
                                            depgl=depsettings_obj.get_depgl(),
                                            depreservegl=depsettings_obj.get_depreservegl(),
                                                    created_by=emp_id)

                refid = ref_type = -1
                relrefid = depsettings.id
                self.audit_function(depsettings, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus)

            except IntegrityError as error:
                logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        depsetting_resp = DepreciationSettingResponse()
        depsetting_resp.set_id(depsettings.id)
        depsetting_resp.set_doctype(depsettings.doctype)
        depsetting_resp.set_depgl(depsettings.depgl)
        depsetting_resp.set_depreservegl(depsettings.depreservegl)
        return depsetting_resp

    def fetch_depsetting_list(self,query, vys_page):
        depsetting_data = DepSettings.objects.filter(status=1).order_by('created_by')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(depsetting_data)
        #print(list_length)
        assetcat_list = NWisefinList()
        if list_length > 0:
            for depsetting in depsetting_data:
                depsetting_resp = DepreciationSettingResponse()
                depsetting_resp.set_id(depsetting.id)
                depsetting_resp.set_doctype(depsetting.doctype)
                depsetting_resp.set_depgl(depsetting.depgl)
                depsetting_resp.set_depreservegl(depsetting.depreservegl)
                assetcat_list.append(depsetting_resp)
            vpage = NWisefinPaginator(depsetting_data, vys_page.get_index(), 10)
            assetcat_list.set_pagination(vpage)
        return assetcat_list

    def fetch_depsetting(self,depsetting_id):
        try:
            depsetting = DepSettings.objects.get(id=depsetting_id)
            depsetting_resp = DepreciationSettingResponse()
            depsetting_resp.set_id(depsetting.id)
            depsetting_resp.set_doctype(depsetting.doctype)
            depsetting_resp.set_depgl(depsetting.depgl)
            depsetting_resp.set_depreservegl(depsetting.depreservegl)
            return depsetting_resp
        except DepSettings.DoesNotExist:
            logger.info('FAL_DEPSETTINGS_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DEPSETTING_ID)
            error_obj.set_description(ErrorDescription.INVALID_DEPSETTING_ID)
            return error_obj

    def delete_depsetting(self,depsetting_id,emp_id):
        depsetting = DepSettings.objects.filter(id=depsetting_id).delete()
        reqstatus = FaRequestStatusUtil.ONBORD

        refid = ref_type = -1
        relrefid = depsetting_id
        self.audit_function(depsetting, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.DELETE, reqstatus)
        if depsetting[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DEPSETTING_ID)
            error_obj.set_description(ErrorDescription.INVALID_DEPSETTING_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request=None):
        if action == FaModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        scope=request.scope
        audit_service = FaAuditService(scope)
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.DEPRECIATION_SETTING)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)