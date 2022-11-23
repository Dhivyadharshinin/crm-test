import json
import traceback

import requests
from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models import AssetDetails, AssetSplitHeader, AssetSplitDetails,AssetHeader
from faservice.service.assetcatservice import AssetCatService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FaModifyStatus, AssetRequestStatus, FaRefType, asset_requeststatus, \
    asset_requestfor_status, FaRequestStatusUtil, assetvaluedtl_status, AssetStatus, AssetSource, AssetRequestfor

from nwisefin.settings import logger, SERVER_IP
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class SplitService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
#split make
    def create_split(self, assetdetailsid, assetdetails_value, reason, date, split_detail,details_json, emp_id, request):
        reqstatus = FaRequestStatusUtil.ONBORD
        split_status = AssetRequestStatus.PENDING
        data=json.loads(request.body)
    # try:
        ######### FASPLITN
        dataid=None
        try:
            dataid=AssetDetails.objects.filter(barcode=details_json['barcode'])[0]
            dataid=AssetHeader.objects.filter(id=dataid.assetheader_id)[0]
            print(dataid.id)
        except:
            pass
        assetdtls = AssetDetails.objects.get(assetdetails_id=assetdetailsid, status=1)
        source_id = assetdtls.id
        product_id = assetdtls.product_id
        qty = 1
        old_asset_id=assetdetailsid
        new_assetid_list=[]
        count=-1
        negative_id = details_json['assetdetails_id_negative']
        new_assetid_list.append(negative_id)
        for data in split_detail:
            if data['newassetdetailid'] not in new_assetid_list:
                new_assetid_list.append(data['newassetdetailid'])
                count+=1
        valid_list=['old_negative','old_positive']
        split_detail.insert(0,'old_positive')
        for i in range(count):
            valid_list.append('new'+str(i))
        for data in valid_list:
            if data=='old_negative':
                code_gen = new_assetid_list[0]
                barcode = code_gen[:-6]
                source=AssetSource.FASPLITN
                asset_stat=AssetStatus.ACTIVE
                value=assetdtls.assetdetails_value
                capdate = assetdtls.capdate
            elif 'new' in data:
                ind=valid_list.index(data)
                asset=new_assetid_list[ind]
                code_gen=asset
                barcode=code_gen[:-6]
                source=AssetSource.FASPLITP
                asset_stat=AssetStatus.ACTIVE
                print(valid_list,data,split_detail,ind)
                value=split_detail[ind]['value']
                capdate=details_json['date']
            else:
                capdate = details_json['date']
                code_gen = new_assetid_list[1]
                barcode = code_gen[:-6]
                value=split_detail[1]['value']
                source=AssetSource.FASPLITP
                asset_stat=AssetStatus.ACTIVE

            assetdtls_data = AssetDetails.objects.create(assetdetails_id=code_gen,
                                                     assetheader_id=dataid.id,
                                                     qty=assetdtls.qty,
                                                     barcode=barcode,
                                                     date=assetdtls.date,
                                                     assetcat_id=assetdtls.assetcat_id,
                                                     assetgroup_id=assetdtls.assetgroup_id,
                                                     product_id=assetdtls.product_id,
                                                     cat=assetdtls.cat,
                                                     subcat=assetdtls.subcat,
                                                     assetdetails_value=value,
                                                     assetdetails_cost=value,
                                                     description=assetdtls.description,
                                                     capdate=capdate,
                                                     source=source,
                                                     requestfor=0,
                                                     requeststatus=AssetRequestStatus.APPROVED,
                                                     assetdetails_status=asset_stat,
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
                                                     created_by=emp_id)

        refid = ref_type = -1
        relrefid = assetdtls_data.id
        self.audit_function(assetdtls_data, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.CREATE, reqstatus,request)

        splith = AssetSplitHeader.objects.create(assetdetailsid=assetdetailsid,
                                            date=date,
                                            assetsplitheader_value=assetdetails_value,
                                            assetsplitheader_status=split_status,
                                            reason=reason,
                                            created_by=emp_id)
        refid = ref_type = -1
        relrefid = splith.id
        self.audit_function(splith, refid, ref_type, relrefid,
                            emp_id, FaModifyStatus.CREATE, reqstatus,request)
        assetdetails_resp = AssetDetailsResponse()
        assetdetails_resp.set_id(splith.id)
        return assetdetails_resp

        # except IntegrityError as error:
        #     error_obj = ErrorMessage.INVALID_DATA
        #     return error_obj
        # except:
        #     error_obj = ErrorMessage.UNEXPECTED_ERROR
        #     return error_obj

    def create_splitdetail(self, split_detail, assetsplitheader, assetsplitheader_value, emp_id,request):
        scope=request.scope
        reqstatus = FaRequestStatusUtil.ONBORD
        try:
            for i in split_detail:
                newassetdetailsid = i['newassetdetailid']
                assetsplitdetail_value = i['value']
                splith = AssetSplitDetails.objects.create(assetsplitheader_id=assetsplitheader,
                                                         newassetdetailsid=newassetdetailsid,
                                                         assetsplitdetails_value=assetsplitdetail_value,
                                                         created_by=emp_id)
                refid = ref_type = -1
                relrefid = splith.id
                self.audit_function(splith, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,request)
            success_obj = SuccessMessage.CREATE_MESSAGE
            return success_obj

        except IntegrityError as error:
            traceback.print_exc()
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj
        except:
            traceback.print_exc()
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request=None):
        if action == FaModifyStatus.DELETE:
            data = None
        else:
            data = audit_data
        scope=request.scope
        audit_service = FaAuditService(scope)
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.SPLIT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

#splt maker summary
    def fetch_split_list(self, vys_page, emp_id, request):
        scope=request.scope
        conditiond = Q(status=1)
        assetdetails_data = AssetSplitDetails.objects.filter(conditiond).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        logger.info("split maker summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for i in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                splith = AssetSplitHeader.objects.filter(id=i.assetsplitheader_id)[0]
                try:
                    assetdetails = AssetDetails.objects.get(assetdetails_id=splith.assetdetailsid)
                except:
                    continue
                # from splitdetail
                assetdetails_resp.set_id(i.id)
                assetdetails_resp.asssetsplit_value = str(i.assetsplitdetails_value)
                assetdetails_resp.new_asset_id = i.newassetdetailsid
                # from assetdetails
                assetdetails_resp.assettran_id = assetdetails.assetdetails_id
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.assetdetailsgid = assetdetails.id
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                asset_status=AssetStatus()
                assetdetails_resp.set_assetdetails_status(asset_status.get_val(assetdetails.status))
                # from splitheader
                assetdetails_resp.splitheader_id = splith.id
                assetdetails_resp.split_reason = splith.reason
                assetdetails_resp.splitheader_status = asset_requeststatus(splith.assetsplitheader_status)
                assetdetails_resp.split_date = str(splith.date)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#split maker_summarysearch
    def split_maker_summarysearch(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition = Q(status=1)
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
        assetdetails_data = AssetDetails.objects.filter(condition)
        asset_id = list()
        if len(assetdetails_data) > 0:
            for dt in assetdetails_data:
                    asset_id.append(dt.assetdetails_id)
        condition1 = Q(status=1) & Q(assetdetailsid__in=asset_id)
        split = AssetSplitHeader.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(split) > 0:
            for wo in split:
                if wo.id not in w_id:
                    w_id.append(wo.id)
        else:
            return assetdetails_list1
        logger.info("split_w_id :" + str(w_id))
        logger.info("split_a_id :" + str(a_id))
        conditiond = Q(assetsplitheader_id__in=w_id)
        assetdetails_data = AssetSplitDetails.objects.filter(conditiond).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        logger.info("split maker summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        if list_length > 0:
            for i in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                splith = AssetSplitHeader.objects.filter(id=i.assetsplitheader_id)[0]
                assetdetails = AssetDetails.objects.get(assetdetails_id=splith.assetdetailsid)
                # from splitdetail
                assetdetails_resp.set_id(i.id)
                assetdetails_resp.asssetsplit_value = str(i.assetsplitdetails_value)
                assetdetails_resp.new_asset_id = i.newassetdetailsid
                assetdetails_resp.assettran_id = assetdetails.assetdetails_id
                # from assetdetails
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.assetdetailsgid = assetdetails.id
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(
                    assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                asst_status=AssetStatus()
                assetdetails_resp.set_assetdetails_status(asst_status.get_val(assetdetails.assetdetails_status))
                # from splitheader
                assetdetails_resp.splitheader_id = splith.id
                assetdetails_resp.split_reason = splith.reason
                assetdetails_resp.splitheader_status = asset_requeststatus(splith.assetsplitheader_status)
                assetdetails_resp.split_date = str(splith.date)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#split maker summary view
    def split_get(self, assetdetails_id, emp_id, request):
        scope=request.scope
        try:
            assetdetails_data = AssetSplitDetails.objects.get(newassetdetailsid=assetdetails_id)
            assetdetails_resp = AssetDetailsResponse()
            api_obj = FaApiService(scope)
            assetlocation_serv = AssetLocationService(scope)
            assetcat_serv = AssetCatService(scope)
            splith = AssetSplitHeader.objects.filter(id=assetdetails_data.assetsplitheader_id)[0]
            assetdetails = AssetDetails.objects.get(assetdetails_id=splith.assetdetailsid)
            # from splitdetail
            assetdetails_resp.set_id(assetdetails_data.id)
            assetdetails_resp.asssetsplit_value = str(assetdetails_data.assetsplitdetails_value)
            assetdetails_resp.new_asset_id = assetdetails_data.newassetdetailsid
            # from assetdetails
            assetdetails_resp.assettran_id = assetdetails.assetdetails_id
            assetdetails_resp.set_product_id(
                api_obj.fetch_product(assetdetails.product_id, emp_id, request))
            assetdetails_resp.set_capdate(str(assetdetails.capdate))
            assetdetails_resp.set_barcode(assetdetails.barcode)
            assetdetails_resp.assetdetailsgid = assetdetails.id
            assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
            assetdetails_resp.set_branch_id(
                api_obj.fetch_branch(assetdetails.branch_id))
            assetdetails_resp.set_assetlocation_id(
                assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
            assetdetails_resp.set_assetcatchange_id(
                assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
            assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
            # from splitheader
            assetdetails_resp.splitheader_id = splith.id
            assetdetails_resp.split_reason = splith.reason
            assetdetails_resp.splitheader_status = asset_requeststatus(splith.assetsplitheader_status)
            assetdetails_resp.split_date = str(splith.date)
            return assetdetails_resp
        except AssetDetails.DoesNotExist:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETID_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETID_ID)
            return error_obj

#reject
    def split_reject(self, details_json, emp_id,request):
        sassetsplitheader_status = AssetRequestStatus.APPROVED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("split DATA FOR APPROVE : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        for assetdetails_id in data_arr:
            asst_head=AssetSplitHeader.objects.get(id=assetdetails_id)
            asst_head.assetsplitheader_status=AssetRequestStatus.REJECTED
            asst_head.save()
            asst_split_details=AssetSplitDetails.objects.filter(assetsplitheader_id=asst_head.id)
            for record in asst_split_details:
                record.status=AssetRequestStatus.REJECTED
                record.save()
                asset_data=AssetDetails.objects.filter(assetdetails_id=record.newassetdetailsid).update(
                    requestfor=AssetRequestfor.DEFAULT,
                    requeststatus=AssetRequestStatus.APPROVED,
                    assetdetails_status=AssetStatus.IN_ACTIVE,
                    status=AssetStatus.IN_ACTIVE,
                )
            assetdetails=AssetDetails.objects.get(assetdetails_id=asst_head.assetdetailsid)
            refid = ref_type = -1
            relrefid = assetdetails.id
            self.audit_function(assetdetails, refid, ref_type, relrefid,emp_id, FaModifyStatus.UPDATE, reqstatus,request)
            splits = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id).update(
                                                assetsplitheader_status=AssetRequestStatus.REJECTED,
                                                # reason=reason,
                                                updated_by=emp_id,
                                                updated_date=now())
            refid = ref_type = AssetSource.FASPLITP
            relrefid = asst_head.id
            self.audit_function(details_json, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.UPDATE, reqstatus,request)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
            return success_obj



#approve
    def split_approve(self, details_json, emp_id,request):
        assetsplitheader_status = AssetRequestStatus.APPROVED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("split DATA FOR APPROVE : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        for assetdetails_id in data_arr:
            asst_head=AssetSplitHeader.objects.get(id=assetdetails_id)
            asst_head.assetsplitheader_status=AssetRequestStatus.APPROVED
            asst_head.save()
            asst_split_details=AssetSplitDetails.objects.filter(assetsplitheader_id=asst_head.id)
            for record in asst_split_details:
                record.status=AssetRequestStatus.APPROVED
                record.save()
                asset_data=AssetDetails.objects.filter(assetdetails_id=record.newassetdetailsid).update(
                    requestfor=AssetRequestfor.DEFAULT,
                    requeststatus=AssetRequestStatus.APPROVED,
                    assetdetails_status=AssetStatus.ACTIVE,
                    status=AssetStatus.ACTIVE,
                )
            assetdetails=AssetDetails.objects.get(assetdetails_id=asst_head.assetdetailsid)
            refid = ref_type = -1
            relrefid = assetdetails.id
            self.audit_function(assetdetails, refid, ref_type, relrefid,emp_id, FaModifyStatus.UPDATE, reqstatus,request)
            splits = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id).update(
                                                assetsplitheader_status=assetsplitheader_status,
                                                # reason=reason,
                                                updated_by=emp_id,
                                                updated_date=now())
            refid = ref_type = AssetSource.FASPLITP
            relrefid = asst_head.id
            self.audit_function(details_json, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.UPDATE, reqstatus,request)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj
#checker_summary
    def split_checker_list(self, vys_page, emp_id, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(assetsplitheader_status=5)
        writeoff = AssetSplitHeader.objects.filter(condition1).order_by('-id')
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
                    continue
        else:
            return assetdetails_list1
        logger.info("split checker w_id :" + str(w_id))
        logger.info("split checker a_id :" + str(a_id))
        print(a_id)
        conditiond = Q(status=1) & Q(assetsplitheader__assetsplitheader_status=5)
        assetdetails_data1 = AssetSplitDetails.objects.filter(conditiond)
        condition = Q(id__in=a_id)
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("AssetSplitHeader ch summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        asset_spl = []
        source_clr_id=[]
        if list_length > 0:
            # source asset
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
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_checkbox(False)

                split = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id)
                if len(split)>0:
                    split=split[0]
                assetdetails_resp.split_id = split.id
                if split.id not in source_clr_id:
                    source_clr_id.append(split.id)
                assetdetails_resp.splitheaderid=split.id
                assetdetails_resp.color_id=len(source_clr_id)
                assetdetails_resp.split_reason = split.reason
                assetdetails_resp.splitheader_status = asset_requeststatus(split.assetsplitheader_status)
                assetdetails_resp.split_date = str(split.date)
                assetdetails_list.append(assetdetails_resp)
            # split asset
            for i in assetdetails_data1:
                assetdetails_resp1 = AssetDetailsResponse()
                splith = AssetSplitHeader.objects.filter(id=i.assetsplitheader_id)[0]
                assetdetails = AssetDetails.objects.filter(assetdetails_id=splith.assetdetailsid,status=AssetStatus.ACTIVE)[0]
                print(assetdetails)
                # from splitdetail
                assetdetails_resp1.set_id(i.id)
                assetdetails_resp1.asssettran_value = str(i.assetsplitdetails_value)
                assetdetails_resp1.assettran_id = i.newassetdetailsid
                # from assetdetails
                assetdetails_resp1.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp1.set_capdate(str(assetdetails.capdate))
                assetdetails_resp1.set_barcode(assetdetails.barcode)
                assetdetails_resp1.assetdetailsgid = assetdetails.id
                assetdetails_resp1.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp1.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp1.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp1.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                #splitheader
                assetdetails_resp1.split_date = str(splith.date)
                split = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id)
                if len(split) > 0:
                    split = split[0]
                assetdetails_resp1.split_id = split.id
                assetdetails_resp1.splitheader_status = asset_requeststatus(split.assetsplitheader_status)
                if split.id in source_clr_id:
                    assetdetails_resp1.color_id=source_clr_id.index(split.id)+1
                splitdt = AssetSplitDetails.objects.filter(assetsplitheader_id=i.assetsplitheader_id)
                len_dtl = len(splitdt)
                # print(len_dtl)
                assetdetails_resp1.split_count = len_dtl
                asset_spl.append(json.loads(assetdetails_resp1.get()))
            assetdetails_list.__dict__['asset_split']=(asset_spl)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#checker_summarysearch
    def split_checker_search(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(assetsplitheader_status=5)
        writeoff = AssetSplitHeader.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        asset_spl = []
        source_clr_id = []
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
        logger.info("split checker w_id :" + str(w_id))
        logger.info("split checker a_id :" + str(a_id))
        conditiond = Q(status=1) & Q(assetsplitheader__assetsplitheader_status=5)
        assetdetails_data1 = AssetSplitDetails.objects.filter(conditiond)
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
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_resp.set_checkbox(False)

                split = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id)[0]
                assetdetails_resp.split_id = split.id
                if split.id not in source_clr_id:
                    source_clr_id.append(split.id)
                assetdetails_resp.color_id=len(source_clr_id)
                assetdetails_resp.split_reason = split.reason
                assetdetails_resp.splitheader_status = asset_requeststatus(split.assetsplitheader_status)
                assetdetails_resp.split_date = str(split.date)

                assetdetails_list.append(assetdetails_resp)
                # split asset
            for i in assetdetails_data1:
                assetdetails_resp1 = AssetDetailsResponse()
                splith = AssetSplitHeader.objects.filter(id=i.assetsplitheader_id)[0]
                assetdetails = AssetDetails.objects.filter(assetdetails_id=splith.assetdetailsid)[0]
                # from splitdetail
                assetdetails_resp1.set_id(i.id)
                assetdetails_resp1.asssettran_value = str(i.assetsplitdetails_value)
                assetdetails_resp1.assettran_id = i.newassetdetailsid
                # from assetdetails
                assetdetails_resp1.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp1.set_capdate(str(assetdetails.capdate))
                assetdetails_resp1.assetdetailsgid = assetdetails.id
                assetdetails_resp1.barcode=assetdetails.barcode
                assetdetails_resp1.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp1.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp1.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp1.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                # splitheader
                assetdetails_resp1.split_date = str(splith.date)
                split = AssetSplitHeader.objects.filter(assetdetailsid=assetdetails.assetdetails_id)[0]
                assetdetails_resp1.split_id = split.id
                assetdetails_resp1.splitheader_status = asset_requeststatus(split.assetsplitheader_status)
                if split.id in source_clr_id:
                    assetdetails_resp1.color_id = source_clr_id.index(split.id) + 1
                splitdt = AssetSplitDetails.objects.filter(assetsplitheader_id=i.assetsplitheader_id)
                len_dtl = len(splitdt)
                # print(len_dtl)
                assetdetails_resp1.split_count = len_dtl
                asset_spl.append(json.loads(assetdetails_resp1.get()))
            assetdetails_list.__dict__['asset_split'] = (asset_spl)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    def split_assetlist(self, vys_page, emp_id, request):
        scope=request.scope
        conditiond = Q(status=1)
        assetdetails_data = AssetSplitDetails.objects.filter(conditiond).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        logger.info("split asset summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetcat_serv = AssetCatService(scope)
        a = 0
        if list_length > 0:
            for i in assetdetails_data:
                assetdetails_resp = AssetDetailsResponse()
                splith = AssetSplitHeader.objects.filter(id=i.assetsplitheader_id)[0]
                assetdetails = AssetDetails.objects.get(assetdetails_id=splith.assetdetailsid)
                # from splitdetail
                assetdetails_resp.set_id(i.id)
                assetdetails_resp.asssettran_value = str(i.assetsplitdetails_value)
                assetdetails_resp.assettran_id = i.newassetdetailsid
                # from assetdetails
                assetdetails_resp.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_barcode(assetdetails.barcode)
                assetdetails_resp.assetdetailsgid = assetdetails.id
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                #splitheader
                assetdetails_resp.split_date = str(splith.date)

                splitdt = AssetSplitDetails.objects.filter(assetsplitheader_id=i.assetsplitheader_id)
                len_dtl = len(splitdt)
                print(len_dtl)
                assetdetails_resp.split_count = len_dtl
                # assetdetails_resp.index = len_dtl
                a = a + 1
                print("index", a)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    def codegenerator_split(self, assetdetails_id,count, emp_id, request):
        try:
            scope=request.scope
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetdetails_code=AssetDetails.objects.filter(barcode=assetdetails.barcode).order_by('-assetdetails_id')[0]
            product_id = assetdetails.product_id
            subcat=assetdetails.subcat
            new_old=assetdetails_code.assetdetails_id.split('/')

            negative_asset_id=new_old[0]+'/'+str(int(new_old[1])).zfill(2)+'/'+str(int(new_old[2])+1).zfill(2)
            new_id=new_old[0]+'/'+str(int(new_old[1])).zfill(2)+'/'+str(int(new_old[2])+2).zfill(2)
            old_assetid = [new_id]
            old_barcode=old_assetid[0][:-6]
            qty = count                  #QUANTITY HARDCODE BCZ GENERATE LIMIT-2##Now changed to Dynamic
            asst_obj = FaApiService(scope)
            params = {'product_id': product_id ,'subcat':subcat,'QTY': qty}
            asset_dtls_id_list = asst_obj.fetch_codegenerator_list(params, request)
            try:
                asset_dtls_id_list = json.loads(asset_dtls_id_list.content.decode('utf-8'))
            except:
                err=Error()
                err.set_code(ErrorMessage.INVALID_CODEGENDATA)
                err.set_description(ErrorMessage.INVALID_CODEGENDATA)
                return err
            logger.info("codegenerator resp: " + str(asset_dtls_id_list))
            resp_json1 = asset_dtls_id_list.get('data')
            logger.info("codegenerator resp: " + str(resp_json1))
            new_code = resp_json1
            assetdetails_resp = AssetDetailsResponse()
            old_assetid.extend(new_code)
            assetdetails_resp.id = old_assetid
            assetdetails_resp.old_barcode=old_barcode
            assetdetails_resp.assetdetails_id_negative=negative_asset_id
            return assetdetails_resp
        except AssetDetails.DoesNotExist:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETID_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETID_ID)
            return error_obj