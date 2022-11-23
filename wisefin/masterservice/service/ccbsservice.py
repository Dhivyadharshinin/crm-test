import traceback

from django.db import IntegrityError
from django.db.models import Q
from masterservice.data.response.ccbsresponse import BusinessSegmentResponse
from masterservice.data.response.ccbsresponse import CostCentreResponse,MasterBusinessSegmentResponse
from masterservice.models import CostCentre, BusinessSegment, MasterBusinessSegment,Apsector
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from masterservice.util.masterutil import Code_Gen_Type, Code_Gen_Value, MasterStatus
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.Codegenerator import CodeGen
import json


# costcentre
class CostCentreService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_costcentre(self, costcentre_obj, user_id):
        if not costcentre_obj.get_id() is None:
            try:
                logger.error('COSTCENTRE: CostCentre Update Started')
                costcentre = CostCentre.objects.using(self._current_app_schema()).filter(id=costcentre_obj.get_id(),
                                                                                         entity_id=self._entity_id()).update(
                    no=costcentre_obj.get_no(),
                    name=costcentre_obj.get_name(),
                    code=costcentre_obj.get_name(),
                    remarks=costcentre_obj.get_remarks(),
                    description=costcentre_obj.get_description(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                costcentre = CostCentre.objects.using(self._current_app_schema()).get(id=costcentre_obj.get_id(),
                                                                                      entity_id=self._entity_id())
                logger.error('COSTCENTRE: CostCentre Update Success' + str(costcentre))
            except IntegrityError as error:
                logger.error('ERROR_CostCentre_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except CostCentre.DoesNotExist:
                logger.error('ERROR_CostCentre_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
                error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
                return error_obj
            except:
                logger.error('ERROR_CostCentre_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('COSTCENTRE: CostCentre Creation Started')
                data_len = CostCentre.objects.using(self._current_app_schema()).filter(
                    name=costcentre_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                costcentre = CostCentre.objects.using(self._current_app_schema()).create(
                    no=costcentre_obj.get_no(),
                    name=costcentre_obj.get_name(),
                    remarks=costcentre_obj.get_remarks(),
                    description=costcentre_obj.get_description(),
                    businesssegment_id=costcentre_obj.get_businesssegment_id(),
                    code=costcentre_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                logger.error('COSTCENTRE: CostCentre Creation Success' + str(costcentre))

                # code = CostCentre.objects.using(self._current_app_schema()).filter(code=costcentre_obj.get_name())
                # costcentre.code = code
                # costcentre.save()
            except IntegrityError as error:
                logger.error('ERROR_CostCentre_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_CostCentre_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = CostCentreResponse()
        data_obj.set_id(costcentre.id)
        data_obj.set_code(costcentre.code)
        data_obj.set_no(costcentre.no)
        data_obj.set_name(costcentre.name)
        data_obj.set_remarks(costcentre.remarks)
        data_obj.set_description(costcentre.description)
        return data_obj

    def fetch_costcentre(self, costcentre_id):
        try:
            costcentre = CostCentre.objects.using(self._current_app_schema()).get(id=costcentre_id, status=1,
                                                                                  entity_id=self._entity_id())
            data_obj = CostCentreResponse()
            data_obj.set_id(costcentre.id)
            data_obj.set_code(costcentre.code)
            data_obj.set_no(costcentre.no)
            data_obj.set_name(costcentre.name)
            data_obj.set_remarks(costcentre.remarks)
            data_obj.set_description(costcentre.description)
            return data_obj
        except ObjectDoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
            error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
            return error_obj

    def fetch_costcentre_list(self, vys_page):
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data

    def delete_costcentre(self, costcentre_id):
        costcentre = CostCentreResponse.objects.using(self._current_app_schema()).filter(id=costcentre_id,
                                                                                         entity_id=self._entity_id()).delete()
        if costcentre[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COSTCENTRE_ID)
            error_obj.set_description(ErrorDescription.INVALID_COSTCENTRE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def updateCCstatus(self, costcentre_id, status, user_id):
        costcentre = CostCentre.objects.using(self._current_app_schema()).filter(id=costcentre_id,
                                                                                 entity_id=self._entity_id()).update(
            status=status,
            updated_by=user_id,
            updated_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def costcentresearch(self, vys_page, query):
        no = query.get('no')
        name = query.get('name')
        condition = Q(no__icontains=no) & Q(name__icontains=name, status=1) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length > 0:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                data_obj.set_status(costcentre.status)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data
    def costcentresearch_overall(self, vys_page, query):
        no = query.get('no')
        name = query.get('name')
        condition = Q(no__icontains=no) & Q(name__icontains=name) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length > 0:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                data_obj.set_status(costcentre.status)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data

    def costcentresearch_overall_mst(self, vys_page, request):
        status = request.GET.get('status', 2)
        condition = Q() & Q(entity_id=self._entity_id())
        if status == '':
            status = 2
        if int(status) != 2:
            condition = Q(status=status) & Q(entity_id=self._entity_id())
        if 'no' in request.GET:
            condition &= Q(no__icontains=request.GET.get('no'))
        if 'name' in request.GET:
            condition &= Q(name__icontains=request.GET.get('name'))
        # no = query.get('no')
        # name = query.get('name')
        # condition = Q(no__icontains=no) & Q(name__icontains=name) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length > 0:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                data_obj.set_status(costcentre.status)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data
    def costcentrelist(self, vys_page):
        try:
            costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(costcentreList)
            costcentre_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for costcentre in costcentreList:
                    data_obj = CostCentreResponse()
                    data_obj.set_id(costcentre.id)
                    data_obj.set_code(costcentre.code)
                    data_obj.set_no(costcentre.no)
                    data_obj.set_name(costcentre.name)
                    data_obj.set_remarks(costcentre.remarks)
                    data_obj.set_description(costcentre.description)
                    data_obj.set_status(costcentre.status)
                    costcentre_list_data.append(data_obj)
                    vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                    costcentre_list_data.set_pagination(vpage)
            return costcentre_list_data
        except:
            logger.error('ERROR_CostCentre_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def fetch_costcentre_download(self, user_id):
        try:
            costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')
            list_length = len(costcentreList)
            costcentre_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for costcentre in costcentreList:
                    data_obj = CostCentreResponse()
                    data_obj.Code = (costcentre.code)
                    data_obj.No = (costcentre.no)
                    data_obj.Name = (costcentre.name)
                    data_obj.Remarks = (costcentre.remarks)
                    data_obj.Description = (costcentre.description)
                    status = MasterStatus()
                    if costcentre.status == status.Active:
                        data_obj.Status = status.Active_VALUE
                    if costcentre.status == status.Inactive:
                        data_obj.Status = status.Inactive_VALUE
                    costcentre_list_data.append(data_obj)
            return costcentre_list_data
        except:
            logger.error('ERROR_CostCentre_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def costcentreActivelist(self, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                data_obj.set_status(costcentre.status)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data

    def costcentreInactivelist(self, vys_page):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        costcentreList = CostCentre.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(costcentreList)
        costcentre_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for costcentre in costcentreList:
                data_obj = CostCentreResponse()
                data_obj.set_id(costcentre.id)
                data_obj.set_code(costcentre.code)
                data_obj.set_no(costcentre.no)
                data_obj.set_name(costcentre.name)
                data_obj.set_remarks(costcentre.remarks)
                data_obj.set_description(costcentre.description)
                data_obj.set_status(costcentre.status)
                costcentre_list_data.append(data_obj)
                vpage = NWisefinPaginator(costcentreList, vys_page.get_index(), 10)
                costcentre_list_data.set_pagination(vpage)
        return costcentre_list_data

    def create_costcentre_mtom(self, costcentre_obj, action, user_id):
        if action == 'update':
            try:
                costcentre = CostCentre.objects.using(self._current_app_schema()).filter(code=costcentre_obj.get_code(),
                                                                                         entity_id=self._entity_id()).update(
                    no=costcentre_obj.get_no(),
                    name=costcentre_obj.get_name(),
                    code=costcentre_obj.get_code(),
                    remarks=costcentre_obj.get_remarks(),
                    description=costcentre_obj.get_description(),
                    status=costcentre_obj.get_status(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                costcentre = CostCentre.objects.using(self._current_app_schema()).get(code=costcentre_obj.get_code(),
                                                                                      entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action == 'create':
            # try:
            bs_data = BusinessSegment.objects.using(self._current_app_schema()).get(code=costcentre_obj.get_bscode(),
                                                                                    entity_id=self._entity_id())
            costcentre = CostCentre.objects.using(self._current_app_schema()).create(
                businesssegment=bs_data,
                no=costcentre_obj.get_no(),
                name=costcentre_obj.get_name(),
                code=costcentre_obj.get_code(),
                remarks=costcentre_obj.get_remarks(),
                description=costcentre_obj.get_description(),
                created_by=user_id, entity_id=self._entity_id())

        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        data_obj = CostCentreResponse()
        data_obj.set_id(costcentre.id)
        data_obj.set_code(costcentre.code)
        data_obj.set_no(costcentre.no)
        data_obj.set_name(costcentre.name)
        data_obj.set_remarks(costcentre.remarks)
        data_obj.set_description(costcentre.description)
        return data_obj


    def cc_data_frame(self):
        costcentre = CostCentre.objects.using(self._current_app_schema()).filter(status=1,
                                                                              entity_id=self._entity_id()).values("id","name")
        return costcentre


# businesssegement
class BusinessSegmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_businesssegment(self, businesssegment_obj, user_id):
        if not businesssegment_obj.get_id() is None:
            try:
                logger.error('BUSINESSSEGMENT: BusinessSegment Update Started')
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).filter(
                    id=businesssegment_obj.get_id(), entity_id=self._entity_id()).update(
                    no=businesssegment_obj.get_no(),
                    name=businesssegment_obj.get_name(),
                    code=businesssegment_obj.get_name(),
                    remarks=businesssegment_obj.get_remarks(),
                    description=businesssegment_obj.get_description(),
                    masterbussinesssegment_id=businesssegment_obj.get_masterbussinesssegment_id(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).get(
                    id=businesssegment_obj.get_id(), entity_id=self._entity_id())
                logger.error('BUSINESSSEGMENT: BusinessSegment Update Success' + str(businesssegment))
            except IntegrityError as error:
                logger.error('ERROR_BusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except BusinessSegment.DoesNotExist:
                logger.error('ERROR_BusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_businesssegment_ID)
                error_obj.set_description(ErrorDescription.INVALID_businesssegment_ID)
                return error_obj
            except:
                logger.error('ERROR_BusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('BUSINESSSEGMENT: BusinessSegment Creation Started')
                data_len = BusinessSegment.objects.using(self._current_app_schema()).filter(
                    name=businesssegment_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).create(
                    no=businesssegment_obj.get_no(),
                    name=businesssegment_obj.get_name(),
                    remarks=businesssegment_obj.get_remarks(),
                    description=businesssegment_obj.get_description(),
                    masterbussinesssegment_id=businesssegment_obj.get_masterbussinesssegment_id(),
                    code=businesssegment_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                logger.error('BUSINESSSEGMENT: BusinessSegment Creation Success' + str(businesssegment))
                # code = BusinessSegment.objects.using(self._current_app_schema()).get(code=businesssegment_obj.get_name())
                # businesssegment.code = code
                # businesssegment.save()
            except IntegrityError as error:
                logger.error('ERROR_BusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_BusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = BusinessSegmentResponse()
        data_obj.set_id(businesssegment.id)
        data_obj.set_code(businesssegment.code)
        data_obj.set_no(businesssegment.no)
        data_obj.set_name(businesssegment.name)
        data_obj.set_remarks(businesssegment.remarks)
        data_obj.set_description(businesssegment.description)
        return data_obj

    def mastersegmentname_get(self, request, vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        masterbusinesssegment_data = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
                                     vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        masterbsname_list = NWisefinList()
        list_data = len(masterbusinesssegment_data)
        if list_data <= 0:
            vpage = NWisefinPaginator(masterbusinesssegment_data, vys_page.get_index(), 10)
            masterbsname_list.set_pagination(vpage)
            return masterbsname_list
        else:
            for i in masterbusinesssegment_data:
                # print(i)
                response = BusinessSegmentResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                masterbsname_list.append(response)
            vpage = NWisefinPaginator(masterbusinesssegment_data, vys_page.get_index(), 10)
            masterbsname_list.set_pagination(vpage)
            return masterbsname_list
    def fetch_businesssegment(self, businesssegment_id):
        try:
            businesssegment = BusinessSegment.objects.using(self._current_app_schema()).get(id=businesssegment_id,
                                                                                            entity_id=self._entity_id())
            data_obj = BusinessSegmentResponse()
            data_obj.set_id(businesssegment.id)
            data_obj.set_code(businesssegment.code)
            data_obj.set_no(businesssegment.no)
            data_obj.set_name(businesssegment.name)
            data_obj.set_remarks(businesssegment.remarks)
            data_obj.set_description(businesssegment.description)
            return data_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_businesssegment_ID)
            error_obj.set_description(ErrorDescription.INVALID_businesssegment_ID)
            return error_obj

    def fetch_businesssegment_list(self, vys_page, query):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if query != None and query != "":
            condition &= Q(name__icontains=query)
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_code(businesssegment.code)
                data_obj.set_no(businesssegment.no)
                data_obj.set_name(businesssegment.name)
                data_obj.set_remarks(businesssegment.remarks)
                data_obj.set_description(businesssegment.description)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data

    def delete_businesssegment(self, businesssegment_id):
        businesssegment = BusinessSegmentResponse.objects.using(self._current_app_schema()).filter(
            id=businesssegment_id, entity_id=self._entity_id()).delete()
        if businesssegment[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BUSINESSSEGMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_BUSINESSSEGMENT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def businesssegmentlist(self, vys_page):
        try:
            businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                                  vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(businesssegmentList)
            businesssegment_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for businesssegment in businesssegmentList:
                    data_obj = BusinessSegmentResponse()
                    data_obj.set_id(businesssegment.id)
                    data_obj.set_code(businesssegment.code)
                    data_obj.set_no(businesssegment.no)
                    data_obj.set_name(businesssegment.name)
                    data_obj.set_remarks(businesssegment.remarks)
                    data_obj.set_description(businesssegment.description)
                    data_obj.set_status(businesssegment.status)
                    businesssegment_list_data.append(data_obj)
                    vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                    businesssegment_list_data.set_pagination(vpage)
            return businesssegment_list_data
        except:
            logger.error('ERROR_BusinessSegment_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_businesssegment_ID)
            error_obj.set_description(ErrorDescription.INVALID_businesssegment_ID)
            return error_obj

    def fetch_businesssegment_download(self, vys_page):
        try:
            businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')
            list_length = len(businesssegmentList)
            businesssegment_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for businesssegment in businesssegmentList:
                    data_obj = BusinessSegmentResponse()
                    data_obj.Code = (businesssegment.code)
                    data_obj.No = (businesssegment.no)
                    data_obj.Name = (businesssegment.name)
                    data_obj.Remarks = (businesssegment.remarks)
                    data_obj.Description = (businesssegment.description)
                    status = MasterStatus()
                    if businesssegment.status == status.Active:
                        data_obj.Status = status.Active_VALUE
                    if businesssegment.status == status.Inactive:
                        data_obj.Status = status.Inactive_VALUE
                    businesssegment_list_data.append(data_obj)

            return businesssegment_list_data
        except:
            logger.error('ERROR_BusinessSegment_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_businesssegment_ID)
            error_obj.set_description(ErrorDescription.INVALID_businesssegment_ID)
            return error_obj


    def updateBSstatus(self, businesssegment_id, status, user_id):

        businesssegment = BusinessSegment.objects.using(self._current_app_schema()).filter(id=businesssegment_id,
                                                                                           entity_id=self._entity_id()).update(
            status=status,
            updated_by=user_id,
            updated_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def businesssegmentsearch(self, vys_page, query):
        no = query.get('no')
        name = query.get('name')
        condition = Q(no__icontains=no) & Q(name__icontains=name) & Q(entity_id=self._entity_id())
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition)[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length > 0:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_code(businesssegment.code)
                data_obj.set_no(businesssegment.no)
                data_obj.set_name(businesssegment.name)
                data_obj.set_remarks(businesssegment.remarks)
                data_obj.set_description(businesssegment.description)
                data_obj.set_status(businesssegment.status)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data
    def businesssegmentsearch_mst(self, vys_page, request):
        status = request.GET.get('status', 2)
        condition = Q() & Q(entity_id=self._entity_id())
        if status == '':
            status = 2
        if int(status) != 2:
            condition = Q(status=status) & Q(entity_id=self._entity_id())
        if 'no' in request.GET:
            condition &= Q(no__icontains=request.GET.get('no'))
        if 'name' in request.GET:
            condition &= Q(name__icontains=request.GET.get('name'))
        # no = query.get('no')
        # name = query.get('name')
        # condition = Q(no__icontains=no) & Q(name__icontains=name) & Q(entity_id=self._entity_id())
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition)[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length > 0:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_code(businesssegment.code)
                data_obj.set_no(businesssegment.no)
                data_obj.set_name(businesssegment.name)
                data_obj.set_remarks(businesssegment.remarks)
                data_obj.set_description(businesssegment.description)
                data_obj.set_status(businesssegment.status)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data
    def businesssegmentlistActive(self, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_code(businesssegment.code)
                data_obj.set_no(businesssegment.no)
                data_obj.set_name(businesssegment.name)
                data_obj.set_remarks(businesssegment.remarks)
                data_obj.set_description(businesssegment.description)
                data_obj.set_status(businesssegment.status)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data

    def businesssegmentlistInactive(self, vys_page):
        condition = Q(status=0) & Q(entity_id=self._entity_id())
        businesssegmentList = BusinessSegment.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(businesssegmentList)
        businesssegment_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for businesssegment in businesssegmentList:
                data_obj = BusinessSegmentResponse()
                data_obj.set_id(businesssegment.id)
                data_obj.set_code(businesssegment.code)
                data_obj.set_no(businesssegment.no)
                data_obj.set_name(businesssegment.name)
                data_obj.set_remarks(businesssegment.remarks)
                data_obj.set_description(businesssegment.description)
                data_obj.set_status(businesssegment.status)
                businesssegment_list_data.append(data_obj)
                vpage = NWisefinPaginator(businesssegmentList, vys_page.get_index(), 10)
                businesssegment_list_data.set_pagination(vpage)
        return businesssegment_list_data

    def create_businesssegment_mtom(self, businesssegment_obj, action, user_id):
        if action == 'update':
            try:
                mb_data = MasterBusinessSegment.objects.using(self._current_app_schema()).get(
                    code=businesssegment_obj.get_buscode(), entity_id=self._entity_id())
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).filter(
                    code=businesssegment_obj.get_code(), entity_id=self._entity_id()).update(
                    no=businesssegment_obj.get_no(),
                    name=businesssegment_obj.get_name(),
                    status=businesssegment_obj.get_status(),
                    code=businesssegment_obj.get_code(),
                    remarks=businesssegment_obj.get_remarks(),
                    description=businesssegment_obj.get_description(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).get(
                    code=businesssegment_obj.get_code(), entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action == 'create':
            try:
                mb_data = MasterBusinessSegment.objects.using(self._current_app_schema()).get(
                    code=businesssegment_obj.get_buscode(), entity_id=self._entity_id())
                businesssegment = BusinessSegment.objects.using(self._current_app_schema()).create(
                    masterbussinesssegment=mb_data,
                    no=businesssegment_obj.get_no(),
                    name=businesssegment_obj.get_name(),
                    code=businesssegment_obj.get_code(),
                    remarks=businesssegment_obj.get_remarks(),
                    description=businesssegment_obj.get_description(),
                    created_by=user_id, entity_id=self._entity_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = BusinessSegmentResponse()
        data_obj.set_id(businesssegment.id)
        data_obj.set_code(businesssegment.code)
        data_obj.set_no(businesssegment.no)
        data_obj.set_name(businesssegment.name)
        data_obj.set_remarks(businesssegment.remarks)
        data_obj.set_description(businesssegment.description)
        return data_obj

    def fetch_cc(self, query):
        query = query
        cc1 = CostCentre.objects.using(self._current_app_schema()).filter(code=query, status=1,
                                                                          entity_id=self._entity_id())
        if len(cc1) != 0:
            cc = cc1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        cc_data = {"id": cc.id, "code": cc.code, "name": cc.name}
        cc_dic = json.dumps(cc_data, indent=4)
        return cc_data

    def fetch_cclist(request, cc_ids):
        # cc_ids = json.loads(request.body)
        cc_id2 = cc_ids.get('cc_code')
        obj = CostCentre.objects.using(request._current_app_schema()).filter(code__in=cc_id2,
                                                                             entity_id=request._entity_id()).values(
            'id', 'name', 'code')
        cc_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            cc_list_data.append(data)
        return cc_list_data.get()

    def fetch_bs(self, query):
        query = query
        bs1 = BusinessSegment.objects.using(self._current_app_schema()).filter(code=query, entity_id=self._entity_id())
        if len(bs1) != 0:
            bs = bs1[0]
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
        bs_data = {"id": bs.id, "code": bs.code, "name": bs.name}
        bs_dic = json.dumps(bs_data, indent=4)
        return bs_data

    def fetch_bslist(request, bs_ids):
        # bs_ids = json.loads(request.body)
        bs_id2 = bs_ids.get('bs_code')
        obj = BusinessSegment.objects.using(request._current_app_schema()).filter(code__in=bs_id2,
                                                                                  entity_id=request._entity_id()).values(
            'id', 'name', 'code')
        bs_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name'], "code": i['code']}
            bs_list_data.append(data)
        return bs_list_data.get()

    def mastersegmentname_get(self, request, vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        masterbusinesssegment_data = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
               vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        masterbsname_list = NWisefinList()
        list_data = len(masterbusinesssegment_data)
        if list_data <= 0:
            vpage = NWisefinPaginator(masterbusinesssegment_data, vys_page.get_index(), 10)
            masterbsname_list.set_pagination(vpage)
            return masterbsname_list
        else:
            for i in masterbusinesssegment_data:
                # print(i)
                response = BusinessSegmentResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                masterbsname_list.append(response)
            vpage = NWisefinPaginator(masterbusinesssegment_data, vys_page.get_index(), 10)
            masterbsname_list.set_pagination(vpage)
            return masterbsname_list

    def bs_name_get(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        businesssegment_data = BusinessSegment.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
                                     vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        bsname_list = NWisefinList()
        list_data = len(businesssegment_data)
        if list_data <= 0:
            vpage = NWisefinPaginator(businesssegment_data, vys_page.get_index(), 10)
            bsname_list.set_pagination(vpage)
            return bsname_list
        else:
            for i in businesssegment_data:
                # print(i)
                response = BusinessSegmentResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                bsname_list.append(response)
            vpage = NWisefinPaginator(businesssegment_data, vys_page.get_index(), 10)
            bsname_list.set_pagination(vpage)
            return bsname_list


    def bs_activate_inactivate(self,request,bs_obj):
        # print(prdct_obj.status)
        if(int(bs_obj.status)==0):

            bs_data = BusinessSegment.objects.using(self._current_app_schema()).filter(id=bs_obj.id).update(
                    status=1)
        else:
            bs_data = BusinessSegment.objects.using(self._current_app_schema()).filter(id=bs_obj.id).update(
                    status=0)
        bs_var = BusinessSegment.objects.using(self._current_app_schema()).get(id=bs_obj.id)
        data = BusinessSegmentResponse()
        data.set_status(bs_var.status)
        status=bs_var.status
        # print(status)
        data.set_id(bs_var.id)
        # return data

        if status==1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data

    def cc_activate_inactivate(self, request, cc_obj):

        if (int(cc_obj.status) == 0):

            cc_data = CostCentre.objects.using(self._current_app_schema()).filter(id=cc_obj.id, entity_id=self._entity_id()).update(
                status=1)
        else:
            cc_data = CostCentre.objects.using(self._current_app_schema()).filter(id=cc_obj.id, entity_id=self._entity_id()).update(
                status=0)
        cc_var = CostCentre.objects.using(self._current_app_schema()).get(id=cc_obj.id)
        data = CostCentreResponse()
        data.set_status(cc_var.status)
        status = cc_var.status
        # print(status)
        data.set_id(cc_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data

        # return data
    def create_masterbusinesssegment(self, businesssegment_obj, user_id):
        if not businesssegment_obj.get_id() is None:
            try:
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Update Started')
                masterbusinesssegment_data = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(id=businesssegment_obj.get_id(), entity_id=self._entity_id()).update(
                                                    no=businesssegment_obj.get_no(),
                                                    sector_id=businesssegment_obj.get_sector_id(),
                                                    name=businesssegment_obj.get_name(),
                                                    remarks=businesssegment_obj.get_remarks(),
                                                    description=businesssegment_obj.get_description(),
                                                    updated_by=user_id,
                                                    updated_date=timezone.now())
                masterbusinesssegment = MasterBusinessSegment.objects.get(id=businesssegment_obj.get_id())
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Update Success' + str(masterbusinesssegment_data))
            except IntegrityError as error:
                logger.error('ERROR_MasterBusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            except:
                logger.error('ERROR_MasterBusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:

            try:
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Creation Started')
                masterbusinesssegment = MasterBusinessSegment.objects.using(self._current_app_schema()).create(
                                                                no=businesssegment_obj.get_no(),
                                                                sector_id=businesssegment_obj.get_sector_id(),
                                                                name=businesssegment_obj.get_name(),
                                                                remarks=businesssegment_obj.get_remarks(),
                                                                description=businesssegment_obj.get_description(),
                                                                created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(
                        code__icontains='BS').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "BS" + str(new_rnsl).zfill(2)
                masterbusinesssegment.code = code
                masterbusinesssegment.save()
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Creation Success' + str(masterbusinesssegment))

            except IntegrityError as error:
                logger.error('ERROR_MasterBusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_MasterBusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = MasterBusinessSegmentResponse()
        data_obj.set_id(masterbusinesssegment.id)
        data_obj.set_code(masterbusinesssegment.code)
        data_obj.set_sector_id(masterbusinesssegment.sector_id)
        data_obj.set_no(masterbusinesssegment.no)
        data_obj.set_name(masterbusinesssegment.name)
        data_obj.set_remarks(masterbusinesssegment.remarks)
        data_obj.set_description(masterbusinesssegment.description)
        return data_obj

    def apsectorname_get(self,request,vys_page):
        condition = Q(status=1)
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        Sector_data = Apsector.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'description')[
                               vys_page.get_offset():vys_page.get_query_limit()]
        # print(data)
        sector_list = NWisefinList()
        list_data = len(Sector_data)
        if list_data <= 0:
            vpage = NWisefinPaginator(Sector_data, vys_page.get_index(), 10)
            sector_list.set_pagination(vpage)
            return sector_list
        else:
            for i in Sector_data:
                # print(i)
                response = BusinessSegmentResponse()
                response.set_id(i['id'])
                response.set_description(i['description'])
                response.set_name(i['name'])
                sector_list.append(response)
            vpage = NWisefinPaginator(Sector_data, vys_page.get_index(), 10)
            sector_list.set_pagination(vpage)
            return sector_list

    def bs_data_frame(self):
        costcentre = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(status=1,
                                                                              entity_id=self._entity_id()).values("id","name")
        return costcentre
