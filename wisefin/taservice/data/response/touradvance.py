
import json
from taservice.data.response.tourmaker import TourMaker

class TourAdvanceResponse:
    id = None
    tourgid = None
    reason = None
    reqamount = None
    appamount = None
    invoiceheadergid = None
    status = None
    requestno = None
    requestdate = None
    empgid = None
    empdesignation = None
    empgrade = None
    empbranchgid = None
    startdate = None
    enddate = None
    remarks = None
    approvedby = None
    detail = []
    approve = []
    opening_balance=0
    quantum_of_funds=0
    employee_name=None
    employee_code=None
    is_tour_ended=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_id(self, id):
        self.id = id
    def set_tourgid(self, tourgid):
        self.tourgid = tourgid
    def set_requestno(self, requestno):
        self.requestno = requestno
    def set_requestdate(self, requestdate):
        requestdate = requestdate.strftime("%d-%b-%Y")
        self.requestdate = requestdate
    def set_empgid(self, empgid):
        self.empgid = empgid
    def set_reason(self, reason):
        self.reason = reason
    def set_reason_id(self, reason_id):
        self.reason_id = reason_id
    def set_empdesignation(self, empdesignation):
        self.empdesignation = empdesignation
    def set_empgrade(self, empgrade):
        self.empgrade = empgrade
    def set_empbranchgid(self, empbranchgid):
        self.empbranchgid = empbranchgid
    def set_startdate(self, startdate):
        self.startdate = startdate.strftime("%d-%b-%Y")
    def set_enddate(self, enddate):
        self.enddate = enddate.strftime("%d-%b-%Y")
    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof
    def set_status(self, status):
        self.status = status
    def set_status_name(self, status_name):
        self.status_name = status_name
    def set_approveddate(self, approveddate):
        self.approveddate = approveddate.strftime("%d-%b-%Y")
    def set_approvedby(self, approvedby):
        self.approvedby = approvedby
    def set_approver_id(self, approver_id):
        self.approver_id = approver_id
    def set_approver_code(self, approver_code):
        self.approver_code = approver_code
    def set_approver(self, approver):
        self.approver = approver
    def set_paid_advance_amount(self, paid_advance_amount):
        self.paid_advance_amount = paid_advance_amount
    def set_paid_advance_balance(self, paid_advance_balance):
        self.paid_advance_balance = paid_advance_balance
    def set_ppxheader_date(self, ppxheader_date):
        self.ppxheader_date = ppxheader_date
    def set_total_paid_advance(self, total_paid_advance):
        self.total_paid_advance = total_paid_advance
    def set_branch_name(self, branch_name):
        self.branch_name = branch_name
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_branch_code(self, branch_code):
        self.branch_code = branch_code
    def set_apptype(self, apptype):
        self.apptype = apptype
    def set_applevel(self, applevel):
        self.applevel = applevel
    def set_appcomment(self, appcomment):
        self.appcomment = appcomment
    def set_reqamount(self, reqamount):
        self.reqamount = reqamount
    def set_appamount(self, appamount):
        self.appamount = appamount
    def set_invoiceheadergid(self, invoiceheadergid):
        self.invoiceheadergid = invoiceheadergid
    def set_advance(self, advance):
        self.advance = advance
    def set_adjustamount(self, adjustamount):
        self.adjustamount = adjustamount
    def set_crnno(self, crnno):
        self.crnno = crnno
    def set_debit_categorygid(self, debit_categorygid):
        self.debit_categorygid = debit_categorygid
    def set_debit_subcategorygid(self, debit_subcategorygid):
        self.debit_subcategorygid = debit_subcategorygid
    def set_ppx_headergid(self, ppx_headergid):
        self.ppx_headergid = ppx_headergid
    def set_approver_branch_data(self, approver_branch_data):
        self.approver_branch_data = approver_branch_data

    def set_approver_data(self, id, name, code):
        response = TourMaker()
        response.set_id(id)
        response.set_name(name)
        response.set_code(code)
        self.approver_data = response

    def set_approve(self, approve):
        self.approve = approve
    def set_detail(self, detail):
        self.detail = detail

    def get_id(self):
        return self.id
    def get_requestno(self):
        return self.requestno
    def get_requestdate(self):
        return self.requestdate
    def get_empgid(self):
        return self.empgid
    def get_reason(self):
        return self.reason
    def get_empdesignation(self):
        return self.empdesignation
    def get_empgrade(self):
        return self.empgrade
    def get_empbranchgid(self):
        return self.empbranchgid
    def get_startdate(self):
        return self.startdate
    def get_enddate(self):
        return self.enddate
    def get_remarks(self):
        return self.remarks
    def get_onbehalfof(self):
        return self.onbehalfof
    def get_status(self):
        return self.status
    def get_detail(self):
        return self.detail
    def get_approvedby(self):
        return self.approvedby
    def get_approveddate(self):
        return self.approveddate
    def get_apptype(self):
        return self.apptype
    def get_applevel(self):
        return self.applevel
    def get_appcomment(self):
        return self.appcomment
    def get_approve(self):
        return self.approve
    def get_tourgid(self):
        return self.tourgid
    def get_reqamount(self):
        return self.reqamount
    def get_appamount(self):
        return self.appamount
    def get_invoiceheadergid(self):
        return self.invoiceheadergid
    def set_opening_balance(self,opening_balance):
        self.opening_balance=opening_balance
    def set_quantum_of_funds(self,quantum_of_funds):
        self.quantum_of_funds=quantum_of_funds
    def set_tour_status(self, tour_status):
        self.tour_status = tour_status
    def set_advance_status(self, advance_status):
        self.advance_status = advance_status
    def set_advance_cancel_status(self, advance_cancel_status):
        self.advance_cancel_status = advance_cancel_status
    def set_advance_cancel_status_id(self, advance_cancel_status_id):
        self.advance_cancel_status_id = advance_cancel_status_id
    def set_claim_status(self, claim_status):
        self.claim_status = claim_status
    def set_tour_status_id(self, tour_status_id):
        self.tour_status_id = tour_status_id
    def set_advance_status_id(self, advance_status_id):
        self.advance_status_id = advance_status_id
    def set_claim_status_id(self, claim_status_id):
        self.claim_status_id = claim_status_id
    def set_is_tour_ended(self, is_tour_ended):
        self.is_tour_ended = is_tour_ended
    def set_requested_amount(self, requested_amount):
        self.requested_amount = requested_amount
    def set_approved_amount(self, approved_amount):
        self.approved_amount = approved_amount
