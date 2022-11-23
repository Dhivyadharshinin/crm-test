import traceback

import pandas as pd
import requests
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils.timezone import now

from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models import WriteOff, AssetDetails, AssetHeader, AssetSplitHeader
from faservice.service.assetcatservice import AssetCatService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService, DictObj
from faservice.util.fautil import FaModifyStatus, AssetRequestStatus, FaRefType, asset_requeststatus, \
    asset_requestfor_status, FaRequestStatusUtil, AssetRequestfor, AssetStatus, assetvaluedtl_status, AssetSource

from nwisefin.settings import logger, SERVER_IP
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class WriteOffService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_writeoff(self, assetdetails_id, reason, date, emp_id,request):
        reqstatus = FaRequestStatusUtil.ONBORD
        writeoff_status = AssetRequestStatus.PENDING      #1
        try:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetdetailsid = assetdetails.assetdetails_id
            assetdetailsvalue = assetdetails.assetdetails_value
            barcode = assetdetails.barcode
            writeoff = WriteOff.objects.create(assetdetailsid=assetdetailsid,
                                               barcode=barcode,
                                                date=date,
                                                writeoff_status=writeoff_status,
                                                reason=reason,
                                                value=assetdetailsvalue,
                                                created_by=emp_id)
            refid = ref_type = -1
            relrefid = writeoff.id
            self.audit_function(writeoff, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus,request)
            assetdetails_resp = AssetDetailsResponse()
            assetdetails_resp.set_id(assetdetails.id)
            return assetdetails_resp

        except IntegrityError as error:
            traceback.print_exc()
            logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))

            error_obj = ErrorMessage.INVALID_DATA
            return error_obj
        except:
            traceback.print_exc()
            logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

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
        audit_obj.set_relreftype(FaRefType.WRITEOFF)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_writeoff_list(self, vys_page, emp_id, request):
        scope=request.scope
        condition = Q(status=1)
        writeoff = WriteOff.objects.filter(condition).order_by('-id')
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetailsid)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    return assetdetails_list1
        else:
            return assetdetails_list1
        assetdetails_data = AssetDetails.objects.filter(id__in=a_id).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("writeoff summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)

                writeoff = WriteOff.objects.get(assetdetailsid=assetdetails.assetdetails_id)
                assetdetails_resp.set_writeoff_reason(writeoff.reason)
                assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))

                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#add-summary
    def search_writeoff_add(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition = Q(status=1) & Q(requestfor=AssetRequestfor.DEFAULT) & Q(assetdetails_status=AssetStatus.ACTIVE)
        if 'asset_value' in data_obj:
            condition &= Q(assetdetails_value__icontains=data_obj['asset_value'])
        if 'branch_id' in data_obj:
            condition &= Q(branch_id=data_obj['branch_id'])
        if 'assetcat_id' in data_obj:
            condition &= Q(assetcat_id=data_obj['assetcat_id'])
        if 'assetdetails_id' in data_obj:
            condition &= Q(barcode__icontains=data_obj['assetdetails_id'])
        if 'capdate' in data_obj:
            condition &= Q(capdate=data_obj['capdate'])
        asst_split_datas=AssetSplitHeader.objects.filter(assetsplitheader_status=5)
        header_id=[]
        for record in asst_split_datas:
            if record.assetdetailsid not in header_id:
                header_id.append(record.assetdetailsid)
        barcode_exc=[]
        for data in header_id:
            try:
                asst_data=AssetDetails.objects.get(assetdetails_id=data)
            except:
                logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
                continue
            if asst_data.barcode not in barcode_exc:
                barcode_exc.append(asst_data.barcode)
        assetdetails_data = AssetDetails.objects.exclude(barcode__in=barcode_exc).filter(condition).values().order_by('-updated_date')
        df=pd.DataFrame(assetdetails_data)
        try:
            agg=dict.fromkeys(assetdetails_data[0].keys(),'first')
            df=df.groupby('barcode').agg(agg)
        except:
            logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            err=Error()
            err.set_code(ErrorMessage.NO_DATA)
            err.set_description(ErrorDescription.NO_DATA_FOUND)
            return err
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        df = df.to_dict('records')
        df=df[vys_page.get_offset():vys_page.get_query_limit()]
        if len(df) > 0:
            for assetdetails in df:
                dict_obj=DictObj()
                assetdetails=dict_obj.get_obj(assetdetails)
                assetdetails_resp = AssetDetailsResponse()
                print(assetdetails.requestfor)
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                fa_obj=FaApiService(scope)
                assetdetails_resp.set_subcat(fa_obj.fetchsubcategory(assetdetails.subcat))
                assetdetails_resp.set_checkbox(False)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#maker_summary
    def writeoff_maker_summary(self, vys_page, emp_id, request):
        scope=request.scope
        condition1 = Q(status=1)
        writeoff = WriteOff.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetailsid)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    pass
        else:
            return assetdetails_list1
        logger.info("writeoff_w_id :" + str(w_id))
        logger.info("writeoff_a_id :" + str(a_id))
        print(a_id)
        condition = Q(id__in=a_id)
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("writeoff summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))

                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))

                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))

                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                try:
                    writeoff = WriteOff.objects.filter(assetdetailsid=assetdetails.assetdetails_id)[0]
                except:
                    continue
                assetdetails_resp.set_writeoff_reason(writeoff.reason)
                assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))

                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#maker_summarysearch
    def writeoff_maker_summarysearch(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition1 = Q(status=1)
        writeoff = WriteOff.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetailsid)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    pass
        else:
            return assetdetails_list1
        logger.info("writeoff_w_id :" + str(w_id))
        logger.info("writeoff_a_id :" + str(a_id))
        print(a_id)
        condition = Q(id__in=a_id)
        if 'asset_value' in data_obj:
            condition &= Q(assetdetails_value__icontains=data_obj['asset_value'])
        if 'branch_id' in data_obj:
            condition &= Q(branch_id=data_obj['branch_id'])
        if 'assetcat_id' in data_obj:
            condition &= Q(assetcat_id=data_obj['assetcat_id'])
        if 'assetdetails_id' in data_obj:
            condition &= Q(assetdetails_id__icontains=data_obj['assetdetails_id'])
        if 'capdate' in data_obj:
            condition &= Q(capdate=data_obj['capdate'])
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("writeoff summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                try:
                    writeoff = WriteOff.objects.filter(assetdetailsid=assetdetails.assetdetails_id)[0]
                except:
                    continue
                assetdetails_resp.set_writeoff_reason(writeoff.reason)
                assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#view
    def fetch_assetdetails(self,assetdetails_id, emp_id, request):
        scope=request.scope
        try:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            api_obj = FaApiService(scope)
            assetlocation_serv = AssetLocationService(scope)
            assetcat_serv = AssetCatService(scope)
            assetdetails_resp = AssetDetailsResponse()
            assetdetails_resp.set_id(assetdetails.id)
            assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
            assetdetails_resp.set_barcode(assetdetails.barcode)
            assetdetails_resp.set_product_id(
                api_obj.fetch_product(assetdetails.product_id, emp_id, request))
            assetdetails_resp.set_capdate(str(assetdetails.capdate))
            assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
            assetdetails_resp.set_branch_id(
                api_obj.fetch_branch(assetdetails.branch_id))
            assetdetails_resp.set_assetlocation_id(
                assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
            assetdetails_resp.set_assetcatchange_id(
                assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
            assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
            assetdetails_resp.set_subcat(assetdetails.subcat)

            writeoff = WriteOff.objects.get(assetdetailsid=assetdetails.assetdetails_id)
            assetdetails_resp.set_writeoff_reason(writeoff.reason)
            assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))
            return assetdetails_resp
        except WriteOff.DoesNotExist:
            logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETID_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETID_ID)
            return error_obj

#reject
    def writeoff_reject(self, details_json, emp_id,request):
        writeoff_status = AssetRequestStatus.REJECTED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("WRITEOFF DATA FOR Reject : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        reason = details_json.get("reason")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetdetailsid = assetdetails.assetdetails_id
            writeoff = WriteOff.objects.get(assetdetailsid=assetdetailsid)
            creatby = writeoff.created_by
            if creatby != emp_id:
                asset_req_status = AssetRequestStatus.REJECTED
                assetdetails_status = AssetStatus.IN_ACTIVE
                assetdetailss = AssetDetails.objects.filter(id=assetdetails_id).update(
                    requestfor=AssetRequestfor.DEFAULT,
                    requeststatus=asset_req_status,
                    # assetdetails_status=assetdetails_status,
                    updated_by=emp_id,
                    updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)
                writeoffs = WriteOff.objects.filter(assetdetailsid=assetdetailsid).update(
                                                   writeoff_status=writeoff_status,
                                                   reason=reason,
                                                   updated_by=emp_id,
                                                   updated_date=now())
                refid = ref_type = -1
                relrefid = writeoff.id
                self.audit_function(writeoff, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.code = ErrorMessage.INVALID_APPROVER_ID
                success_obj.description = ErrorDescription.INVALID_APPROVER_ID
        return success_obj
#approve
    def writeoff_approve(self, details_json, emp_id,request):
        writeoff_status = AssetRequestStatus.APPROVED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("WRITEOFF DATA FOR APPROVE : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetdetailsid = assetdetails.assetdetails_id
            writeoff = WriteOff.objects.get(assetdetailsid=assetdetailsid)
            creatby = writeoff.created_by
            if creatby != emp_id:
                asset_req_status = AssetRequestStatus.APPROVED
                assetdetails_status = AssetStatus.IN_ACTIVE
                assetdetail=AssetDetails.objects.get(id=assetdetails_id)
                assetdetailss = AssetDetails.objects.filter(barcode=assetdetail.barcode).update(
                                                            requestfor=0,
                                                            requeststatus=asset_req_status,
                                                            assetdetails_status=assetdetails_status,
                                                            updated_by=emp_id,
                                                            updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

                writeoffs = WriteOff.objects.filter(assetdetailsid=assetdetailsid).update(
                                                    writeoff_status=writeoff_status,
                                                    # reason=reason,
                                                    updated_by=emp_id,
                                                    updated_date=now())
                refid = ref_type = -1
                relrefid = writeoff.id
                self.audit_function(writeoff, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)

            else:
                success_obj = NWisefinSuccess()
                success_obj.code=ErrorMessage.INVALID_APPROVER_ID
                success_obj.description=ErrorDescription.INVALID_APPROVER_ID
        return success_obj
#checker_summary
    def writeoff_checker_list(self, vys_page, emp_id, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(writeoff_status=AssetRequestStatus.PENDING)
        writeoff = WriteOff.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetailsid)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    return assetdetails_list1
        else:
            return assetdetails_list1
        logger.info("writeoff_w_id :" + str(w_id))
        logger.info("writeoff_a_id :" + str(a_id))
        print(a_id)
        condition = Q(id__in=a_id)
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("writeoff ch summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))

                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))

                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)

                writeoff = WriteOff.objects.get(assetdetailsid=assetdetails.assetdetails_id)
                assetdetails_resp.set_writeoff_reason(writeoff.reason)
                assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))

                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#checker_summarysearch
    def writeoff_checker_search(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(writeoff_status=AssetRequestStatus.PENDING)
        writeoff = WriteOff.objects.filter(condition1).order_by('-id')
        print('lenwrite',len(writeoff))
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetailsid)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    pass
        else:
            return assetdetails_list1
        logger.info("writeoff_w_id :" + str(w_id))
        logger.info("writeoff_a_id :" + str(a_id))
        print(a_id)
        condition = Q(id__in=a_id)
        if 'asset_value' in data_obj:
            condition &= Q(assetdetails_value__icontains=data_obj['asset_value'])
        if 'branch_id' in data_obj:
            condition &= Q(branch_id=data_obj['branch_id'])
        if 'assetcat_id' in data_obj:
            condition &= Q(assetcat_id=data_obj['assetcat_id'])
        if 'assetdetails_id' in data_obj:
            condition &= Q(assetdetails_id__icontains=data_obj['assetdetails_id'])
        if 'capdate' in data_obj:
            condition &= Q(capdate=data_obj['capdate'])
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')#[
                            #vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("writeoff summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for assetdetails in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                assetdetails_resp.set_id(assetdetails.id)
                assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                try:
                    writeoff = WriteOff.objects.filter(assetdetailsid=assetdetails.assetdetails_id)[0]
                except:
                    continue
                assetdetails_resp.set_writeoff_reason(writeoff.reason)
                assetdetails_resp.set_writeoff_status(asset_requeststatus(writeoff.writeoff_status))
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_list.data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list


    def create_asset_writeoff(self, data_arr, emp_id, request):
        # try:
        data_arr = data_arr.get("assetdetails_id")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetheader = AssetHeader.objects.get(barcode=assetdetails.barcode)
            assetheader.revisedcbtot = 1
            assetheader.save()

            assetdtl1 = AssetDetails.objects.all().order_by('-id')
            assetdtl1 = assetdtl1[0]
            last_assetdtls_id = assetdtl1.assetdetails_id
            first_split_old = last_assetdtls_id[:-11]   #l

            print("first_split_old",first_split_old)
            logger.info("first_split_old" + str(first_split_old))
            barcode = last_assetdtls_id[:-6]
            add1 = str(int(last_assetdtls_id[-2:])+1).zfill(2)
            code_gen = last_assetdtls_id[:-3] +"/"+str(add1)
            logger.info("barcode" + str(barcode))
            logger.info("assetdetails_id" + str(code_gen))
            reqstatus = FaRequestStatusUtil.ONBORD
            assetdtls = AssetDetails.objects.get(id=assetdetails_id)
            assetheader_data=assetdtls.assetheader
            assetdtls_data = AssetDetails.objects.create(assetdetails_id=code_gen,
                                                         qty=assetdtls.qty,
                                                         barcode=barcode,
                                                         date=assetdtls.date,
                                                         assetcat_id=assetdtls.assetcat_id,
                                                         assetgroup_id=assetdtls.assetgroup_id,
                                                         product_id=assetdtls.product_id,
                                                         cat=assetdtls.cat,
                                                         subcat=assetdtls.subcat,
                                                         assetdetails_value=assetdtls.assetdetails_value,
                                                         assetdetails_cost=assetdtls.assetdetails_cost,
                                                         description=assetdtls.description,
                                                         capdate=assetdtls.capdate,
                                                         source=AssetSource.FAWRITEOFF,
                                                         requestfor=AssetRequestfor.DEFAULT,
                                                         requeststatus=AssetRequestStatus.APPROVED,
                                                         assetdetails_status=AssetStatus.ACTIVE,
                                                         assettfr_id=assetdtls.assettfr_id,
                                                         assetsale_id=assetdtls.assetsale_id,
                                                         not5k=assetdtls.not5k,
                                                         assetowner=assetdtls.assetowner,
                                                         lease_startdate=assetdtls.lease_startdate,
                                                         lease_enddate=assetdtls.lease_enddate,
                                                         impairasset_id=assetdtls.impairasset_id,
                                                         impairasset=assetdtls.impairasset,
                                                         writeoff_id=assetdtls.writeoff_id,
                                                         assetcatchange_id=assetdtls.assetcatchange_id,
                                                         assetvalue_id=assetdtls.assetvalue_id,
                                                         assetcapdate_id=assetdtls.assetcapdate_id,
                                                         assetsplit_id=assetdtls.assetsplit_id,
                                                         assetmerge_id=assetdtls.assetmerge_id,
                                                         assetcatchangedate=assetdtls.assetcatchangedate,
                                                         reducedvalue=assetdtls.reducedvalue,
                                                         branch_id=assetdtls.branch_id,
                                                         assetlocation_id=assetdtls.assetlocation_id,
                                                         assetdetails_bs=assetdtls.assetdetails_bs,
                                                         assetdetails_cc=assetdtls.assetdetails_cc,
                                                         deponhold=assetdtls.deponhold,
                                                         deprate=assetdtls.deprate,
                                                         enddate=assetdtls.enddate,
                                                         parent_id=assetdtls.parent_id,
                                                         assetserialno=assetdtls.assetserialno,
                                                         invoice_id=assetdtls.invoice_id,
                                                         faclringdetails_id=assetdtls.faclringdetails_id,
                                                         inwheader_id=assetdtls.inwheader_id,
                                                         inwdetail_id=assetdtls.inwdetail_id,
                                                         inwarddate=assetdtls.inwarddate,
                                                         mepno=assetdtls.mepno,
                                                         ponum=assetdtls.ponum,
                                                         crnum=assetdtls.crnum,
                                                         debit_id=assetdtls.debit_id,
                                                         # imagepath = assetdetails_obj.get_imagepath(),
                                                         vendorname=assetdtls.vendorname,
                                                         created_by=emp_id,
                                                         assetheader=assetheader_data)
            refid = ref_type = -1
            relrefid = assetdtls_data.id
            self.audit_function(assetdtls_data, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus,request)
        success_obj = SuccessStatus.SUCCESS
        return success_obj

    def writeoff_add(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        try:
            assetid_list = NWisefinList()
            condition = Q(assetdetails_status=AssetStatus.ACTIVE) & Q(requestfor=AssetRequestfor.DEFAULT)
            if 'asset_value' in data_obj:
                condition &= Q(assetdetails_value__icontains=data_obj['asset_value'])
            if 'branch_id' in data_obj:
                condition &= Q(branch_id=data_obj['branch_id'])
            if 'assetcat_id' in data_obj:
                condition &= Q(assetcat_id=data_obj['assetcat_id'])
            if 'assetdetails_id' in data_obj:
                condition &= Q(barcode__icontains=data_obj['assetdetails_id'])
            if 'capdate' in data_obj:
                condition &= Q(capdate=data_obj['capdate'])
            bulk_tuple = tuple(
                AssetDetails.objects.filter(condition).order_by('-id').values('id', 'barcode'))

            data_count = 0
            barcode_list = list()
            id_list = list()
            stop_point = len(bulk_tuple)

            for asset_data in bulk_tuple:
                if data_count == int(stop_point):
                    break
                if asset_data['barcode'] not in barcode_list:
                    barcode_list.append(asset_data['barcode'])
                    id_list.append(asset_data['id'])
                    data_count = data_count + 1

            get_list = id_list
            assetdetails_data = AssetDetails.objects.filter(id__in=get_list).values()
            list_length = len(assetdetails_data)
            print(list_length)
            logger.info("writeoff add datasummary" + str(list_length))
            assetdetails_list = NWisefinList()
            api_obj = FaApiService(scope)
            assetlocation_serv = AssetLocationService(scope)
            assetcat_serv = AssetCatService(scope)
            df = pd.DataFrame(assetdetails_data)
            try:
                agg = dict.fromkeys(assetdetails_data[0].keys(), 'first')
                df = df.groupby('barcode').agg(agg)
            except:
                logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
                err = Error()
                err.set_code(ErrorMessage.NO_DATA)
                err.set_description(ErrorDescription.NO_DATA_FOUND)
                return err
            df = df[vys_page.get_offset():vys_page.get_query_limit()]
            df = df.to_dict('records')
            if list_length > 0:
                for assetdetails in df:
                    dict_obj = DictObj()
                    assetdetails = dict_obj.get_obj(assetdetails)
                    assetdetails_resp = AssetDetailsResponse()
                    assetdetails_resp.set_id(assetdetails.id)
                    assetdetails_resp.set_assetdetails_id(assetdetails.assetdetails_id)
                    assetdetails_resp.set_barcode(assetdetails.barcode)
                    assetdetails_resp.set_product_id(
                        api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                    assetdetails_resp.set_capdate(str(assetdetails.capdate))
                    asst_hdr=AssetHeader.objects.filter(id=assetdetails.assetheader_id)
                    if len(asst_hdr)>0:
                        assetdetails_resp.set_assetdetails_value(str(asst_hdr[0].valuetot))
                    else:
                        continue
                    assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                    assetdetails_resp.set_assetlocation_id(assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                    assetdetails_resp.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                    assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                    assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                    assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                    assetdetails_resp.set_vendorname(assetdetails.vendorname)
                    assetdetails_resp.set_qty(assetdetails.qty)
                    assetdetails_resp.set_barcode(assetdetails.barcode)
                    assetdetails_resp.set_date(assetdetails.date)
                    assetdetails_resp.set_assetgroup_id(assetdetails.assetgroup_id)
                    assetdetails_resp.set_subcat(assetdetails.subcat)
                    assetdetails_resp.set_checkbox(False)
                    assetid_list.append(assetdetails_resp)
                assetid_list.data=assetid_list.data
                vpage = NWisefinPaginator(assetid_list.data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)
        except Exception as excep:
            logger.info('FAL_WRITEOFFSERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        return assetid_list
