from hrmsservice.util.hrmsutil import DayUtil
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from hrmsservice.models import WorkWeek, WorkShift, PayDay, PayrollConfigStatus
from hrmsservice.data.response.payrollresponse import WorkWeekResponse, WorkShiftResponse, PayDayResponse, \
    PayrollConfigStatusResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessMessage, SuccessStatus, NWisefinSuccess
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.data.response.nwisefinlist import NWisefinList



# class DefaultRecordService(NWisefinThread):
#     def __init__(self, scope):
#         super().__init__(scope)
#         self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
#
#     def check_work_week(self):
#         work_week = WorkWeek.objects.using(self._current_app_schema()).all().values_list('day', flat=True)
#         work_week = list(work_week)
#         days_list = DayUtil.ID_ARR
#         if set(work_week) == set(days_list):
#             return True
#         else:
#             return False



class WorkWeekService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_workweek(self,Body_data,user_id):
        var = DayUtil()
        arr = []
        for i in Body_data['data']:
            arr.append(i['day'])
        insert_arr = []
        if arr == var.ID_ARR:
            obj = WorkWeek.objects.all()
            if len(obj)>0:
                try:
                  for i in Body_data['data']:
                      tab=WorkWeek.objects.filter(day=i['day']).update(is_working=i['is_weekend'])
                  error_obj = MessageResponse()
                  error_obj.set_status(StatusType.SUCCESS)
                  error_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                  return error_obj
                except:
                    error_obj = MessageResponse()
                    error_obj.set_status(StatusType.FAILED)
                    error_obj.set_message(ErrorDescription.INVALID_ID)
                    return error_obj
            else:
               try:
                    for i in Body_data['data']:
                        obj=WorkWeek(day=i['day'],is_working=i['is_weekend'],created_by=user_id)
                        insert_arr.append(obj)
                    WorkWeek.objects.bulk_create(insert_arr)
                    error_obj = MessageResponse()
                    error_obj.set_status(SuccessStatus.SUCCESS)
                    error_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return error_obj
               except:
                   error_obj = MessageResponse()
                   error_obj.set_status(StatusType.FAILED)
                   error_obj.set_message(ErrorDescription.INVALID_DATA)
                   return error_obj
        else:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj


    def summary_workweek(self):
        try:
            work =WorkWeek.objects.using(self._current_app_schema()).all()
            work_obj = NWisefinList()
            for i in work:
                resp=WorkWeekResponse()
                resp.set_day(i.day)
                resp.set_is_working(i.is_working)
                resp.set_created_by(i.created_by)
                work_obj.append(resp)
            return work_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj


    # def fetch_workweek(self,id):
    #     try:
    #         work = WorkWeek.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id())
    #         print(type(work))
    #         resp = WorkWeekResponse()
    #         resp.set_day(work.day)
    #         resp.set_is_working(work.is_working)
    #         resp.set_created_by(work.created_by)
    #         resp.set_created_date(work.created_date)
    #         return resp
    #
    #     except:
    #         error_obj = MessageResponse()
    #         error_obj.set_status(StatusType.FAILED)
    #         error_obj.set_message(ErrorDescription.INVALID_DATA)
    #         return error_obj



    # def del_workweek(self, id):
    #     try:
    #         work = WorkWeek.objects.filter(id=id,entity=self._entity_id()).delete()
    #         print(work)
    #         print(type(work))
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #         return success_obj
    #     except:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ID)
    #         return error_obj

    # def srch_workweek(self, day):
    #     try:
    #         work = WorkWeek.objects.filter(day__icontains=day)
    #         work_data = WorkWeekResponse()
    #         work_data.set_id(work.id)
    #         work_data.set_day(work.day)
    #         work_data.set_is_working(work.is_working)
    #         work_data.set_created_by(work.created_by)
    #         work_data.set_created_date(work.created_date)
    #     except:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_ID)
    #         error_obj.set_description(ErrorDescription.INVALID_ID)
    #         return error_obj




class WorkShiftService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_WorkShift(self,work_request,user_id):
        update = 0
        if work_request.get_id() is not None:
            update = 1
            # try:
            start_time = work_request.get_start_time()
            shiftstart = self.checktime(start_time)
            end_time = work_request.get_end_time()
            shiftend = self.checktime(end_time)
            if shiftstart & shiftend:
                work = WorkShift.objects.using(self._current_app_schema()).filter(id=work_request.get_id(),
                                                                                 entity_id=self._entity_id()).update(
                                                                         entity_id=self._entity_id(),
                                                                        shift_name=work_request.get_shift_name(),
                                                                        start_time=work_request.get_start_time(),
                                                                         end_time = work_request.get_end_time(),
                                                                         updated_by = user_id)


                work = WorkShift.objects.using(self._current_app_schema()).get(id=work_request.get_id(), entity_id=self._entity_id())
            else:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj

        else:
            # try:
                start_time = work_request.get_start_time()
                shiftstart = self.checktime(start_time)
                end_time = work_request.get_end_time()
                shiftend = self.checktime(end_time)
                if shiftstart & shiftend:
                    work = WorkShift.objects.using(self._current_app_schema()).create(
                                                    entity_id=self._entity_id(),
                                                    shift_name=work_request.get_shift_name(),
                                                    start_time=work_request.get_start_time (),
                                                     end_time = work_request.get_end_time(),
                                                     created_by = user_id)
                else:
                    error_obj = MessageResponse()
                    error_obj.set_status(StatusType.FAILED)
                    error_obj.set_message(ErrorDescription.INVALID_DATA)
                    return error_obj
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj
    def checktime(self,time):
        num = str(time).split('.')
        integer = int(num[0])
        decimal = int(num[1])
        if (integer < 24) & (decimal < 60):
            return True
        else:
            return False

    def summary_WorkShift(self):
        try:
            work =WorkShift.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)
            work_obj = NWisefinList()
            for i in work:
                resp=WorkShiftResponse()
                resp.set_id(i.id)
                resp.set_shift_name(i.shift_name)
                resp.set_start_time(i.start_time)
                resp.set_end_time(i.end_time)
                resp.set_created_by(i.created_by)
                work_obj.append(resp)
            return work_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def hrms_shiftmap_summary(self, shift_arr):
        work_shift = WorkShift.objects.using(self._current_app_schema()).filter(id__in=shift_arr)
        work_obj = []
        for i in work_shift:
            resp = WorkShiftResponse()
            resp.set_id(i.id)
            resp.set_shift_name(i.shift_name)
            resp.set_start_time(i.start_time)
            resp.set_end_time(i.end_time)
            work_obj.append(resp)
        return work_obj


    def fetch_WorkShift(self,id):
        try:
            work = WorkShift.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            resp = WorkShiftResponse()
            resp.set_id(work.id)
            resp.set_shift_name(work.shift_name)
            resp.set_start_time(work.start_time)
            resp.set_end_time(work.end_time)
            resp.set_created_by(work.created_by)
            return resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def del_WorkShift(self,id):
        try:
            work = WorkShift.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).delete()

            error_obj = MessageResponse()
            error_obj.set_status(StatusType.SUCCESS)
            error_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return error_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj



class PayDayService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
    def create_payday(self,pay_obj,user_id):
        obj=PayDay.objects.all()


        if len(obj)>0:
            try:
                update_data=PayDay.objects.using(self._current_app_schema()).filter(id=obj[0].id).update(
                                                                        is_month_last_day=pay_obj.get_is_month_last_day(),
                                                                        is_month_first_day=pay_obj.get_is_month_first_day(),
                                                                        day=pay_obj.get_day())
                update_data=PayDay.objects.using(self._current_app_schema()).get(id=obj[0].id)
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.SUCCESS)
                error_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj
        else:
            try:
                 update=PayDay.objects.using(self._current_app_schema()).create( entity_id=self._entity_id(),
                                                                        is_month_last_day=pay_obj.get_is_month_last_day(),
                                                                        is_month_first_day=pay_obj.get_is_month_first_day(),
                                                                        day=pay_obj.get_day(),
                                                                        created_by=user_id)
                 error_obj = MessageResponse()
                 error_obj.set_status(StatusType.SUCCESS)
                 error_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                 return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj



    def fetch_payday(self,id):
        try:
            pay_day=PayDay.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            resp=PayDayResponse()
            resp.set_id(pay_day.id)
            resp.set_is_month_last_day(pay_day.is_month_last_day)
            resp.set_is_month_first_day(pay_day.is_month_first_day)
            resp.set_day(pay_day.day)
            return resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID)
            return error_obj






class PayrollConfigStatusService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
    def create_payrollconfigstatus(self,roll_obj,user_id):
        update=0
        if roll_obj.get_id() is not None:
            update=1
            try:
                update_data=PayrollConfigStatus.objects.using(self._current_app_schema()).filter(id=roll_obj.get_id(),
                                                                                 entity_id=self._entity_id()).update(
                                                                         entity_id=self._entity_id(),
                                                                        is_work_week_configured=roll_obj.get_is_work_week_configured(),
                                                                        is_shift_configured=roll_obj.get_is_shift_configured(),
                                                                        is_pay_day_configured=roll_obj.get_is_pay_day_configured(),
                                                                        is_pay_component_configured=roll_obj.get_is_pay_component_configured())

                update_data=PayrollConfigStatus.objects.using(self._current_app_schema()).get(id=roll_obj.get_id())
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj
        else:
            try:
                update=PayrollConfigStatus.objects.using(self._current_app_schema()).create( entity_id=self._entity_id(),
                                                                        is_work_week_configured=roll_obj.get_is_work_week_configured(),
                                                                        is_shift_configured=roll_obj.get_is_shift_configured(),
                                                                        is_pay_day_configured=roll_obj.get_is_pay_day_configured(),
                                                                        is_pay_component_configured=roll_obj.get_is_pay_component_configured())

            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)

                return error_obj
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj




    def fetch_payrollconfigstatus(self,id):
        try:
            pay_day=PayrollConfigStatus.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            resp=PayrollConfigStatusResponse()
            resp.set_id(pay_day.id)
            resp.set_is_work_week_configured(pay_day.is_work_week_configured)
            resp.set_is_shift_configured(pay_day.is_shift_configured)
            resp.set_is_pay_day_configured(pay_day.is_pay_day_configured)
            resp.set_is_pay_component_configured(pay_day.is_pay_component_configured)
            return resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID)
            return error_obj







