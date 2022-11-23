import json

import pandas as pd

from entryservice.util.entryutil import EntryType
from reportservice.util.reportutil import DictObj

entrytype=EntryType()
import json
from django.template.defaultfilters import length
class templateResponse:
    id = None
    code = None
    name = None
    is_parent = None
    displayname = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_name(self, name):
        self.name = name
    def set_is_parent(self, is_parent):
        self.is_parent = is_parent
    def set_displayname(self, displayname):
        self.displayname = displayname

class TemplateResponse:
    #parametername_id, gl_no, transaction, Values,value_to_taken, wisefin_category, wisefin_subcategory,display
    id = None
    parametername_id = None
    gl_no = None
    transaction = None
    Values = None
    value_to_taken = None
    wisefin_category = None
    wisefin_subcategory = None
    display = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_gl_no(self, gl_no):
        self.debitglno = gl_no
    def set_transaction(self, transaction):
        self.transaction = transaction
    def set_Values(self, Values):
        self.amount = str(Values)
    # def set_value_to_taken(self, value_to_taken):
    #     self.value_to_taken = value_to_taken
    def set_wisefin_category(self, wisefin_category):
        self.category_code = {"code":wisefin_category}
    def set_wisefin_subcategory(self, wisefin_subcategory):
        self.subcategory_code = {"code":wisefin_subcategory}
    def set_display(self, display):
        self.display = display


class DebitList:
    apdebit = []
    pagination = None
    count = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        self.apdebit = []

    def set_list(self, list):
        self.apdebit = list

    def get_list(self):
        return self.apdebit

    def append(self, obj):
        self.apdebit.append(obj)

    def set_listcount(self, count):
        self.count = count

    def get_listcount(self):
        return self.count

    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.apdebit) > pagination.limit:
            self.apdebit.pop()

    def get_pagination(self):
        return self.pagination

class ParamnametemplateResponse:
    id = None
    code = None
    paramname = None
    columnnamedebit = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_paramname(self, paramname):
        self.paramname = paramname
    def set_columnnamedebit(self, columnnamedebit):
        self.columnnamedebit = columnnamedebit

class templatenameResponse:
    id = None
    gl_no = None
    transaction = None
    value_to_taken = None
    wisefin_category = None
    wisefin_subcategory = None
    display = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_gl_no(self, gl_no):
        self.debitglno = gl_no
    def set_transaction(self, transaction):
        self.transaction = transaction
    def set_Values(self, Values):
        self.amount = str(Values)
    def set_value_to_taken(self, value_to_taken):
         self.value_to_taken = value_to_taken
    def set_wisefin_category(self, wisefin_category):
        self.category_code = wisefin_category
    def set_wisefin_subcategory(self, wisefin_subcategory):
        self.subcategory_code = wisefin_subcategory
    def set_display(self, display):
        self.display = display

class CreditList:
    apcredit = []
    pagination = None
    count = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        self.apcredit = []

    def set_list(self, list):
        self.apcredit = list

    def get_list(self):
        return self.apcredit

    def append(self, obj):
        self.apcredit.append(obj)

    def set_listcount(self, count):
        self.count = count

    def get_listcount(self):
        return self.count

    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.apcredit) > pagination.limit:
            self.apcredit.pop()

    def get_pagination(self):
        return self.pagination


class VendorReportResponse:
    id = None
    Invoice_Date = None
    payment_Date = None
    tax_name = None
    Invoiceno = None
    Total_Amount = None
    Base_Amount = None
    Tax_Amount = None
    TDS_Amount = None
    Bank_Payment = None
    LIQ_Amount = None
    debit_amount = None
    credit_amount = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_ID(self, ID):
        self.ID = ID
    def set_Invoice_Date(self, Invoice_Date):
        self.Invoice_Date = Invoice_Date
    def set_payment_Date(self, payment_Date):
        self.payment_Date = payment_Date
    def set_UTRNO(self, UTRNO):
        self.UTRNO = UTRNO
    def set_tax_name(self, tax_name):
        # obj = []
        # obj.append(j['name'])
        self.Description = tax_name['name']
    def set_Invoiceno(self, Invoiceno):
        self.Invoiceno = Invoiceno
    def set_Amount(self, Amount):
        self.Amount = Amount['name']
    def set_Total_Amount(self, Total_Amount):
        self.Total_Amount = Total_Amount
    def set_Base_Amount(self, Base_Amount):
        self.Base_Amount = Base_Amount
    def set_Tax_Amount(self, Tax_Amount):
        self.Tax_Amount = Tax_Amount
    def set_TDS_Amount(self, TDS_Amount):
        self.TDS_Amount = TDS_Amount
    def set_Bank_Payment(self, Bank_Payment):
        self.Bank_Payment = Bank_Payment
    def set_LIQ_Amount(self, LIQ_Amount):
        self.LIQ_Amount = LIQ_Amount
    def set_debit_amount(self, debit_amount):
        self.debit = debit_amount
    def set_credit_amount(self, credit_amount):
        self.credit = credit_amount
    def set_opening_balance(self, opening_balance):
        self.opening_balance = opening_balance
    def set_closing_balance(self, closing_balance):
        self.closing_balance = closing_balance

