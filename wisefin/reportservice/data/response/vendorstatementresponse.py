import json
from django.template.defaultfilters import length
class VendorstatementResponse:
    Crno = None
    Invoiceno = None
    Invoice_Date = None
    Total_Amount = None
    Base_Amount = None
    Tax_Amount = None
    TDS_Amount = None
    supplier_name = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_Crno(self, Crno):
        self.Crno = Crno
    def set_Invoiceno(self, Invoiceno):
        self.Invoiceno = Invoiceno
    def set_Invoice_Date(self, Invoice_Date):
        self.Invoice_Date = Invoice_Date
    def set_Base_Amount(self, Base_Amount):
        self.Base_Amount = str(Base_Amount)
    def set_Tax_Amount(self, Tax_Amount):
        self.Tax_Amount = Tax_Amount
    def set_TDS_Amount(self, TDS_Amount):
        self.TDS_Amount = TDS_Amount
