import json
from vendorservice.data.response.taxresponse import TaxResponse

class SubTaxResponse:
    id = None
    tax_id = None
    subtaxamount = None
    code = None
    name = None
    remarks = None
    glno = None
    uom_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_uom_name(self, uom_name):
        self.uom_name = uom_name

    def set_code(self, code):
        self.code = code
    def set_subtaxamount(self, amount):
        self.subtaxamount = amount

    def set_name(self, name):
        self.name = name

    def set_subtaxamount(self, subtaxamount):
        self.subtaxamount = str(subtaxamount)

    def set_tax_id(self, tax_id):
        self.tax_id = tax_id

    def set_tax(self, tax):
        tax_data = TaxResponse()
        tax_data.set_id(tax.id)
        tax_data.set_code(tax.code)
        tax_data.set_name(tax.name)
        tax_data.set_receivable(tax.receivable)
        tax_data.set_payable(tax.payable)
        tax_data.set_glno(tax.glno)
        self.tax = tax_data

    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_category_id(self, cat_id):
        self.remarks = cat_id
    def set_subcategory_id(self, subcat_id):
        self.remarks = subcat_id

    def set_glno(self, glno):
        self.glno = glno

    def set_unitprice(self, unitprice):
        self.unitprice = unitprice