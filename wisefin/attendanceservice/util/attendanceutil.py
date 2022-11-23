from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
import time

# 0002
class HolidayType:
    NATIONAL = 1
    LOCAL = 2
    STATE = 3
    COMPANY = 4
    OTHERS = 5

    NATIONAL_VAL = 'NATIONAL'
    LOCAL_VAL = 'LOCAL'
    STATE_VAL = 'STATE'
    COMPANY_VAL = 'COMPANY'
    OTHERS_VAL = 'OTHERS'

    ID_ARR = [NATIONAL, LOCAL, STATE, COMPANY, OTHERS]
    TEXT_ARR = [NATIONAL_VAL, LOCAL_VAL, STATE_VAL, COMPANY_VAL, OTHERS_VAL]
    ID_LENGTH = len(ID_ARR)


# 0003
def holiday_type_summary():
    hd_type = HolidayType()
    list_data = NWisefinList()
    for i in range(hd_type.ID_LENGTH):
        data = NWisefinLiteList()
        data.set_id(hd_type.ID_ARR[i])
        data.set_text(hd_type.TEXT_ARR[i])
        list_data.append(data)
    return list_data


# 0004
def holiday_type_get(type_id):
    hd_type = HolidayType()
    type_id = int(type_id)
    data = NWisefinLiteList()
    id_val = ''
    text_val = ''
    if type_id == hd_type.NATIONAL:
        id_val = hd_type.NATIONAL
        text_val = hd_type.NATIONAL_VAL
    elif type_id == hd_type.LOCAL:
        id_val = hd_type.LOCAL
        text_val = hd_type.LOCAL_VAL
    elif type_id == hd_type.STATE:
        id_val = hd_type.STATE
        text_val = hd_type.STATE_VAL
    elif type_id == hd_type.COMPANY:
        id_val = hd_type.COMPANY
        text_val = hd_type.COMPANY_VAL
    elif type_id == hd_type.OTHERS:
        id_val = hd_type.OTHERS
        text_val = hd_type.OTHERS_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data


class CheckLogType:
    CHECK_IN = 1
    CHECK_OUT = 2

    CHECK_IN_VAL = 'Check_In'
    CHECK_OUT_VAL = 'Check_Out'

    ID_ARR = [CHECK_IN, CHECK_OUT]
    TEXT_ARR = [CHECK_IN_VAL, CHECK_OUT_VAL]
    ID_LENGTH = len(ID_ARR)


def check_log_summary():
    c_type = CheckLogType()
    list_data = NWisefinList()
    for i in range(c_type.ID_LENGTH):
        data = NWisefinLiteList()
        data.set_id(c_type.ID_ARR[i])
        data.set_text(c_type.TEXT_ARR[i])
        list_data.append(data)
    return list_data


def check_log_get(type_id):
    c_type = CheckLogType()
    type_id = int(type_id)
    data = NWisefinLiteList()
    id_val = ''
    text_val = ''
    if type_id == c_type.CHECK_IN:
        id_val = c_type.CHECK_IN
        text_val = c_type.CHECK_IN_VAL
    elif type_id == c_type.CHECK_OUT:
        id_val = c_type.CHECK_OUT
        text_val = c_type.CHECK_OUT_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data

# TIME TO MILLISEC
def time_to_m_sec(time_data):
    if time_data == None or time_data == '':
        a=''
        return a
    time_data = int(time_data.timestamp() * 1000)
    return time_data

def date_to_m_sec(time_data):
    if time_data == None or time_data == '':
        a = ''
        return a
    a = int(time.mktime(time_data.timetuple()) * 1000)
    return a

class LeaveApproveType:
    APPROVE = 1
    REJECTED = 2
    PENDING = -1

    APPROVE_VAL = 'Approved'
    REJECTED_VAL = 'Rejected'
    PENDING_VAL = 'Pending'


def get_leave_approve_type(type_id):
    data = NWisefinLiteList()
    lat = LeaveApproveType()
    type_id = int(type_id)
    id_val = ''
    text_val = ''
    if type_id == lat.APPROVE:
        id_val = lat.APPROVE
        text_val = lat.APPROVE_VAL
    elif type_id == lat.REJECTED:
        id_val = lat.REJECTED
        text_val = lat.REJECTED_VAL
    elif type_id == lat.PENDING:
        id_val = lat.PENDING
        text_val = lat.PENDING_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data


class AttendanceSummaryType:
    CREATED_BY_ME = 1
    APPROVED_BY_ME = 2
    REJECTED_BY_ME = 3
    PENDING = 4
    ALL = 5

    CREATED_BY_ME_VAL = 'CREATED BY ME'
    APPROVED_BY_ME_VAL = 'APPROVED BY ME'
    REJECTED_BY_ME_VAL = 'REJECTED BY ME'
    PENDING_VAL = 'PENDING'
    ALL_VAL = 'ALL'

    ID_ARR = [CREATED_BY_ME, APPROVED_BY_ME, REJECTED_BY_ME, PENDING, ALL]
    TEXT_ARR = [CREATED_BY_ME_VAL, APPROVED_BY_ME_VAL, REJECTED_BY_ME_VAL, PENDING_VAL, ALL_VAL]
    ID_LENGTH = len(ID_ARR)


def attendance_summary_type():
    atd_type = AttendanceSummaryType()
    list_data = NWisefinList()
    for i in range(atd_type.ID_LENGTH):
        data = NWisefinLiteList()
        data.set_id(atd_type.ID_ARR[i])
        data.set_text(atd_type.TEXT_ARR[i])
        list_data.append(data)
    return list_data


def attendance_summary_type_get(type_id):
    atd_type = AttendanceSummaryType()
    type_id = int(type_id)
    data = NWisefinLiteList()
    id_val = ''
    text_val = ''
    if type_id == atd_type.CREATED_BY_ME:
        id_val = atd_type.CREATED_BY_ME
        text_val = atd_type.CREATED_BY_ME_VAL
    elif type_id == atd_type.APPROVED_BY_ME:
        id_val = atd_type.APPROVED_BY_ME
        text_val = atd_type.APPROVED_BY_ME_VAL
    elif type_id == atd_type.REJECTED_BY_ME:
        id_val = atd_type.REJECTED_BY_ME
        text_val = atd_type.REJECTED_BY_ME_VAL
    elif type_id == atd_type.PENDING:
        id_val = atd_type.PENDING
        text_val = atd_type.PENDING_VAL
    elif type_id == atd_type.ALL:
        id_val = atd_type.ALL
        text_val = atd_type.ALL_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data


class AlertType:
    REPEATED_CHECK_IN = 1
    LEAVE_INFO = 2
    PER_DAY_ATTENDANCE = 3

    REPEATED_CHECK_IN_VAL = 'Repeated Check_in'
    LEAVE_INFO_VAL = 'Leaves'
    PER_DAY_ATTENDANCE_VAL = 'Non Presence'

    ID_ARR = [REPEATED_CHECK_IN, LEAVE_INFO, PER_DAY_ATTENDANCE]
    TEXT_ARR = [REPEATED_CHECK_IN_VAL, LEAVE_INFO_VAL, PER_DAY_ATTENDANCE_VAL]
    ID_LENGTH = len(ID_ARR)


def alert_type_summary():
    alert_type = AlertType()
    list_data = NWisefinList()
    for i in range(alert_type.ID_LENGTH):
        data = NWisefinLiteList()
        data.set_id(alert_type.ID_ARR[i])
        data.set_text(alert_type.TEXT_ARR[i])
        list_data.append(data)
    return list_data


def alert_type_get(type_id):
    alert_type = AlertType()
    type_id = int(type_id)
    data = NWisefinLiteList()
    id_val = ''
    text_val = ''
    if type_id == alert_type.REPEATED_CHECK_IN:
        id_val = alert_type.REPEATED_CHECK_IN
        text_val = alert_type.REPEATED_CHECK_IN_VAL
    elif type_id == alert_type.LEAVE_INFO:
        id_val = alert_type.LEAVE_INFO
        text_val = alert_type.LEAVE_INFO_VAL
    elif type_id == alert_type.PER_DAY_ATTENDANCE:
        id_val = alert_type.PER_DAY_ATTENDANCE
        text_val = alert_type.PER_DAY_ATTENDANCE_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data


class AlertMessageType:
    REPEATED_CHECK_IN_MESSAGE = 'Repeated check_in log form the user'
    LEAVE_INFO_MESSAGE = 'User applied leave for multiple days'
    PER_DAY_ATTENDANCE_MESSAGE = 'user was not login the whole day'


class AttendanceDocumentUtil:
    LEAVE_REQUEST = 1


class InOut:
    IN = 1
    OUT = 2

    IN_VAL = 'IN'
    OUT_VAL = 'OUT'

class ActiveStatus:
    Active=1
    delete=2

class leaveTypeUtil:
    holiday = {"id":1,"text":"Holiday"}
    weekend = {"id":2,"text":"Weekend"}
    other = {'id':3,"text":'Leave'}

    arr = [holiday,weekend,other]


def common_util_fetch(arr,id):
    for  i in arr :
        if i['id'] == id:
            return i
    return

# role
def role_validation(request,emp_id,module):
    from utilityservice.permissions.filter.commonpermission import ModulePermission
    scope=request.scope
    module_permission = ModulePermission(scope)
    role_arr = module_permission.employee_modulerole(emp_id, module)
    return role_arr

class BalanceUtil:
    opening = {"id":1,"name":"Opening_balance"}
    earned = {"id":2,"name":"Earn_balance"}
    utilized = {"id":3,"name":"Utilized_balance"}

    arr=[opening,earned,utilized]
    arr_id=[opening['id'],earned['id'],utilized['id']]

class AttendanceActivityUtil:
    present='Present'
    absent='Absent'
    PL='PL'
    CL='CL'
    SL='SL'
    LOP='LOP'
    WFH='WFH'
    COMOFFF='COMP-OFF'
    holiday='Holiday'
    weekend='Weekend'

    arr =[present,absent,PL,CL,SL,LOP,WFH,COMOFFF,holiday,weekend]

    def common_util_fetch(self,arr, x):
        for i in arr:
            if i == x:
                return i
        return