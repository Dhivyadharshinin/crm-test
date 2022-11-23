import json

class EmployeeEducationDetailResponse:
    id, inst_name, passing_year, passing_month, percentage,city,title,stream = (None,)*8

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_inst_name(self, inst_name):
        self.inst_name = inst_name

    def set_passing_year(self, passing_year):
        self.passing_year = passing_year

    def set_passing_month(self, passing_month):
        self.passing_month = passing_month

    def set_percentage(self, percentage):
        self.percentage = percentage

    def set_city(self, city):
        self.city = city

    def set_title(self, title):
        self.title = title

    def set_stream(self, stream):
        self.stream = stream



class EmployeeExperiencesResponse:
    id, company, work_experience, doj, dor,role,city = (None,)*7

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_company(self, company):
        self.company = company

    def set_work_experience(self, work_experience):
        self.work_experience = work_experience

    def set_doj(self, doj):
        self.doj = str(doj)

    def set_dor(self, dor):
        self.dor = str(dor)

    def set_role(self, role):
        self.role = role

    def set_city(self, city):
        self.city = city