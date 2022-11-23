import json


class Payment_resp:
    category_id=None
    subcategory_id=None
    gl_id=None
    branch_id=None
    narration=None
    vendor_id=None
    expense_date=None
    amount=None
    gst_amount=None
    cc_id=None
    bs_id=None
    reference_number=None
    reference_code=None
    reference_text=None
    module=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_category_id(self,category_id):
        self.category_id=category_id
    def set_subcategory_id(self,subcategory_id):
        self.subcategory_id=subcategory_id
    def set_gl_id(self,gl_id):
        self.gl_id=gl_id
    def set_branch_id(self,branch_id):
        self.branch_id=branch_id
    def set_narration(self,narration):
        self.narration=narration
    def set_vendor_id(self,vendor_id):
        self.vendor_id=vendor_id
    def set_expense_date(self,expense_date):
        self.expense_date=expense_date.strftime("%Y-%m-%d")
        self.expense_date_ms =round(expense_date.timestamp() * 1000)
    def set_amount(self,amount):
        self.amount=amount
    def set_gst_amount(self,gst_amount):
        self.gst_amount=gst_amount
    def set_cc_id(self,cc_id):
        self.cc_id=cc_id
    def set_bs_id(self,bs_id):
        self.bs_id=bs_id
    def set_reference_number(self,reference_number):
        self.reference_number=reference_number
    def set_reference_code(self,reference_code):
        self.reference_code=reference_code
    def set_reference_text(self,reference_text):
        self.reference_text=reference_text
    def set_module(self,module):
        self.module=module
