import json

class Designation_get:
    traveltime = None
    grade = None
    expense_id = None
    designation = None
    driverbata = None
    daysdrivereng = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_traveltime(self, traveltime):
        self.traveltime = traveltime
    def set_grade(self, grade):
        self.grade = grade
    def set_expense_id(self, expense_id):
        self.expense_id = expense_id
    def set_designation(self, designation):
        self.designation = designation
    def set_driverbata(self, driverbata):
        self.driverbata = driverbata
    def set_daysdrivereng(self, daysdrivereng):
        self.daysdrivereng = daysdrivereng

