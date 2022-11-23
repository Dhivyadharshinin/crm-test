import json

class MasterBusinessSegmentrequest:
    id = None
    code = None
    no = None
    name = None
    description = None
    remarks = None
    sector_id = None
    bscode = None

    def __init__(self,masterbusiness_obj):
        if 'id' in masterbusiness_obj:
            self.id = masterbusiness_obj['id']
        if 'code' in masterbusiness_obj:
            self.code = masterbusiness_obj['code']
        if 'no' in masterbusiness_obj:
            self.no = masterbusiness_obj['no']
        if 'name' in masterbusiness_obj:
            self.name = masterbusiness_obj['name']
        if 'description' in masterbusiness_obj:
            self.description = masterbusiness_obj['description']
        if 'remarks' in masterbusiness_obj:
            self.remarks = masterbusiness_obj['remarks']
        if 'sector_id' in masterbusiness_obj:
            self.sector_id = masterbusiness_obj['sector_id']
        if 'bscode' in masterbusiness_obj:
            self.bscode = masterbusiness_obj['bscode']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_no(self):
        return self.no
    def get_name(self):
        return self.name
    def get_description(self):
        return self.description
    def get_remarks(self):
        return self.remarks
    def get_sector(self):
        return self.sector_id
