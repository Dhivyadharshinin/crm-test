import json



class Asset_Details_Request:
    id=None
    assetdetails_gid=None
    assetdetails_productgid =None
    assetdetails_branchgid =None
    branch_name=None

    def __init__(self,json_input):
        if 'id' in json_input:
            self.id=json_input['id']
        if 'assetdetails_gid' in json_input:
            self.assetdetails_gid = json_input['assetdetails_gid']
        if 'assetdetails_productgid' in json_input:
            self.assetdetails_productgid = json_input['assetdetails_productgid']
        if 'assetdetails_branchgid' in json_input:
            self.assetdetails_branchgid = json_input['assetdetails_branchgid']
        if 'branch_name' in json_input:
            self.branch_name = json_input['branch_name']

    def get_id(self):
        return self.id
    def get_assetdetails_gid(self):
        return self.assetdetails_gid
    def get_assetdetails_productgid(self):
        return self.assetdetails_productgid
    def get_assetdetails_branchgid(self):
        return self.assetdetails_branchgid
    def get_branch_name(self):
        return self.branch_name
