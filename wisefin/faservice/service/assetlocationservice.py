import traceback

from django.db import IntegrityError
from django.db.models import Q

from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import  AssetLocation
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
# from inwardservice.models import EscalationType
from userservice.data.response.branchresponse import EmployeeBranchResponse
from userservice.models import EmployeeBranch
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


class AssetLocationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetlocation(self, assetlocation_obj, emp_id,request):
        reqstatus = FaRequestStatusUtil.ONBORD
        if not assetlocation_obj.get_id() is None:
            try:
                assetlocation_var = AssetLocation.objects.filter(id=assetlocation_obj.get_id()).update(
                    refgid=1,
                    reftablegid=assetlocation_obj.get_branch_id(),
                    name=assetlocation_obj.get_name(),
                    floor=assetlocation_obj.get_floor(),
                    remarks=assetlocation_obj.get_remarks(),
                    updated_date=now(),
                    updated_by=emp_id)

                assetlocation = AssetLocation.objects.get(id=assetlocation_obj.get_id())

                refid = ref_type = -1
                relrefid = assetlocation.id
                self.audit_function(assetlocation, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus)
            except IntegrityError as error:
                logger.info('FAL_ASSETLOCATION_EXCEPT:{}'.format(traceback.print_exc()))

                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            # except EscalationType.DoesNotExist:
            #     error_obj = Error()
            #     error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
            #     return error_obj
            except:
                logger.info('FAL_ASSETLOCATION_EXCEPT:{}'.format(traceback.print_exc()))

                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
           # try:
                assetlocation = AssetLocation.objects.create(
                                        refgid=1,
                                        reftablegid=assetlocation_obj.get_branch_id(),
                                        name=assetlocation_obj.get_name(),
                                        floor=assetlocation_obj.get_floor(),
                                        remarks=assetlocation_obj.get_remarks(),
                                                    created_by=emp_id)

                refid = ref_type = -1
                relrefid = assetlocation.id 
                self.audit_function(assetlocation, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,request)

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
        assetlocation_resp = NWisefinSuccess()
        assetlocation_resp.set_status(SuccessStatus.SUCCESS)
        assetlocation_resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return assetlocation_resp



    def fetch_assetlocation_list(self,query, vys_page,request):
        if query ==None:
            assetlocation_data = AssetLocation.objects.filter(status=1).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            q=Q(reftablegid=query) & Q(status=1)
            assetlocation_data = AssetLocation.objects.filter(q).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(assetlocation_data)
        #print(list_length)
        scope=request.scope
        api_obj = FaApiService(scope)
        assetlocation_list = NWisefinList()
        if list_length > 0:
            for assetlocation in assetlocation_data:
                assetlocation_resp = AssetLocationResponse()
                assetlocation_resp.set_id(assetlocation.id)
                assetlocation_resp.set_refgid(assetlocation.refgid)
                assetlocation_resp.set_reftablegid(assetlocation.reftablegid)
                assetlocation_resp.set_name(assetlocation.name)
                assetlocation_resp.set_floor(assetlocation.floor)
                assetlocation_resp.set_remarks(assetlocation.remarks)
                assetlocation_list.append(assetlocation_resp)
                assetlocation_resp.set_expanded(False)
                assetlocation_resp.set_branch(api_obj.fetch_branch(assetlocation.reftablegid,request))
            vpage = NWisefinPaginator(assetlocation_data, vys_page.get_index(), 10)
            assetlocation_list.set_pagination(vpage)
        return assetlocation_list

    def fetch_assetlocation(self,assetlocation_id):
        try:
            assetlocation = AssetLocation.objects.get(id=assetlocation_id)

            assetlocation_resp = AssetLocationResponse()
            assetlocation_resp.set_id(assetlocation.id)
            assetlocation_resp.set_refgid(assetlocation.refgid)
            assetlocation_resp.set_reftablegid(assetlocation.reftablegid)
            assetlocation_resp.set_name(assetlocation.name)
            assetlocation_resp.set_floor(assetlocation.floor)
            assetlocation_resp.set_remarks(assetlocation.remarks)
            return assetlocation_resp
        except AssetLocation.DoesNotExist:
            logger.info('FAL_ASSETLOCATION_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
            return error_obj

    def delete_assetlocation(self,assetlocation_id,emp_id):
        assetlocation = AssetLocation.objects.filter(id=assetlocation_id).delete()
        reqstatus = FaRequestStatusUtil.ONBORD

        refid = ref_type = -1
        relrefid = assetlocation_id
        self.audit_function(assetlocation, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.DELETE, reqstatus)
        if assetlocation[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETLOCATION_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETLOCATION_ID)
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
        audit_obj.set_relreftype(FaRefType.ASSETLOCATION)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)