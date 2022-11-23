import json

class HierarchyResponse:
    id = None
    layer = None
    order = None
    remarks = None
    flag = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_layer(self, layer):
        self.layer = layer

    def set_order(self, order):
        self.order = order

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_flag(self, flag):
        self.flag = flag

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
