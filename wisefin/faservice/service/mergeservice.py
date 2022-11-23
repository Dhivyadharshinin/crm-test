import json
import traceback

import requests
from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models import AssetDetails, AssetMergeHeader, AssetMerge, AssetHeader
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


class MergeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
#merge make
    def create_merge(self, source_id, assetdetails_value, reason, date, emp_id, request):
        reqstatus = FaRequestStatusUtil.ONBORD
        merge_status = AssetRequestStatus.PENDING
        try:
            ######### FAMERN
            assetdtls = AssetDetails.objects.get(id=source_id)
            subcat_id = assetdtls.subcat
            qty = 1
            code_gen_serv=FaApiService(request.scope)
            params={'QTY':1,'subcat':subcat_id}
            resp=code_gen_serv.fetch_codegenerator_list(params,request)

            import json
            resp_json = json.loads(resp.content)
            logger.info("codegenerator resp: " + str(resp_json))
            resp_json1 = resp_json.get('data')
            logger.info("codegenerator resp: " + str(resp_json1))
            resp_json1 = resp_json1[0]
            new_code = resp_json1
            code_gen = new_code
            barcode = new_code[:-6]
            head_data=AssetHeader.objects.get(barcode=assetdtls.barcode)
            assetdtls_data = AssetDetails.objects.create(assetdetails_id=code_gen,
                                                         assetheader=head_data,
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
                                                         source=AssetSource.FAMERN,
                                                         requestfor=AssetRequestfor.DEFAULT,
                                                         requeststatus=AssetRequestStatus.APPROVED,
                                                         assetdetails_status=AssetStatus.IN_ACTIVE,
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

            ######### FAMERP
            assetdtls = AssetDetails.objects.get(id=source_id)
            assetdtls_code=AssetDetails.objects.filter(barcode=assetdtls.barcode).order_by('-assetdetails_id')[0]
            last_assetdtls_id = assetdtls_code.assetdetails_id
            barcode_p = last_assetdtls_id[:-6]
            add1 = str(int(last_assetdtls_id[-2:]) + 1).zfill(2)
            code_gen_p = last_assetdtls_id[:-3] + "/" + str(add1)
            header_data=assetdtls.assetheader
            reqstatus = FaRequestStatusUtil.ONBORD
            assetdtls_data = AssetDetails.objects.create(assetdetails_id=code_gen_p,
                                                         assetheader=header_data,
                                                         qty=assetdtls.qty,
                                                         barcode=barcode_p,
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
                                                         source=AssetSource.FAMERP,
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
                                                         created_by=emp_id)
            refid = ref_type = -1
            relrefid = assetdtls_data.id
            self.audit_function(assetdtls_data, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus,request)

            mergeh = AssetMergeHeader.objects.create(newassetid=code_gen_p,
                                                date=date,
                                                assetmergeheader_value=assetdetails_value,
                                                assetmergeheader_status=merge_status,
                                                reason=reason,
                                                created_by=emp_id)
            refid = ref_type = -1
            relrefid = mergeh.id
            self.audit_function(mergeh, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus,request)
            assetdetails_resp = AssetDetailsResponse()
            assetdetails_resp.set_id(mergeh.id)
            return assetdetails_resp

        except IntegrityError as error:
            logger.info('FAL_MERGESERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj
        except:
            logger.info('FAL_MERGESERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.UNEXPECTED_ERROR
            return error_obj

    def create_mergedetail(self, data_arr, assetsplitheader, assetsplitheader_value, emp_id,request):
        reqstatus = FaRequestStatusUtil.ONBORD
        try:
            scope=request.scope
            for asset_id in data_arr:
                assetdetails = AssetDetails.objects.get(id=asset_id)
                assetdetails_id = assetdetails.assetdetails_id
                splith = AssetMerge.objects.create(assetmergeheader_id=assetsplitheader,
                                                         assetdetails_id=assetdetails_id,
                                                         assetmerge_value=assetsplitheader_value,
                                                         created_by=emp_id)
                refid = ref_type = -1
                relrefid = splith.id
                self.audit_function(splith, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,request)
            success_obj = SuccessMessage.CREATE_MESSAGE
            return success_obj

        except IntegrityError as error:
            logger.info('FAL_MERGESERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = ErrorMessage.INVALID_DATA
            return error_obj
        except:
            logger.info('FAL_MERGESERVICE_EXCEPT:{}'.format(traceback.print_exc()))
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
        scope=request.scope
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.MERGE)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

#splt maker summary
    def merge_maker_list(self, vys_page, emp_id, request):
        scope=request.scope
        conditiond = Q(status=1)
        writeoff = AssetMerge.objects.filter(conditiond).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetails_id)
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
        condition = Q(id__in=a_id)
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
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp.merge_id = writeoff1.id
                assetdetails_resp.assettran_id = writeoff1.newassetid
                assetdetails_resp.merge_reason = writeoff1.reason
                assetdetails_resp.merge_status=asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp.merge_value=str(writeoff1.assetmergeheader_value)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#merge maker_summarysearch
    def merge_maker_search(self, vys_page, emp_id, data_obj, request):
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
        conditiond = Q(status=1) & Q(assetdetails_id__in=asset_id)
        writeoff = AssetMerge.objects.filter(conditiond).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            for wo in writeoff:
                assetdetails1 = AssetDetails.objects.filter(assetdetails_id=wo.assetdetails_id)
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
        condition = Q(id__in=a_id)
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
                assetdetails_resp.set_date(assetdetails.date)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp.merge_id = writeoff1.id
                assetdetails_resp.assettran_id = writeoff1.newassetid
                assetdetails_resp.merge_reason = writeoff1.reason
                assetdetails_resp.merge_status = asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp.merge_value = str(writeoff1.assetmergeheader_value)
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#merge maker summary view
    def merge_get(self, assetdetails_id, emp_id, request):
        scope=request.scope
        try:
            assetdetails_data = AssetMerge.objects.get(assetdetails_id=assetdetails_id)
            assetdetails_resp = AssetDetailsResponse()
            api_obj = FaApiService(scope)
            assetlocation_serv = AssetLocationService(scope)
            assetcat_serv = AssetCatService(scope)
            splith = AssetMergeHeader.objects.filter(id=assetdetails_data.assetmergeheader_id)[0]
            assetdetails = AssetDetails.objects.get(assetdetails_id=assetdetails_id)
            # from MERGEdetail
            assetdetails_resp.mergedetail_id = assetdetails_data.id
            assetdetails_resp.assetmerge_value = str(assetdetails_data.assetmerge_value)
            assetdetails_resp.assetdetails_id = assetdetails_data.assetdetails_id
            # from assetdetails
            assetdetails_resp.assettran_id = assetdetails.assetdetails_id
            assetdetails_resp.set_product_id(
                api_obj.fetch_product(assetdetails.product_id, emp_id, request))
            assetdetails_resp.set_capdate(str(assetdetails.capdate))
            assetdetails_resp.assetdetailsgid = assetdetails.id
            assetdetails_resp.set_barcode(assetdetails.barcode)
            assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
            assetdetails_resp.set_branch_id(
                api_obj.fetch_branch(assetdetails.branch_id))
            assetdetails_resp.set_assetlocation_id(
                assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
            assetdetails_resp.set_assetcatchange_id(
                assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
            assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
            # from MERGEheader
            assetdetails_resp.mergeheader_id = splith.id
            assetdetails_resp.merge_newassetid = splith.newassetid
            assetdetails_resp.merge_reason = splith.reason
            assetdetails_resp.assetmergeheader_status = asset_requeststatus(splith.assetmergeheader_status)
            assetdetails_resp.merge_date = str(splith.date)
            return assetdetails_resp
        except:
            logger.info('FAL_MERGESERVICE_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETID_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETID_ID)
        return error_obj

#reject
    def merge_reject(self, details_json, emp_id,request):
        assetmergeheader_status = AssetRequestStatus.REJECTED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("merge DATA FOR Reject : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        reason = details_json.get("reason")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            assetdetailsid = assetdetails.assetdetails_id
            mergedtl = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
            merge = AssetMergeHeader.objects.get(id=mergedtl.assetmergeheader_id)
            creatby = merge.created_by
            if creatby != emp_id:
                asset_req_status = AssetRequestStatus.REJECTED
                assetdetailss = AssetDetails.objects.filter(id=assetdetails_id).update(
                                                            requestfor=AssetRequestfor.DEFAULT,
                                                            requeststatus=asset_req_status,
                                                            updated_by=emp_id,
                                                            updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)
                splits = AssetMergeHeader.objects.filter(id=mergedtl.assetmergeheader_id).update(
                                                   assetmergeheader_status=assetmergeheader_status,
                                                   reason=reason,
                                                   updated_by=emp_id,
                                                   updated_date=now())
                refid = ref_type = -1
                relrefid = merge.id
                self.audit_function(merge, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)

            else:
                success_obj = NWisefinSuccess()
                success_obj.code = ErrorMessage.INVALID_APPROVER_ID
                success_obj.description = ErrorDescription.INVALID_APPROVER_ID
        return success_obj

#approve
    def merge_approve(self, details_json, emp_id,request):
        assetmergeheader_status = AssetRequestStatus.APPROVED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("merge DATA FOR APPROVE : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            mergedtl = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
            merge = AssetMergeHeader.objects.get(id=mergedtl.assetmergeheader_id)

            creatby = merge.created_by
            if creatby != emp_id:
                asset_req_status = AssetRequestStatus.APPROVED
                #CREATE New ASSET WITH BARCODE IN ASSSETDETAILS TABLE
                assetdetailss = AssetDetails.objects.filter(id=assetdetails_id).update(
                                                            requestfor=AssetRequestfor.DEFAULT,
                                                            requeststatus=asset_req_status,
                                                            updated_by=emp_id,
                                                            updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)

                splits = AssetMergeHeader.objects.filter(id=mergedtl.assetmergeheader_id).update(
                                                    assetmergeheader_status=assetmergeheader_status,
                                                    # reason=reason,
                                                    updated_by=emp_id,
                                                    updated_date=now())
                refid = ref_type = -1
                relrefid = merge.id
                self.audit_function(merge, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)

            else:
                success_obj = NWisefinSuccess()
                success_obj.code = ErrorMessage.INVALID_APPROVER_ID
                success_obj.description = ErrorDescription.INVALID_APPROVER_ID
        return success_obj
    #checker_summary
    def merge_checker_list(self, vys_page, emp_id, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(assetmergeheader_status=AssetRequestStatus.PENDING)
        writeoff = AssetMergeHeader.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            mh_id = list()
            for wo in writeoff:
                if wo.id not in mh_id:
                    mh_id.append(wo.id)
            mhd_id = list()
            assetdetails1 = AssetMerge.objects.filter(assetmergeheader_id__in=mh_id)
            if len(assetdetails1) > 0:
                for i in assetdetails1:
                    assetdt_id = i.assetdetails_id
                    if i.assetmergeheader_id not in mhd_id:
                        mhd_id.append(i.assetmergeheader_id)
                        a_id.append(assetdt_id)
            else:
                return assetdetails_list1
        else:
            return assetdetails_list1
        logger.info("merge checker w_id :" + str(w_id))
        logger.info("merge checker a_id :" + str(a_id))
        assetdetails_data1 = AssetMerge.objects.filter(assetmergeheader_id__in=mh_id).order_by('-created_date')
        condition = Q(assetdetails_id__in=a_id)
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        logger.info("AssetMergeHeader ch summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        asset_spl = []
        source_clr_id = []
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
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_resp.set_checkbox(False)
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp.merge_id = writeoff1.id
                assetdetails_resp.assettran_id = writeoff1.newassetid
                assetdetails_resp.merge_reason = writeoff1.reason
                assetdetails_resp.merge_status = asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp.merge_value = str(writeoff1.assetmergeheader_value)
                if writeoff1.id not in source_clr_id:
                    source_clr_id.append(writeoff1.id)
                assetdetails_resp.color_id = len(source_clr_id)
                assetdetails_list.append(assetdetails_resp)
            # merge asset
            for i in assetdetails_data1:
                assetdetails_resp1 = AssetDetailsResponse()
                assetdetails = AssetDetails.objects.get(assetdetails_id=i.assetdetails_id)
                # from assetdetails
                assetdetails_resp1.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp1.set_capdate(str(assetdetails.capdate))
                assetdetails_resp1.assetdetailsgid = assetdetails.id
                assetdetails_resp1.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp1.set_branch_id(
                    api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp1.set_assetcatchange_id(
                    assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp1.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                # merge
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp1.asssettran_value = str(writeoff1.assetmergeheader_value)
                assetdetails_resp1.assettran_id = writeoff1.newassetid
                assetdetails_resp1.merge_id = writeoff1.id
                assetdetails_resp1.merge_reason = writeoff1.reason
                assetdetails_resp1.merge_status = asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp1.merge_value = str(writeoff1.assetmergeheader_value)
                if writeoff1.id in source_clr_id:
                    assetdetails_resp1.color_id = source_clr_id.index(writeoff1.id) + 1
                asset_spl.append(json.loads(assetdetails_resp1.get()))
            assetdetails_list.__dict__['asset_merge'] = (asset_spl)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

#checker_summarysearch
    def merge_checker_search(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition1 = Q(status=1) & Q(assetmergeheader_status=AssetRequestStatus.PENDING)
        writeoff = AssetMergeHeader.objects.filter(condition1).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(writeoff) > 0:
            mh_id = list()
            for wo in writeoff:
                if wo.id not in mh_id:
                    mh_id.append(wo.id)
            mhd_id = list()
            assetdetails1 = AssetMerge.objects.filter(assetmergeheader_id__in=mh_id)
            if len(assetdetails1) > 0:
                for i in assetdetails1:
                    assetdt_id = i.assetdetails_id
                    if i.assetmergeheader_id not in mhd_id:
                        mhd_id.append(i.assetmergeheader_id)
                        a_id.append(assetdt_id)
            else:
                return assetdetails_list1
        else:
            return assetdetails_list1
        logger.info("merge checker w_id :" + str(w_id))
        logger.info("merge checker a_id :" + str(a_id))
        assetdetails_data1 = AssetMerge.objects.filter(assetmergeheader_id__in=mh_id).order_by('-created_date')
        condition = Q(assetdetails_id__in=a_id)
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
        logger.info("AssetMergeHeader ch summary" + str(list_length))
        assetdetails_list = NWisefinList()
        api_obj = FaApiService(scope)
        assetlocation_serv = AssetLocationService(scope)
        assetcat_serv = AssetCatService(scope)
        asset_spl = []
        source_clr_id = []
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
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_resp.set_checkbox(False)
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp.merge_id = writeoff1.id
                assetdetails_resp.assettran_id = writeoff1.newassetid
                assetdetails_resp.merge_reason = writeoff1.reason
                assetdetails_resp.merge_status = asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp.merge_value = str(writeoff1.assetmergeheader_value)
                if writeoff1.id not in source_clr_id:
                    source_clr_id.append(writeoff1.id)
                assetdetails_resp.color_id = len(source_clr_id)
                assetdetails_list.append(assetdetails_resp)
            # merge asset
            for i in assetdetails_data1:
                assetdetails_resp1 = AssetDetailsResponse()
                assetdetails = AssetDetails.objects.get(assetdetails_id=i.assetdetails_id)
                # from assetdetails
                assetdetails_resp1.set_product_id(
                    api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp1.set_capdate(str(assetdetails.capdate))
                assetdetails_resp1.assetdetailsgid = assetdetails.id
                assetdetails_resp1.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp1.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp1.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp1.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                # merge
                writeoff = AssetMerge.objects.get(assetdetails_id=assetdetails.assetdetails_id)
                writeoff1 = AssetMergeHeader.objects.get(id=writeoff.assetmergeheader_id)
                assetdetails_resp1.asssettran_value = str(writeoff1.assetmergeheader_value)
                assetdetails_resp1.assettran_id = writeoff1.newassetid
                assetdetails_resp1.merge_id = writeoff1.id
                assetdetails_resp1.merge_reason = writeoff1.reason
                assetdetails_resp1.merge_status = asset_requeststatus(writeoff1.assetmergeheader_status)
                assetdetails_resp1.merge_value = str(writeoff1.assetmergeheader_value)
                if writeoff1.id in source_clr_id:
                    assetdetails_resp1.color_id = source_clr_id.index(writeoff1.id) + 1
                asset_spl.append(json.loads(assetdetails_resp1.get()))
            assetdetails_list.__dict__['asset_merge'] = (asset_spl)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list
