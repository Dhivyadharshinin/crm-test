import json

class CwipGroupRequest:

    id = name =  doctype = None
    gl = 0

    def __init__(self, assetlocation_data):
        if 'id' in assetlocation_data:
            self.id = assetlocation_data['id']
        if 'name' in assetlocation_data:
            self.name = assetlocation_data['name']
        if 'gl' in assetlocation_data:
            self.gl = assetlocation_data['gl']
        if 'doctype' in assetlocation_data:
            self.doctype = assetlocation_data['doctype']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_gl(self):
        return self.gl
    def get_doctype(self):
        return self.doctype

