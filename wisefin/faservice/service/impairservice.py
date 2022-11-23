from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.data.response.impairresponse import ImpairHeaderresponse
from faservice.models import AssetDetails, CGUAssetMap, ImpairDetails, ImpairHeader
from faservice.service.assetcatservice import AssetCatService
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import asset_requeststatus, \
    asset_requestfor_status, assetvaluedtl_status, FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetRequestStatus, \
    AssetStatus, AssetRequestfor

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ImpairService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    #add-Impair map summary
    def search_impairmapping(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition = Q(status=1) & Q(requestfor=0) & Q(assetdetails_status=1)
        if 'branch_id' in data_obj:
            condition &= Q(branch_id=data_obj['branch_id'])
        if 'assetdetails_id' in data_obj:
            condition &= Q(barcode__icontains=data_obj['assetdetails_id'])
        if 'capdate' in data_obj:
            condition &= Q(capdate=data_obj['capdate'])
        assetdetails_data = AssetDetails.objects.filter(condition).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        logger.info("Impair map summary" + str(list_length))
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
                assetdetails_resp.set_product_id(api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_checkbox(False)           #FE Need for action
                assetdetails_list.append(assetdetails_resp)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    def cgu_mapping(self, details_json, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        Status = AssetStatus.ACTIVE
        logger.info("cgu_mapping : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        name = details_json.get("name")
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            barcode = assetdetails.barcode
            assetdetails_value = assetdetails.assetdetails_value
            cgu_list = CGUAssetMap.objects.filter(barcode=barcode, cgu_status=Status)

            if len(cgu_list) > 0:
                cgu_status = CGUAssetMap.objects.filter(barcode=barcode, cgu_status=Status).update(
                                                        cgu_status=AssetStatus.IN_ACTIVE,
                                                        status=0,
                                                        updated_by=emp_id,
                                                        updated_date=now())
            cgu = CGUAssetMap.objects.create(name=name,
                                            barcode=barcode,
                                            cgu_status=Status,
                                            cgu_mappeddate=now(),
                                            cgu_value=assetdetails_value,
                                            created_by=emp_id)
            refid = ref_type = -1
            relrefid = cgu.id
            self.audit_function(cgu, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus)

        assetdetails_resp = AssetDetailsResponse()
        assetdetails_resp.set_id(cgu.id)
        assetdetails_resp.set_barcode(cgu.barcode)
        return assetdetails_resp

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
        audit_obj.set_relreftype(FaRefType.IMPAIR)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    # add-summary  impair
    def search_impair_add(self, vys_page, emp_id, data_obj, request):
        scope=request.scope
        condition = Q(status=1)
        if 'cgu_name' in data_obj:
            condition &= Q(name=data_obj['cgu_name'])
        cgu_list = CGUAssetMap.objects.filter(condition).order_by('-id')
        w_id = list()
        a_id = list()
        assetdetails_list1 = NWisefinList()
        if len(cgu_list) > 0:
            for wo in cgu_list:
                assetdetails1 = AssetDetails.objects.filter(barcode=wo.barcode)
                if len(assetdetails1) > 0:
                    assetdetails = assetdetails1[0]
                    assetdt_id = assetdetails.id
                    a_id.append(assetdt_id)
                else:
                    continue
                    return assetdetails_list1
        else:
            return assetdetails_list1
        logger.info("impair :" + str(w_id))
        logger.info("impair :" + str(a_id))
        condition1 = Q(id__in=a_id) & Q(assetdetails_status=1)
        assettotal_value = 0
        assetdetails_data = AssetDetails.objects.filter(condition1).order_by('-updated_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetdetails_data)
        print(list_length)
        logger.info("impair summary" + str(list_length))
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
                assetdetails_resp.set_product_id(api_obj.fetch_product(assetdetails.product_id, emp_id, request))
                assetdetails_resp.set_capdate(str(assetdetails.capdate))
                assetdetails_resp.set_assetdetails_value(str(assetdetails.assetdetails_value))
                assetdetails_resp.set_branch_id(api_obj.fetch_branch(assetdetails.branch_id))
                assetdetails_resp.set_assetlocation_id(assetlocation_serv.fetch_assetlocation(assetdetails.assetlocation_id))
                assetdetails_resp.set_assetcatchange_id(assetcat_serv.fetch_assetcat(assetdetails.assetcat_id,request))
                assetdetails_resp.set_requestfor(asset_requestfor_status(assetdetails.requestfor))
                assetdetails_resp.set_requeststatus(asset_requeststatus(assetdetails.requeststatus))
                assetdetails_resp.set_vendorname(assetdetails.vendorname)
                assetdetails_resp.set_qty(assetdetails.qty)
                assetdetails_resp.set_assetdetails_status(assetvaluedtl_status(assetdetails.assetdetails_status))
                assetdetails_resp.set_subcat(assetdetails.subcat)
                assetdetails_resp.set_checkbox(False)  # FE Need for action
                condition2=Q(barcode=assetdetails.barcode)
                if 'cgu_name' in data_obj:
                    condition2&=Q(name=data_obj['cgu_name'])
                cguassetmap = CGUAssetMap.objects.get(condition2)
                assetdetails_resp.cgu_id = cguassetmap.id
                assetdetails_resp.cgu_name = cguassetmap.name
                assetdetails_list.append(assetdetails_resp)

                assettotal_value += assetdetails.assetdetails_value
                assetdetails_list.__dict__['assettotal_value'] = str(assettotal_value)
            vpage = NWisefinPaginator(assetdetails_data, vys_page.get_index(), 10)
            assetdetails_list.set_pagination(vpage)
        return assetdetails_list

    #impair make
    def create_impair(self, data_arr, reversed_value, reason, cgu_id, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        impairheader_status = AssetRequestStatus.PENDING
        old_cguvalue = 0
        asset_count = 0
        for barcode in data_arr:
            assetdetails = AssetDetails.objects.filter(barcode=barcode)
            for ass in assetdetails:
                old_cguvalue += ass.assetdetails_value
                asset_count += ass.qty
        newcgu_value = reversed_value
        old_cguvalue = old_cguvalue
        asset_count = asset_count
        for cgu_id in cgu_id:
            impairhd = ImpairHeader.objects.create(cgu_id=cgu_id,
                                                old_cguvalue=old_cguvalue,
                                                newcgu_value=newcgu_value,
                                                date=now(),
                                                asset_count=asset_count,
                                                impairheader_status=impairheader_status,
                                                reason=reason,
                                                created_by=emp_id)
            refid = ref_type = -1
            relrefid = impairhd.id
            self.audit_function(impairhd, refid, ref_type, relrefid,
                                emp_id, FaModifyStatus.CREATE, reqstatus)

        impairheader_resp = ImpairHeaderresponse()
        impairheader_resp.set_id(impairhd.id)
        impairheader_resp.set_cgu_id(impairhd.cgu_id)
        impairheader_resp.set_old_cguvalue(str(impairhd.old_cguvalue))
        impairheader_resp.set_newcgu_value(str(impairhd.newcgu_value))
        impairheader_resp.set_date(str(impairhd.date))
        impairheader_resp.set_asset_count(impairhd.asset_count)
        return impairheader_resp
        # impair make
    def create_impairdt(self, data_arr, impairh_id, newcgu_value, emp_id):
        reqstatus = FaRequestStatusUtil.ONBORD
        for barcode in data_arr:
            assetdetails = AssetDetails.objects.filter(barcode=barcode)
            for ass in assetdetails:
                impairdtl = ImpairDetails.objects.create(impair_id_id=impairh_id,
                                                      asset_barcode=ass.barcode,
                                                      oldbassetvalue=ass.assetdetails_value,
                                                      changedassetvalue=newcgu_value,
                                                      created_by=emp_id)
                refid = ref_type = -1
                relrefid = impairdtl.id
                self.audit_function(impairdtl, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus)
        impairheader_resp = ImpairHeaderresponse()
        impairheader_resp.newcgu_value = newcgu_value
        impairheader_resp.impairh_id = impairh_id
        return impairheader_resp

    # impair_maker_summary
    def impairmaker_summary(self, vys_page):
        condition = Q(status=1)
        impairheader_data = ImpairHeader.objects.filter(condition).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(impairheader_data)
        print(list_length)
        logger.info("impair_maker_summary" + str(list_length))
        impairheader_list = NWisefinList()
        if list_length > 0:
            for impairheader in impairheader_data:
                impairheader_resp = ImpairHeaderresponse()
                impairheader_resp.set_id(impairheader.id)
                impairheader_resp.set_cgu_id(impairheader.cgu_id)
                impairheader_resp.set_old_cguvalue(str(impairheader.old_cguvalue))
                impairheader_resp.set_newcgu_value(str(impairheader.newcgu_value))
                impairheader_resp.set_date(str(impairheader.date))
                impairheader_resp.set_asset_count(impairheader.asset_count)
                impairheader_resp.set_reason(impairheader.reason)
                impairheader_resp.set_impairheader_status(asset_requeststatus(impairheader.impairheader_status))
                cguassetmap = CGUAssetMap.objects.get(id=impairheader.cgu_id)
                impairheader_resp.id = cguassetmap.id
                impairheader_resp.name = cguassetmap.name
                impairheader_resp.barcode = cguassetmap.barcode
                impairheader_resp.cgu_status = cguassetmap.cgu_status
                impairheader_resp.cgu_mappeddate = str(cguassetmap.cgu_mappeddate)
                impairheader_resp.cgu_value = str(cguassetmap.cgu_value)
                impairheader_resp.checkbox = False
                impairheader_list.append(impairheader_resp)
            vpage = NWisefinPaginator(impairheader_data, vys_page.get_index(), 10)
            impairheader_list.set_pagination(vpage)
        return impairheader_list

    # impairchecker_summary_search
    def impairmaker_summary_search(self, vys_page, data_obj):
        condition = Q(status=1)
        if 'name' in data_obj:
            condition &= Q(name__icontains=data_obj['name'])
        if 'cgu_value' in data_obj:
            condition &= Q(cgu_value__icontains=data_obj['cgu_value'])
        cguassetmap = CGUAssetMap.objects.filter(condition).order_by('-id')
        ih_id = list()
        impairheader_list1 = NWisefinList()
        if len(cguassetmap) > 0:
            for cg in cguassetmap:
                if cg.id not in ih_id:
                    ih_id.append(cg.id)
        else:
            return impairheader_list1
        logger.info("impair ch :" + str(cguassetmap))
        print(cguassetmap)
        condition1 = Q(cgu_id__in=ih_id) & Q(status=1)
        impairheader_data = ImpairHeader.objects.filter(condition1).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(impairheader_data)
        print(list_length)
        logger.info("impairmaker_summary_search" + str(list_length))
        impairheader_list = NWisefinList()
        if list_length > 0:
            for impairheader in impairheader_data:
                impairheader_resp = ImpairHeaderresponse()
                impairheader_resp.set_id(impairheader.id)
                impairheader_resp.set_cgu_id(impairheader.cgu_id)
                impairheader_resp.set_old_cguvalue(str(impairheader.old_cguvalue))
                impairheader_resp.set_newcgu_value(str(impairheader.newcgu_value))
                impairheader_resp.set_asset_count(impairheader.asset_count)
                impairheader_resp.set_impairheader_status(asset_requeststatus(impairheader.impairheader_status))
                cguassetmap = CGUAssetMap.objects.get(id=impairheader.cgu_id)
                impairheader_resp.name = cguassetmap.name
                impairheader_list.append(impairheader_resp)
            vpage = NWisefinPaginator(impairheader_data, vys_page.get_index(), 10)
            impairheader_list.set_pagination(vpage)
        return impairheader_list

    # reject
    def impair_reject(self, details_json, emp_id):
        impair_status = AssetRequestStatus.REJECTED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("impair DATA FOR Reject : " + str(details_json))
        data_arr = details_json.get("cgu_id")
        reason = details_json.get("reason")
        for cgu_id in data_arr:
            cgu_list = CGUAssetMap.objects.get(id=cgu_id)
            cgu_barcode = cgu_list.barcode
            impair = ImpairHeader.objects.get(cgu_id=cgu_id, status=1)
            creatby = impair.created_by
            if creatby != emp_id:
                assetdetails = AssetDetails.objects.get(barcode=cgu_barcode, requestfor=AssetRequestfor.IMPAIRMENT, status=1)
                assetdetailss = AssetDetails.objects.filter(barcode=cgu_barcode, requestfor=AssetRequestfor.IMPAIRMENT).update(
                                requestfor=0,
                                requeststatus=impair_status,
                                updated_by=emp_id,
                                updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus)
                impairr = ImpairHeader.objects.filter(cgu_id=cgu_id).update(
                    impairheader_status=impair_status,
                    reason=reason,
                    updated_by=emp_id,
                    updated_date=now())
                refid = ref_type = -1
                relrefid = impair.id
                self.audit_function(impair, refid, ref_type, relrefid,emp_id, FaModifyStatus.UPDATE, reqstatus)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.code = ErrorMessage.INVALID_APPROVER_ID
                success_obj.description = ErrorDescription.INVALID_APPROVER_ID
        return success_obj

    # approve
    def impair_approve(self, details_json, emp_id):
        impair_status = AssetRequestStatus.APPROVED
        reqstatus = FaRequestStatusUtil.MODIFICATION
        logger.info("impair DATA FOR APPROVE : " + str(details_json))
        data_arr = details_json.get("cgu_id")
        reason = details_json.get("reason")
        for cgu_id in data_arr:
            cgu_list = CGUAssetMap.objects.get(id=cgu_id)
            cgu_barcode = cgu_list.barcode
            impair = ImpairHeader.objects.get(cgu_id=cgu_id, status=1)
            creatby = impair.created_by
            if creatby != emp_id:
                assetdetails = AssetDetails.objects.get(barcode=cgu_barcode, requestfor=AssetRequestfor.IMPAIRMENT,
                                                        status=1)
                assetdetailss = AssetDetails.objects.filter(barcode=cgu_barcode,
                                                            requestfor=AssetRequestfor.IMPAIRMENT).update(
                    requestfor=0,
                    requeststatus=impair_status,
                    updated_by=emp_id,
                    updated_date=now())
                refid = ref_type = -1
                relrefid = assetdetails.id
                self.audit_function(assetdetails, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus)
                impairr = ImpairHeader.objects.filter(cgu_id=cgu_id).update(
                    impairheader_status=impair_status,
                    reason=reason,
                    updated_by=emp_id,
                    updated_date=now())
                refid = ref_type = -1
                relrefid = impair.id
                self.audit_function(impair, refid, ref_type, relrefid, emp_id, FaModifyStatus.UPDATE, reqstatus)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.code = ErrorMessage.INVALID_APPROVER_ID
                success_obj.description = ErrorDescription.INVALID_APPROVER_ID
        return success_obj

    def impairchecker_summary(self, vys_page):
        condition = Q(status=1) & Q(impairheader_status=AssetRequestStatus.PENDING)
        impairheader_data = ImpairHeader.objects.filter(condition).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(impairheader_data)
        print(list_length)
        logger.info("impair ch summary" + str(list_length))
        impairheader_list = NWisefinList()
        if list_length > 0:
            for impairheader in impairheader_data:
                impairheader_resp = ImpairHeaderresponse()
                impairheader_resp.set_id(impairheader.id)
                impairheader_resp.set_cgu_id(impairheader.cgu_id)
                impairheader_resp.set_old_cguvalue(str(impairheader.old_cguvalue))
                impairheader_resp.set_newcgu_value(str(impairheader.newcgu_value))
                impairheader_resp.set_date(str(impairheader.date))
                impairheader_resp.set_asset_count(impairheader.asset_count)
                impairheader_resp.set_reason(impairheader.reason)
                impairheader_resp.set_impairheader_status(asset_requeststatus(impairheader.impairheader_status))
                cguassetmap = CGUAssetMap.objects.get(id=impairheader.cgu_id)
                impairheader_resp.id = cguassetmap.id
                impairheader_resp.name = cguassetmap.name
                impairheader_resp.barcode = cguassetmap.barcode
                impairheader_resp.cgu_status = cguassetmap.cgu_status
                impairheader_resp.cgu_mappeddate = str(cguassetmap.cgu_mappeddate)
                impairheader_resp.cgu_value = str(cguassetmap.cgu_value)
                impairheader_resp.checkbox = False
                impairheader_list.append(impairheader_resp)
            vpage = NWisefinPaginator(impairheader_data, vys_page.get_index(), 10)
            impairheader_list.set_pagination(vpage)
        return impairheader_list

    # impairchecker_summary_search
    def impairchecker_summary_search(self, vys_page,data_obj):
        condition = Q(status=1)
        if 'name' in data_obj:
            condition &= Q(name__icontains=data_obj['name'])
        if 'cgu_value' in data_obj:
            condition &= Q(cgu_value__icontains=data_obj['cgu_value'])
        cguassetmap = CGUAssetMap.objects.filter(condition).order_by('-id')
        ih_id = list()
        impairheader_list1 = NWisefinList()
        if len(cguassetmap) > 0:
            for cg in cguassetmap:
                if cg.id not in ih_id:
                    ih_id.append(cg.id)
        else:
            return impairheader_list1
        logger.info("impair ch :" + str(cguassetmap))
        print(cguassetmap)
        condition1 = Q(cgu_id__in=ih_id) & Q(status=1) & Q(impairheader_status=AssetRequestStatus.PENDING)
        impairheader_data = ImpairHeader.objects.filter(condition1).order_by('-created_date')[
                            vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(impairheader_data)
        print(list_length)
        logger.info("impairchecker_summary_search" + str(list_length))
        impairheader_list = NWisefinList()
        if list_length > 0:
            for impairheader in impairheader_data:
                impairheader_resp = ImpairHeaderresponse()
                impairheader_resp.set_id(impairheader.id)
                impairheader_resp.set_cgu_id(impairheader.cgu_id)
                impairheader_resp.set_old_cguvalue(str(impairheader.old_cguvalue))
                impairheader_resp.set_newcgu_value(str(impairheader.newcgu_value))
                impairheader_resp.set_date(str(impairheader.date))
                impairheader_resp.set_asset_count(impairheader.asset_count)
                impairheader_resp.set_reason(impairheader.reason)
                impairheader_resp.set_impairheader_status(asset_requeststatus(impairheader.impairheader_status))
                cguassetmap = CGUAssetMap.objects.get(id=impairheader.cgu_id)
                impairheader_resp.id = cguassetmap.id
                impairheader_resp.name = cguassetmap.name
                impairheader_resp.barcode = cguassetmap.barcode
                impairheader_resp.cgu_status = cguassetmap.cgu_status
                impairheader_resp.cgu_mappeddate = str(cguassetmap.cgu_mappeddate)
                impairheader_resp.cgu_value = str(cguassetmap.cgu_value)
                impairheader_resp.checkbox = False
                impairheader_list.append(impairheader_resp)
            vpage = NWisefinPaginator(impairheader_data, vys_page.get_index(), 10)
            impairheader_list.set_pagination(vpage)
        return impairheader_list


