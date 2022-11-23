import json


class EmployeeLeavecountResponse():

    def set_leave_count(self, leave_count):
        self.leave_count = leave_count

    def set_leave_data(self, leave_data):
        self.leave_data = leave_data

    def set_emp_leave(self,id,leave_arr):
        for i in leave_arr:
            if i.id==id:
                leave_data = {"id": i.id, "name": i.name, "code": i.code}
                self.leave_data=leave_data

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)