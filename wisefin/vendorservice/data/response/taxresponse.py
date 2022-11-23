import decimal
import json


class TaxResponse:
    id = None
    payable = None
    code = None
    name = None
    receivable = None
    status = None
    glno =None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name
        
    def set_payable(self, payable):
        self.payable = payable
        
    def set_receivable(self, receivable):
        self.receivable = receivable

    def set_glno(self,glno):
        self.glno = glno


class TaxsummaryResponse:
    id=None
    taxname=None
    subtax_id=None
    subtax_name=None
    subtaxamount=None
    taxrate_id=None
    taxrate_name=None
    taxrate_rate=None
    status=None
    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_id(self,id):
        self.id=id
    def set_name(self,name):
        self.name=name
    def set_subtax_id(self,subtax_id):
        self.subtax_id=subtax_id

    def set_subtax_name(self,subtax_name):
        self.subtax_name=subtax_name
    def set_subtaxamount(self,subtax_amount):
        self.subtax_amount=subtax_amount
    def set_taxrate_id(self,taxrate_id):
        self.taxrate_id=taxrate_id
    def set_taxrate_name(self,taxrate_name):
        self.taxrate_name=taxrate_name
    def set_taxrate_rate(self,taxrate_rate):
        self.taxrate_rate=taxrate_rate

    def set_status(self,status):
        self.status=status
def dictdefault(data):

    if isinstance(data,decimal.Decimal):
        return int(data)
    else:
        try:
            return data.__dict__
        except:
            return str(data)
import json

from django.template.defaultfilters import length


class List:
    data = []
    pagination = None
    count=None

    def get(self):
        return json.dumps(self, default=dictdefault,
                          sort_keys=True, indent=4)


    def __init__(self):
        self.data = []

    def set_list(self, list):
        self.data = list

    def get_list(self):
        return self.data

    def append(self, obj):
        self.data.append(obj)

    def set_listcount(self, count):
        self.count = count

    def get_listcount(self):
        return self.count


    def set_pagination(self, pagination):
        self.pagination = pagination
        if length(self.data) > pagination.limit:
            self.data.pop()



    def get_pagination(self):
        return self.pagination