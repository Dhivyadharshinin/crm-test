"""Changes made to minimize the error occur when the variable names are incorrect."""
# 0001


class LeaveRequestVariable:
    ID = 'id'
    USER_ID = 'user_id'
    LEAVE_TYPE = 'leave_type'
    FROM_DATE = 'from_date'
    TO_DATE = 'to_date'
    TOTAL_DAYS = 'total_days'
    STATUS = 'status'
    REASON = 'reason'
    CREATED_BY = 'created_date'
    CREATED_DATE = 'created_by'
    UPDATED_BY = 'updated_date'
    UPDATED_DATE = 'updated_by'
    APPROVE_STATUS = 'approve_status'
    APPROVED_BY = 'approved_by'


class LeaveApproveQueueVariable:
    ID = 'id'
    LEAVE_REQUEST_ID = 'leave_request_id'
    STATUS = 'status'
    REMARKS = 'remarks'
    CREATED_DATE = 'created_date'
    CREATED_BY = 'created_by'
    UPDATED_DATE = 'updated_date'
    UPDATED_BY = 'updated_by'


class CheckInLogVariable:
    ID = 'id'
    USER_ID = 'user_id'
    LOG_DATE = 'log_date'
    LOG_TIME = 'log_time'
    LOG_TYPE = 'log_type'
    CHECK_IN_MODE = 'check_in_mode'
    STATUS = 'status'
    ORG_DETAIL_ID = 'org_detail_id'
    LATITUDE = 'latitude'
    LONGITUDE = 'longitude'
    IP = 'ip'


class AttendanceVariable:
    ID = 'id'
    USER_ID = 'user_id'
    FIRST_CHECK_IN = 'first_check_in'
    LAST_CHECK_IN = 'last_check_in'
    IS_PRESENT = 'is_present'
    LOG_DATE = 'log_date'
    IS_HOLIDAY = 'is_holiday'
    IS_WEEKEND = 'is_weekend'
    DURATION = 'duration'
    STATUS = 'status'


class AlertMessageVariable:
    ID = 'id'
    LEAVE_DATA_ID = 'leave_data_id'
    STATUS = 'status'
    MESSAGE = 'message'
    CREATED_DATE = 'created_date'
    ALERT_TO = 'alert_to'
    ALERT_FROM = 'alert_from'
