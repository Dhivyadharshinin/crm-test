import json


class BSCCmapingResponse:
    id = None
    code = None
    name = None
    bsname = None
    subcat_id = None
    allocationlevel = None
    costdriver = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_bsname(self, bsname):
        self.bsname = bsname

    def set_subcat_id(self,subcat_id):
        self.subcat_id=subcat_id

    def set_allocationlevel(self,allocationlevel):
        self.allocationlevel=allocationlevel

    def set_costdriver(self,costdriver):
        self.costdriver=costdriver