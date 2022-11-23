import pandas as pd
import json

from django.db.models import QuerySet

from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from environs import Env
env = Env()
env.read_env()
DB_NAME_masterdb = env.str('DB_NAME_masterdb')
# DB_NAME_masterdb = 'nwisefin'
DB_NAME_vendordb = env.str('DB_NAME_vendordb')
# DB_NAME_vendordb = 'nwisefin'
DB_NAME_apdb = 'napservice'
DB_NAME_entry = 'nentry'

class APDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)
    def get_ap_schema(self):
        return self._current_app_schema()

class Fetch_Data(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.REPORT_SERVICE)
    def dynamic_query(self, id, scope):
        Dynamic_query = ()
        from django.db import connection
        ##set dynamic schema name
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        from nwisefin.settings import DATABASES
        #DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")
        # DB_NAME_apdb = 'nwisefin'

        if id == 'AP':
            # h.code as supplier_code d.product_isblocked,d.product_isrcm
            Dynamic_query = (
                    " select a.aptype,b.invoicegst ,pro.code as product_code,e.code "
                    " as hsn_code,k.code as paymode_code,g.code as branch_code,pro.product_isblocked,pro.product_isrcm "
                    " from " + str(DB_NAME_apdb) + " .apservice_apheader a inner join " + str(
                DB_NAME_apdb) + " .apservice_apinvoiceheader "
                                " b on a.id=b.apheader_id "
                                " inner join " + str(
                DB_NAME_apdb) + " .apservice_apinvoicedetail c on b.id=c.apinvoiceheader_id "
                                " inner join " + str(DB_NAME_apdb) + " .apservice_apcredit d "
                                                                     " on b.id=d.apinvoiceheader_id left join " + str(
                DB_NAME_masterdb) + " .masterservice_paymode k on d.paymode_id=k.code "
                                    " left join " + str(
                DB_NAME_masterdb) + " .masterservice_product pro on c.productcode=pro.code "
                                    " left join " + str(DB_NAME_masterdb) + " .masterservice_hsn e on e.code=c.hsn "
                                                                            " left join " + str(
                DB_NAME_masterdb) + " .masterservice_uom f on c.uom=f.code "
                                    " left join " + str(
                DB_NAME_masterdb) + " .masterservice_apcategory m on m.code=d.category_code "
                                    " left join " + str(
                DB_NAME_masterdb) + " .masterservice_apsubcategory j on j.code=d.subcategory_code "
                                    " left join userservice_employeebranch g on g.id=a.raiserbranch "
                                    " left join " + str(
                DB_NAME_vendordb) + ".vendorservice_supplierbranch h on h.id=b.supplier_id "
                                    " where a.id=0 ; ")

        elif id == 'JV':
            Dynamic_query = ("select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'SM':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'TDSR':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'TB':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'TDSR2':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'INVOICE NOT PAID':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'ECRD':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'DR':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'CR':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'VS':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'PR':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        elif id == 'PCR':
            Dynamic_query = (
                        "select transactiondate, crno from " + str(DB_NAME_entry) + " .entryservice_entry where id=0;")

        print(Dynamic_query)
        with connection.cursor() as cursor:
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            # resp = {"DATA": json.loads(df_data.to_json(orient='records'))}
            out_data = []
            for col in columns:
                out_dict = {}
                out_dict['name'] = col
                out_data.append(out_dict.copy())
            resp = {"DATA": out_data}
        return resp


class bold_color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class DictObj:
    queryset_data=[]
    result_set=[]
    def get(self,dict1):
        if isinstance(dict1,str):
            dict1=json.loads(dict1)
        self.__dict__.update(dict1)
        return self.__dict__
    def get_obj(self,dict1):
        if isinstance(dict1,QuerySet):

            for data in dict1:
                self.__dict__.update(data)
                self.queryset_data.append(self)
            return self.queryset_data
        else:
            self.__dict__.update(dict1)
            return self

    def values_list(self, field):
        for data in self.queryset_data:
            for key, value in data.items():
                if key == field:
                    self.result_set.append(value)
        return self.result_set