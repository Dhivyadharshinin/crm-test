import json



class SecurityguardResponse:
    id = None
    empcat = None
    empcatdesc = None
    empdesc=None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_empcat(self, empcat):
        self.empcat = empcat

    def set_empcatdesc(self, empcatdesc):
        self.empcatdesc = empcatdesc
    def set_empdesc(self, empdesc):
        self.empdesc = empdesc

class EmployeementtypeResponse:
    id = None
    emptype = None
    emptypedesc = None
    empcat_id = None
    empcat = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_emptype(self, emptype):
        self.emptype = emptype

    def set_emptypedesc(self, emptypedesc):
        self.emptypedesc = emptypedesc
    def set_empcat_id(self, empcat_id):
        self.empcat_id = empcat_id

    def set_empcat(self,empcat):
        empcat_data=SecurityguardResponse()
        empcat_data.set_empcat(empcat.id)
        empcat_data.set_empcat(empcat.empcat)
        empcat_data.set_empcatdesc(empcat.empcatdesc)
        dish_name=empcat.empcat+"-" +empcat.empcatdesc
        empcat_data.set_empdesc(dish_name)
        self.empcat=empcat_data