import json


class VendorResponse:
    id = None
    name = None
    pan = None
    gst = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_pan(self, pan):
        self.pan = pan

    def set_gst(self, gst):
        self.gst = gst
