import json

class General_LedgerResponse:

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
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_no(self, no):
        self.no = no

    def set_description(self, description):
        self.description = description

    def set_currency(self, currency):
        self.currency = currency

    def set_sortorder(self, sortorder):
        self.sortorder = sortorder

    def set_sortorderdescription(self, sortorderdescription):
        self.sortorderdesc = sortorderdescription

    def set_sch16_descbank(self , sch16_descbank):
        self.sch16_desc_bank = sch16_descbank

    def set_type(self, type):
        self.type = type

    def set_sch16_sortorder(self,sch16_sortorder):
        self.sch16_sortorder = sch16_sortorder
    def set_status(self,status):
        self.status=status