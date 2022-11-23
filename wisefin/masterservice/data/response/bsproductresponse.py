import json
#test
class BusinessProductResponse:
    id = None
    bsproduct_code = None
    bsproduct_name = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_bsproduct_code(self, bsproduct_code):
        self.bsproduct_code = bsproduct_code

    def set_bsproduct_name(self, bsproduct_name):
        self.bsproduct_name = bsproduct_name
