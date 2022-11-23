import json

class CostCentreResponse:
    id = None
    agreelandlord_mapid = None
    code = None
    no = None
    name= None
    remarks = None
    description = None
    status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_agreelandlord_mapid(self, agreelandlord_mapid):
        self.agreelandlord_mapid = agreelandlord_mapid

    def set_code(self, code):
        self.code = code

    def set_no(self, no):
        self.no = no

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_description(self, description):
        self.description = description

    def set_status(self, status):
        self.status = status

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_remarks(self):
        return self.remarks

    def get_description(self):
        return self.description

    def get_no(self):
        return self.no

    def get_name(self):
        return self.name


class BusinessSegmentResponse:
    id = None
    code = None
    no = None
    name = None
    remarks = None
    description = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_no(self, no):
        self.no = no

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_description(self, description):
        self.description = description

    def set_status(self, status):
        self.status = status

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_remarks(self):
        return self.remarks

    def get_description(self):
        return self.description

    def get_no(self):
        return self.no

    def get_name(self):
        return self.name
    def get_status(self):
        return self.status

class MasterBusinessSegmentResponse:
    id = None
    code = None
    no = None
    name = None
    remarks = None
    description = None
    sector_id=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_no(self, no):
        self.no = no
    def set_sector_id(self,sector_id):
        self.sector_id=sector_id

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_description(self, description):
        self.description = description

    def set_status(self, status):
        self.status = status



    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_remarks(self):
        return self.remarks

    def get_description(self):
        return self.description

    def get_no(self):
        return self.no

    def get_name(self):
        return self.name
    def get_status(self):
        return self.status