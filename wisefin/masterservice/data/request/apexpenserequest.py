import json
class APexpenseRequest:
    id = None
    head = None
    linedesc = None
    group = None
    sch16 = None
    sch16desc = None
    code =None
    exp_grp_id=None

    def __init__(self, cat_obj):
        if 'id' in cat_obj:
            self.id = cat_obj['id']
        if 'head' in cat_obj:
            self.head = cat_obj['head']
        if 'linedesc' in cat_obj:
            self.linedesc = cat_obj['linedesc']
        if 'group' in cat_obj:
            self.group = cat_obj['group']
        if 'sch16' in cat_obj:
            self.sch16 = cat_obj['sch16']
        if 'sch16desc' in cat_obj:
            self.sch16desc = cat_obj['sch16desc']
        if 'code' in cat_obj:
            self.code = cat_obj['code']
        if 'exp_grp_id' in cat_obj:
            self.exp_grp_id = cat_obj['exp_grp_id']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_head(self, head):
        self.head = head

    def set_linedesc(self, linedesc):
        self.linedesc = linedesc

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

    def get_code(self):
        return self.code
    def get_exp_grp_id(self):
        return self.exp_grp_id