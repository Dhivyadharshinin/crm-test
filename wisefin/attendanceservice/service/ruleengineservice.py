from attendanceservice.util.attendanceutil import ActiveStatus,AttendanceActivityUtil


class RuleEngineServ:
    # Attendance flag rule
    def flag_df(self,df):
        if df['is_present'] == True:
            if df['is_leave']== -1:
                if df['is_holiday'] == True:
                    d = AttendanceActivityUtil.holiday
                elif df['is_weekend'] == True:
                    d = AttendanceActivityUtil.weekend
                else:
                    d=AttendanceActivityUtil.present
            else:
                d=AttendanceActivityUtil().common_util_fetch(AttendanceActivityUtil.arr,df['code'])
        else:
            if df['is_holiday'] == True:
                d = AttendanceActivityUtil.holiday
            elif df['is_weekend'] == True:
                d = AttendanceActivityUtil.weekend
            else:
                leave_type = AttendanceActivityUtil().common_util_fetch(AttendanceActivityUtil.arr, df['code'])
                if leave_type == None:
                    d=AttendanceActivityUtil.absent
                else:
                    d=AttendanceActivityUtil.absent +" ("+leave_type+")"
        return d