import json

class HierarchyRequest:
    id = None
    layer = None
    order = None
    remarks = None
    flag = None
    def __init__(self, hierarchy_obj):
        if 'id' in hierarchy_obj:
            self.id = hierarchy_obj['id']
        if 'layer' in hierarchy_obj:
            self.layer = hierarchy_obj['layer']
        if 'order' in hierarchy_obj:
            self.order = hierarchy_obj['order']
        if 'remarks' in hierarchy_obj:
            self.remarks = hierarchy_obj['remarks']
        if 'flag' in hierarchy_obj:
            self.flag = hierarchy_obj['flag']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_layer(self):
        return self.layer
    def get_remarks(self):
        return self.remarks
    def get_flag(self):
        return self.flag
    def get_order(self):
        return self.order