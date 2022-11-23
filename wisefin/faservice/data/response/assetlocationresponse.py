import json


class AssetLocationResponse:
    id = refgid = reftablegid = name = floor = remarks = branch = expanded = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_refgid(self, refgid):
        self.refgid = refgid

    def set_reftablegid(self, reftablegid):
        self.reftablegid = reftablegid

    def set_branch(self, branch):
        self.branch = branch

    def set_expanded(self, expanded):
        self.expanded = expanded

    def set_name(self, name):
        self.name = name

    def set_floor(self, floor):
        self.floor = floor

    def set_remarks(self, remarks):
        self.remarks = remarks
