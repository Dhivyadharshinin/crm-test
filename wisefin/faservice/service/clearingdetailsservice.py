import logging
from dateutil import parser
import traceback
from datetime import datetime
from struct import Struct

import dateutil.parser
from django.db import IntegrityError
from django.db.models import Q

from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.assetlocationresponse import AssetLocationResponse
from faservice.data.response.clearingDetailsresponse import ClearingDetailsResponse
from faservice.data.response.clearingheaderresponse import ClearingHeaderResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models.famodels import AssetLocation, ClearingDetails, ClearingHeader
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService, DictObj
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, ClearingHeader_Status, Fa_Doctype
# from inwardservice.models import EscalationType
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.service.productservice import ProductService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.service.vendorservice import VendorService
from faservice.data.response.clearingDetailsresponse import ClearingDetailsCapitalizeResponse

class ClearingDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_clearingdetails(self, clearindetails_obj, emp_id,clearingheader_id,request=None):
        try:
            reqstatus = FaRequestStatusUtil.ONBORD
            scope=request.scope
            fa_obj = FaApiService(scope)
            clearingdetails_arr=[]
            log_list=[]
            for obj in  clearindetails_obj :
                err_obj=Error()
                try:
                    prod_data=fa_obj.fetch_product_code(obj.get_product_id(),request.user.id,request)['id']
                except:
                    traceback.print_exc()
                    logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
                    err=Error()
                    err.set_code(ErrorMessage.INVALID_PRODUCT_ID)
                    err.set_description(ErrorDescription.INVALID_PRODUCT_ID)
                    return err
                try:
                    supp_data = fa_obj.fetch_data_code(obj.get_supplier_id(), request)['id']
                except:
                    traceback.print_exc()
                    logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
                    err_obj=Error()
                    err_obj.set_code(ErrorMessage.INVALID_SUPPLIERBRANCH_ID)
                    err_obj.set_description(ErrorDescription.INVALID_SUPPLIERBRANCH_ID)
                    return err_obj

                try:
                    branch_data = fa_obj.fetch_branch_code(obj.get_branch_id(), request)['id']
                except:
                    traceback.print_exc()
                    logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
                    err_obj=Error()
                    err_obj.set_code(ErrorMessage.INVALID_branch_ID)
                    err_obj.set_description(ErrorDescription.INVALID_branch_ID)
                    return err_obj

                try:
                    logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
                    apcat_data = fa_obj.fetch_code_subcategory(obj.get_apsubcat_id(), request)['id']
                except:
                    logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
                    err=Error()
                    err.set_code(ErrorMessage.INVALID_SUB_CATEGORY_ID)
                    err.set_description(ErrorDescription.INVALID_SUB_CATEGORY_ID)
                    return err

                clearindetails = ClearingDetails(

                    clearingheader_id=clearingheader_id,
                    supplier_id = supp_data,
                    product_id = prod_data,#obj.get_product_id(),
                    # product_id = self.fa_obj.fetch_product_code("P00002",request.user.id,request)['id'],#obj.get_product_id(),
                    branch_id = branch_data,
                    invoice_id = obj.get_invoice_id(),
                    invoicedtails_id = obj.get_invoicedtails_id(),
                    apsubcat_id = apcat_data,
                    doctype = obj.get_doctype(),
                    productname = obj.get_productname(),
                    qty = obj.get_qty(),
                    balanceqty = obj.get_balanceqty(),
                    invoiceno = obj.get_invoiceno(),
                    invoicedate = obj.get_invoicedate(),
                    taxamount = obj.get_taxamount(),
                    otheramount = obj.get_otheramount(),
                    amount = obj.get_amount(),
                    totamount = obj.get_totamount(),
                    markedup = obj.get_markedup(),
                    mepno = obj.get_mepno(),
                    ponum = obj.get_ponum(),
                    ecfnum = obj.get_ecfnum(),created_by=emp_id,
                    inv_debit_tax=obj.get_inv_debit_tax())
                log_list.append(clearindetails.__dict__)
                clearingdetails_arr.append(clearindetails)
            logging.error("FA_CLEARING_DETAILS_DATA:" + str(log_list))
            ClearingDetails.objects.bulk_create(clearingdetails_arr)
        except:
            err=Error()
            err.set_code(ErrorMessage.INVALID_DATA)
            err.set_description(ErrorDescription.INVALID_DATA)
            return err
        return


    def fetch_clearingdetails_list(self,dctype,clearingheader_id,request=None):
        scope=request.scope
        fa_obj=FaApiService(scope)
        condition = Q(clearingheader_id =clearingheader_id) & Q(doctype=dctype)
        clearingdetails_data = ClearingDetails.objects.filter(condition)
        clearingdetails_list = NWisefinList()
        for clearindetails in clearingdetails_data:
            clearingdetails_resp = ClearingDetailsResponse()
            clearingdetails_resp.set_id(clearindetails.id)
            clearingdetails_resp.set_clearingheader(clearindetails.clearingheader_id)
            clearingdetails_resp.set_supplier_id(clearindetails.supplier_id)
            data = fa_obj.fetch_data(clearindetails.supplier_id, request)
            
            if 'Params' in data.keys():
                clearingdetails_resp.set_supplier_name(fa_obj.fetch_data(clearindetails.supplier_id,request)['Params']['name'])
            else:
                clearingdetails_resp.set_supplier_name(fa_obj.fetch_data(clearindetails.supplier_id,request)['name'])
            clearingdetails_resp.set_product_id(clearindetails.product_id)
            clearingdetails_resp.set_branch_id(clearindetails.branch_id)
            clearingdetails_resp.set_invoice_id(clearindetails.invoice_id)
            clearingdetails_resp.set_invoicedtails_id(clearindetails.invoicedtails_id)
            clearingdetails_resp.set_doctype(clearindetails.doctype)
            clearingdetails_resp.set_apsubcat_id(clearindetails.apsubcat_id)
            clearingdetails_resp.set_productname(clearindetails.productname)
            clearingdetails_resp.set_qty(clearindetails.qty)
            clearingdetails_resp.set_invoiceno(clearindetails.invoiceno)
            clearingdetails_resp.set_invoicedate(clearindetails.invoicedate)
            clearingdetails_resp.set_taxamount(clearindetails.taxamount)
            clearingdetails_resp.set_otheramount(clearindetails.otheramount)
            clearingdetails_resp.set_amount(clearindetails.amount)
            clearingdetails_resp.set_totamount(clearindetails.totamount)
            clearingdetails_resp.set_markedup(clearindetails.markedup)
            clearingdetails_resp.set_mepno(clearindetails.mepno)
            clearingdetails_resp.set_ponum(clearindetails.ponum)
            clearingdetails_resp.set_ecfnum(clearindetails.ecfnum)
            clearingdetails_resp.set_clearingheader_status(clearindetails.clearingdetails_status)
            clearingdetails_list.append(clearingdetails_resp)
        return clearingdetails_list

    def fetch_clearingdetails(self,clearingdetails_id):
        try:
            clearindetails = ClearingDetails.objects.get(id=clearingdetails_id,status=1)

            clearingdetails_resp = ClearingDetailsResponse()
            clearingdetails_resp.set_id(clearindetails.id)
            clearingdetails_resp.set_clearingheader(clearindetails.clearingheader_id)
            clearingdetails_resp.set_supplier_id(clearindetails.supplier_id)
            clearingdetails_resp.set_product_id(clearindetails.product_id)
            clearingdetails_resp.set_branch_id(clearindetails.branch_id)
            clearingdetails_resp.set_invoice_id(clearindetails.invoice_id)
            clearingdetails_resp.set_invoicedtails_id(clearindetails.invoicedtails_id)
            clearingdetails_resp.set_doctype(clearindetails.doctype)
            clearingdetails_resp.set_apsubcat_id(clearindetails.apsubcat_id)
            clearingdetails_resp.set_productname(clearindetails.productname)
            clearingdetails_resp.set_qty(clearindetails.qty)
            clearingdetails_resp.set_invoiceno(clearindetails.invoiceno)
            clearingdetails_resp.set_invoicedate(clearindetails.invoicedate)
            clearingdetails_resp.set_taxamount(clearindetails.taxamount)
            clearingdetails_resp.set_otheramount(clearindetails.otheramount)
            clearingdetails_resp.set_amount(clearindetails.amount)
            clearingdetails_resp.set_totamount(clearindetails.totamount)
            clearingdetails_resp.set_markedup(clearindetails.markedup)
            clearingdetails_resp.set_mepno(clearindetails.mepno)
            clearingdetails_resp.set_ponum(clearindetails.ponum)
            clearingdetails_resp.set_ecfnum(clearindetails.ecfnum)
            return clearingdetails_resp
        except ClearingDetails.DoesNotExist:
            logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_CLEARINGDETAILS_ID)
            error_obj.set_description(ErrorDescription.INVALID_CLEARINGDETAILS_ID)
            return error_obj

    def fetch_invoicedetailsforfaqery(self,clearingdetails_id):
        clearingdetails_resp = ClearingDetailsResponse()
        try:
            clearindetails = ClearingDetails.objects.get(id=clearingdetails_id)


            clearingdetails_resp.set_invoiceno(clearindetails.invoiceno)
            split_todate = parser.parse(str(clearindetails.invoicedate)).date()#, '%Y-%m-%d %H:%M:%S%z').date()
            clearingdetails_resp.set_invoicedate(split_todate)
            clearingdetails_resp.set_ecfnum(clearindetails.ecfnum)
        except ClearingDetails.DoesNotExist:
            logger.info('FAL_CLEARINGDETAILS_EXCEPT:{}'.format(traceback.print_exc()))
        return clearingdetails_resp

    def view_clearingdetails(self,clearingheader_id,emp_id,request):
        scope=request.scope
        vendor_obj = master_obj = branch_obj=FaApiService(scope)
        clearingheaderdata = ClearingHeader.objects.get(id=clearingheader_id, status=1)
        if clearingheaderdata.islock!=1:
            err=Error()
            err.set_code(ErrorMessage.ASSET_CREATE_LOCK)
            err.set_description(ErrorDescription.ASSET_CREATION_LOCKED_OR_BEING_USED)
            return err
        else:
            clearingheaderdata.islock=0
            clearingheaderdata.updated_date=now()
            clearingheaderdata.save()
        clearingdetailsdata = ClearingDetails.objects.filter(clearingheader=clearingheader_id,status=1)
        vndrdata = []
        prod_data = []
        branch_data = []
        for record in clearingdetailsdata:
            vendor_data = vendor_obj.fetch_data(record.supplier_id,request)
            vndrdata.append([record.supplier_id,vendor_data])
            productdata = master_obj.fetch_product(record.product_id,emp_id,request)
            prod_data.append(productdata)
            branchdata=branch_obj.fetch_branch(record.branch_id,request)
            branch_data.append(branchdata)
        assetdetails_data = []
        taxamt=0
        for clearing in clearingdetailsdata:
            taxamt+=clearing.inv_debit_tax
        for clearingdet in clearingdetailsdata:
            clearingresponse = ClearingDetailsCapitalizeResponse()
            clearingresponse.set_faclringheader_gid(clearingdet.clearingheader_id)
            clearingresponse.set_faclringdetails_gid(clearingdet.id)
            clearingresponse.set_faclringdetails_productgid(clearingdet.product_id)
            clearingresponse.set_product_name(clearingdet.productname)
            clearingresponse.set_faclringheader_balanceqty(clearingdet.qty)
            clearingresponse.set_faclringdetails_qty(clearingdet.balanceqty)

            taxamount=0
            clearingresponse.set_faclringheader_balanceamount(clearingheaderdata.balanceamount)
            clearingresponse.set_faclringheader_tottaxamount(taxamt)
            clearingresponse.set_faclringheader_totinvamount(clearingheaderdata.totinvoiceamount)
            for vendor in vndrdata:
                if(vendor[0]==clearingdet.supplier_id):
                    clearingresponse.set_supplier_name(vendor[1]['name'])
            for branch in branch_data:
                if(isinstance(branch,dict)):
                    dict_obj=DictObj()
                    branch=dict_obj.get_obj(branch)
                if (branch.id == clearingdet.branch_id):
                    clearingresponse.set_branch_name(branch.name)
            clearingresponse.set_faclringdetail_totamount(float(clearingdet.amount)+taxamount)
            if clearingdet.doctype!=Fa_Doctype.BUC:
                clearingresponse.set_inv_debit_tax(clearingdet.inv_debit_tax/2)
            else:
                clearingresponse.set_inv_debit_tax(clearingdet.inv_debit_tax)
            clearingresponse.set_invoicedetails_totalamt(clearingdet.totamount)
            clearingresponse.set_faclringdetails_ponum(clearingdet.ponum)
            clearingresponse.set_crnum(clearingdet.ecfnum)
            clearingresponse.set_faclringheader_captalizedamount(clearingheaderdata.capitalizedamount)
            clearingresponse.set_isChecked(False)
            clearingresponse.set_isChecked_apportion(False)
            assetdetails_data.append(clearingresponse.get())
        return assetdetails_data


    def delete_clearingdetails(self,clearingdetails_id,emp_id):
        clearingdetails = ClearingDetails.objects.filter(id=clearingdetails_id).delete()
        reqstatus = FaRequestStatusUtil.ONBORD

        refid = ref_type = -1
        relrefid = clearingdetails_id
        self.audit_function(clearingdetails, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.DELETE, reqstatus)
        if clearingdetails[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_CLEARINGDETAILS_ID)
            error_obj.set_description(ErrorDescription.INVALID_CLEARINGDETAILS_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request):
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
        audit_obj.set_relreftype(FaRefType.CLEARINGDETAILS)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
