import json

from cmsservice.util.cmsutil import get_approvalstatus,get_agreementtemplate_util


class LegalResponse:
    id = None
    name = None
    clauses = None
    description = None
    type = None
    approval_status = None
    approval_by=None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type(self, type):
        self.type = get_agreementtemplate_util(type)

    def set_name(self, name):
        self.name = name
    def set_is_approver(self, is_approver):
        self.is_approver = is_approver
    def set_is_created_by(self, is_created_by):
        self.is_created_by = is_created_by
    def set_clauses(self, clauses):
        self.clauses = clauses
    def set_description(self, description):
        self.description = description
    def set_approval_status(self, approval_status):
        self.approval_status = get_approvalstatus(approval_status)
    def set_proposalclauses(self, proposalclauses):
        self.proposalclauses = proposalclauses
    def set_clauses_name(self, clauses_name):
        self.clauses_name = clauses_name
    def set_proposal_id(self, proposal_id):
        self.proposal_id = proposal_id
    def set_proposal_name(self, proposal_name):
        self.proposal_name = proposal_name
    def set_agreement(self, agreement):
        self.agreement = agreement
    def set_end_date(self, end_date):
        self.end_date = str(end_date)
    def set_start_date(self, start_date):
        self.start_date = str(start_date)
    def set_is_issued(self, is_issued):
        self.is_issued = is_issued
    def set_is_accepted(self, is_accepted):
        self.is_accepted = is_accepted

    def set_is_return(self,is_return):
        self.is_return = is_return
    def set_version(self,version):
        self.version = version
    def set_is_created(self, is_created):
        self.is_created = is_created

    def set_order(self, order):
        self.order = order
    # def set_approval_by(self, approval_by):
    #     self.approval_by = approval_by

    def set_approval_by(self, approver, appr_arr):
        for i in appr_arr:
            if i['id'] == approver:
                self.approval_by = i
                break

class SuperscriptResponse:
    id = None
    start_index ,end_index = None,None
    comments,order = None,None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_start_index(self,start_index):
        self.start_index=start_index

    def set_end_index(self,end_index):
        self.end_index=end_index

    def set_order(self,order):
        self.order=order

    def set_comments(self, v_id, arr,emp_arr,vow_emp_arr):
        # cmt_arr=[{"id":i.id,"content":i.comment}for i in arr if i.ref_id == v_id]
        # self.comments = cmt_arr

        cmt_arr=[]
        for i in arr :
            created_by=None
            if i.ref_id == v_id:
                if i.is_user == False:
                    # vow employee
                    for v in vow_emp_arr:
                        if v['id'] == i.created_by:
                            created_by = v
                            break
                else:
                    # employee
                    for e in emp_arr:
                        if e['id'] == i.created_by:
                            created_by = e
                            break
                d={"id":i.id,"content":i.comment,"created_by":created_by,"created_date":str(i.created_date),"is_user":i.is_user}
                cmt_arr.append(d)

        self.comments = cmt_arr

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