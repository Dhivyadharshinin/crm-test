import calendar
import datetime
from attendanceservice.models.attendancemodels import CheckInLog
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.data.response.nwisefinerror import NWisefinError
from attendanceservice.data.response.attendanceresponse import CheckINLOGResponse, PerDayCheckInResponse, PerDayData
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from attendanceservice.util.attendanceutil import CheckLogType, check_log_get, time_to_m_sec, AlertType,AlertMessageType, InOut,ActiveStatus
from nwisefin.settings import logger
from ipware import get_client_ip
from django.db import IntegrityError
from utilityservice.service.attendanceapiservice import AttendanceAPIService
from masterservice.service.leaveattendanceservice import AttendanceConfigService, OrgDetailsService, CalculationService,OrgIpService
from attendanceservice.service.allertservice import AlertService
from django.db.models import Q

from hrmsservice.util.hrmsutil import day_get
from hrmsservice.models.hrmsmodels import WorkWeek,EmployeeShiftMapping
from hrmsservice.service.employeedetailsservice import EmployeeDetailsService

class CheckInLogService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def create_check_in_log(self, emp_id, mode, login_data):
        mode = int(mode)
        login_type = login_data['login_type']
        location = login_data['location']
        if (login_type is None) or (location is None):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        if mode == CheckLogType.CHECK_IN:
            try:
                check_in = CheckInLog.objects.using(self._current_app_schema()
                                                    ).create(user_id=emp_id,
                                                             log_date=datetime.datetime.today(),
                                                             log_time=datetime.datetime.now(),
                                                             log_type=CheckLogType.CHECK_IN,
                                                             check_in_mode=login_type,
                                                             org_detail_id=location,
                                                             entity_id=self._entity_id())
                logger.info('check_in log created for id : ' + str(check_in.id))
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
        else:
            try:
                check_in = CheckInLog.objects.using(self._current_app_schema()
                                                    ).create(user_id=emp_id,
                                                             log_type=CheckLogType.CHECK_OUT,
                                                             check_in_mode=login_type,
                                                             org_detail_id=location,
                                                             log_date=datetime.datetime.today(),
                                                             log_time=datetime.datetime.now(),
                                                             entity_id=self._entity_id())
                logger.info('check_out log created for id : ' + str(check_in.id))
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

        # data = CheckINLOGResponse()
        # data.set_id(check_in.id)
        # data.set_user_id(check_in.user_id)
        # data.set_log_date(check_in.log_date)
        # data.set_log_time(check_in.log_time)
        # data.set_log_type(check_in.log_type)
        # data.set_check_in_mode(check_in.check_in_mode)
        # data.set_status(check_in.status)
        # data.set_org_detail_id(check_in.org_detail_id)
        # return data
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def checkin_out_log(self,emp_id,mode,org_id,checkin_mode):
        check_in = CheckInLog.objects.using(self._current_app_schema()).create(user_id=emp_id,
                                                     log_type=mode,
                                                     check_in_mode=checkin_mode,
                                                     org_detail_id=org_id,
                                                     log_date=datetime.datetime.today(),
                                                     log_time=datetime.datetime.now(),
                                                     entity_id=self._entity_id())
        logger.info('check_out log created for id : ' + str(check_in.id))
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def check_in_log_list(self, vys_page, emp_id):
        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(user_id=emp_id,
            entity_id=self._entity_id()).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for check_in in check_in_list:
            data = CheckINLOGResponse()
            data.set_id(check_in.id)
            data.set_user_id(check_in.user_id)
            data.set_log_date(check_in.log_date)
            # m_sec = time_to_m_sec(check_in.log_time)
            data.set_log_time(check_in.log_time)
            data.set_log_date_time(check_in.log_time)
            type_data = check_log_get(check_in.log_type)
            data.set_log_type(type_data)
            check_in_serv = AttendanceConfigService(self._scope())
            check_id_data = check_in_serv.fetch_attendance_config(check_in.check_in_mode)
            data.set_check_in_mode(check_id_data)
            data.set_status(check_in.status)
            org_serv = OrgDetailsService(self._scope())
            org_data = org_serv.fetch_org_details(check_in.org_detail_id)
            data.set_org_detail_id(org_data)
            list_data.append(data)
        paginator = NWisefinPaginator(check_in_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def fetch_check_in_log(self, log_id):
        try:
            check_in = CheckInLog.objects.using(self._current_app_schema()).get(id=log_id, entity_id=self._entity_id())
            data = CheckINLOGResponse()
            data.set_id(check_in.id)
            data.set_user_id(check_in.user_id)
            data.set_log_date(check_in.log_date)
            # m_sec = time_to_m_sec(check_in.log_time)
            data.set_log_time(check_in.log_time)
            data.set_log_date_time(check_in.log_time)
            data.set_log_type(check_in.log_type)
            check_in_serv = AttendanceConfigService(self._scope())
            check_id_data = check_in_serv.fetch_attendance_config(check_in.check_in_mode)
            data.set_check_in_mode(check_id_data)
            data.set_status(check_in.status)
            org_serv = OrgDetailsService(self._scope())
            org_data = org_serv.fetch_org_details(check_in.org_detail_id)
            data.set_org_detail_id(org_data)
            return data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_check_in_log(self, log_id):
        try:
            leave_delete = CheckInLog.objects.using(self._current_app_schema()).filter(id=log_id).delete()
            logger.info('Check In Log deleted status(' + str(leave_delete) + '), for id : ' + str(log_id))
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def check_in_general_list(self, vys_page):
        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for check_in in check_in_list:
            data = CheckINLOGResponse()
            data.set_id(check_in.id)
            usr_serv = AttendanceAPIService(self._scope())
            user_data = usr_serv.get_emp_data_by_id(check_in.user_id)
            data.set_user_id(user_data)
            data.set_log_date(check_in.log_date)
            # m_sec = time_to_m_sec(check_in.log_time)
            data.set_log_time(check_in.log_time)
            data.set_log_date_time(check_in.log_time)
            data.set_log_type(check_in.log_type)
            check_in_serv = AttendanceConfigService(self._scope())
            check_id_data = check_in_serv.fetch_attendance_config(check_in.check_in_mode)
            data.set_check_in_mode(check_id_data)
            data.set_status(check_in.status)
            org_serv = OrgDetailsService(self._scope())
            org_data = org_serv.fetch_org_details(check_in.org_detail_id)
            data.set_org_detail_id(org_data)
            list_data.append(data)
        paginator = NWisefinPaginator(check_in_list, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        return list_data

    def type_validation(self, user_agent, req_obj, request):
        atd_serv = AttendanceConfigService(self._scope())
        latitude = req_obj.get_latitude()
        longitude = req_obj.get_longitude()
        log_type = None
        location = None
        error = 0
        calc = CalculationService(self._scope())
        if user_agent == 'ANDROID':
            data = calc.location_finder(latitude, longitude)
            if data['inside'] is True:
                log_type = atd_serv.get_id_and_namespace(user_agent)
                # log_type = 3
                location = data['id']
            else:
                error = 1
        elif user_agent == 'WEB':
            val = get_client_ip(request)
            client_ip = val[0]
            data = calc.check_ip(client_ip)
            if data['valid'] is True:
                log_type = atd_serv.get_id_and_namespace(user_agent)
                # log_type = 4
                location = data['id']
            else:
                error = 2
        else:
            log_type = atd_serv.get_id_and_namespace(user_agent)
            location = 3  # default
        if log_type is None or location is None:
            error = 3

        data = {'login_type': log_type, 'location': location, 'error': error}
        return data

    def type_validation_new(self, req_obj, request):
        atd_serv = AttendanceConfigService(self._scope())
        latitude = req_obj.get_latitude()
        longitude = req_obj.get_longitude()
        log_type = None
        location = None
        error = 0
        calc = CalculationService(self._scope())
        if 'User-Agent' in request.headers:
            user_agent = request.headers['User-Agent']
            if user_agent == 'ANDROID':
                data = calc.location_finder(latitude, longitude)
                if data['inside'] is True:
                    log_type = atd_serv.get_id_and_namespace(user_agent)
                    # log_type = 3
                    location = data['id']
                else:
                    error = 1
            else:
                val = get_client_ip(request)
                client_ip = val[0]
                data = calc.check_ip(client_ip)
                if data['valid'] is True:
                    log_type = atd_serv.get_id_and_namespace('WEB')
                    # log_type = 4
                    location = data['id']
                else:
                    error = 2
        else:
            val = get_client_ip(request)
            client_ip = val[0]
            data = calc.check_ip(client_ip)
            if data['valid'] is True:
                log_type = atd_serv.get_id_and_namespace('WEB')
                # log_type = 4
                location = data['id']
            else:
                error = 2
        if log_type is None or location is None:
            error = 3
        data = {'login_type': log_type, 'location': location, 'error': error}
        return data

    def check_repeated_entry(self, emp_id, mode):
        mode = int(mode)
        # 1-entry, 2-delete, 3-duplicate
        attendance = CheckInLog.objects.using(self._current_app_schema()).filter(status=1, user_id=emp_id).order_by('-id')
        result = 1
        check_in = ''
        if len(attendance) != 0:
            check_in = attendance[0]
            last_entry = attendance[0].log_type
            if mode == last_entry:
                now = datetime.datetime.now()
                time_data = str(attendance[0].log_time)
                last = datetime.datetime.strptime(time_data[:26], "%Y-%m-%d %H:%M:%S.%f")
                time_dif = now - last
                seconds_dif = time_dif.total_seconds()
                if int(seconds_dif) <= 300:
                    result = 2
                else:
                    result = 3
        data = {'result': result, 'check_in': check_in}
        return data

    #  check in - out validation
    def check_in_out_val(self, emp_id, mode):
        mode = int(mode)
        now = datetime.datetime.now()
        cond = Q(status=ActiveStatus.Active, user_id=emp_id,log_date=now)
        att_obj = CheckInLog.objects.using(self._current_app_schema()).filter(cond).order_by('-id')

        if len(att_obj) == 0 :
            if mode == CheckLogType.CHECK_IN :
                return True
        else:
            last_log = att_obj[0]
            last_mode = last_log.log_type
            if last_mode == CheckLogType.CHECK_IN and mode == CheckLogType.CHECK_OUT:
                return True
            elif last_mode == CheckLogType.CHECK_OUT and mode == CheckLogType.CHECK_IN:
                return True

        return False

    # location employee validation
    def location_validation(self,req_obj,org_id):
        latitude = req_obj.get_latitude()
        longitude = req_obj.get_longitude()
        if latitude == None or longitude == None:
            d={"status":False,"msg":"latitude / longitude is missing"}
            return d
        else:
            calc = CalculationService(self._scope())
            d = calc.employee_location_finder(latitude, longitude,org_id)
            return d

    def get_org_id(self,emp_id):
        atd_serv = AttendanceAPIService(self._scope())
        emp_obj= atd_serv.get_employee_info(emp_id)
        org_id = emp_obj.org_id
        return org_id

    def ip_validation(self,request,org_id):
        val = get_client_ip(request)
        client_ip = val[0]
        calc = CalculationService(self._scope())
        data = calc.check_ip(org_id)
        if client_ip not in data:
            d = {"status": False, "msg": "INVALID IP Address"}
        else:
            d = {"status": True, "msg": None}
        return d

    def get_checkin_mode(self,request):
        atd_serv = AttendanceConfigService(self._scope())

        if 'User-Agent' in request.headers:
            user_agent = request.headers['User-Agent']

            if user_agent == 'ANDROID':
                log_type = atd_serv.get_id_and_namespace(user_agent)
                return log_type
        log_type = atd_serv.get_id_and_namespace('WEB')
        return log_type


    def return_previous_response(self, check_in):
        data = CheckINLOGResponse()
        data.set_id(check_in.id)
        data.set_user_id(check_in.user_id)
        data.set_log_date(check_in.log_date)
        data.set_log_time(check_in.log_time)
        data.set_log_type(check_in.log_type)
        data.set_check_in_mode(check_in.check_in_mode)
        data.set_status(check_in.status)
        data.set_org_detail_id(check_in.org_detail_id)
        return data

    def create_alert_for_check_in(self, emp_id):
        alert_serv = AlertService(self._scope())
        alert_type = AlertType.REPEATED_CHECK_IN
        default_header = 1
        message = AlertMessageType.REPEATED_CHECK_IN_MESSAGE
        data_obj = {'message': message, 'alert_to': default_header, 'alert_from': emp_id}
        alert_serv.create_alert_message(alert_type, data_obj)

    def get_per_day_check_in(self):
        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                    log_date=datetime.datetime.today()
                                                                                    ).order_by('log_date')
        return check_in_list

    def get_check_in_by_date(self,log_date):
        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),log_date=log_date).order_by('log_date')

        return check_in_list

    def per_day_response(self, emp_id):
        total_data = self.per_day_check_in_list(emp_id)
        check_in_list = total_data['list_data']
        list_data = NWisefinList()
        for check_in in check_in_list:
            data = PerDayCheckInResponse()
            data.set_check_in_time(check_in['check_in_time'])
            data.set_check_out_time(check_in['check_out_time'])
            data.set_duration(check_in['duration'])
            data.set_check_in_date_time(check_in['check_in_date_time'])
            data.set_check_out_date_time(check_in['check_out_date_time'])
            data.set_status(check_in['status'])
            list_data.append(data)
        return list_data

    def per_day_data_list(self, emp_id):
        total_data = self.per_day_check_in_list(emp_id)
        check_in_list = total_data['list_data']
        single_data = total_data['single_data']
        list_data = []
        single_data_list = []
        for check_in in check_in_list:
            data = PerDayCheckInResponse()
            data.set_check_in_time(check_in['check_in_time'])
            data.set_check_out_time(check_in['check_out_time'])
            data.set_duration(check_in['duration'])
            data.set_check_in_date_time(check_in['check_in_date_time'])
            data.set_check_out_date_time(check_in['check_out_date_time'])
            data.set_status(check_in['status'])
            list_data.append(data)
        if single_data['in_or_out'] is not None:
            single_resp = PerDayData()
            single_resp.set_first_check_in(single_data['first_check_in'])
            single_resp.set_first_check_in_val(single_data['first_check_in_val'])
            single_resp.set_last_check_in(single_data['last_check_in'])
            single_resp.set_last_check_in_val(single_data['last_check_in_val'])
            single_resp.set_in_or_out(single_data['in_or_out'])
            single_data_list.append(single_resp)
        total_resp = PerDayData()
        total_resp.set_list_data(list_data)
        total_resp.set_single_data(single_data_list)
        return total_resp

    def per_day_check_in_list(self, emp_id):
        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(user_id=emp_id,entity_id=self._entity_id(),log_date=datetime.datetime.today()).order_by('id')
        list_data = []
        previous = 0
        count = 0
        for i in check_in_list:
            entry = 0
            user_id, check_in_time, check_out_time, duration, check_in_date_time, check_out_date_time = (None,)*6
            if i.log_type == CheckLogType.CHECK_IN:
                entry = 1
                user_id = i.user_id
                time_val = time_to_m_sec(i.log_time)
                check_in_time = time_val
                check_in_date_time = str(i.log_time)
                previous = CheckLogType.CHECK_IN
            else:
                if previous == CheckLogType.CHECK_IN:
                    data_val = list_data[count-1]
                    time_val = time_to_m_sec(i.log_time)
                    data_val['check_out_time'] = time_val
                    data_val['check_out_date_time'] = str(i.log_time)
                    check_in = datetime.datetime.strptime(data_val['check_in_date_time'][:26], "%Y-%m-%d %H:%M:%S.%f")
                    check_out = datetime.datetime.strptime(data_val['check_out_date_time'][:26], "%Y-%m-%d %H:%M:%S.%f")
                    time_dif = check_out - check_in
                    seconds_dif = time_dif.total_seconds()
                    total_duration = seconds_dif / 3600
                    res = "{:.2f}".format(total_duration)
                    data_val['duration'] = res
                else:
                    entry = 1
                    user_id = i.user_id
                    time_val = time_to_m_sec(i.log_time)
                    check_out_time = time_val
                    check_out_date_time = str(i.log_time)
                previous = CheckLogType.CHECK_OUT
            if entry == 1:
                data = {'user_id': user_id, 'check_in_time': check_in_time, 'check_out_time': check_out_time,
                        'duration': duration, 'status': 1, 'check_in_date_time': check_in_date_time,
                        'check_out_date_time': check_out_date_time}
                list_data.append(data)
                count = count + 1
        first_check_in = None
        first_check_in_val = None
        first_check_in_bool = False
        last_check_in = None
        last_check_in_val = None
        in_or_out = None
        for j in check_in_list:
            if j.log_type == CheckLogType.CHECK_IN:
                in_or_out = InOut.IN_VAL
                if first_check_in_bool is False:
                    time_val = time_to_m_sec(j.log_time)
                    first_check_in = time_val
                    first_check_in_val = str(j.log_time)
                    first_check_in_bool = True
            else:
                in_or_out = InOut.OUT_VAL
                time_val = time_to_m_sec(j.log_time)
                last_check_in = time_val
                last_check_in_val = str(j.log_time)
        single_data = {"first_check_in": first_check_in, "first_check_in_val": first_check_in_val,
                       "last_check_in": last_check_in, "last_check_in_val": last_check_in_val,
                       "in_or_out": in_or_out}
        total_data = {'list_data': list_data, "single_data": single_data}
        return total_data


    def check_in_log_history(self, emp_id,request):
        cond = Q(user_id=emp_id,entity_id=self._entity_id())
        log_date=request.GET.get('log_date')
        if log_date == None:
            log_date =datetime.datetime.now()
        cond &= Q(log_date=log_date)

        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(cond).order_by('id')
        list_data = NWisefinList()
        check_in_list= list(check_in_list)
        if len(check_in_list) >0 :
            last_data=check_in_list[-1]
            last_seen=None
            if last_data.log_type == CheckLogType.CHECK_OUT:
                last_seen =time_to_m_sec(last_data.log_time)
            d={"status":last_data.log_type,"last_seen":last_seen}
        else:
            d={"status":None,"last_seen":None}
        check_in_serv = AttendanceConfigService(self._scope())

        org_arc_id = [a.org_detail_id for a in check_in_list]
        org_serv=OrgIpService(self._scope())
        org_arc_info = org_serv.get_org_arc_info(org_arc_id)
        for check_in in check_in_list:
            data = CheckINLOGResponse()
            data.set_id(check_in.id)
            # data.set_user_id(check_in.user_id)
            data.set_log_date(check_in.log_date)
            data.set_log_time(check_in.log_time)
            data.set_log_type(check_in.log_type)
            check_id_data = check_in_serv.fetch_attendance_config(check_in.check_in_mode)
            data.set_check_in_mode(check_id_data)
            data.set_org_arc_detail(check_in.org_detail_id,org_arc_info)
            list_data.append(data)
        list_data.active_status=d
        return list_data

    def get_workweek(self):
        working_day=WorkWeek.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),is_working=True).values_list('day',flat=True)
        return working_day

    def get_workend_month(self, month, year, org_id):
        weekendleave_day = WorkWeek.objects.using(self._current_app_schema()).filter(org_id=org_id, is_working=False)
        start = year + '-' + month + '-' + '01'
        start_date = datetime.datetime.strptime(start[:10], '%Y-%m-%d')
        end_date = start_date.replace(day=calendar.monthrange(start_date.year, start_date.month)[1])
        day_arr = []
        for i in weekendleave_day:
            days = i.day
            days_details = day_get(days)
            days_text = days_details.text
            day_arr.append(days_text)
        delta = end_date - start_date
        data = []
        for i in range(delta.days + 1):
            date = (start_date + datetime.timedelta(days=i))
            if (date.strftime('%A')).upper() in day_arr:
                millisec = time_to_m_sec(date)
                data.append(millisec)
        return data


    def perday_log(self,request,emp_id):
        cond = Q(user_id=emp_id, entity_id=self._entity_id())
        log_date = request.GET.get('log_date')
        if log_date == None or log_date=='':
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description('log date missing')
            return error_obj
        cond &= Q(log_date=log_date)
        serv = EmployeeDetailsService(self._scope())

        emp_shift= serv.get_shiftmapping_logdate(emp_id,log_date)
        if emp_shift == None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description('Employee shift mapping missing')
            return error_obj
        shift_start=emp_shift['start_time']
        shift_end=emp_shift['end_time']

        check_in_list = CheckInLog.objects.using(self._current_app_schema()).filter(cond).order_by('id')
        list_data = NWisefinList()
        check_in_list = list(check_in_list)
        if len(check_in_list) > 0:
            last_data = check_in_list[-1]
            last_seen = None
            if last_data.log_type == CheckLogType.CHECK_OUT:
                last_seen = time_to_m_sec(last_data.log_time)
            d = {"status": last_data.log_type, "last_seen": last_seen}
        else:
            d = {"status": None, "last_seen": None}

        arr=[]
        first_checkin = True
        for i in check_in_list:
            log_time = i.log_time
            m_log_time= time_to_m_sec(i.log_time)
            if i.log_type == CheckLogType.CHECK_IN:
                if first_checkin == True:
                    first_checkin=False
                    out_time=0
                else:
                    out_time=0
                d={"check_in":m_log_time,"check_out":None,"in_time":0,"out_time":out_time,"in":log_time,"out":out_time}
                arr.append(d)

            if (i.log_type == CheckLogType.CHECK_OUT) and (first_checkin==False):
                last_data =arr[-1]
                in_time = last_data['in']
                last_data['check_out']=m_log_time
                in_time = self.logtime_calculation(in_time,log_time)
                last_data['in_time']=  in_time

        for j in arr:
            del j['in']
            del j['out']
        list_data.active_status = d
        list_data.log =arr
        return list_data
    
    
    def logtime_calculation(self,login,logout):
        duration = logout - login
        if duration == 0:
            a = 0
        else:
            d = str(duration)
            arr = d.split(":")
            a = float(arr[0] + "." + arr[1])

        return a
