import json


class GradeResponse:
    id=None
    name=None
    is_active=None
    code=None
    points=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
            self.name = name

    def set_is_active(self,is_active):
        self.is_active=is_active

    def set_code(self,code):
        self.code=code

    def set_points(self,points):
        self.points=points

class DesignationGradeMappingResponse:
    id=None
    designation_id = None
    grade_id = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None


    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_designation_id(self, designation_id):
            self.designation_id = designation_id

    def set_grade_id(self, grade_id):
            self.grade_id = grade_id

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def get_created_date(self, created_date):
        self.created_date = created_date

    def get_updated_by(self, updated_by):
        self.updated_by = updated_by

    def get_updated_date(self, updated_date):
        self.updated_date = updated_date

