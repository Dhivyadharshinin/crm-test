import json
class Date_relaxation_resp:
    id= None
    tour_id= None
    status=None


    def set_id(self,id):
        self.id=id
    def set_tour_id(self,tour_id):
        self.tour_id=tour_id
    def set_status(self,status):
        self.status=status
    def set_request_no(self,request_no):
        self.request_no=request_no
    def set_request_date(self,request_date):
        if request_date is not None:
            self.request_date=request_date.strftime("%d-%b-%Y")
            self.request_date_ms =round(request_date.timestamp() * 1000)
        else:
            self.request_date = request_date
    def set_from_date(self,from_date):
        if from_date is not None:
            self.from_date=from_date.strftime("%d-%b-%Y")
            self.from_date_ms =round(from_date.timestamp() * 1000)
        else:
            self.from_date = from_date
    def set_to_date(self,to_date):
        if to_date is not None:
            self.to_date=to_date.strftime("%d-%b-%Y")
            self.to_date_ms =round(to_date.timestamp() * 1000)
        else:
            self.to_date = to_date
    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_reason(self,reason):
        self.reason=reason
    def set_reason_id(self,reason_id):
        self.reason_id=reason_id
    def set_approved_by(self,approved_by):
        self.approved_by=approved_by
    def set_approved_date(self,approved_date):
        if approved_date is not None:
            self.approved_date = approved_date.strftime("%d-%b-%Y")
            self.approved_date_ms =round(approved_date.timestamp() * 1000)
        else:
            self.approved_date = approved_date
    def set_insured(self,insured):
        self.insured=insured
    def set_insurance_no(self,insurance_no):
        self.insurance_no=insurance_no
    def set_comments(self,comments):
        self.comments=comments


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


