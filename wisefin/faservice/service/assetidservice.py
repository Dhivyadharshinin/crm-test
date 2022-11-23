from django.db import IntegrityError
from django.db.models import Q
from faservice.data.response.assetidresponse import AssetidResponse
from faservice.models.famodels import AssetId
from faservice.service.faauditservice import FaAuditService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.data.response.faauditresponse import FaAuditResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetidService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetid(self, assetid_obj, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        if not assetid_obj.get_id() is None:
            assetid_var = AssetId.objects.filter(id=assetid_obj.get_id()).update(
                po_id=assetid_obj.get_po_id(),
                podetails_id=assetid_obj.get_podetails_id(),
                pono=assetid_obj.get_pono(),
                assetid=assetid_obj.get_assetid(),
                receiveddate=assetid_obj.get_receiveddate(),
                grninwarddetails_id=assetid_obj.get_grninwarddetails_id(),
                source=assetid_obj.get_source(),
                manufacturer=assetid_obj.get_manufacturer(),
                serialno=assetid_obj.get_serialno(),
                details=assetid_obj.get_details(),
                updated_date=now(),
                updated_by=emp_id)

            assetid_var = AssetId.objects.get(id=assetid_obj.get_id())

            refid = ref_type = -1
            relrefid = assetid_var.id
            self.audit_function(assetid_var, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.UPDATE, reqstatus)

        else:
            assetid_var = AssetId.objects.create(
                po_id=assetid_obj.get_po_id(),
                podetails_id=assetid_obj.get_podetails_id(),
                pono=assetid_obj.get_pono(),
                assetid=assetid_obj.get_assetid(),
                receiveddate=assetid_obj.get_receiveddate(),
                grninwarddetails_id=assetid_obj.get_grninwarddetails_id(),
                source=assetid_obj.get_source(),
                manufacturer=assetid_obj.get_manufacturer(),
                serialno=assetid_obj.get_serialno(),
                details=assetid_obj.get_details(),
                created_by=emp_id)

            refid = ref_type = -1
            relrefid = assetid_var.id
            self.audit_function(assetid_var, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus)

        assetid_resp = AssetidResponse()
        assetid_resp.set_id(assetid_var.id)
        assetid_resp.set_po_id(assetid_var.po_id)
        assetid_resp.set_podetails_id(assetid_var.podetails_id)
        assetid_resp.set_pono(assetid_var.pono)
        assetid_resp.set_assetid(assetid_var.assetid)
        assetid_resp.set_receiveddate(assetid_var.receiveddate)
        assetid_resp.set_grninwarddetails_id(assetid_var.grninwarddetails_id)
        assetid_resp.set_source(assetid_var.source)
        assetid_resp.set_manufacturer(assetid_var.manufacturer)
        assetid_resp.set_serialno(assetid_var.serialno)
        assetid_resp.set_details(assetid_var.details)

        return assetid_resp

    def fetch_assetid_list(self, vys_page):
        condition = Q(status=1)

        assetid_data = AssetId.objects.filter(condition).order_by('created_by'
                                                                  )[vys_page.get_offset():vys_page.get_query_limit()]
        assetid_list = NWisefinList()
        for assetid in assetid_data:
            assetid_resp = AssetidResponse()
            assetid_resp.set_id(assetid.id)
            assetid_resp.set_po_id(assetid.po_id)
            assetid_resp.set_podetails_id(assetid.podetails_id)
            assetid_resp.set_pono(assetid.pono)
            assetid_resp.set_assetid(assetid.assetid)
            assetid_resp.set_receiveddate(assetid.receiveddate)
            assetid_resp.set_grninwarddetails_id(assetid.grninwarddetails_id)
            assetid_resp.set_source(assetid.source)
            assetid_resp.set_manufacturer(assetid.manufacturer)
            assetid_resp.set_serialno(assetid.serialno)
            assetid_resp.set_details(assetid.details)
            assetid_resp.set_received(assetid.received)
            assetid_resp.set_captalised(assetid.captalised)

            assetid_list.append(assetid_resp)
        vpage = NWisefinPaginator(assetid_data, vys_page.get_index(), 10)
        assetid_list.set_pagination(vpage)

        return assetid_list

    def fetch_assetid(self, assetcat_id):
        try:
            assetid = AssetId.objects.get(id=assetcat_id)
            assetid_resp = AssetidResponse()
            assetid_resp.set_id(assetid.id)
            assetid_resp.set_po_id(assetid.po_id)
            assetid_resp.set_podetails_id(assetid.podetails_id)
            assetid_resp.set_pono(assetid.pono)
            assetid_resp.set_assetid(assetid.assetid)
            assetid_resp.set_receiveddate(assetid.receiveddate)
            assetid_resp.set_grninwarddetails_id(assetid.grninwarddetails_id)
            assetid_resp.set_source(assetid.source)
            assetid_resp.set_manufacturer(assetid.manufacturer)
            assetid_resp.set_serialno(assetid.serialno)
            assetid_resp.set_details(assetid.details)
            assetid_resp.set_received(assetid.received)
            assetid_resp.set_captalised(assetid.captalised)
            return assetid_resp

        except AssetId.DoesNotExist:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETID_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETID_ID)
            return error_obj

    def delete_assetid(self, assetcat_id, emp_id):
        assetcat = AssetId.objects.filter(id=assetcat_id).delete()
        reqstatus = FaRequestStatusUtil.ONBORD

        refid = ref_type = -1
        relrefid = assetcat_id
        self.audit_function(assetcat, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.DELETE, reqstatus)
        if assetcat[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETCAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETCAT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self, audit_data, refid, reftype, relrefid, emp_id, action, reqstatus,request=None):
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
        audit_obj.set_relreftype(FaRefType.ASSETID)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def update_assetid(self, assetid_id, data):
        obj = data
        obj = Q(data)
        AssetId.objects.filter(id=assetid_id).update(obj)
        return