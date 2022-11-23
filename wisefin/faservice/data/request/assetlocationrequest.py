import json

class AssetLocationRequest:

    id =  refgid = branch_id = name = floor = remarks = None

    def __init__(self, assetlocation_data):
        if 'id' in assetlocation_data:
            self.id = assetlocation_data['id']
        if 'branch_id' in assetlocation_data:
            self.reftablegid = assetlocation_data['branch_id']
        if 'name' in assetlocation_data:
            self.name = assetlocation_data['name']
        if 'floor' in assetlocation_data:
            self.floor = assetlocation_data['floor']
        if 'remarks' in assetlocation_data:
            self.remarks = assetlocation_data['remarks']


    def get_id(self):
        return self.id
    def get_refgid(self):
        return self.refgid
    def get_branch_id(self):
        return self.reftablegid
    def get_name(self):
        return self.name
    def get_floor(self):
        return self.floor
    def get_remarks(self):
        return self.remarks
