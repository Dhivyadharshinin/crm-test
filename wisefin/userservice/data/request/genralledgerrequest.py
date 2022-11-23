class General_LedgerRequest:
    id = None
    no = None
    description = None
    currency = None
    sortorder = None
    sortorderdescription = None
    sch16_sortorder = None
    type = None
    sch16_descbank = None
    status=None
    def __init__(self, gl_data):
        if 'id' in gl_data:
            self.id = gl_data['id']
        if 'GL_NUMBER' in gl_data:
            self.no = gl_data['GL_NUMBER']
        if 'GL_DESCRIPTION' in gl_data:
            self.description = gl_data['GL_DESCRIPTION']
        if 'CURRENCY' in gl_data:
            self.currency = gl_data['CURRENCY']
        if 'N_SORT_ORDER' in gl_data:
            self.sortorder = gl_data['N_SORT_ORDER']
        if 'SORT_ORDER_DESCRIPTION' in gl_data:
            self.sortorderdescription = gl_data['SORT_ORDER_DESCRIPTION']
        if 'SCH16_SORT_ORDER' in gl_data:
            self.sch16_sortorder = gl_data['SCH16_SORT_ORDER']
        if 'V_TYPE' in gl_data:
            self.type = gl_data['V_TYPE']
        if 'SCH16_DESC_BANK' in gl_data:
            self.sch16_descbank = gl_data['SCH16_DESC_BANK']
        if 'status' in gl_data:
            self.status=gl_data['status']

    def get_id(self):
        return self.id
    def get_no(self):
        return self.no
    def get_description(self):
        return self.description
    def get_currency(self):
        return self.currency
    def get_sortorder(self):
        return self.sortorder
    def get_sortorder_description(self):
        return self.sortorderdescription
    def get_sch16_descbank(self):
        return self.sch16_descbank
    def get_type(self):
        return self.type
    def get_sch16_sortorder(self):
        return self.sch16_sortorder
    def get_status(self):
        return self.status
