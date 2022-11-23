import json
from attendanceservice.util.attendanceutil import time_to_m_sec

# 0006
class LeaveResponse:
    id = ''
    user_id = ''
    leave_type = ''
    from_date = ''
    to_date = ''
    total_days = ''
    status = 1
    created_by = ''
    created_date = ''
    updated_by = ''
    updated_date = ''
    approve_status = ''
    approved_by = ''
    approve_message = ''
    reason = ''
    file = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_user_id(self, user_id,arr):
        self.user_id = ''
        for i in arr:
            if i.id == user_id:
                self.user_id = i
                break
    def set_user_id_data(self, user_id):
        self.user_id = ''
        if user_id is not None:
            self.user_id = user_id
    def set_leave_type(self, leave_type,typearr):
        self.leave_type = ''
        for i in typearr:
            if i.id == leave_type:
                self.leave_type = i
                break

    def set_leave_type_data(self, leave_type):
        self.leave_type = ''
        if leave_type is not None:
            self.leave_type = leave_type

    def set_from_date(self, from_date):
        self.from_date = ''
        if from_date is not None:
            self.from_date = time_to_m_sec(from_date)

    def set_to_date(self, to_date):
        self.to_date = ''
        if to_date is not None:
            self.to_date = time_to_m_sec(to_date)

    def set_total_days(self, total_days):
        self.total_days = ''
        if total_days is not None:
            self.total_days = total_days

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_created_by(self, created_by):
        self.created_by = ''
        if created_by is not None:
            self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_by = ''
        if created_date is not None:
            self.created_date = str(created_date)

    def set_updated_by(self, updated_by):
        self.updated_by = ''
        if updated_by is not None:
            self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = ''
        if updated_date is not None:
            self.updated_date = str(updated_date)

    def set_approve_status(self, approve_status):
        self.approve_status = ''
        if approve_status is not None:
            self.approve_status = approve_status

    def set_approved_by(self, approved_by, approve_arr):
        self.approved_by = ''
        for i in approve_arr:
            if i.id == approved_by:
                self.approved_by = i
                break
    def set_approved_by_data(self, approved_by):
        self.approved_by = ''
        if approved_by is not None:
            self.approved_by = approved_by


    def set_approve_message(self, approve_message):
        self.approve_message = ''
        if approve_message is not None:
            self.approve_message = approve_message

    def set_reason(self, reason):
        self.reason = ''
        if reason is not None:
            self.reason = reason

    def set_file(self, file):
        self.file = ''
        if file is not None:
            self.file = file


class LeaveApproveResponse:
    id = ''
    leave_request_id = ''
    status = 1
    remarks = ''
    created_by = ''
    created_date = ''
    updated_by = ''
    updated_date = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_leave_request_id(self, leave_request_id):
        self.leave_request_id = ''
        if leave_request_id is not None:
            self.leave_request_id = leave_request_id

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_remarks(self, remarks):
        self.remarks = ''
        if remarks is not None:
            self.remarks = remarks

    def set_created_by(self, created_by):
        self.created_by = ''
        if created_by is not None:
            self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = ''
        if created_date is not None:
            self.created_date = str(created_date)

    def set_updated_by(self, updated_by):
        self.updated_by = ''
        if updated_by is not None:
            self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = ''
        if updated_date is not None:
            self.updated_date = str(updated_date)


class AttendanceFileResponse:
    id = ''
    ref_id = ''
    tab_type = ''
    file_name = ''
    gen_file_name = ''
    status = ''
    file_id = ''

    def get(self):
        return not json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_ref_id(self, ref_id):
        self.ref_id = ''
        if ref_id is not None:
            self.ref_id = ref_id

    def set_tab_type(self, tab_type):
        self.tab_type = ''
        if tab_type is not None:
            self.tab_type = tab_type

    def set_file_name(self, file_name):
        self.file_name = ''
        if file_name is not None:
            self.file_name = file_name

    def set_gen_file_name(self, gen_file_name):
        self.gen_file_name = ''
        if gen_file_name is not None:
            self.gen_file_name = gen_file_name

    def set_status(self, status):
        self.status = ''
        if status is not None:
            self.status = status

    def set_file_id(self, file_id):
        self.file_id = ''
        if file_id is not None:
            self.file_id = file_id
