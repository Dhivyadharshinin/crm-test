from attendanceservice.models.attendancemodels import Attendance,AttendanceSchd,AttendanceReport
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from attendanceservice.data.response.attendanceresponse import DailyAttendanceResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from nwisefin.settings import logger
from django.db import IntegrityError
import datetime
from django.db.models import Q
from attendanceservice.util.attendanceutil import ActiveStatus
from utilityservice.service.attendanceapiservice import AttendanceAPIService
import pandas as pd
import numpy as np
from calendar import monthrange
from attendanceservice.service.leaverequestservice import LeaveRequestService
from masterservice.service.leaveattendanceservice import HolidayService
from attendanceservice.service.checkinlogservice import CheckInLogService
from hrmsservice.models.hrmsmodels import WorkWeek
from hrmsservice.util.hrmsutil import day_get
from attendanceservice.util.attendanceutil import time_to_m_sec
from attendanceservice.service.ruleengineservice import RuleEngineServ
import json
class DailyAttendanceService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def create_attendance(self, attendance_data):
        try:
            attendance = Attendance.objects.using(self._current_app_schema()
                                              ).create(user_id=attendance_data['user_id'],
                                                       first_check_in=attendance_data['first_check_in'],
                                                       last_check_in=attendance_data['last_check_in'],
                                                       is_present=attendance_data['is_present'],
                                                       log_date=attendance_data['log_date'],
                                                       is_holiday=attendance_data['is_holiday'],
                                                       is_weekend=attendance_data['is_weekend'],
                                                       duration=attendance_data['duration'])
            return True
        except:
            return False

    def attendance_summary(self, emp_id,request):
        scope=request.scope
        condition = Q(user_id=emp_id)&Q(status=ActiveStatus.Active)
        year = request.GET.get('year')
        month = request.GET.get('month')
        if month == '' or year == '' or month == None or year == None :
            month = datetime.datetime.now().month
            year = datetime.datetime.now().year

        order_by = request.GET.get('order_by')
        if order_by == '-1':
            order_log_date='-log_date'
        else:
            order_log_date='log_date'

        condition &= Q(log_date__year=year)&Q(log_date__month=month)
        attendance_list = Attendance.objects.using(self._current_app_schema()).filter(condition).order_by(order_log_date)
        apiserv = AttendanceAPIService(self._scope())
        org_id = apiserv.get_employee_info(emp_id).org_id
        leave_req_serv = LeaveRequestService(scope)
        leave_list = leave_req_serv.get_leave_by_month(emp_id,month,year)
        holiday_serv = HolidayService(scope)
        holiday_list = holiday_serv.get_holiday_by_month(month,year)
        check_in_serv = CheckInLogService(scope)
        weekend_list = check_in_serv.get_workend_month(month, year, org_id)

        # LEAVE TYPE
        leave_obj=apiserv.get_leave_type()

        list_data = NWisefinList()
        for attendance in attendance_list:
            data = DailyAttendanceResponse()
            data.set_id(attendance.id)
            data.set_log_date(attendance.log_date)
            data.set_first_check_in(attendance.first_check_in)
            data.set_last_check_in(attendance.last_check_in)
            data.set_is_present(attendance.is_present)
            # LEAVE FLAG
            leave_type = self.get_leavetype(attendance.is_leave,leave_obj)
            d= attendance.__dict__
            d['code']=leave_type
            flag = RuleEngineServ().flag_df(d)
            data.flag=flag
            data.set_is_leave(attendance.is_leave,attendance.is_holiday,attendance.is_weekend)
            # data.set_is_holiday(attendance.is_holiday)
            # data.set_is_weekend(attendance.is_weekend)
            data.set_duration(attendance.duration)
            list_data.append(data)
        list_data.holiday=holiday_list
        list_data.weekend=weekend_list
        list_data.leave=leave_list

        # paginator = NWisefinPaginator(attendance_list, vys_page.get_index(), 10)
        # list_data.set_pagination(paginator)
        return list_data

    def get_leavetype(self,is_leave,leave_obj):
        for i in leave_obj :
            if i.id == is_leave:
                return i.code
        return

    def get_holiday_weekend_count(self,month,year,org_id):
        holidayserv = HolidayService(self._scope())
        holiday_arr = holidayserv.get_holiday_by_month(month, year)
        holiday_date = []
        for i in holiday_arr:
            hdate = i['date']
            holiday_date.append(hdate)
        weekendleave_day = WorkWeek.objects.using(self._current_app_schema()).filter(org_id=org_id, is_working=False)
        start = year + '-' + month + '-' + '01'
        start_date = datetime.datetime.strptime(start[:10], '%Y-%m-%d')
        end_date = start_date.replace(day=monthrange(start_date.year, start_date.month)[1])
        day_arr = []
        for i in weekendleave_day:
            days = i.day
            days_details = day_get(days)
            days_text = days_details.text
            day_arr.append(days_text)
        delta = end_date - start_date
        data1 = []
        for i in range(delta.days + 1):
            date = (start_date + datetime.timedelta(days=i))
            if (date.strftime('%A')).upper() in day_arr:
                data1.append(date.date())
        finalarray = []
        newdata = list(set(np.array(holiday_date+data1)))
        for holiday in newdata:
            is_weekend = False
            if holiday in data1:
                is_weekend = True
            is_holiday = False
            if holiday in holiday_date:
                is_holiday = True
            name = None
            for holiday_name in holiday_arr:
                if holiday_name['date'] == holiday:
                    name = holiday_name['name']
            holidaydataa = {str(holiday): {"is_holiday": is_holiday, "is_weekend": is_weekend, "name": name}}
            finalarray.append(holidaydataa)
        return finalarray

    def fetch_attendance(self, attendance_id):
        attendance = Attendance.objects.using(self._current_app_schema()
                                              ).filter(id=attendance_id, entity_id=self._entity_id())
        if len(attendance) != 0:
            data = DailyAttendanceResponse()
            data.set_id(attendance[0].id)
            data.set_user_id(attendance[0].user_id)
            data.set_log_date(attendance[0].log_date)
            data.set_first_check_in(attendance[0].first_check_in)
            data.set_last_check_in(attendance[0].last_check_in)
            data.set_is_present(attendance[0].is_present)
            data.set_is_holiday(attendance[0].is_holiday)
            data.set_is_weekend(attendance[0].is_weekend)
            data.set_duration(attendance[0].duration)
            data.set_status(attendance[0].status)
            return data
        else:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def delete_attendance(self, attendance_id):
        try:
            attendance_delete = Attendance.objects.using(self._current_app_schema()).filter(id=attendance_id).delete()
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def attenance_bulk_create(self, attendance_arr):
        create = Attendance.objects.using(self._current_app_schema()).bulk_create(attendance_arr)
        return create

    # attendance report
    def attendance_report(self,request,data,vys_page):
        condition =  Q(status=ActiveStatus.Active)
        year = request.GET.get('year')
        month = request.GET.get('month')
        query = request.GET.get('query')
        if month == '' or year == '':
            month = datetime.datetime.now().month
            year = datetime.datetime.now().year
        if query == '':
            query =None
        apiserv=AttendanceAPIService(self._scope())
        emp_arr=[]
        if 'arr' in data:
            emp_arr = data['arr']

        emp_data= apiserv.get_employee_info_hrms(emp_arr,vys_page,query)
        arr=[m['employee__id'] for m in emp_data][0:10]
        condition &= Q(log_date__year=year) & Q(log_date__month=month) &Q(user_id__in=arr)

        attendance_list = Attendance.objects.using(self._current_app_schema()).filter(condition).order_by('log_date').values('user_id','first_check_in','last_check_in','is_present','is_leave','log_date','duration','is_holiday','is_weekend')

        attendance_df = pd.DataFrame(attendance_list)
        if len(attendance_df)==0:
            attendance_df =pd.DataFrame(columns=['user_id','first_check_in','last_check_in','is_present','is_leave','log_date','duration','is_holiday','is_weekend'])

        # log_date_arr=[m.log_date for m in attendance_list:
        attendance_df['log_date'] = attendance_df['log_date'].astype(str)
        attendance_df['duration'].replace({np.nan:0}, inplace=True)
        attendance_df.replace({np.nan:'', pd.NaT: ''}, inplace=True)
        # attendance_df['first_check_in'] = attendance_df['first_check_in'].astype(str)
        attendance_df['first_check_in'] = attendance_df['first_check_in'].apply(time_to_m_sec)
        attendance_df['last_check_in'] = attendance_df['last_check_in'].apply(time_to_m_sec)
        # attendance_df['last_check_in'] = attendance_df['last_check_in'].astype(str)
        log_date_arr = list(set(attendance_df['log_date']))

        att_arr=[]
        for i in log_date_arr :
            att_data = {}
            d = attendance_df.loc[attendance_df['log_date'] == i].to_dict('records')
            att_data[i]=d
            att_arr.append(att_data)

        # emp report
        att_report=AttendanceReport.objects.using(self._current_app_schema()).filter(month=month,year=year,status=ActiveStatus.Active,employee_id__in=arr).values('employee_id','present_count','duration')
        if len(att_report)==0:
            att_report_df = pd.DataFrame(columns=['employee_id','present_count','duration'])
        else:
            att_report_df = pd.DataFrame(att_report)

        emp_df =pd.DataFrame(emp_data)

        df=pd.merge(emp_df,att_report_df,how='left',left_on='employee__id',right_on='employee_id')
        df.fillna(0, inplace=True)
        df =df.rename({"employee__code":"code","employee__full_name":"name","employee__id":"id"},axis=1)

        final_df=df[['code','name','id','present_count','duration']]
        final_data_list=final_df.to_dict('record')
        # final_df
        # response set
        list_data = NWisefinList()
        for i in final_data_list:
            list_data.append(i)
        paginator = NWisefinPaginator(emp_data, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)
        list_data.attendance_data= att_arr
        list_data.other = None
        return list_data

    # attendance report
    def attendance_new_report(self, request, data, vys_page):
        year = request.GET.get('year')
        month = request.GET.get('month')
        query =request.GET.get('query')
        if month == '' or year == '':
            month = datetime.datetime.now().month
            year = datetime.datetime.now().year
        else:
            year=int(year)
            month=int(month)

        api_serv = AttendanceAPIService(self._scope())
        # employee DF
        emp_arr = []
        if 'arr' in data:
            emp_arr = data['arr']
        employee_list = api_serv.get_employee_info_hrms(emp_arr, vys_page, query)
        arr = [m['employee__id'] for m in employee_list][0:10]

        # employee_list = api_serv.attendance_employee_info()
        employee_df = pd.DataFrame(employee_list)
        employee_df = employee_df.rename(
            {"employee__code": "code", "employee__full_name": "name", "employee__id": "id"}, axis=1)
        if len(employee_list) == 0:
            employee_df = pd.DataFrame(columns=['id', 'name', 'code'])

        # attendance report DF
        att_report = AttendanceReport.objects.using(self._current_app_schema()).filter(month=month, year=year,status=ActiveStatus.Active,employee_id__in=arr).values('employee_id', 'present_count', 'duration')

        att_report_df = pd.DataFrame(att_report)
        if len(att_report) == 0:
            att_report_df = pd.DataFrame(columns=['employee_id', 'present_count', 'duration'])

        employee_df = pd.merge(employee_df, att_report_df, how='left', left_on='id', right_on='employee_id')

        monthlydatetime_arr = [
            datetime.datetime.strptime('{:04d}-{:02d}-{:02d} 00:00:00'.format(year, month, date), '%Y-%m-%d %H:%M:%S')
            for date in range(1, monthrange(year, month)[1] + 1)]

        condition = Q(log_date__year=year) & Q(log_date__month=month)&Q(status=ActiveStatus.Active)&Q(user_id__in=arr)

        # attendance
        attendance_obj = Attendance.objects.using(self._current_app_schema()).filter(condition)
        leave_obj = api_serv.get_leave_type()

        attendance_df = self.attendance_details_info(attendance_obj, leave_obj)
        attendance_df = attendance_df[['log_date', 'flag', 'user_id']]
        attendance_df['log_date'] = attendance_df['log_date'].astype('datetime64[ns]')

        for mdate in monthlydatetime_arr:
            df = attendance_df[attendance_df['log_date'] == mdate]
            if len(df) == 0:
                df2 = None
            else:
                df2 = df.pivot(index='user_id', columns='log_date', values='flag')
                df2=df2[mdate]
                df2.reset_index(inplace=True,drop=True)
            employee_df[mdate] = df2
        # print(employee_df)

        employee_df.index = employee_df.index + 1
        employee_df = employee_df.drop(['employee_id'], axis=1)

        # rename
        col = employee_df.columns
        d = {}
        for k in col:
            if k.__class__.__name__ == 'datetime':
                s = str(k).split(' ')
                d[k] = s[0]
        employee_df = employee_df.rename(d, axis=1)
        employee_df['duration'] = employee_df['duration'].replace({np.nan: 0})
        employee_df['present_count'] = employee_df['present_count'].replace({np.nan: 0})

        resp_data=employee_df.to_dict('records')

        # response set
        list_data = NWisefinList()
        for i in resp_data:
            list_data.append(i)
        paginator = NWisefinPaginator(resp_data, vys_page.get_index(), 10)
        list_data.set_pagination(paginator)

        return list_data

    def month_year_report(self,request):
        year = request.GET.get('year')
        month = request.GET.get('month')
        if month == '' or year == '' or month == None or year == None:
            month = datetime.datetime.now().month
            year = datetime.datetime.now().year
        else:
            month = int(month)
            year = int(year)

        d={"year":year,"month":month}
        return d
    def attendancereportexcel(self, request,month,year):

        api_serv= AttendanceAPIService(self._scope())
        # employee DF
        employee_list = api_serv.attendance_employee_info()
        employee_df = pd.DataFrame(employee_list)
        employee_df = employee_df.rename({"employee__code": "code", "employee__full_name": "name", "employee__id": "id"}, axis=1)
        if len(employee_list) == 0:
            employee_df = pd.DataFrame(columns=['id', 'name', 'code'])

        # attendance report DF
        att_report =AttendanceReport.objects.using(self._current_app_schema()).filter(month=month,year=year,status=ActiveStatus.Active).values('employee_id','present_count','duration')
        att_report_df =pd.DataFrame(att_report)
        if len(att_report)==0:
            att_report_df = pd.DataFrame(columns=['employee_id','present_count','duration'])

        employee_df = pd.merge(employee_df,att_report_df,how='left',left_on='id',right_on='employee_id')

        # month date
        # monthlydatetime_arr=[]
        # monthlydays = ['{:04d}-{:02d}-{:02d} 00:00:00'.format(year, month, date) for date in range(1, monthrange(year, month)[1] + 1)]
        # for i in monthlydays:
        #     # df1[i]=None
        #     datetime_object = datetime.datetime.strptime(i, '%Y-%m-%d %H:%M:%S')
        #     monthlydatetime_arr.append(datetime_object)

        monthlydatetime_arr = [
            datetime.datetime.strptime('{:04d}-{:02d}-{:02d} 00:00:00'.format(year, month, date), '%Y-%m-%d %H:%M:%S')
            for date in range(1, monthrange(year, month)[1] + 1)]

        condition = Q(log_date__year=year) & Q(log_date__month=month)

        # attendance
        attendance_obj = Attendance.objects.using(self._current_app_schema()).filter(condition)
        leave_obj=api_serv.get_leave_type()

        attendance_df=self.attendance_details_info(attendance_obj,leave_obj)
        attendance_df=attendance_df[['log_date','flag','user_id']]
        attendance_df['log_date']=attendance_df['log_date'].astype('datetime64[ns]')

        for mdate in monthlydatetime_arr:
            df = attendance_df[attendance_df['log_date'] == mdate]
            if len(df) == 0:
                df2 = None
            else:
                df2 = df.pivot(index='user_id', columns='log_date', values='flag')
            employee_df[mdate] = df2
        # print(employee_df)

        employee_df.index = employee_df.index + 1
        employee_df=employee_df.drop(['id','employee_id'],axis=1)

        # rename
        col=employee_df.columns
        d={}
        for k in col :
            if k.__class__.__name__ == 'datetime':
                s=str(k).split(' ')
                d[k]=s[0]
        employee_df=employee_df.rename(d,axis=1)

        return employee_df

    def attendance_scheduler_val(self,s_date,entity_id):
        obj=AttendanceSchd.objects.using(self._current_app_schema()).filter(log_date=s_date,status=ActiveStatus.Active,entity_id=entity_id).order_by('id')
        print(obj)
        if len(obj)==0:
            return True
        return False

    def attendance_scheduler_insert(self,s_date):
        obj = AttendanceSchd.objects.using(self._current_app_schema()).create(log_date=s_date,is_scheduler=True,created_date=datetime.datetime.now(),entity_id=self._entity_id())
        return obj

    def attendance_report_update(self,month_data,arr,month,year,entity_id):
        # emp_arr=[j.employee_id for j in month_data]
        report_arr=[]
        if len(month_data) == 0:
            for i in arr:
                present,is_holiday ,is_weekend = i['is_present'],i['is_holiday'],i['is_weekend']
                duration = i['duration']
                if present ==True:
                    att_count=1
                else:
                    att_count=0
                #     if is_holiday == True or is_weekend == True:
                #         att_count = 0
                #     else:
                #         att_count, leave_count = 0,1
                print(i)
                print(att_count)
                r=AttendanceReport(employee_id=i['user_id'], month=month,year=year, status=ActiveStatus.Active,present_count=att_count,duration=duration,entity_id=entity_id)
                report_arr.append(r)

            AttendanceReport.objects.using(self._current_app_schema()).bulk_create(report_arr)

        # elif len(month_data) !=

        else:
            for j in month_data:
                for i in arr:
                    present_count = j['present_count']
                    # absent_count = j['leave_count']
                    month_duration = j['duration']
                    if j['employee_id'] == i['user_id']:
                        present, is_holiday, is_weekend = i['is_present'], i['is_holiday'], i['is_weekend']
                        day_duration = i['duration']
                        if present == True:
                            att_count = present_count+1
                        else:
                            att_count = present_count
                        #     if is_holiday == True or is_weekend == True:
                        #         att_count, leave_count = present_count, absent_count
                        #     else:
                        #         att_count, leave_count = present_count, absent_count+1

                        if month_duration == None:
                            duration = day_duration
                        elif day_duration ==None:
                            duration = month_duration
                        else:
                            duration = month_duration+day_duration
                        AttendanceReport.objects.using(self._current_app_schema()).filter(employee_id=i['user_id'], month=month,year=year,entity_id=entity_id,status=ActiveStatus.Active).update( present_count=att_count,duration=duration)
                        break

            # new employee
            if len(month_data) != len(arr):
                month_emp_arr=[m['employee_id'] for m in month_data]
                day_emp_arr=[n['user_id'] for n in arr]

                # diff_arr = month_emp_arr-day_emp_arr
                diff_arr=set(day_emp_arr).symmetric_difference(set(month_emp_arr))
                diff_arr =list(diff_arr)
                for j in diff_arr :
                    for i in arr:
                        if i['user_id']==j:
                            present, is_holiday, is_weekend = i['is_present'], i['is_holiday'], i['is_weekend']
                            duration = i['duration']
                            if present == True:
                                att_count = 1
                            else:
                                att_count = 0
                            AttendanceReport.objects.using(self._current_app_schema()).create(employee_id=i['user_id'], month=month, year=year,status=ActiveStatus.Active, present_count=att_count, duration=duration,entity_id=entity_id)



        return

    def get_attend_report(self,emp_arr,month,year,entity_id):
        att_rep_obj = AttendanceReport.objects.using(self._current_app_schema()).filter(employee_id__in=emp_arr, month=month,year=year,status=ActiveStatus.Active,entity_id=entity_id).values()
        return att_rep_obj


    def common_merge(self,df1,df2,type,on_left,on_right):
        df=pd.merge(df1,df2,how=type,on_left=on_left,on_right=on_right)
        return df

    def attendance_details_info(self,attendance_obj,leave_obj):
        attendance_data=attendance_obj.values()
        leave_data=leave_obj.values()

        attendance_df =pd.DataFrame(attendance_data)
        leave_df = pd.DataFrame(leave_data)
        leave_df = leave_df.rename({"id":"leave_id"},axis=1)
        leave_df=leave_df.drop(columns=['is_leave'],axis=1)

        df = pd.merge(attendance_df,leave_df,how='left',left_on='is_leave',right_on='leave_id')

        df['flag'] = df.apply(RuleEngineServ().flag_df, axis=1)

        return df



    def payroll_attendance_serv(self,request):
        employee_id = request.GET.get('employeeid', None)
        month = request.GET.get('month', None)
        year = request.GET.get('year', None)
        month = int(month)
        year = int(year)
        att_report = AttendanceReport.objects.using(self._current_app_schema()).filter(month=month, year=year,
                                                                                       status=ActiveStatus.Active,
                                                                                       employee_id=employee_id)
        present = 0
        if len(att_report) != 0:
            present = att_report[0].present_count
        days = monthrange(year, month)
        total_days = days[1]
        attendancedict = {"totaldays": total_days, "attendancedays": present, "paydays": present}
        resp = json.dumps(attendancedict, indent=4)
        return resp