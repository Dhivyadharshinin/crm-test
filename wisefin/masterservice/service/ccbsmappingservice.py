import traceback

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.ccbsmappingresponse import CcbsmappingResponse
from masterservice.data.response.ccbsresponse import CostCentreResponse, BusinessSegmentResponse
from masterservice.service.ccbsservice import BusinessSegmentService, CostCentreService
from masterservice.models import CostCentreBusinessSegmentMaping, CostCentre, BusinessSegment
from django.utils import timezone
import json

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.util.masterutil import Code_Gen_Type, Code_Gen_Value
from masterservice.service.Codegenerator import CodeGen


class CcbsMappingService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_ccbsmapping(self, ccbsmapping_obj, user_id):
        if not ccbsmapping_obj.get_id() is None:
            try:
                logger.error('COSTCENTREBUSINESSSEGMENTMAPING: CostCentreBusinessSegmentMaping Update Started')
                ccbsmapping = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                    id=ccbsmapping_obj.get_id(), entity_id=self._entity_id()).update(
                    no=ccbsmapping_obj.get_no(),
                    name=ccbsmapping_obj.get_name(),
                    remarks=ccbsmapping_obj.get_remarks(),
                    description=ccbsmapping_obj.get_description(),
                    costcentre_id=ccbsmapping_obj.get_costcentre(),
                    businesssegment_id=ccbsmapping_obj.get_businesssegment(),
                    glno=ccbsmapping_obj.get_glno(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                ccbsmapping = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).get(
                    id=ccbsmapping_obj.get_id(), entity_id=self._entity_id())
                logger.error('COSTCENTREBUSINESSSEGMENTMAPING: CostCentreBusinessSegmentMaping Update Success' + str(ccbsmapping))
            except IntegrityError as error:
                logger.error('ERROR_CostCentreBusinessSegmentMaping_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except CostCentreBusinessSegmentMaping.DoesNotExist:
                logger.error('ERROR_CostCentreBusinessSegmentMaping_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ccbsmapping_ID)
                error_obj.set_description(ErrorDescription.INVALID_ccbsmapping_ID)
                return error_obj
            except:
                logger.error('ERROR_CostCentreBusinessSegmentMaping_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('COSTCENTREBUSINESSSEGMENTMAPING: CostCentreBusinessSegmentMaping Creation Started')
                data_len = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                    name=ccbsmapping_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                ccbsmapping = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).create(
                    no=ccbsmapping_obj.get_no(),
                    name=ccbsmapping_obj.get_name(),
                    remarks=ccbsmapping_obj.get_remarks(),
                    description=ccbsmapping_obj.get_description(),
                    costcentre_id=ccbsmapping_obj.get_costcentre(),
                    businesssegment_id=ccbsmapping_obj.get_businesssegment(),
                    glno=ccbsmapping_obj.get_glno(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                try:
                    max_cat_code = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(code__icontains='CCBS').order_by('-code')[0].code
                    rnsl = int(max_cat_code[4:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CCBS" + str(new_rnsl).zfill(5)
                ccbsmapping.code = code
                ccbsmapping.save()
                logger.error('COSTCENTREBUSINESSSEGMENTMAPING: CostCentreBusinessSegmentMaping Creation Success' + str(ccbsmapping))
            except IntegrityError as error:
                logger.error('ERROR_CostCentreBusinessSegmentMaping_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_CostCentreBusinessSegmentMaping_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = CcbsmappingResponse()
        data_obj.set_id(ccbsmapping.id)
        data_obj.set_code(ccbsmapping.code)
        data_obj.set_no(ccbsmapping.no)
        data_obj.set_name(ccbsmapping.name)
        data_obj.set_remarks(ccbsmapping.remarks)
        data_obj.set_description(ccbsmapping.description)
        data_obj.set_costcentre(ccbsmapping.costcentre_id)
        data_obj.set_businesssegment(ccbsmapping.businesssegment_id)
        data_obj.set_glno(ccbsmapping.glno)
        return data_obj

    def fetch_ccbsmapping(self, ccbsmapping_id):
        try:
            ccbsmapping = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).get(
                id=ccbsmapping_id, entity_id=self._entity_id())
            data_obj = CcbsmappingResponse()
            data_obj.set_id(ccbsmapping.id)
            data_obj.set_code(ccbsmapping.code)
            data_obj.set_no(ccbsmapping.no)
            data_obj.set_name(ccbsmapping.name)
            data_obj.set_remarks(ccbsmapping.remarks)
            data_obj.set_description(ccbsmapping.description)
            data_obj.set_costcentre(ccbsmapping.costcentre_id)
            data_obj.set_businesssegment(ccbsmapping.businesssegment_id)
            data_obj.set_glno(ccbsmapping.glno)
            return data_obj
        except CcbsmappingResponse.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ccbsmapping_ID)
            error_obj.set_description(ErrorDescription.INVALID_ccbsmapping_ID)
            return error_obj

    def fetch_ccbsmapping_list(self, vys_page):
        try:
            businesssegment_service = BusinessSegmentService(self._scope())
            costcentre_service = CostCentreService(self._scope())
            ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(ccbsmappingList)
            ccbsmapping_list_data = NWisefinList()
            if list_length <= 0:
                return ccbsmapping_list_data
            else:
                for ccbsmapping in ccbsmappingList:
                    data_obj = CcbsmappingResponse()
                    data_obj.set_id(ccbsmapping.id)
                    data_obj.set_code(ccbsmapping.code)
                    data_obj.set_no(ccbsmapping.no)
                    data_obj.set_name(ccbsmapping.name)
                    data_obj.set_remarks(ccbsmapping.remarks)
                    data_obj.set_description(ccbsmapping.description)
                    data_obj.set_costcentre(costcentre_service.fetch_costcentre(ccbsmapping.costcentre_id))
                    data=businesssegment_service.fetch_businesssegment(ccbsmapping.businesssegment_id)
                    if(data.code=='INVALID_businesssegment_ID'):
                        data_obj.set_businesssegment({
                            "code": "",
                            "description": "",
                            "name": "",
                            "remarks": ""})
                    else:
                        data_obj.set_businesssegment(data)
                    # data_obj.set_costcentre(ccbsmapping.costcentre_id)
                    # data_obj.set_businesssegment(ccbsmapping.businesssegment_id)
                    data_obj.set_glno(ccbsmapping.glno)
                    ccbsmapping_list_data.append(data_obj)
                    vpage = NWisefinPaginator(ccbsmappingList, vys_page.get_index(), 10)
                    ccbsmapping_list_data.set_pagination(vpage)

            return ccbsmapping_list_data
        except:
            logger.error('ERROR_CostCentreBusinessSegmentMaping_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ccbsmapping_ID)
            error_obj.set_description(ErrorDescription.INVALID_ccbsmapping_ID)

    def fetch_ccbsmapping_download(self, user_id):
        try:
            businesssegment_service = BusinessSegmentService(self._scope())
            costcentre_service = CostCentreService(self._scope())
            ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')
            list_length = len(ccbsmappingList)
            ccbsmapping_list_data = NWisefinList()
            if list_length <= 0:
                return ccbsmapping_list_data
            else:
                for ccbsmapping in ccbsmappingList:
                    data_obj = CcbsmappingResponse()
                    data_obj.Code = ccbsmapping.code
                    data_obj.No = ccbsmapping.no
                    data = businesssegment_service.fetch_businesssegment(ccbsmapping.businesssegment_id)
                    if data.code == 'INVALID_businesssegment_ID':
                        data_obj.BusinessSegment_Name = ""
                    else:
                        data_obj.BusinessSegment_Name = data.name
                    try:
                        costcentre = costcentre_service.fetch_costcentre(ccbsmapping.costcentre_id)
                        data_obj.Costcentre_Name = costcentre.name
                    except:
                        data_obj.Costcentre_Name = ""
                    data_obj.Name = ccbsmapping.name
                    data_obj.Remarks = ccbsmapping.remarks
                    data_obj.Description = ccbsmapping.description

                    data_obj.GLNo = ccbsmapping.glno
                    ccbsmapping_list_data.append(data_obj)
                return ccbsmapping_list_data
        except:
            logger.error('ERROR_CostCentreBusinessSegmentMapping_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ccbsmapping_ID)
            error_obj.set_description(ErrorDescription.INVALID_ccbsmapping_ID)


    def ccbsmapping_listactive(self, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
            condition).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(ccbsmappingList)
        ccbsmapping_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for ccbsmapping in ccbsmappingList:
                data_obj = CcbsmappingResponse()
                data_obj.set_id(ccbsmapping.id)
                data_obj.set_code(ccbsmapping.code)
                data_obj.set_no(ccbsmapping.no)
                data_obj.set_name(ccbsmapping.name)
                data_obj.set_remarks(ccbsmapping.remarks)
                data_obj.set_description(ccbsmapping.description)
                data_obj.set_costcentre(ccbsmapping.costcentre_id)
                data_obj.set_businesssegment(ccbsmapping.businesssegment_id)
                data_obj.set_glno(ccbsmapping.glno)
                ccbsmapping_list_data.append(data_obj)
                vpage = NWisefinPaginator(ccbsmappingList, vys_page.get_index(), 10)
                ccbsmapping_list_data.set_pagination(vpage)
        return ccbsmapping_list_data

    def ccbsmapping_listInactive(self, vys_page):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
            condition).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(ccbsmappingList)
        ccbsmapping_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for ccbsmapping in ccbsmappingList:
                data_obj = CcbsmappingResponse()
                data_obj.set_id(ccbsmapping.id)
                data_obj.set_code(ccbsmapping.code)
                data_obj.set_no(ccbsmapping.no)
                data_obj.set_name(ccbsmapping.name)
                data_obj.set_remarks(ccbsmapping.remarks)
                data_obj.set_description(ccbsmapping.description)
                data_obj.set_costcentre(ccbsmapping.costcentre_id)
                data_obj.set_businesssegment(ccbsmapping.businesssegment_id)
                data_obj.set_glno(ccbsmapping.glno)
                ccbsmapping_list_data.append(data_obj)
                vpage = NWisefinPaginator(ccbsmappingList, vys_page.get_index(), 10)
                ccbsmapping_list_data.set_pagination(vpage)

        return ccbsmapping_list_data

    def delete_ccbsmapping(self, ccbsmapping_id):
        ccbsmapping = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
            id=ccbsmapping_id, entity_id=self._entity_id()).delete()
        if ccbsmapping[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CostCentreBusinessSegmentMaping_ID)
            error_obj.set_description(ErrorDescription.INVALID_CostCentreBusinessSegmentMaping_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def searchcostcentre(self, vys_page, query):
        condition = Q(status=1) & Q(name__icontains=query) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length > 0:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_name(costcentre.name)
                data_obj.set_no(costcentre.no)
                costcentre_list_data.append(data_obj)
            vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
            costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data

    def searchbusinesssegment(self, vys_page, query):
        condition = Q(status=1) & Q(name__icontains=query) & Q(entity_id=self._entity_id())
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition)[
                              vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length > 0:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_name(businesssegment.name)
                data_obj.set_no(businesssegment.no)
                data_obj.set_code(businesssegment.code)
                data_obj.set_description(businesssegment.description)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data

    def search_ccbs(self, vys_page, ccbs_obj):
        businesssegment_service = BusinessSegmentService(self._scope())
        costcentre_service = CostCentreService(self._scope())
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if 'no' in ccbs_obj:
            condition &= Q(no__icontains=ccbs_obj['no'])
        if 'name' in ccbs_obj:
            condition &= Q(name__icontains=ccbs_obj['name'])
        if 'businesssegment_id' in ccbs_obj:
            condition &= Q(businesssegment_id=ccbs_obj['businesssegment_id'])
        if 'costcentre_id' in ccbs_obj:
            condition &= Q(costcentre_id=ccbs_obj['costcentre_id'])
        ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
            condition).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(ccbsmappingList)
        ccbsmapping_list_data = NWisefinList()
        if list_length > 0:
            for ccbsmapping in ccbsmappingList:
                data_obj = CcbsmappingResponse()
                data_obj.set_id(ccbsmapping.id)
                data_obj.set_code(ccbsmapping.code)
                data_obj.set_no(ccbsmapping.no)
                data_obj.set_name(ccbsmapping.name)
                data_obj.set_remarks(ccbsmapping.remarks)
                data_obj.set_description(ccbsmapping.description)
                data_obj.set_costcentre(costcentre_service.fetch_costcentre(ccbsmapping.costcentre_id))
                data_obj.set_businesssegment(
                    businesssegment_service.fetch_businesssegment(ccbsmapping.businesssegment_id))
                data_obj.set_glno(ccbsmapping.glno)
                ccbsmapping_list_data.append(data_obj)
                vpage = NWisefinPaginator(ccbsmappingList, vys_page.get_index(), 10)
                ccbsmapping_list_data.set_pagination(vpage)
        return ccbsmapping_list_data

    def searchbs_cc(self, bs_id, query):
        bs_id = int(bs_id)
        if query is None:
            ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                businesssegment_id=bs_id, entity_id=self._entity_id())
        else:
            condition = Q(status=1) & Q(costcentre_id__name__icontains=query) & Q(businesssegment_id=bs_id) & Q(
                entity_id=self._entity_id())
            ccbsmappingList = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(
                condition)
        cc_list = []
        for ccbsmapping in ccbsmappingList:
            cc_list.append(ccbsmapping.costcentre_id)
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(id__in=cc_list,
                                                                                     entity_id=self._entity_id())
        costcentre_list_data = NWisefinList()
        for costcentre in costcentreList:
            data_obj = CostCentreResponse()
            data_obj.set_id(costcentre.id)
            data_obj.set_code(costcentre.code)
            data_obj.set_no(costcentre.no)
            data_obj.set_name(costcentre.name)
            data_obj.set_description(costcentre.description)
            costcentre_list_data.append(data_obj)
        return costcentre_list_data
