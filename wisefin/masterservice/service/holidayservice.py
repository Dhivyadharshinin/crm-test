import json
from masterservice.data.response.holidayresponse import HolidayResponse
from masterservice.models import Holidaymst ,Holiday
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription

from masterservice.service.addressservice import AddressService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.util.masterutil import ModifyStatus
from django.db.models import Q
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from datetime import datetime

class HolidayService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    # def create_holiday(self, foliodtls_obj, emp_id, state_id, validfrom, validto):
    #     if not foliodtls_obj.get_id() is None:
    #         # try:
    #         holiday = Holidaymst.objects.using(self._current_app_schema()).filter(id=foliodtls_obj.get_id(),
    #                                                                               entity_id=self._entity_id()).update(
    #             holidayname=foliodtls_obj.get_holidayname(),
    #             state=foliodtls_obj.get_state(),
    #             date=foliodtls_obj.get_date(),
    #             validfrom=validfrom,
    #             validto=validto,
    #
    #         )
    #         holiday = Holidaymst.objects.using(self._current_app_schema()).get(id=foliodtls_obj.get_id(),
    #                                                                            entity_id=self._entity_id())
    #
    #
    #     else:
    #         # try:
    #         holiday = Holidaymst.objects.using(self._current_app_schema()).create(
    #             holidayname=foliodtls_obj.get_holidayname(),
    #             state_id=foliodtls_obj.get_state(),
    #             date=foliodtls_obj.get_date(),
    #             validfrom=validfrom,
    #             validto=validto, entity_id=self._entity_id()
    #             )
    #
    #     holiday_data = HolidayResponse()
    #     holiday_data.set_id(holiday.id)
    #     holiday_data.set_holidayname(holiday.holidayname)
    #     holiday_data.set_state(holiday.state_id)
    #     holiday_data.set_validfrom(holiday.validfrom)
    #     holiday_data.set_validto(holiday.validto)
    #     holiday_data.set_date(holiday.date)
    #     return holiday_data
    #
    # def holiday_list(self, vys_page):
    #     holiday_list = Holidaymst.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
    #     list_length = len(holiday_list)
    #     holiday_list_data = NWisefinList()
    #     if list_length > 0:
    #         for holiday in holiday_list:
    #             holiday_data = HolidayResponse()
    #             holiday_data.set_id(holiday.id)
    #             holiday_data.set_state(holiday.state)
    #             holiday_data.set_holidayname(holiday.holidayname)
    #             holiday_data.set_validfrom(holiday.validfrom)
    #             holiday_data.set_validto(holiday.validto)
    #             holiday_data.set_date(holiday.date)
    #             holiday_list_data.append(holiday_data)
    #             vpage = NWisefinPaginator(holiday_list, vys_page.get_index(), 10)
    #             holiday_list_data.set_pagination(vpage)
    #     return holiday_list_data
    #
    # def bulk_insert_holiday(self, holiday_obj, emp_id, state_id, validfrom, validto):
    #     arr = []
    #     for obj in holiday_obj:
    #         data = Holidaymst(holidayname=obj.get_holidayname(), state_id=obj.get_state(),
    #                           date=obj.get_date(),
    #                           validfrom=validfrom,
    #                           validto=validto, created_by=emp_id)
    #         arr.append(data)
    #     Holidaymst.objects.using(self._current_app_schema()).bulk_create(arr)
    #
    #     return


    def create_holiday(self,data,emp_id):
        year = data['year']
        state = data['state']
        arr=data['arr']

        for i in arr:
            h_date=i['date']

            date_time_obj = datetime.strptime(h_date, '%Y-%m-%d').year
            if int(year) != date_time_obj:
                error_obj = MessageResponse()
                error_obj.set_status(ErrorMessage.INVALID_DATA)
                return error_obj

        obj=Holidaymst.objects.using(self._current_app_schema()).filter(year=year,state_id=state,status=ModifyStatus.create)

        if len(obj) == 0 :
            obj = Holidaymst.objects.using(self._current_app_schema()).create(year=year, state_id=state, created_by=emp_id,entity_id=self._entity_id())
        else:
            obj=obj[0]
        h_arr=[]
        for m in arr :
            h_date=m['date']
            h_name = m['name']
            h_obj=Holiday(name=h_name,holiday_date=h_date,holiday_mst_id = obj.id,entity_id=self._entity_id())
            h_arr.append(h_obj)


        Holiday.objects.using(self._current_app_schema()).bulk_create(h_arr)

        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def update_holiday(self,data,emp_id):

        arr=data['arr']
        for m in arr :
            h_date=m['date']
            h_name = m['name']
            id =m['id']
            Holiday.objects.using(self._current_app_schema()).filter(id=id).update(name=h_name,holiday_date=h_date,updated_by=emp_id,updated_date=now())

        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def holiday_list(self, state,year):
        holiday_list_data = NWisefinList()
        cond = Q(status=ModifyStatus.create,entity_id=self._entity_id())
        if state !=None :
            cond &= Q(holiday_mst__state_id=state)
        if  year != None:
            cond &= Q(holiday_mst__year=year)

        holiday_list = Holiday.objects.using(self._current_app_schema()).filter(cond)
        for holiday in holiday_list:
            holiday_data = HolidayResponse()
            holiday_data.set_id(holiday.id)
            holiday_data.set_holidayname(holiday.name)
            holiday_data.set_date(holiday.holiday_date)
            holiday_list_data.append(holiday_data)

        return holiday_list_data

    def holidaysummary(self, request,vys_page):
        query = request.GET.get('query', None)
        year = request.GET.get('year', None)
        condition = Q(status=ModifyStatus.create)
        if (year != '') and (year != None):
            year = int(year)
            condition = Q(year=year)
        elif (query != '') and (query != None):
            pass
        else:
            year= datetime.now().year
            condition = Q(year=year)

        if (query != '') and (query != None):
            condition &= Q(state_id__name__icontains=query)
        holiday_list = NWisefinList()
        holiday_data = Holidaymst.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        for holiday in holiday_data:
            data = HolidayResponse()
            data.set_id(holiday.id)
            data.set_state(holiday.state)
            data.set_year(holiday.year)
            holiday_list.append(data)
        paginator = NWisefinPaginator(holiday_data, vys_page.get_index(), 10)
        holiday_list.set_pagination(paginator)
        return holiday_list
