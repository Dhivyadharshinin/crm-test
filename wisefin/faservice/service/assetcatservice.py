import json
import logging
import traceback

from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse

from nwisefin.settings import logger
from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.data.response.assetcatresponse import AssetCatResponse
from faservice.models.famodels import AssetCat
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil
#from inwardservice.data.response.escalatontyperesponse import EscalationTypeResponse
#from inwardservice.models import EscalationType
#from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess as Success,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetCatService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetcat(self, assetcat_obj, emp_id,request):
        reqstatus = FaRequestStatusUtil.ONBORD
        if not assetcat_obj.get_id() is None:
            try:
                logger.info('FAL_ASSETCAT: AssetCat Update Started')

                assetcat_var = AssetCat.objects.filter(id=assetcat_obj.get_id()).update(
                    # subcategory_id=assetcat_obj.get_subcategory_id(),
                    # subcatname=assetcat_obj.get_subcatname(),
                    # lifetime=assetcat_obj.get_lifetime(),
                    deptype=assetcat_obj.get_deptype(),
                    # deprate_itc=assetcat_obj.get_deprate_itc(),
                    # deprate_ca=assetcat_obj.get_deprate_ca(),
                    # deprate_mgmt=assetcat_obj.get_deprate_mgmt(),
                    # depgl_itc=assetcat_obj.get_depgl_itc(),
                    # # depgl_ca=assetcat_obj.get_depgl_ca(),
                    depgl_mgmt=assetcat_obj.get_depgl_mgmt(),
                    itcatname=assetcat_obj.get_itcatname(),
                    # depresgl_itc=assetcat_obj.get_depresgl_itc(),
                    # depresgl_ca=assetcat_obj.get_depresgl_ca(),
                    # depresgl_mgmt=assetcat_obj.get_depresgl_mgmt(),
                    # apcatnodep_mgmt=assetcat_obj.get_apcatnodep_mgmt(),
                    # apscatnodep_mgmt=assetcat_obj.get_apscatnodep_mgmt(),
                    # apcatnodepres_mgmt=assetcat_obj.get_apcatnodepres_mgmt(),
                    # apscatnodepres_mgmt=assetcat_obj.get_apscatnodepres_mgmt(),
                    # deprate=assetcat_obj.get_deprate(),
                    # barcoderequired=assetcat_obj.get_barcoderequired(),
                    # remarks=assetcat_obj.get_remarks(),
                    updated_date=now(),
                    updated_by=emp_id)
                logger.info('FAL_ASSETCAT: AssetCat Update Success')

                assetcat = AssetCat.objects.get(id=assetcat_obj.get_id())

                refid = ref_type = -1
                relrefid = assetcat.id
                self.audit_function(assetcat, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.UPDATE, reqstatus,request)
            except IntegrityError as error:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except AssetCat.DoesNotExist:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_ASSETCAT_ID)
                error_obj.set_description(ErrorDescription.INVALID_ASSETCAT_ID)
                return error_obj
            except:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            # try:
                fa_api=FaApiService(request.scope)
                subcat_data={'subcat_id':assetcat_obj.get_subcategory_id()}
                resp=fa_api.create_codegen_detail(subcat_data,request)
                assetcat = AssetCat.objects.create(subcategory_id=assetcat_obj.get_subcategory_id(),
                    subcatname = assetcat_obj.get_subcatname(),
                    lifetime = assetcat_obj.get_lifetime(),
                    deptype = assetcat_obj.get_deptype(),
                    deprate_itc = assetcat_obj.get_deprate_itc(),
                    itcatname=assetcat_obj.get_itcatname(),
                    deprate_ca = assetcat_obj.get_deprate_ca(),
                    deprate_mgmt = assetcat_obj.get_deprate_mgmt(),
                    depgl_itc = assetcat_obj.get_depgl_itc(),
                    depgl_ca = assetcat_obj.get_depgl_ca(),
                    depgl_mgmt = assetcat_obj.get_depgl_mgmt(),
                    depresgl_itc = assetcat_obj.get_depresgl_itc(),
                    depresgl_ca = assetcat_obj.get_depresgl_ca(),
                    depresgl_mgmt = assetcat_obj.get_depresgl_mgmt(),
                    apcatnodep_mgmt = assetcat_obj.get_apcatnodep_mgmt(),
                    apscatnodep_mgmt = assetcat_obj.get_apscatnodep_mgmt(),
                    apcatnodepres_mgmt = assetcat_obj.get_apcatnodepres_mgmt(),
                    apscatnodepres_mgmt = assetcat_obj.get_apscatnodepres_mgmt(),
                    deprate = assetcat_obj.get_deprate_mgmt(),
                    barcoderequired = assetcat_obj.get_barcoderequired(),
                    remarks = assetcat_obj.get_remarks(),
                                                    created_by=emp_id)

                refid = ref_type = -1
                relrefid = assetcat.id
                self.audit_function(assetcat, refid, ref_type, relrefid,
                                    emp_id, FaModifyStatus.CREATE, reqstatus,request)
            #
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
        assetcat_resp = AssetCatResponse()
        assetcat_resp.set_id(assetcat.id)
        assetcat_resp.set_subcategory_id(assetcat.subcategory_id)
        assetcat_resp.set_subcatname(assetcat.subcatname)
        assetcat_resp.set_lifetime(assetcat.lifetime)
        assetcat_resp.set_deptype(assetcat.deptype)
        assetcat_resp.set_deprate_itc(assetcat.deprate_itc)
        assetcat_resp.set_deprate_ca(assetcat.deprate_ca)
        assetcat_resp.set_deprate_mgmt(assetcat.deprate_mgmt)
        assetcat_resp.set_depgl_itc(assetcat.depgl_itc)
        assetcat_resp.set_depgl_ca(assetcat.depgl_ca)
        assetcat_resp.set_depgl_mgmt(assetcat.depgl_mgmt)
        assetcat_resp.set_depresgl_itc(assetcat.depresgl_itc)
        assetcat_resp.set_depresgl_ca(assetcat.depresgl_ca)
        assetcat_resp.set_depresgl_mgmt(assetcat.depresgl_mgmt)
        assetcat_resp.set_apcatnodep_mgmt(assetcat.apcatnodep_mgmt)
        assetcat_resp.set_apscatnodep_mgmt(assetcat.apscatnodep_mgmt)
        assetcat_resp.set_apcatnodepres_mgmt(assetcat.apcatnodepres_mgmt)
        assetcat_resp.set_apscatnodepres_mgmt(assetcat.apscatnodepres_mgmt)
        assetcat_resp.set_deprate(assetcat.deprate)
        assetcat_resp.set_barcoderequired(assetcat.barcoderequired)
        assetcat_resp.set_remarks(assetcat.remarks)
        return assetcat_resp

    def fetch_assetcat_list(self,subcatname,deptype, vys_page,request):
        condition = Q(status=1)
        if 'subcat_id' in request.GET:
            condition&=Q(subcategory_id=request.GET.get('subcat_id'))
        if not subcatname is None and subcatname is not str():
            condition&=Q(subcatname__icontains=subcatname)
        if not deptype is None and deptype is not str():
            condition &= Q(deptype__exact=deptype)

        assetcat_data = AssetCat.objects.filter(condition).order_by('created_by')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(assetcat_data)
        #print(list_length)
        assetcat_list = NWisefinList()
        if list_length > 0:
            for assetcat in assetcat_data:
                assetcat_resp = AssetCatResponse()
                scope = request.scope
                subcategory =SubcategoryService(scope)
                assetcat_resp.set_id(assetcat.id)
                assetcat_resp.set_subcatname(assetcat.subcatname)
                assetcat_resp.set_subcategory_id(subcategory.fetchsubcategory(assetcat.subcategory_id))
                assetcat_resp.set_itcatname(assetcat.itcatname)
                assetcat_resp.set_lifetime(assetcat.lifetime)
                assetcat_resp.set_deptype(assetcat.deptype)
                assetcat_resp.set_deprate_itc(assetcat.deprate_itc)
                assetcat_resp.set_deprate_ca(assetcat.deprate_ca)
                assetcat_resp.set_deprate_mgmt(assetcat.deprate_mgmt)
                assetcat_resp.set_depgl_itc(assetcat.depgl_itc)
                assetcat_resp.set_depgl_ca(assetcat.depgl_ca)
                assetcat_resp.set_depgl_mgmt(assetcat.depgl_mgmt)
                assetcat_resp.set_depresgl_itc(assetcat.depresgl_itc)
                assetcat_resp.set_depresgl_ca(assetcat.depresgl_ca)
                assetcat_resp.set_depresgl_mgmt(assetcat.depresgl_mgmt)
                assetcat_resp.set_apcatnodep_mgmt(assetcat.apcatnodep_mgmt)
                assetcat_resp.set_apscatnodep_mgmt(assetcat.apscatnodep_mgmt)
                assetcat_resp.set_apcatnodepres_mgmt(assetcat.apcatnodepres_mgmt)
                assetcat_resp.set_apscatnodepres_mgmt(assetcat.apscatnodepres_mgmt)
                assetcat_resp.set_deprate(assetcat.deprate)
                assetcat_resp.set_barcoderequired(assetcat.barcoderequired)
                assetcat_resp.set_remarks(assetcat.remarks)
                assetcat_list.append(assetcat_resp)
            vpage = NWisefinPaginator(assetcat_data, vys_page.get_index(), 10)
            assetcat_list.set_pagination(vpage)
        return assetcat_list

    def fetch_assetcat(self,assetcat_id,request=None):
        try:
            assetcat = AssetCat.objects.get(id=assetcat_id)
            assetcat_resp = AssetCatResponse()
            scope = request.scope
            subcategory = FaApiService(scope)
            assetcat_resp.set_id(assetcat.id)
            assetcat_resp.set_subcategory_id(subcategory.fetchsubcategory(assetcat.subcategory_id,request))
            assetcat_resp.set_subcatname(assetcat.subcatname)
            assetcat_resp.set_lifetime(assetcat.lifetime)
            assetcat_resp.set_deptype(assetcat.deptype)
            assetcat_resp.set_deprate_itc(assetcat.deprate_itc)
            assetcat_resp.set_deprate_ca(assetcat.deprate_ca)
            assetcat_resp.set_deprate_mgmt(assetcat.deprate_mgmt)
            assetcat_resp.set_depgl_itc(assetcat.depgl_itc)
            assetcat_resp.set_depgl_ca(assetcat.depgl_ca)
            assetcat_resp.set_depgl_mgmt(assetcat.depgl_mgmt)
            assetcat_resp.set_depresgl_itc(assetcat.depresgl_itc)
            assetcat_resp.set_depresgl_ca(assetcat.depresgl_ca)
            assetcat_resp.set_depresgl_mgmt(assetcat.depresgl_mgmt)
            assetcat_resp.set_apcatnodep_mgmt(assetcat.apcatnodep_mgmt)
            assetcat_resp.set_apscatnodep_mgmt(assetcat.apscatnodep_mgmt)
            assetcat_resp.set_apcatnodepres_mgmt(assetcat.apcatnodepres_mgmt)
            assetcat_resp.set_apscatnodepres_mgmt(assetcat.apscatnodepres_mgmt)
            assetcat_resp.set_deprate(assetcat.deprate)
            assetcat_resp.set_barcoderequired(assetcat.barcoderequired)
            return assetcat_resp
        except AssetCat.DoesNotExist:
            logger.info('FAL_ASSETCAT_FETCH_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_ASSETCAT_ID)
            error_obj.set_description(ErrorDescription.INVALID_ASSETCAT_ID)
            return error_obj

    def delete_assetcat(self, assetcat_id,emp_id):
        assetcat = AssetCat.objects.filter(id=assetcat_id).delete()
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
            success_obj = Success()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


    def audit_function(self, audit_data, refid,reftype, relrefid, emp_id, action,reqstatus,request=None):
        scope=request.scope
        if action == FaModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = FaAuditService(scope)
        audit_obj = FaAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(reftype)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(FaRefType.ASSETCAT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)