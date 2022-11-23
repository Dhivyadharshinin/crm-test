import json

class OracleRequest:

    id = None
    CR_Number = None
    AP_Type = None

    def __init__(self,obj_apinv):
        if 'id' in obj_apinv:
            self.id=obj_apinv['id']
        if 'AP_Type' in obj_apinv:
            self.AP_Type = obj_apinv['AP_Type']
        if 'CR_Number' in obj_apinv:
            self.CR_Number = obj_apinv['CR_Number']

    def get_id(self):
        return self.id
    def get_AP_Type(self):
        return self.AP_Type
    def get_CR_Number(self):
        return self.CR_Number




