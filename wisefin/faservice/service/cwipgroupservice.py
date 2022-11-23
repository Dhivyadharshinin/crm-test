import traceback

from django.db import IntegrityError
from django.db.models import Q
from faservice.data.response.cwipgroupresponse import CwipGroupResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import AssetLocation, CwipGroup
from faservice.service.faauditservice import FaAuditService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
#from inwardservice.models import EscalationType
from inwardservice.models import EscalationType
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CwipGroupService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_cwipgroup(self, cwipgroup_obj, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        if not cwipgroup_obj.get_id() is None:
            try:
                cwipgroup_var = CwipGroup.objects.filter(id=cwipgroup_obj.get_id()).update(
                    name=cwipgroup_obj.get_name(),
                    gl=cwipgroup_obj.get_gl(),
                    doctype=cwipgroup_obj.get_doctype(),
                    updated_date=now(),
                    updated_by=emp_id)

                cwipgroup = CwipGroup.objects.get(id=cwipgroup_obj.get_id())

                refid = ref_type = -1
                relrefid = cwipgroup.id
                self.audit_function(cwipgroup, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus)
            except IntegrityError as error:
                logger.info('FAL_CWIPGROUP_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EscalationType.DoesNotExist:
                logger.info('FAL_CWIPGROUP_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_CWIPGROUP_ID)
                error_obj.set_description(ErrorDescription.INVALID_CWIPGROUP_ID)
                return error_obj
            except:
                logger.info('FAL_CWIPGROUP_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
           # try:
                cwipgroup = CwipGroup.objects.create(
                                                    name=cwipgroup_obj.get_name(),
                                                    gl=cwipgroup_obj.get_gl(),
                                                    doctype=cwipgroup_obj.get_doctype(),
                                                    created_by=emp_id)

                code = "FACG" + str(cwipgroup.id)
                cwipgroup.code = code
                cwipgroup.save()

                refid = ref_type = -1
                relrefid = cwipgroup.id
                self.audit_function(cwipgroup, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus)

            # except IntegrityError as error:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        cwipgroup_resp = CwipGroupResponse()
        cwipgroup_resp.set_id(cwipgroup.id)
        cwipgroup_resp.set_code(cwipgroup.code)
        cwipgroup_resp.set_gl(cwipgroup.gl)
        cwipgroup_resp.set_name(cwipgroup.name)
        cwipgroup_resp.set_doctype(cwipgroup.doctype)
        return cwipgroup_resp

    def fetch_cwipgroup_list(self,query, vys_page):
        condition=Q(status=1)
        if not query is str():
            condition&= Q(name__icontains=query)
        cwipgroup_data = CwipGroup.objects.filter(condition).order_by('created_by')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cwipgroup_data)
        #print(list_length)
        cwipgroup_list = NWisefinList()
        if list_length > 0:
            for cwipgroup in cwipgroup_data:
                cwipgroup_resp = CwipGroupResponse()
                cwipgroup_resp.set_id(cwipgroup.id)
                cwipgroup_resp.set_code(cwipgroup.code)
                cwipgroup_resp.set_gl(cwipgroup.gl)
                cwipgroup_resp.set_name(cwipgroup.name)
                cwipgroup_resp.set_doctype(cwipgroup.doctype)
                cwipgroup_list.append(cwipgroup_resp)
            vpage = NWisefinPaginator(cwipgroup_data, vys_page.get_index(), 10)
            cwipgroup_list.set_pagination(vpage)
        return cwipgroup_list

    # def fetch_assetlocation(self,assetlocation_id):
    #     try:
    #         assetlocation = AssetLocation.objects.get(id=assetlocation_id)
    #
    #         assetlocation_resp = AssetLocationResponse()
    #         assetlocation_resp.set_id(assetlocation.id)
    #         assetlocation_resp.set_refgid(assetlocation.refgid)
    #         assetlocation_resp.set_reftablegid(assetlocation.reftablegid)
    #         assetlocation_resp.set_name(assetlocation.name)
    #         assetlocation_resp.set_floor(assetlocation.floor)
    #         assetlocation_resp.set_remarks(assetlocation.remarks)
    #         return assetlocation_resp
    #     except AssetLocation.DoesNotExist:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
    #         return error_obj
    #
    # def delete_assetlocation(self,assetlocation_id,emp_id):
    #     assetlocation = AssetLocation.objects.filter(id=assetlocation_id).delete()
    #     reqstatus = FaRequestStatusUtil.ONBORD
    #
    #     refid = ref_type = -1
    #     relrefid = assetlocation_id
    #     self.audit_function(assetlocation, refid, ref_type, relrefid,
    #                         emp_id, FaModifyStatus.DELETE, reqstatus)
    #     if assetlocation[0] == 0:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
    #         return error_obj
    #     else:
    #         success_obj = Success()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #         return success_obj


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
        audit_obj.set_relreftype(FaRefType.ASSETLOCATION)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)