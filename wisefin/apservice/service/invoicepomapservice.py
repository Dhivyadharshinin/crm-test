import json
import traceback
from datetime import datetime
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from apservice.data.response.apauditresponse import APAuditResponse
from apservice.data.response.invoicepomapresponse import APInvoicemapResponse
from apservice.models import  APMapInvoicePO
from apservice.service.apauditservice import APAuditService
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
from apservice.util.aputil import APModifyStatus, APRefType, ap_get_api_caller, get_APType, get_AP_status, AP_Status
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList, ModuleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now

class APInvoicePOMAPService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def apinvoicepomap_create(self,request,apinvoicepomap_obj,apinvoicehdr_id,apinvoicedtls_id,emp_id):
        try:
            with transaction.atomic(using=self._current_app_schema()):
                if not apinvoicepomap_obj.get_id() is None:
                    apinvoicepomap_update = APMapInvoicePO.objects.using(self._current_app_schema()).filter(id=apinvoicepomap_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                        apinvoiceheader_id= apinvoicehdr_id,
                                                                                        apinvoicedetail_id = apinvoicedtls_id,
                                                                                        invoiceno=apinvoicepomap_obj.get_invoiceno(),
                                                                                        pono = apinvoicepomap_obj.get_pono(),
                                                                                        podetailno = apinvoicepomap_obj.get_podetailno(),
                                                                                        grninwardno = apinvoicepomap_obj.get_grninwardno(),
                                                                                        productcode = apinvoicepomap_obj.get_productcode(),
                                                                                        invoicepo_qty = apinvoicepomap_obj.get_invoicepo_qty(),
                                                                                        invoicepo_capitalised = apinvoicepomap_obj.get_invoicepo_capitalised(),
                                                                                        updated_by=emp_id,
                                                                                        updated_date=now())
                    apinvoicepomap = APMapInvoicePO.objects.using(self._current_app_schema()).get(id=apinvoicepomap_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(apinvoicepomap, apinvoicepomap.id, apinvoicepomap.id, emp_id,
                                        APModifyStatus.UPDATE, APRefType.APINVOICEPOMAP)

                else:
                    apinvoicepomap = APMapInvoicePO.objects.using(self._current_app_schema()).create(
                                                        apinvoiceheader_id=apinvoicehdr_id,
                                                        apinvoicedetail_id=apinvoicedtls_id,
                                                        invoiceno=apinvoicepomap_obj.get_invoiceno(),
                                                        pono=apinvoicepomap_obj.get_pono(),
                                                        podetailno=apinvoicepomap_obj.get_podetailno(),
                                                        grninwardno=apinvoicepomap_obj.get_grninwardno(),
                                                        productcode=apinvoicepomap_obj.get_productcode(),
                                                        invoicepo_qty=apinvoicepomap_obj.get_invoicepo_qty(),
                                                        invoicepo_capitalised=apinvoicepomap_obj.get_invoicepo_capitalised(),
                                                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(apinvoicepomap, apinvoicepomap.id, apinvoicepomap.id, emp_id,
                                        APModifyStatus.CREATE, APRefType.APINVOICEPOMAP)

                apinvoicepomap_data = APInvoicemapResponse()
                apinvhdr_serv=APInvoiceheaderService(self._scope())
                apinvdtls_serv=APInvoiceDetailService(self._scope())

                apinvoicepomap_data.set_id(apinvoicepomap.id)
                apinvoicepomap_data.set_apinvoiceheader_id(apinvoicepomap.apinvoiceheader_id)
                apinvoicepomap_data.set_apinvoicedetail_id(apinvoicepomap.apinvoicedetail_id)
                apinvoicepomap_data.set_apinvoiceheader(apinvhdr_serv.single_get_apinwardinvoiceheader(request,apinvoicepomap.apinvoiceheader_id,emp_id))
                apinvoicepomap_data.set_apinvoicedetail(apinvdtls_serv.get_apinvoicedetails_single(request,apinvoicepomap.apinvoicedetail_id))
                apinvoicepomap_data.set_invoiceno(apinvoicepomap.invoiceno)
                apinvoicepomap_data.set_pono(apinvoicepomap.pono)
                apinvoicepomap_data.set_invoicepo_qty(apinvoicepomap.invoicepo_qty)
                apinvoicepomap_data.set_podetailno(apinvoicepomap.podetailno)
                apinvoicepomap_data.set_grninwardno(apinvoicepomap.grninwardno)
                apinvoicepomap_data.set_productcode(apinvoicepomap.productcode)
                apinvoicepomap_data.set_invoicepo_capitalised(apinvoicepomap.invoicepo_capitalised)
                return apinvoicepomap_data
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def get_apinvoicepomap_list(self,request,vys_page,emp_id):
        try:
            apinvoicepomap_data = APMapInvoicePO.objects.using(self._current_app_schema()).filter(
                status=1,is_delete=0,entity_id=self._entity_id())
            return_list=NWisefinList()
            if len(apinvoicepomap_data) > 0:
                for apinvoicepo_map in apinvoicepomap_data:
                    apinvoicepomap_resp = APInvoicemapResponse()
                    apinvhdr_serv = APInvoiceheaderService(self._scope())
                    apinvdtls_serv = APInvoiceDetailService(self._scope())
                    apinvoicepomap_resp.set_id(apinvoicepo_map.id)
                    apinvoicepomap_resp.set_apinvoiceheader_id(apinvoicepo_map.apinvoiceheader_id)
                    apinvoicepomap_resp.set_apinvoicedetail_id(apinvoicepo_map.apinvoicedetail_id)
                    apinvoicepomap_resp.set_apinvoiceheader(apinvhdr_serv.single_get_apinwardinvoiceheader(request, apinvoicepo_map.apinvoiceheader_id,emp_id))
                    apinvoicepomap_resp.set_apinvoicedetail(apinvdtls_serv.get_apinvoicedetails_single(request, apinvoicepo_map.apinvoicedetail_id))
                    apinvoicepomap_resp.set_invoiceno(apinvoicepo_map.invoiceno)
                    apinvoicepomap_resp.set_pono(apinvoicepo_map.pono)
                    apinvoicepomap_resp.set_invoicepo_qty(apinvoicepo_map.invoicepo_qty)
                    apinvoicepomap_resp.set_podetailno(apinvoicepo_map.podetailno)
                    apinvoicepomap_resp.set_grninwardno(apinvoicepo_map.grninwardno)
                    apinvoicepomap_resp.set_productcode(apinvoicepo_map.productcode)
                    apinvoicepomap_resp.set_invoicepo_capitalised(apinvoicepo_map.invoicepo_capitalised)
                    return_list.append(apinvoicepomap_resp)
                vpage = NWisefinPaginator(apinvoicepomap_data, vys_page.get_index(), 10)
                return_list.set_pagination(vpage)
            return return_list
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj



    def single_get_apinvoicepo_map(self,request,invoicepomap_id,emp_id):
        try:
                apinvoicepo_map = APMapInvoicePO.objects.using(self._current_app_schema()).get(id=invoicepomap_id,is_delete=0,entity_id=self._entity_id())
                apinvoicepomap_data = APInvoicemapResponse()
                apinvhdr_serv = APInvoiceheaderService(self._scope())
                apinvdtls_serv = APInvoiceDetailService(self._scope())
                apinvoicepomap_data.set_id(apinvoicepo_map.id)
                apinvoicepomap_data.set_apinvoiceheader_id(apinvoicepo_map.apinvoiceheader_id)
                apinvoicepomap_data.set_apinvoicedetail_id(apinvoicepo_map.apinvoicedetail_id)
                apinvoicepomap_data.set_invoiceno(apinvoicepo_map.invoiceno)
                apinvoicepomap_data.set_pono(apinvoicepo_map.pono)
                apinvoicepomap_data.set_invoicepo_qty(apinvoicepo_map.invoicepo_qty)
                apinvoicepomap_data.set_podetailno(apinvoicepo_map.podetailno)
                apinvoicepomap_data.set_grninwardno(apinvoicepo_map.grninwardno)
                apinvoicepomap_data.set_productcode(apinvoicepo_map.productcode)
                apinvoicepomap_data.set_invoicepo_capitalised(apinvoicepo_map.invoicepo_capitalised)
                apinvoicepomap_data.set_apinvoiceheader(apinvhdr_serv.single_get_apinwardinvoiceheader(request, apinvoicepo_map.apinvoiceheader_id, emp_id))
                apinvoicepomap_data.set_apinvoicedetail(apinvdtls_serv.get_apinvoicedetails_single(request, apinvoicepo_map.apinvoicedetail_id))
                return apinvoicepomap_data
        except APMapInvoicePO.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code('INVALID_APINVOICEPOMAP_ID')
            error_obj.set_description('INVALID APINVOICEPOMAP ID')
            return error_obj
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def apinvoicepomap_delete(self,request,apinvoicepomap_id,emp_id):
        try:
            apinvoicepomap = APMapInvoicePO.objects.using(self._current_app_schema()).filter(id=apinvoicepomap_id,is_delete=0,entity_id=self._entity_id()).update(
                is_delete=1,updated_by=emp_id,updated_date=now())

            if apinvoicepomap == 0:
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_APINVOICEPOMAP_ID')
                error_obj.set_description('INVALID APINVOICEPOMAP ID')
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(APRefType.APHEADER)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.APHEADER)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

