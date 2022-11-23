import json


class AssetGroupResponse:

    id = no= apcatategory = apsubcatategory = capdate = assetvalue = branch_id = remarks = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_no(self, no):
        self.no = no
    def set_apcatategory(self, apcatategory):
        self.apcatategory = apcatategory
    def set_apsubcatategory(self, apsubcatategory):
        self.apsubcatategory = apsubcatategory
    def set_capdate(self, capdate):
        self.capdate =str(capdate)
    def set_assetvalue(self, assetvalue):
        self.assetvalue = str(assetvalue)
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_remarks(self, remarks):
        self.remarks = remarks


