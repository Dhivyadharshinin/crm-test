import json
from cmsservice.util.cmsutil import get_commentsreftype, get_commentstype


class Commentsresponse:
    id = None
    ref_id = None
    ref_type = None
    ref_type_id = None
    comment = None
    type = None
    is_user = None
    file_data = None
    created_by = None
    created_date = None
    q_type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_ref_type(self, ref_type):
        self.ref_type = get_commentsreftype(ref_type)

    def set_ref_type_id(self, ref_type_id):
        self.ref_type_id = ref_type_id

    def set_comment(self, comment):
        self.comment = comment

    def set_type(self, type):
        self.type = get_commentstype(type)

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_is_user(self, is_user):
        self.is_user = is_user

    def set_file_data(self, prj_id, file_data):

        arr = [{"id": i.id, "file_name": i.file_name, "file_id":i.file_id} for i in file_data if i.rel_id == prj_id]
        self.file_data = arr

    def set_reply_id(self, reply_id):
        self.reply_id = reply_id

    def set_reply(self, reply):
        self.reply = reply

    def set_created_date(self, created_date):
        self.created_date = created_date.strftime("%d-%b-%Y %H:%M:%S")

    def set_created_by(self, emp_arr, vow_emp_arr, emp_id, is_user):
        self.created_by = None
        if is_user == False:
            # vow employee
            for i in vow_emp_arr:
                if i['id'] == emp_id:
                    self.created_by = i
                    break
        else:
            # employee
            for i in emp_arr:
                if i['id'] == emp_id:
                    self.created_by = i
                    break

    def set_q_type(self, q_type):
        self.q_type = q_type


class CommentsReplyresponse:
    id = None
    comment = None
    is_user = None
    created_by = None
    created_date = None
    file_data = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_comment(self, comment):
        self.comment = comment

    def set_is_user(self, is_user):
        self.is_user = is_user

    def set_file_data(self, prj_id, file_data):
        arr = [{"id": i.id, "file_name": i.file_name, "file_id": i.file_id} for i in file_data if i.rel_id == prj_id]
        self.file_data = arr

    def set_created_date(self, created_date):
        self.created_date = created_date.strftime("%d-%b-%Y %H:%M:%S")

    def set_created_by(self, emp_arr, vow_emp_arr, emp_id, is_user):
        self.created_by = None
        if is_user == False:
            # vow employee
            for i in vow_emp_arr:
                if i['id'] == emp_id:
                    self.created_by = i
                    break
        else:
            # employee
            for i in emp_arr:
                if i['id'] == emp_id:
                    self.created_by = i
                    break
