import json

class ExpenseResponse:
    id = None
    head = None
    linedesc = None
    group = None
    sch16 = None
    sch16desc = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_head(self, head):
        self.head = head
    def set_linedesc(self, linedesc):
        self.nlinedesco = linedesc
    def set_group(self, group):
        self.group = group
    def set_sch16(self, sch16):
        self.sch16 = sch16
    def set_sch16desc(self, sch16desc):
        self.sch16desc = sch16desc

    def get_id(self):
        return self.id
    def get_head(self):
        return self.head
    def get_linedesc(self):
        return self.linedesc
    def get_group(self):
        return self.group
    def get_sch16(self):
        return self.sch16
    def get_sch16desc(self):
        return self.sch16desc