import json


class CostCentreRequest:
    id = None
    code = None
    no = None
    name =None
    bscode =None
    remarks = None
    description = None
    status = None
    businesssegment_id=None
    def __init__(self, costcentre_obj):
        if 'id' in costcentre_obj:
            self.id = costcentre_obj['id']
        if 'code' in costcentre_obj:
            self.code = costcentre_obj['code']
        if 'no' in costcentre_obj:
            self.no = costcentre_obj['no']
        if 'name' in costcentre_obj:
            self.name = costcentre_obj['name']
        if 'remarks' in costcentre_obj:
            self.remarks = costcentre_obj['remarks']
        if 'description' in costcentre_obj:
            self.description = costcentre_obj['description']
        if 'bscode' in costcentre_obj:
            self.bscode=costcentre_obj['bscode']
        if 'status' in costcentre_obj:
            self.status=costcentre_obj['status']
        if 'businesssegment_id' in costcentre_obj:
            self.businesssegment_id=costcentre_obj['businesssegment_id']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

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

    def get_bscode(self):
        return self.bscode


    def get_status(self):
        return self.status
    def get_businesssegment_id(self):
        return self.businesssegment_id



class BusinessSegmentRequest:
    id = None
    code = None
    no = None
    name =None
    remarks = None
    description = None
    buscode=None
    status=None
    masterbussinesssegment_id=None
    def __init__(self, businesssegment_obj):
        if 'id' in businesssegment_obj:
            self.id = businesssegment_obj['id']
        if 'code' in businesssegment_obj:
            self.code = businesssegment_obj['code']
        if 'no' in businesssegment_obj:
            self.no = businesssegment_obj['no']
        if 'name' in businesssegment_obj:
            self.name = businesssegment_obj['name']
        if 'remarks' in businesssegment_obj:
            self.remarks = businesssegment_obj['remarks']
        if 'description' in businesssegment_obj:
            self.description = businesssegment_obj['description']
        if 'buscode' in businesssegment_obj:
            self.buscode = businesssegment_obj['buscode']

        if 'status' in businesssegment_obj:
            self.status = businesssegment_obj['status']
        if 'masterbussinesssegment_id' in businesssegment_obj:
            self.masterbussinesssegment_id =businesssegment_obj['masterbussinesssegment_id']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

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

    def get_buscode(self):
        return self.buscode
    def get_masterbussinesssegment_id(self):
        return self.masterbussinesssegment_id


class MasterBusinesssegmentRequest:
    id=None
    code=None
    sector_id=None
    no=None
    name=None
    description=None
    remarks=None
    status=None

    def __init__(self, masterbusinesssegment_obj):
        if 'id' in masterbusinesssegment_obj:
            self.id = masterbusinesssegment_obj['id']
        if 'code' in masterbusinesssegment_obj:
            self.code = masterbusinesssegment_obj['code']
        if 'sector_id' in masterbusinesssegment_obj:
            self.sector_id = masterbusinesssegment_obj['sector_id']
        if 'no' in masterbusinesssegment_obj:
            self.no = masterbusinesssegment_obj['no']
        if 'name' in masterbusinesssegment_obj:
            self.name = masterbusinesssegment_obj['name']
        if 'description' in masterbusinesssegment_obj:
            self.description = masterbusinesssegment_obj['description']
        if 'remarks' in masterbusinesssegment_obj:
            self.remarks = masterbusinesssegment_obj['remarks']
        if 'status' in masterbusinesssegment_obj:
            self.status = masterbusinesssegment_obj['status']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code
    def get_sector_id(self):
        return self.sector_id

    def get_no(self):
        return self.no

    def get_name(self):
        return self.name
    def get_remarks(self):
        return self.remarks

    def get_description(self):
        return self.description
    def get_status(self):
        return self.status

