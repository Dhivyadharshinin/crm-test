import json

class EmployeemappingResponse:
    gid = None
    designation = None
    grade = None
    orderno = None
    status = 1
    data = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_gid(self, gid):
        self.gid = gid

    def set_designation(self, designation):
        self.designation = designation

    def set_grade(self, grade):
        self.grade = grade

    def set_orderno(self, orderno):
        self.orderno = orderno

    def set_status(self, status):
        self.status = status

    def set_data(self, data):
        self.data = data
