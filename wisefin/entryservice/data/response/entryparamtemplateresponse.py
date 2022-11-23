import json
from django.template.defaultfilters import length
class ParamtemplateResponse:
    id = None
    name = None
    is_parent = None
    displayname = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_name(self, name):
        self.name = name
    def set_is_parent(self, is_parent):
        self.is_parent = is_parent
    def set_displayname(self, displayname):
        self.displayname = displayname

class EntryTemplateResponse:
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