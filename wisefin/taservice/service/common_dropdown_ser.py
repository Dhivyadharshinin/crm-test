from taservice.data.response.onbehalfresponse import Ccbs_resp
from taservice.models import Common_dropdown, Common_dropdown_details, Ccbs, TourAdvance, TourRequest
from django.utils import timezone
from django.db import IntegrityError
# from userservice.service.ccbsservice import CostCentreService, BusinessSegmentService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist  import NWisefinList
from django.db.models import Q
from taservice.data.request.cd_req import Cd_req, Cd_del_req
from taservice.data.response.cd_res import Cd_res
from taservice.util.ta_util import Filterstatus, Status, Validation
# from utilityservice.service.dbutil import DataBase
from utilityservice.service.ta_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
#test

class Common_dropdown_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_common_dropdown(self,request_obj,employee_id):
        for dtl in request_obj['data']:
            data = Cd_req(dtl)
            if data.id is not None:
                try:
                    com=Common_dropdown.objects.using(self._current_app_schema()).filter(id=data.id,entity_id=self._entity_id()).update(
                            name=data.get_name(),entity=data.get_entity(),
                            code=data.get_code(),
                            updated_by=employee_id,status=data.status,
                            updated_date=timezone.now(),entity_id=self._entity_id())


                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Common_dropdown.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj


            else:
                try:
                    com=Common_dropdown.objects.using(self._current_app_schema()).create(
                                name=data.get_name(),entity=data.get_entity(),status=data.status,
                                code=data.get_code(),created_by=employee_id,entity_id=self._entity_id())



                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
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

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def get_common_dropdown(self,vys_page):
        list=Common_dropdown.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)[
                 vys_page.get_offset():vys_page.get_query_limit()]
        arr=NWisefinList()
        for com_id in list:
            com_res=Cd_res()
            com_res.set_id(com_id.id)
            com_res.set_name(com_id.name)
            com_res.set_code(com_id.code)
            com_res.set_status(com_id.status)
            com_res.set_entity(com_id.entity)
            com_res.set_entity_id(com_id.entity_id)
            arr.append(com_res)
        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        arr.set_pagination(vpage)
        return arr


    def fetch_dropdown(self,fetch_id):
        condition = Q(status=Filterstatus.one,id=fetch_id,entity_id=self._entity_id())

        com_id = Common_dropdown.objects.using(self._current_app_schema()).get(condition)
        com_res = Cd_res()
        com_res.set_id(com_id.id)
        com_res.set_name(com_id.name)
        com_res.set_code(com_id.code)
        com_res.set_status(com_id.status)
        com_res.set_entity(com_id.entity)
        return com_res

    def dropdown_code_search(self, code, vys_page, query):
        condition = Q(status=Filterstatus.one, code=code, entity_id=self._entity_id())

        list = Common_dropdown.objects.using(self._current_app_schema()).get(condition)
        common_id = list.id
        condition1 = Q(common_drop_down_id=common_id, entity_id=self._entity_id(), status=1)
        if query is not None:
            condition1 &= Q(name__icontains=query)
        list1 = Common_dropdown_details.objects.using(self._current_app_schema()).filter(condition1
                                                                                         )[

                vys_page.get_offset(): vys_page.get_query_limit()]
        arr = NWisefinList()
        for detail in list1:
            com_res = Cd_res()
            com_res.set_id(detail.id)
            com_res.set_name(detail.name)
            com_res.set_value(detail.value)
            com_res.set_status(detail.status)
            com_res.set_entity(detail.entity)
            com_res.set_common_id(detail.common_drop_down_id)
            arr.append(com_res)
        vpage = NWisefinPaginator(list1, vys_page.get_index(), 10)
        arr.set_pagination(vpage)
        return arr

    def dropdown_code_get(self, code):
        condition = Q(status=Filterstatus.one, code=code, entity_id=self._entity_id())

        list = Common_dropdown.objects.using(self._current_app_schema()).get(condition)
        common_id = list.id
        list = Common_dropdown_details.objects.using(self._current_app_schema()).filter(
            common_drop_down_id=common_id, entity_id=self._entity_id(), status=1)
        arr = []
        for detail in list:
            com_res = Cd_res()
            com_res.set_id(detail.id)
            com_res.set_name(detail.name)
            com_res.set_value(detail.value)
            com_res.set_status(detail.status)
            com_res.set_entity(detail.entity)
            com_res.set_common_id(detail.common_drop_down_id)
            arr.append(com_res)
        return arr

    def delete_dropdown(self,id):
        try:
            adr = Common_dropdown.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).delete()
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        # except Common_dropdown.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj



    def insert_cd_details(self,request_obj,employee_id):
        for dtl in request_obj['data']:
            data = Cd_del_req(dtl)
            if data.id is not None:
                try:
                    com=Common_dropdown_details.objects.using(self._current_app_schema()).filter(id=data.id,entity_id=self._entity_id()).update(
                            name=data.get_name(),common_drop_down_id=data.get_common_drop_down_id(),
                            value=data.get_value(),entity=data.get_entity(),
                            updated_by=employee_id,status=data.status,
                            updated_date=timezone.now())


                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Common_dropdown_details.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj


            else:
                try:
                    com=Common_dropdown_details.objects.using(self._current_app_schema()).create(
                                name=data.get_name(),common_drop_down_id=data.get_common_drop_down_id(),
                                value=data.get_value(),entity=data.get_entity(),status=data.status,
                                created_by=employee_id,entity_id=self._entity_id())



                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
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

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def get_cd_details(self,vys_page):
        list=Common_dropdown_details.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)[
                 vys_page.get_offset():vys_page.get_query_limit()]
        arr=NWisefinList()
        for det_id in list:
            com_res=Cd_res()
            com_res.set_id(det_id.id)
            com_res.set_name(det_id.name)
            com_res.set_common_drop_down(det_id.common_drop_down)
            com_res.set_common_drop_down_id(det_id.common_drop_down.id)
            com_res.set_value(det_id.value)
            com_res.set_status(det_id.status)
            com_res.set_entity(det_id.entity)
            com_res.set_entity_id(det_id.entity_id)
            arr.append(com_res)

        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        arr.set_pagination(vpage)
        return arr


    def fetch_cd_details(self,fetch_id):
        condition = Q(status=Filterstatus.one,id=fetch_id,entity_id=self._entity_id())

        det_id = Common_dropdown_details.objects.using(self._current_app_schema()).get(condition)
        com_res = Cd_res()
        com_res.set_id(det_id.id)
        com_res.set_name(det_id.name)
        com_res.set_common_drop_down_id(det_id.common_drop_down)
        com_res.set_value(det_id.value)
        com_res.set_status(det_id.status)
        com_res.set_entity(det_id.entity)
        return com_res

    def fetch_cd_details_header(self,fetch_id):
        data = Common_dropdown_details.objects.using(self._current_app_schema()).filter(status=Filterstatus.one,common_drop_down_id=fetch_id,entity_id=self._entity_id())
        arr = NWisefinList()
        for det_id in data:
            com_res = Cd_res()
            com_res.set_id(det_id.id)
            com_res.set_name(det_id.name)
            com_res.set_common_drop_down_id(det_id.common_drop_down_id)
            com_res.set_value(det_id.value)
            com_res.set_status(det_id.status)
            com_res.set_entity(det_id.entity)
            com_res.set_entity_id(det_id.entity_id)
            arr.append(com_res)
        return arr


    def delete_cd_details(self,id):
        try:
            adr = Common_dropdown_details.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).delete()
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        # except Common_dropdown_details.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj



    def ccbs_get(self,tour,type,request,requestid):
        if requestid==0:
            list = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=tour,ccbs_type=type,status=1,entity_id=self._entity_id())
        else:
            list = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=tour, ccbs_type=type, status=1,requestid=requestid,entity_id=self._entity_id())
        arr = []
        for data in list:
            response = Ccbs_resp()
            response.set_id(data.id)
            response.set_tourgid(tour)
            response.set_requestid(data.requestid)
            response.set_ccid(data.ccid)
            response.set_bsid(data.bsid)
            service=ApiService(self._scope())
            # cc_service=CostCentreService()
            # bs_service=BusinessSegmentService()
            cc_data=service.get_cc_details(data.ccid,request)
            bs_data=service.get_bs_details(data.bsid,request)
            response.set_cc_data(cc_data)
            response.set_bs_data(bs_data)
            response.set_percentage(data.percentage)
            response.set_amount(data.amount)
            response.set_ccbs_type(type)
            response.set_status(data.status)
            response.set_ccbs_edit_status(0)
            adv_status=TourAdvance.objects.using(self._current_app_schema()).filter(id=data.requestid,entity_id=self._entity_id()).last()
            if adv_status is not None:
                if adv_status.status==0:
                    response.set_ccbs_edit_status(1)

            arr.append(response)
        return arr


    def delete_ccbs(self,id,employee_id):
        ccbs_data=Ccbs.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
        service=Validation(self._scope())
        permission = service.tour_maker_check(ccbs_data.tour_id, employee_id)
        if permission is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        req_id=ccbs_data.requestid
        if req_id==0:
            clm_status=TourRequest.objects.using(self._current_app_schema()).get(id=ccbs_data.tour_id,entity_id=self._entity_id()).claim_status
            # clm_status_ck=[Status.REQUESTED,Status.APPROVED,Status.REJECTED]
            if clm_status==Status.DEFAULT or clm_status==Status.APPROVED or clm_status==Status.REJECTED:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.CANT_EDIT)
                return error_obj

        else:
            adv_details=TourAdvance.objects.using(self._current_app_schema()).get(id=req_id,entity_id=self._entity_id())
            if adv_details.status!=0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.NOT_PENDING)
                return error_obj


        Ccbs.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(status=0,entity_id=self._entity_id())
        msg_obj = NWisefinSuccess()
        msg_obj.set_status(SuccessStatus.SUCCESS)
        msg_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return msg_obj