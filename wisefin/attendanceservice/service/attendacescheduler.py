from apscheduler.schedulers.background import BackgroundScheduler
schedule = True
import datetime


def data_migration():
    if schedule is True:
        atd_schedule = BackgroundScheduler()
        atd_schedule.add_job(attendance_scheduler, 'cron', hour=23, minute=30)
        # atd_schedule.add_job(generate_per_day_attendance, 'cron', hour=17, minute=16, second=00)
        atd_schedule.start()
        return True
    else:
        return True

# api call
def attendance_scheduler_apicall(request):
    l_date = request.GET.get('date')
    if l_date == None:
        a_date=datetime.datetime.today()
    else:
        a_date=datetime.datetime.strptime(l_date,'%Y-%m-%d').date()

    att_val=generate_per_day_attendance(a_date)
    return att_val

#  scheduler call
def attendance_scheduler():
    log_date = datetime.datetime.today()
    generate_per_day_attendance(log_date)
    return

def get_entity_data():
    from configservice.models import Entity
    obj=Entity.objects.filter(status=1).values_list('id',flat=True)
    entity_list = list(obj)
    return entity_list

def generate_per_day_attendance(log_date):
        entity_list = get_entity_data()
        resp_key = False
        for entity_id in entity_list:

            from attendanceservice.models.attendancemodels import Attendance ,AttendanceSchd,AlertMessage
            from utilityservice.service.attendanceapiservice import AttendanceAPIService
            from attendanceservice.service.checkinlogservice import CheckInLogService
            from attendanceservice.service.leaverequestservice import LeaveRequestService
            from masterservice.service.leaveattendanceservice import HolidayService
            from utilityservice.service.defaultscopeservice import DefaultScopeScheduler
            from attendanceservice.service.attendanceservice import DailyAttendanceService
            from nwisefin.settings import logger
            scope_serv = DefaultScopeScheduler()
            scope = scope_serv.scope_for_multiple_entity(entity_id)
            #  entity mapping validation
            entity_info = scope['entity_info']
            if len(entity_info) ==0 :
                continue
            #  scheduler duplicate validation
            atd_serv = DailyAttendanceService(scope)
            sch_val = atd_serv.attendance_scheduler_val(log_date,entity_id)
            if sch_val == False:
                print("scheduler already done")
                continue
            resp_key =True
            # fetch all employee data
            api_serv = AttendanceAPIService(scope)
            emp_list = api_serv.get_all_employee(entity_id)
            # fetch holiday and leave data
            check_in_serv = CheckInLogService(scope)
            check_in_list = check_in_serv.get_check_in_by_date(log_date)
            leave_req_serv = LeaveRequestService(scope)
            leave_list = leave_req_serv.get_leave_data_by_date(log_date)
            holiday_serv = HolidayService(scope)
            holiday_list = holiday_serv.get_holiday_by_date(log_date)
            workingdays_list = check_in_serv.get_workweek()

            # holiday , weekend marking - logdate wise
            is_holiday,is_weekend = False,False
            total_list,alert_list = [],[]
            date_type = log_date.strftime('%w')
            if int(date_type) not in workingdays_list:
                is_weekend = True
            if len(holiday_list) != 0:
                is_holiday = True

            # log date attendance data
            emp_arr =[i.id for i in emp_list]
            att_empp_arr=Attendance.objects.filter(user_id__in=emp_arr,status=1,entity_id=entity_id,log_date=log_date).values_list('user_id',flat=True)
            att_empp_arr = list(att_empp_arr)

            # month attendance data - report
            month ,year = log_date.month , log_date.year
            att_month_data =atd_serv.get_attend_report(emp_arr,month,year,entity_id)
            att_data_arr=[]

            for employee in emp_list:
                emp_id = employee.id
                is_present = False
                is_leave = -1
                first_check_in = None
                last_check_in = None
                duration = None
                individual_check_in = []
                for check_in in check_in_list:
                    if emp_id == check_in.user_id:
                        individual_check_in.append(check_in)
                check_in_length = len(individual_check_in)
                if check_in_length != 0:
                    is_present = True
                for leave in leave_list:
                    if emp_id == leave.user_id:
                        is_leave = leave.leave_type
                if is_present is True:
                    data = find_duration_timing(individual_check_in)
                    first_check_in = data['first_check_in']
                    last_check_in = data['last_check_in']
                    duration = data['duration']

                # attendance marking data
                if emp_id not in att_empp_arr :
                    data = Attendance(user_id=emp_id, first_check_in=first_check_in, last_check_in=last_check_in,is_present=is_present, log_date=log_date, is_leave=is_leave, is_holiday=is_holiday,is_weekend=is_weekend, duration=duration,entity_id=entity_id)
                    total_list.append(data)
                    # attendance report
                    rep_data={"is_present":is_present,"is_leave":is_leave,"is_holiday":is_holiday,
                              "is_weekend":is_weekend,"duration":duration,"user_id":emp_id}
                    att_data_arr.append(rep_data)
                    if last_check_in == None:
                        alert_list.append(emp_id)
                        print('missed log out employee',emp_id)
            create = atd_serv.attenance_bulk_create(total_list)
            # atd_serv. attendance_report_update(att_month_data,att_data_arr,month,year,entity_id)

            logger.info('Scheduler for attendance completed successfully date : ' + str(log_date))
            print('Scheduler for attendance completed successfully date : ' + str(log_date))
            print('missed log out employee list : ' + str(alert_list))
            # attendance scheduler
            atd_serv.attendance_scheduler_insert(log_date)
        return resp_key


# def find_duration_timing1(atd_list):
#     from attendanceservice.util.attendanceutil import CheckLogType
#     import datetime
#     first_check_in = None
#     duration = None
#     count = 0
#     check_in_time = None
#     check_out_time = None
#     for atd in atd_list:
#         if count == 0:
#             if atd.log_type == CheckLogType.CHECK_IN:
#                 first_check_in = atd.log_time
#                 check_in_time = atd.log_time
#                 duration = (check_in_time - check_in_time)
#             else:
#                 now = datetime.datetime.now()
#                 val = now.strftime('%Y-%m-%d 00:00:01.000000')
#                 first_check_in = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f")
#                 check_out_time = atd.log_time
#                 duration = check_out_time-first_check_in
#         else:
#             if atd.log_type == CheckLogType.CHECK_IN:
#                 check_in_time = atd.log_time
#                 # vendor vignesh
#                 # if check_in_time is None:
#                 #     check_in_time = atd.log_time
#                 # else:
#                 #     check_in_time_2 = atd.log_time
#                 #     duration = duration + (check_in_time_2-check_in_time)
#                 #     check_in_time = check_in_time_2
#             else:
#                 if check_in_time is None:
#                     pass
#                     # check_out_time_2 = atd.log_time
#                     # duration = duration + (check_out_time_2-check_out_time)
#                     # check_out_time = check_out_time_2
#                 else:
#                     check_out_time = atd.log_time
#                     duration = duration + (check_out_time - check_in_time)
#                     check_in_time = None
#         count = count+1
#     # last log_in
#     last_log_type = atd_list[count-1].log_type
#     if last_log_type == CheckLogType.CHECK_IN:
#         now = datetime.datetime.now()
#         val = now.strftime('%Y-%m-%d 23:59:59.000000')
#         last_check_in = datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S.%f")
#         check_in_time = atd_list[count-1].log_time
#         duration = duration + (last_check_in-check_in_time)
#     else:
#         last_check_in = atd_list[count-1].log_time
#
#     # convert duration time into float
#     duration_in_sec = duration.total_seconds()
#     total_duration = duration_in_sec/3600
#     res = "{:.2f}".format(total_duration)
#     data = {"first_check_in": first_check_in, "last_check_in": last_check_in, "duration": res}
#     return data


def find_duration_timing(atd_list):
    from attendanceservice.util.attendanceutil import CheckLogType
    # import datetime
    first_check_in,last_check_in = None,None
    duration = 0
    count = 0
    check_in_time,check_out_time = None,None
    active_check_in , active_check_out =False,False
    for atd in atd_list:
        if atd.log_type == CheckLogType.CHECK_IN and active_check_in ==False :
            # First check in
            if count ==0:
                first_check_in = atd.log_time
                duration = first_check_in-first_check_in

            check_in_time = atd.log_time
            count +=1
            #  to remove duplidate entry
            active_check_in ,active_check_out= True,False

        elif atd.log_type == CheckLogType.CHECK_OUT and active_check_out ==False :
            if count != 0:
                check_out_time = atd.log_time
                duration = duration + (check_out_time-check_in_time)
                last_check_in = atd.log_time
                count += 1
                #  to remove duplidate entry
                active_check_in,active_check_out =False, True

    # convert duration time into float
    # duration_in_sec = duration.total_seconds()
    # total_duration = duration_in_sec/3600
    # res = "{:.2f}".format(total_duration)
    if duration == 0:
        a=0
    else:
        d= str(duration)
        arr=d.split(":")
        a=float(arr[0]+"."+arr[1])
    data = {"first_check_in": first_check_in, "last_check_in": last_check_in, "duration": a}
    return data
