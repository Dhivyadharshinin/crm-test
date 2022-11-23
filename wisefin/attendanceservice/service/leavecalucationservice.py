from datetime import date
from utilityservice.data.response.nwisefinlist import NWisefinList
from attendanceservice.data.response.leavecountresponse import EmployeeLeavecountResponse
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
import pandas as pd
from utilityservice.service.attendanceapiservice import AttendanceAPIService
from attendanceservice.models.attendancemodels import LeaveEmployeeCount
from attendanceservice.util.attendanceutil import ActiveStatus,BalanceUtil,common_util_fetch
import json

class LeaveCalculationServ(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def employee_leave_count(self,year):
        obj=LeaveEmployeeCount.objects.filter(year=year,status=ActiveStatus.Active)
        return obj

    def employee_leave_mapping(self,year):
        apiserv=AttendanceAPIService(self._scope())

        employee_data=apiserv.get_all_employee()
        grade_mapping_data =apiserv.get_active_grade_mapping().values('leave_id','grade_id','grade__code','leave_count')
        empl_count_data = self.employee_leave_count(year).values('employee_id','leave_id','count')

        employee_df = pd.DataFrame(employee_data)
        employee_df = employee_df[['id','grade1']]
        grade_map_df = pd.DataFrame(grade_mapping_data)
        emp_leave_df = pd.DataFrame(empl_count_data)

        df1 = pd.merge(employee_df,grade_map_df,how='left',left_on='grade1',right_on='grade__code')

        df2 = pd.merge(df1,emp_leave_df,how='left',left_on='employee_id',right_on='employee_id')

        return

    def employee_leavecount(self,request, emp_id):
        is_admin = request.GET.get('is_admin')
        if is_admin != None:
            year=request.GET.get('year')
            emp_id = request.GET.get('emp_id')
        else:
            year=date.today().year

        apiserv=AttendanceAPIService(self._scope())
        # leave employee
        leave_emp_count = LeaveEmployeeCount.objects.filter(employee_id=emp_id,status=ActiveStatus.Active,year=year).values('employee_id','leave_id','leave_count','balance_type')
        leave_count_df = pd.DataFrame(leave_emp_count)
        if len(leave_count_df) ==0:
            leave_count_df = pd.DataFrame(columns=['employee_id','leave_id','leave_count','balance_type'])

        # leave type
        leave_type = apiserv.get_isleave_type()
        leave_type_data= leave_type.values('id','code','name')
        leave_type_df = pd.DataFrame(leave_type_data)
        if len(leave_type_df) == 0:
            leave_type_df = pd.DataFrame(columns=['id','code','name'])


        df = leave_count_df.pivot(index='leave_id', columns='balance_type', values='leave_count')

        df2 = pd.merge(df,leave_type_df,how='left',left_on='leave_id',right_on='id')

        # rename
        col = df2.columns
        d = {}
        for k in col:
            if k in BalanceUtil.arr_id:
                a=common_util_fetch(BalanceUtil.arr,k)
                d[k]=a['name']

        df2 = df2.rename(d, axis=1)
        # setting missing columns
        df2 = self.balance_val_df(df2)
        if len(df2)==0:
            df2=pd.DataFrame(columns=[BalanceUtil.opening['name'],BalanceUtil.earned['name'],BalanceUtil.utilized['name'],'id','code','name','balance'])
        else:
            df2['balance'] =df2.apply(self.balance_df,axis=1)

        data = df2.to_dict('records')
        r= {"data":data}
        resp = json.dumps(r,indent=4)

        return resp

    def balance_df(self,df):
        d = df[(BalanceUtil.opening['name'])]+df[(BalanceUtil.earned['name'])]-df[(BalanceUtil.utilized['name'])]
        return d

    def balance_val_df(self,df):
        df_keys = df.columns
        if BalanceUtil.opening['name'] not in df_keys:
            df[BalanceUtil.opening['name']] = 0
        if BalanceUtil.earned['name'] not in df_keys:
            df[BalanceUtil.earned['name']] = 0
        if BalanceUtil.utilized['name'] not in df_keys:
            df[BalanceUtil.utilized['name']] = 0
        return df


































