import json


class MasterBusinessSegmentresponse:
    id = None
    code = None
    sector_id = None
    no = None
    name = None
    description = None
    remarks = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_code(self,code):
        self.code = code
    def set_sector(self,sector_id):
        self.sector_id = sector_id
    def set_no(self,no):
        self.no = no
    def set_name(self,name):
        self.name = name
    def set_description(self,description):
        self.description = description
    def set_remarks(self,remarks):
        self.remarks = remarks