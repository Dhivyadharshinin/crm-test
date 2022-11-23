import json
from cmsservice.util.cmsutil import get_transtatus, get_totype, TranApproverType, get_historystatus


class ProjectApprovalResponse:
    id = None
    to_type = None
    approver = None
    tran_status = None
    order = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_order(self, order):
        self.order = order

    def set_to_type(self, to_type):
        self.to_type = get_totype(to_type)

    def set_approver(self, approver):
        self.approver = approver

    def set_status(self, status):
        self.status = get_transtatus(status)


class ApprovalTranHistoryResponse:
    id = None
    to_type = None
    approver = None
    tran_status = None
    order = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_order(self, order):
        self.order = order

    def set_to_type(self, to_type):
        self.to_type = get_totype(to_type)

    def set_approver(self, approver, approver_type, appr_arr, appr_grp_arr):
        if approver_type == TranApproverType.employee:
            for i in appr_arr:
                if i['id'] == approver:
                    self.approver = i
                    break
        elif approver_type == TranApproverType.group:
            for i in appr_grp_arr:
                if i['id'] == approver:
                    self.approver = i
                    break
        else:
            self.approver = None

    def set_status(self, status):
        self.status = get_transtatus(status)
    def set_tran_status(self, tran_status):
        self.tran_status = get_transtatus(tran_status)


class ApprovalHistoryResponse:
    id = None
    comments = None
    approver = None
    created_date =None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_approver(self, approver, appr_arr):
        self.approver = None
        for i in appr_arr:
            if i['id'] == approver:
                self.approver = i
                break

    def set_comments(self, comments):
        self.comments = comments

    def set_approval_status(self, approval_status):
        self.approval_status = get_historystatus(approval_status)

    def set_created_date(self,created_date):
        self.created_date=str(created_date)