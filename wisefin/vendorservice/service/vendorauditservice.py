import django

import pytz
from django.db import IntegrityError
from vendorservice.data.response.vendorauditresponse  import VendorAuditResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService
from django.db.models import Q
from vendorservice.models.vendormodels import Vendoraudit
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.utils import timezone
now = timezone.now()
from nwisefin.settings import logger
#datetime(2020, 11, 20, 20, 8, 7, 127325, tzinfo=pytz.UTC)


class VendorAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_vendoraudit(self, vendoraudit_obj):

        #try:
            audit_var = Vendoraudit.objects.using(self._current_app_schema()).create(ref_id=vendoraudit_obj.ref_id,
                                ref_type=vendoraudit_obj.ref_type,
                                data=vendoraudit_obj.data,
                                user_id=vendoraudit_obj.user_id,
                                date=now,
                                req_status=vendoraudit_obj.req_status,
                                rel_refid=vendoraudit_obj.rel_refid,
                                rel_reftype=vendoraudit_obj.rel_reftype,
                                action=vendoraudit_obj.action, entity_id=self._entity_id()) #portal_flag=vendoraudit_obj.get_portal_flag())

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

            audit_data = VendorAuditResponse()
            audit_data.set_id(audit_var.id)
            audit_data.set_refid(audit_var.ref_id)
            audit_data.set_reftype(audit_var.ref_type)
            audit_data.set_data(audit_var.data)
            audit_data.set_date(audit_var.date)
            audit_data.set_reqstatus(audit_var.req_status)
            audit_data.set_relrefid(audit_var.rel_refid)
            audit_data.set_relreftype(audit_var.rel_reftype)
            audit_data.set_action(audit_var.action)
            audit_data.set_portal_flag(audit_var.portal_flag)
            return audit_data

    def fetch_vendoraudit_list(self,user_id):
        auditlist = Vendoraudit.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(auditlist)
        logger.info(str(list_length))
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
            return error_obj
        else:
            audit_list_data = NWisefinList()
            for auditobj in auditlist:
                audit_data = VendorAuditResponse()
                audit_data.set_id(auditobj.id)
                audit_data.set_refid(auditobj.ref_id)
                audit_data.set_reftype(auditobj.ref_type)
                audit_data.set_data(auditobj.data)
                audit_data.set_date(auditobj.date)
                audit_data.set_reqstatus(auditobj.req_status)
                audit_data.set_relrefid(auditobj.rel_refid)
                audit_data.set_relreftype(auditobj.rel_reftype)
                audit_data.set_action(auditobj.action)
                audit_data.set_portal_flag(auditobj.portal_flag)
                audit_list_data.append(audit_data)
            return audit_list_data

    def fetch_vendoraudit(self,vendoraudit_id,user_id,vys_page):
        auditlist = Vendoraudit.objects.using(self._current_app_schema()).filter(ref_id=vendoraudit_id, entity_id=self._entity_id()).order_by('date')[vys_page.get_offset():vys_page.get_query_limit()]

        vlist = NWisefinList()
        # user_list = []
        # for vendor in auditlist:
        #     user_list.append(vendor.created_by)
        # user_list = set(user_list)
        # user_list = list(user_list)
        # utility_service = VysfinUtilityService()
        # user_list_obj = utility_service.get_user_info(request, user_list)

        for auditobj in auditlist:
            audit_data = VendorAuditResponse()
            audit_data.set_id(auditobj.id)
            audit_data.set_refid(auditobj.ref_id)
            audit_data.set_reftype(auditobj.ref_type)
            audit_data.set_data(auditobj.data)
            audit_data.set_date(auditobj.date)
            audit_data.set_reqstatus(auditobj.req_status)
            audit_data.set_relrefid(auditobj.rel_refid)
            audit_data.set_relreftype(auditobj.rel_reftype)
            audit_data.set_action(auditobj.action)
            audit_data.set_portal_flag(auditobj.portal_flag)
            # for ul in user_list_obj['data']:
            #     if ul['id'] == SupplierBranch.created_by:
            #         audit_data.set_created_by(ul)
            vlist.append(audit_data)
            vpage = NWisefinPaginator(auditlist, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    # def fetch_vendoraudit(self, vendoraudit_id,user_id):
    #     try:
    #         auditobj = Vendoraudit.objects.get(id=vendoraudit_id)
    #         audit_data = VendorAuditResponse()
    #         audit_data.set_id(auditobj.id)
    #         audit_data.set_refid(auditobj.ref_id)
    #         audit_data.set_reftype(auditobj.ref_type)
    #         audit_data.set_data(auditobj.data)
    #         audit_data.set_date(auditobj.date)
    #         audit_data.set_reqstatus(auditobj.req_status)
    #         audit_data.set_relrefid(auditobj.rel_refid)
    #         audit_data.set_relreftype(auditobj.rel_reftype)
    #         audit_data.set_action(auditobj.action)
    #
    #         return audit_data
    #     except Vendoraudit.DoesNotExist:
    #         error_obj = Error()
    #         error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
    #         return error_obj

    def delete_vendoraudit(self, vendoraudit_id,user_id):
        audit = Vendoraudit.objects.using(self._current_app_schema()).filter(id=vendoraudit_id, entity_id=self._entity_id()).delete()
        if audit[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
