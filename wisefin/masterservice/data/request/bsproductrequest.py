class BusinessProductRequest:
    id = None
    bsproduct_code = None
    bsproduct_name = None

    def __init__(self, bsp_data):
        if 'id' in bsp_data:
            self.id = bsp_data['id']
        if 'bsproduct_code' in bsp_data:
            self.bsproduct_code = bsp_data['bsproduct_code']
        if 'bsproduct_name' in bsp_data:
            self.bsproduct_name = bsp_data['bsproduct_name']

    def get_id(self):
        return self.id
    def get_bsproduct_code(self):
        return self.bsproduct_code
    def get_bsproduct_name(self):
        return self.bsproduct_name

#test