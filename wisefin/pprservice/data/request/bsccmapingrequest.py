import json
class BSCCmapingRequest:
    id = None
    code = None
    name = None
    bsname=None
    subcat_id = None
    allocationlevel = None
    costdriver = None

    def __init__(self, bscc_obj):
        if 'id' in bscc_obj:
            self.id = bscc_obj['id']
        if 'code' in bscc_obj:
            self.code = bscc_obj['code']
        if 'name' in bscc_obj:
            self.name = bscc_obj['name']
        if 'bsname' in bscc_obj:
            self.bsname = bscc_obj['bsname']
        if 'subcat_id' in bscc_obj:
            self.subcat_id = bscc_obj['subcat_id']
        if 'allocationlevel' in bscc_obj:
            self.allocationlevel = bscc_obj['allocationlevel']
        if 'costdriver' in bscc_obj:
            self.costdriver = bscc_obj['costdriver']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_bsname(self):
        return self.bsname
    def get_subcat_id(self):
        return self.subcat_id
    def get_allocationlevel(self):
        return self.allocationlevel
    def get_costdriver(self):
        return self.costdriver
