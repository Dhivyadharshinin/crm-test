from attendanceservice.util.attendancevariables import LeaveRequestVariable, LeaveApproveQueueVariable
import datetime
now = datetime.datetime.now()


# 0005
class LeaveDataRequest:
    id = None
    user_id = None
    leave_type = None
    from_date = None
    to_date = None
    total_days = None
    status = 1
    created_by = None
    created_date = now
    updated_by = None
    updated_date = now
    approve_status = None
    approved_by = None
    reason = None

    def __init__(self, req_obj):
        lr = LeaveRequestVariable()
        if lr.ID in req_obj:
            if req_obj[lr.ID] != '':
                self.id = req_obj[lr.ID]
        if lr.USER_ID in req_obj:
            if req_obj[lr.USER_ID] != '':
                self.user_id = req_obj[lr.USER_ID]
        if lr.LEAVE_TYPE in req_obj:
            if req_obj[lr.LEAVE_TYPE] != '':
                self.leave_type = req_obj[lr.LEAVE_TYPE]
        if lr.FROM_DATE in req_obj:
            if req_obj[lr.FROM_DATE] != '':
                self.from_date = req_obj[lr.FROM_DATE]
        if lr.TO_DATE in req_obj:
            if req_obj[lr.TO_DATE] != '':
                self.to_date = req_obj[lr.TO_DATE]
        if lr.TOTAL_DAYS in req_obj:
            if req_obj[lr.TOTAL_DAYS] != '':
                self.total_days = req_obj[lr.TOTAL_DAYS]
        if lr.STATUS in req_obj:
            if req_obj[lr.STATUS] != '':
                self.status = req_obj[lr.STATUS]
        if lr.CREATED_BY in req_obj:
            if req_obj[lr.CREATED_BY] != '':
                self.created_by = req_obj[lr.CREATED_BY]
        if lr.CREATED_DATE in req_obj:
            if req_obj[lr.CREATED_DATE] != '':
                self.created_date = req_obj[lr.CREATED_DATE]
        if lr.UPDATED_BY in req_obj:
            if req_obj[lr.UPDATED_BY] != '':
                self.updated_by = req_obj[lr.UPDATED_BY]
        if lr.UPDATED_DATE in req_obj:
            if req_obj[lr.UPDATED_DATE] != '':
                self.updated_date = req_obj[lr.UPDATED_DATE]
        if lr.APPROVE_STATUS in req_obj:
            if req_obj[lr.APPROVE_STATUS] != '':
                self.approve_status = req_obj[lr.APPROVE_STATUS]
        if lr.APPROVED_BY in req_obj:
            if req_obj[lr.APPROVED_BY] != '':
                self.approved_by = req_obj[lr.APPROVED_BY]
        if lr.REASON in req_obj:
            if req_obj[lr.REASON] != '':
                self.reason = req_obj[lr.REASON]

    def get_id(self):
        return self.id

    def get_user_id(self):
        return self.user_id

    def get_leave_type(self):
        return self.leave_type

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.to_date

    def get_total_days(self):
        return self.total_days

    def get_status(self):
        return self.status

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_update_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date

    def get_approve_status(self):
        return self.approve_status

    def get_approved_by(self):
        return self.approved_by

    def get_reason(self):
        return self.reason


class LeaveApproveRequest:
    id = None
    leave_request_id = None
    status = 1
    remarks = None

    def __init__(self, req_obj):
        var = LeaveApproveQueueVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]
        if var.REMARKS in req_obj:
            if req_obj[var.REMARKS] != '':
                self.remarks = req_obj[var.REMARKS]
        if var.LEAVE_REQUEST_ID in req_obj:
            if req_obj[var.LEAVE_REQUEST_ID] != '':
                self.leave_request_id = req_obj[var.LEAVE_REQUEST_ID]

    def get_id(self):
        return self.id

    def get_status(self):
        return self.status

    def get_leave_request_id(self):
        return self.leave_request_id

    def get_remarks(self):
        return self.remarks
