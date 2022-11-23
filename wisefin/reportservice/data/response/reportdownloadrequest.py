from entryservice.util.entryutil import EntryType
import json
from django.template.defaultfilters import length
entrytype = EntryType()


class templateDownloadResponse:
    id = None
    module_id = None
    report_id = None
    emp_id = None
    emp_name = None
    emp_column = None
    emp_report = None
    report_template_name = None
    status = None
    file_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_module_id(self, module_id):
        self.module_id = module_id

    def set_report_id(self, report_id):
        self.report_id = report_id

    def set_emp_id(self, emp_id):
        self.emp_id = emp_id

    def set_emp_name(self, emp_name):
        self.emp_name = emp_name

    def set_emp_column(self, emp_column):
        column = json.loads(emp_column)
        self.emp_column = column['column_list']

    def set_emp_report(self, emp_report):
        report = json.loads(emp_report)
        self.emp_report = report['REPORT_FILTER']

    def set_report_template_name(self, report_template_name):
        self.report_template_name = report_template_name

    def set_status(self, status):
        self.status = status

    def set_module_name(self, module_name):
        name = 'ACCOUNT PAYABLE'
        self.module_name = name

    def set_file_name(self, file_name):
        self.file_name = file_name.name


class TemplateDownloadResponse:
    # parametername_id, gl_no, transaction, Values,value_to_taken, wisefin_category, wisefin_subcategory,display
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
        self.category_code = {"code": wisefin_category}

    def set_wisefin_subcategory(self, wisefin_subcategory):
        self.subcategory_code = {"code": wisefin_subcategory}

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


class vendorDownloadResponse:
    invoice_date = None
    description = None
    invoice_no = None
    debit = None
    credit = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_invoice_date(self, invoice_date):
        self.invoice_date = str(invoice_date)

    def set_description(self, description):
        self.description = description

    def set_invoice_no(self, invoice_no):
        self.invoice_no = invoice_no

    def set_debit(self, debit):
        self.debit = float(debit)

    def set_credit(self, credit):
        self.credit = float(credit)
