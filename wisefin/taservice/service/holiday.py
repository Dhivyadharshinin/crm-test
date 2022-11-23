import json
from django.db import IntegrityError
from taservice.data.request.holiday import HolidayRequest
from taservice.data.response.holiday import HolidayResponse
from taservice.models import Holiday
from utilityservice.data.response.nwisefinerror import NWisefinError 
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from datetime import datetime
import pytz
from taservice.util.ta_util import Status
# from utilityservice.service.dbutil import DataBase

# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d')
from utilityservice.service.applicationconstants import ApplicationNamespace

today=datetime.today()

from utilityservice.service.threadlocal import NWisefinThread

class HolidayData(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def create_holiday(self, request_obj, employee_id):
        for dtl in request_obj:
            data = HolidayRequest(dtl)
            if data.get_id() is not None:
                try:
                    holidaydata = Holiday.objects.using(self._current_app_schema()).filter(id=data.get_id(),entity_id=self._entity_id()).update(date=data.get_date(),
                                                                                      holidayname=data.get_holidayname(),
                                                                                      state=data.get_state(),
                                                                                      status=1,
                                                                                      entity=data.get_entity(),
                                                                                      updated_by=employee_id,
                                                                                      updated_date=today,entity_id=self._entity_id())

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
                # except Holiday.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                # return success_obj
            else:
                try:
                    holidaydata=Holiday.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),date=data.get_date(),holidayname=data.get_holidayname(),state=data.get_state())
                    if len(holidaydata)==0:
                        holidaydata = Holiday.objects.using(self._current_app_schema()).create(
                                            date=data.get_date(),
                                            holidayname=data.get_holidayname(),
                                            state=data.get_state(),
                                            entity=data.get_entity(),
                                            status=1,
                                            created_by=employee_id,entity_id=self._entity_id())
                    else:
                        holidaydata = Holiday.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), date=data.get_date(), holidayname=data.get_holidayname(),
                            state=data.get_state()).update(date=data.get_date(),holidayname=data.get_holidayname(),state=data.get_state(),
                                                                                      status=1,
                                                                                      entity=data.get_entity(),
                                                                                      updated_by=employee_id,
                                                                                      updated_date=today,entity_id=self._entity_id())
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj
    def get_holiday(self,vys_page,date):
        holiday = Holiday.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1,date__year=date).all()[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()
        # arr = []
        for i in holiday:
            req_data = HolidayResponse()
            req_data.set_id(i.id)
            req_data.set_date(i.date)
            req_data.set_holidayname(i.holidayname)
            req_data.set_state(i.state)
            req_data.set_entity(i.entity)
            req_data.set_status(i.status)
            resp_list.append(req_data)
        vpage = NWisefinPaginator(holiday, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list
    def delete_holiday(self,delete_id):
        try:
            holiday = Holiday.objects.using(self._current_app_schema()).filter(id=delete_id,entity_id=self._entity_id()).update(status=0)
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj
    def get_holiday_id(self,fetchid):
        holiday = Holiday.objects.using(self._current_app_schema()).get(id=fetchid,entity_id=self._entity_id())
        req_data = HolidayResponse()
        req_data.set_id(holiday.id)
        req_data.set_date(holiday.date)
        req_data.set_holidayname(holiday.holidayname)
        req_data.set_state(holiday.state)
        req_data.set_entity(holiday.entity)
        req_data.set_status(holiday.status)
        return req_data