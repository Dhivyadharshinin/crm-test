from attendanceservice.models.attendancemodels import LeaveRequest
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from attendanceservice.data.response.leaveresponse import LeaveResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from attendanceservice.service.leaveapproveservice import LeaveApproveService
from utilityservice.service.attendanceapiservice import AttendanceAPIService
from masterservice.service.leaveattendanceservice import LeaveTypeService
from attendanceservice.util.attendanceutil import LeaveApproveType, get_leave_approve_type,ActiveStatus
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from attendanceservice.service.attendancedocumentservice import AttendanceDocumentService
from nwisefin.settings import logger
from django.db import IntegrityError
import datetime
from django.db.models import Q
from hrmsservice.models.hrmsmodels import EmployeeShiftMapping ,WorkWeek


class LeaveRequestService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    # 0007
    def create_leave_request(self, resp_obj, emp_id):
        # data = {"leave_type": resp_obj.get_leave_type(), "user_id": emp_id, "start_date": resp_obj.get_from_date(),
        #         "end_date": resp_obj.get_to_date(), 'ref_id': resp_obj.get_id()}
        # count_flag = self.leave_type_count(data)
        # if count_flag is False:
        #     error_obj = MessageResponse()
        #     error_obj.set_status(StatusType.FAILED)
        #     error_obj.set_message(ErrorDescription.ATTENDANCE_LIMIT_REACHED)
        #     return error_obj
        if resp_obj.get_id() is not None:
            try:
                update = LeaveRequest.objects.using(self._current_app_schema()).filter(
                    id=resp_obj.get_id(), entity_id=self._entity_id()).update(leave_type=resp_obj.get_leave_type(),
                                                                              from_date=resp_obj.get_from_date(),
                                                                              to_date=resp_obj.get_to_date(),
                                                                              total_days=resp_obj.get_total_days(),
                                                                              reason=resp_obj.get_reason(),
                                                                              updated_by=emp_id,
                                                                              updated_date=datetime.datetime.now())
                leave_data = LeaveRequest.objects.using(self._current_app_schema()).get(id=resp_obj.get_id())
                logger.info('leave request update status (' + str(update) + '), for id :' + str(leave_data.id))
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except LeaveRequest.DoesNotExist:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ATTENDANCE_ID)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                leave_data = LeaveRequest.objects.using(self._current_app_schema()
                                                        ).create(user_id=emp_id,
                                                                 leave_type=resp_obj.get_leave_type(),
                                                                 from_date=resp_obj.get_from_date(),
                                                                 to_date=resp_obj.get_to_date(),
                                                                 total_days=resp_obj.get_total_days(),
                                                                 reason=resp_obj.get_reason(),
                                                                 created_by=emp_id,
                                                                 created_date=datetime.datetime.now(),
                                                                 entity_id=self._entity_id())
                logger.info('leave request created for id : ' + str(leave_data.id))
            except IntegrityError as error:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        data = LeaveResponse()
        data.set_id(leave_data.id)
        return data


    def new_leave_req(self, resp_obj, emp_id):
        # else:
            api_serv=AttendanceAPIService(self._scope())
            shift_data = self.get_shift_data(emp_id)
            from_date = resp_obj.get_from_date()
            to_date = resp_obj.get_to_date()
            if shift_data == None:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message('Employee Shift mapping missing')
                return error_obj

            org_id=api_serv.get_employee_info(emp_id).org_id
            if org_id == None:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message('Employee ORG mapping missing')
                return error_obj

            working_data=self.get_weekend_day(org_id)
            date_calculation = self.working_hour_calculation(shift_data,working_data,from_date,to_date)

            leave_data = LeaveRequest.objects.using(self._current_app_schema()).create(user_id=emp_id,leave_type=resp_obj.get_leave_type(),from_date=resp_obj.get_from_date(), to_date=resp_obj.get_to_date(),total_days=resp_obj.get_total_days(),reason=resp_obj.get_reason(),created_by=emp_id,created_date=datetime.datetime.now(),
                                                                                       entity_id=self._entity_id())
            logger.info('leave request created for id : ' + str(leave_data.id))


    def get_shift_data(self,emp_id):
        shift_data=EmployeeShiftMapping.objects.using(self._current_app_schema()).filter(employee_id=emp_id,effective_to=None,status=ActiveStatus.Active)
        if len(shift_data)>0:
            return shift_data[0].shift
        else :
            return

    def get_working_day(self,org_id):
        working_days=WorkWeek.objects.using(self._current_app_schema()).filter(org_id=org_id,status=ActiveStatus.Active,is_working=True).values_list('day',flat=True)
        return working_days

    def get_weekend_day(self,org_id):
        working_days=WorkWeek.objects.using(self._current_app_schema()).filter(org_id=org_id,status=ActiveStatus.Active,is_working=False).values_list('day',flat=True)
        return working_days


    def working_hour_calculation(self,shift_data,working_days,start_date,end_date):

        leave_start = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        leave_end = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        total_leave =(leave_end-leave_start)
        total_leave_day=total_leave.days

        weekend=[]
        holiday=[]

        total_leave_day = int(total_leave_day) - len(weekend)  - len(holiday)

        shift_start = shift_data.start
        shift_end = shift_data.end

        bet_days = leave_end - leave_start

        # if shift_start > leave_start :
        #     pass
        # if shift_end > leave_end:
        #     pass
        return

    # 0008
    def leave_request_list(self, vys_page):
        leave_list = LeaveRequest.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for leave in leave_list:
            data = LeaveResponse()
            data.set_id(leave.id)
            usr_serv = AttendanceAPIService(self._scope())
            user_data = usr_serv.get_emp_data_by_id(leave.user_id)
            data.set_user_id(user_data)
            leave_serv = LeaveTypeService(self._scope())
            leave_data = leave_serv.fetch_leave_type(leave.leave_type)
            data.set_leave_type(leave_data)
            data.set_from_date(leave.from_date)
            data.set_to_date(leave.to_date)
            data.set_total_days(leave.total_days)
            data.set_reason(leave.reason)
            data.set_status(leave.status)
            data.set_created_date(leave.created_date)
            data.set_created_by(leave.created_by)
            data.set_updated_date(leave.updated_date)
            data.set_updated_by(leave.updated_by)
            list_data.append(data)
        paginator = NWisefinPaginator(leave_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    # 0009
    def fetch_leave_request(self, leave_id):
            leave = LeaveRequest.objects.using(self._current_app_schema()).get(id=leave_id, entity_id=self._entity_id())
            data = LeaveResponse()
            data.set_id(leave.id)
            usr_serv = AttendanceAPIService(self._scope())
            user_data = usr_serv.get_emp_data_by_id(leave.user_id)
            data.set_user_id_data(user_data)
            leave_serv = LeaveTypeService(self._scope())
            leave_data = leave_serv.fetch_leave_type(leave.leave_type)
            data.set_leave_type_data(leave_data)
            data.set_from_date(leave.from_date)
            data.set_to_date(leave.to_date)
            data.set_total_days(leave.total_days)
            data.set_reason(leave.reason)
            approve_status = get_leave_approve_type(leave.approve_status)
            data.set_approve_status(approve_status)
            approve_by = usr_serv.get_emp_data_by_id(leave.approved_by)
            data.set_approved_by_data(approve_by)
            approve_service = LeaveApproveService(self._scope())
            approve_message = approve_service.get_approve_status(leave.id, leave.approve_status)
            data.set_approve_message(approve_message)
            doc_serv = AttendanceDocumentService(self._scope())
            file_data = doc_serv.get_file_attachment(leave.id)
            data.set_file(file_data)
            return data

    # 0010
    def delete_leave_request(self, leave_id):
        leave_delete = LeaveRequest.objects.using(self._current_app_schema()).filter(id=leave_id).update(status=ActiveStatus.delete)
        logger.info('leave request deleted status(' + str(leave_delete) + '), for id : ' + str(leave_id))
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def leave_summary(self, l_type, vys_page, emp_id, from_date, to_date):
        if l_type is not None and l_type != '':
            leave_type = int(l_type)
        else:
            leave_type = 1
        # 1- created_by_me 2- approved_by_me 3-rejected_by_me 4-pending 5-all
        condition = Q(entity_id=self._entity_id())
        if (from_date is not None) and (from_date != ''):
            condition &= Q(from_date__gte=from_date)
        if (to_date is not None) and (to_date != ''):
            condition &= Q(to_date__lte=to_date)
        if leave_type == 1:
            condition &= Q(created_by=emp_id, status=1)
        elif leave_type == 2:
            condition &= Q(approved_by=emp_id, approve_status=LeaveApproveType.APPROVE, status=1)
        elif leave_type == 3:
            condition &= Q(approved_by=emp_id, approve_status=LeaveApproveType.REJECTED, status=1)
        elif leave_type == 4:
            condition &= Q(approved_by=-1, approve_status=-1, status=1) & ~Q(created_by=emp_id)
        elif leave_type == 5:
            condition &= Q(status=1)
        leave_list = LeaveRequest.objects.using(self._current_app_schema()).filter(
            condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        user_id_arr = []
        leave_type_arr = []
        approve_by_arr = []
        usr_serv = AttendanceAPIService(self._scope())
        leave_serv = LeaveTypeService(self._scope())
        for leave in leave_list:
            user_id_arr.append(leave.user_id)
            leave_type_arr.append(leave.leave_type)
            approve_by_arr.append(leave.approved_by)
        user_data = usr_serv.get_employee_list(user_id_arr)
        leave_data = leave_serv.fetch_leave_type_arr(leave_type_arr)
        approve_by = usr_serv.get_employee_list(approve_by_arr)
        list_data = NWisefinList()
        for leave in leave_list:
            data = LeaveResponse()
            data.set_id(leave.id)
            data.set_user_id(leave.user_id, user_data)
            data.set_leave_type(leave.leave_type, leave_data)
            data.set_from_date(leave.from_date)
            data.set_to_date(leave.to_date)
            data.set_total_days(leave.total_days)
            data.set_reason(leave.reason)
            data.set_status(leave.status)
            approve_status = get_leave_approve_type(leave.approve_status)
            data.set_approve_status(approve_status)
            data.set_approved_by(leave.approved_by, approve_by)
            # approve_service = LeaveApproveService(self._scope())
            # approve_message = approve_service.get_approve_status(leave.id, leave.approve_status)
            # data.set_approve_message(approve_message)
            list_data.append(data)
        paginator = NWisefinPaginator(leave_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def condition_type(self,request,emp_id):
        action = request.GET.get('action')
        from_date = request.GET.get('fromdate', None)
        to_date = request.GET.get('todate', None)
        status = request.GET.get('status', 1)
        condition = Q(entity_id=self._entity_id())
        if (from_date is not None) and (from_date != ''):
            condition &= Q(from_date__gte=from_date)
        if (to_date is not None) and (to_date != ''):
            condition &= Q(to_date__lte=to_date)
        if (status is not None) and (status != ''):
            condition &= Q(approve_status=status)
        if action == 'user' or action == None:
            condition &= Q(created_by=emp_id)
        return condition

    def new_leave_summary(self,vys_page,request,emp_id):
        condition = self.condition_type(request, emp_id)
        action = request.GET.get('action')
        leave_list = LeaveRequest.objects.using(self._current_app_schema()).filter(
            condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        user_id_arr = []
        leave_type_arr = []
        approve_by_arr = []
        usr_serv = AttendanceAPIService(self._scope())
        leave_serv = LeaveTypeService(self._scope())
        for leave in leave_list:
            user_id_arr.append(leave.user_id)
            leave_type_arr.append(leave.leave_type)
            approve_by_arr.append(leave.approved_by)
        user_data = usr_serv.get_employee_list(user_id_arr)
        leave_data = leave_serv.fetch_leave_type_arr(leave_type_arr)
        approve_by = usr_serv.get_employee_list(approve_by_arr)
        list_data = NWisefinList()
        for leave in leave_list:
            data = LeaveResponse()
            data.set_id(leave.id)
            if action == 'admin' or action == None:
                data.set_user_id(leave.user_id, user_data)
            data.set_leave_type(leave.leave_type, leave_data)
            data.set_from_date(leave.from_date)
            data.set_to_date(leave.to_date)
            data.set_total_days(leave.total_days)
            data.set_reason(leave.reason)
            data.set_status(leave.status)
            approve_status = get_leave_approve_type(leave.approve_status)
            data.set_approve_status(approve_status)
            data.set_approved_by(leave.approved_by, approve_by)
            # approve_service = LeaveApproveService(self._scope())
            # approve_message = approve_service.get_approve_status(leave.id, leave.approve_status)
            # data.set_approve_message(approve_message)
            list_data.append(data)
        paginator = NWisefinPaginator(leave_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data
    def update_approve(self, emp_id, approve_type, leave_id):
        leave = LeaveRequest.objects.using(self._current_app_schema()).filter(
            id=leave_id, entity_id=self._entity_id())
        if (leave_id is not None) and (len(leave) != 0):
            update = LeaveRequest.objects.using(self._current_app_schema()).filter(
                id=leave_id, entity_id=self._entity_id()).update(approve_status=approve_type,
                                                                 approved_by=emp_id)
            return True
        else:
            return False

    def get_leave_data(self):
        leave_list = LeaveRequest.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), approve_status=LeaveApproveType.APPROVE,
            from_date__gte=datetime.datetime.today(), to_date__lte=datetime.datetime.today())
        return leave_list

    def get_leave_data_by_date(self,l_date):
        leave_list = LeaveRequest.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), approve_status=LeaveApproveType.APPROVE,
            from_date__gte=l_date, to_date__lte=l_date)
        return leave_list

    def leave_type_count(self, data):
        leave_type = data['leave_type']
        user_id = data['user_id']
        start_date = data['start_date']
        end_date = data['end_date']
        ref_id = data['ref_id']
        leave_type = int(leave_type)
        dates = self.get_all_days(start_date, end_date)
        for date in dates:
            month = date['month']
            year = date['year']
            days_count = len(date['date'])
            condition = Q(user_id=user_id, leave_type=leave_type) & Q(
                Q(from_date__year=year, from_date__month=month) | Q(to_date__year=year, to_date__month=month))
            if ref_id is not None:
                condition &= ~Q(id=ref_id)
            previous_leave = LeaveRequest.objects.using(self._current_app_schema()).filter(condition)
            leave_count = 0
            for leave in previous_leave:
                leave_start_date = leave.from_date
                leave_end_date = leave.to_date
                leave_days = self.get_day_count_month(leave_start_date, leave_end_date, month)
                leave_count = leave_count + leave_days
            total_count = days_count + leave_count
            flag = self.leave_count_check(leave_type, total_count)
            if flag is False:
                return False
        return True

    def get_all_days(self, start_date, end_date):
        delta = end_date - start_date
        date_list = []
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            data = {
                "date": str(day),
                "month_year": str(day.month) + '_' + str(day.year),
                "month": day.month,
                "year": day.year
            }
            date_list.append(data)
        temp = []
        final_list = []
        for j in date_list:
            if j['month_year'] in temp:
                for k in final_list:
                    if k['month_year'] == j['month_year']:
                        k['date'].append(j['date'])
            else:
                data_1 = {
                    'month_year': j['month_year'],
                    'date': [j['date']],
                    'month': j['month'],
                    'year': j['year']
                }
                final_list.append(data_1)
                temp.append(j['month_year'])
        return final_list

    def get_day_count_month(self, start_date, end_date, month):
        delta = end_date - start_date
        date_list = []
        for i in range(delta.days + 1):
            day = start_date + datetime.timedelta(days=i)
            data = {
                "date": str(day),
                "month_year": str(day.month) + '_' + str(day.year),
                "month": day.month,
                "year": day.year
            }
            date_list.append(data)
        count = 0
        for j in date_list:
            if j['month'] == month:
                count = count + 1
        return count

    def leave_count_check(self, leave_type, leave_count):
        casual = 1
        sick = 2
        on_duty = 3
        work_from_home = 4
        others = 5
        flag = False
        count = 0
        if leave_type == others:
            count = 5
        elif leave_type == casual:
            count = 2
        elif leave_type == sick:
            count = 1
        elif leave_type == on_duty:
            count = 3
        elif leave_type == work_from_home:
            count = 3
        if count >= leave_count:
            flag = True
        return flag

    def get_leave_by_month(self,emp_id,month,year):
        pass



    # def leave_emp_summary(self,status):
