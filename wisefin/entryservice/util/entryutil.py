import re
from entryservice.models.entrymodels import ParameterName,ParameterTables
from apservice.models.apmodels import APDebit,APHeader,APCredit,APInvoiceHeader
from django.db.models import Q
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///:memory:', echo=True)
# from sqlalchemy import Table, Column, Integer, String, MetaData
# metadata = MetaData()
import pandas as pd
import json

from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
#from django.db.connection import introspection
#from vysfin.settings import logger
from environs import Env
env = Env()
env.read_env()
DB_NAME_masterdb = env.str('DB_NAME_masterdb')
DB_NAME_vendordb = env.str('DB_NAME_vendordb')

ORACLE_CLIENT_BASE_URL = env.str('ORACLE_CLIENT_BASE_URL')
ORACLE_CLIENT_AUTH_USER_NAME = env.str('ORACLE_CLIENT_AUTH_USER_NAME')
ORACLE_CLIENT_AUTH_PASSWORD = env.str('ORACLE_CLIENT_AUTH_PASSWORD')
#DB_NAME_apdb = 'napservice'
#DB_NAME_apdb = env.str('DB_NAME_masterdb')
class APDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)
    def get_ap_schema(self):
        return self._current_app_schema()

class MASTERDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def get_master_schema(self):
        return self._current_app_schema()

class VENDORDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def get_vendor_schema(self):
        return self._current_app_schema()

class ENTRYDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    def get_entry_schema(self):
        return self._current_app_schema()

class FADBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)

    def get_fa_schema(self):
        return self._current_app_schema()


class EntryType:
    DEBIT= 1
    CREDIT= 2

    DEBIT_VAL = 'DEBIT'
    CREDIT_VAL='CREDIT'
    def get_val(self,data):
        if data==self.DEBIT:
            return self.DEBIT_VAL
        elif data==self.CREDIT:
            return self.CREDIT_VAL
class ModuleType:
    AP_APPROVED= 1
    AP_PAYMENT= 2
    JV_PAYMENT= 3

    APAPPROVED_VAL = 'AP_APPROVED'
    APPAYMENT_VAL='AP_PAYMENT'
    JVPAYMENT_VAL='JV_PAYMENT'
    def get_val(self,data):
        if data==self.AP_APPROVED:
            return self.APAPPROVED_VAL
        elif data==self.AP_PAYMENT:
            return self.APPAYMENT_VAL
        elif data==self.JV_PAYMENT:
            return self.JVPAYMENT_VAL

    def get_value_to_id(self,data):
        if data==self.APAPPROVED_VAL:
            return self.AP_APPROVED
        elif data==self.APPAYMENT_VAL:
            return self.AP_PAYMENT
        elif data==self.JVPAYMENT_VAL:
            return self.JV_PAYMENT
class Fetch_Data(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    def dynamic_querydr(self,id,scope):
        Dynamic_query=()
        from django.db import connection
        ##set dynamic schema name
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        from nwisefin.settings import DATABASES
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")

        if id == '1':
            #h.code as supplier_code d.product_isblocked,d.product_isrcm
            #d.code as product_code,e.code "
                #" as hsn_code,k.code as paymode_code,g.code as branch_code,
            Dynamic_query = (
                " select a.aptype,b.invoicegst ,d.product_isblocked,d.product_isrcm "
                " from "+str(DB_NAME_apdb)+" .apservice_apheader a inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader "
                " b on a.id=b.apheader_id "
                " inner join "+str(DB_NAME_apdb)+" .apservice_apinvoicedetail c on b.id=c.apinvoiceheader_id "
                " inner join "+str(DB_NAME_apdb)+" .apservice_apcredit d "
                " on b.id=d.apinvoiceheader_id left join "+str(DB_NAME_masterdb)+" .masterservice_paymode k on d.paymode_id=k.code "
                " left join "+str(DB_NAME_masterdb)+" .masterservice_product d on c.productcode=d.code "
                " left join "+str(DB_NAME_masterdb)+" .masterservice_hsn e on e.code=c.hsn "
                " left join "+str(DB_NAME_masterdb)+" .masterservice_uom f on c.uom=f.code "
                " left join "+str(DB_NAME_masterdb)+" .masterservice_apcategory m on m.code=d.category_code "
                " left join "+str(DB_NAME_masterdb)+" .masterservice_apsubcategory j on j.code=d.subcategory_code "
                " left join userservice_employeebranch g on g.id=a.raiserbranch "
                " left join "+str(DB_NAME_vendordb)+".vendorservice_supplierbranch h on h.id=b.supplier_id "
                " where a.id=0 ; ")

        #print(Dynamic_query)
        with connection.cursor() as cursor:
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            #resp = {"DATA": json.loads(df_data.to_json(orient='records'))}
            out_data=[]
            for col in columns:
                out_dict = {}
                out_dict['name']=col
                out_data.append(out_dict.copy())
            resp = {"DATA": out_data}
        return resp
    def dynamic_querycr(self,id,scope):
        Dynamic_query=()
        from django.db import connection
        ##set dynamic schema name
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        from nwisefin.settings import DATABASES
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")
        if id == '1':
            Dynamic_query = ("select e.name as paymode_name, "
                             #" e.code as paymode_code,e.name as paymode_name, "
                             #" k.code as category_code,j.code as subcategory_code"
                             #" ,g.code as branch_code,g.name as branch_name,"
                             "h.name as supplier_name"
                             #",h.code as supplier_code "
                             " from " 
                            " "+str(DB_NAME_apdb)+" .apservice_apheader a inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader  b "
                             " on a.id=b.apheader_id inner join "+str(DB_NAME_apdb)+" .apservice_apcredit d "
                             " on b.id=d.apinvoiceheader_id left join "+str(DB_NAME_masterdb)+" .masterservice_paymode e on d.paymode_id=e.code  "
                             " left join userservice_employeebranch g on g.id=a.raiserbranch "
                            " left join "+str(DB_NAME_vendordb)+" .vendorservice_supplierbranch h on h.id=b.supplier_id "
                             " left join "+str(DB_NAME_masterdb)+" .masterservice_apcategory k on k.code=d.category_code "
                             " left join "+str(DB_NAME_masterdb)+" .masterservice_apsubcategory j on j.code=d.subcategory_code where b.id=0   ")

        #print(Dynamic_query)
        with connection.cursor() as cursor:
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            #resp = {"DATA": json.loads(df_data.to_json(orient='records'))}
            out_data = []
            for col in columns:
                out_dict = {}
                out_dict['name'] = col
                out_data.append(out_dict.copy())
            resp = {"DATA": out_data}
            #resp = {"DATA": columns}
        return resp

    # def Fetch_Parametername(self,crno,code):
    #     ####no use this one
    #     fetch_paramvalues = ParameterName.objects.using(self._current_app_schema()).get(code=code)
    #     columnname=json.loads(fetch_paramvalues.columnname)
    #     ######AP HEADER FETCH COLUMNS NAME
    #     apheader=columnname['apheader']
    #     table_key=apheader['tabel_key']
    #     table_param=apheader['param']
    #     fetch_tables = ParameterTables.objects.get(id=table_key)
    #     apheader_table = fetch_tables.name
    #     clm_arr = []
    #     for i in table_param:
    #         clm_arr.append(i['columnname'])
    #     lenchk_apheader=len(clm_arr)
    #     a=0
    #     apheader_clms=''
    #     for a in range(lenchk_apheader):
    #         if apheader_clms == '':
    #             apheader_clms='a.'+clm_arr[a]
    #         else:
    #             apheader_clms=apheader_clms +","+ 'a.'+clm_arr[a]
    #
    #     #### AP INVOICEHEADER FETCH COLUMNS NAME
    #     apinvoiceheader = columnname['apinvoiceheader']
    #     table_key1 = apinvoiceheader['tabel_key']
    #     APinvoicetable_param = apinvoiceheader['param']
    #     fetch_tables1 = ParameterTables.objects.get(id=table_key1)
    #     apinvoiceheader_table = fetch_tables1.name
    #     clm1_arr = []
    #     for j in APinvoicetable_param:
    #         clm1_arr.append(j['columnname'])
    #     lenchk_apinvoiceheader = len(clm1_arr)
    #     b = 0
    #     apinvoiceheader_clms = ''
    #     for b in range(lenchk_apinvoiceheader):
    #         if apinvoiceheader_clms == '':
    #             apinvoiceheader_clms = 'b.'+ clm1_arr[b]
    #         else:
    #             apinvoiceheader_clms = apinvoiceheader_clms + "," + 'b.'+ clm1_arr[b]
    #
    #     #### AP INVOICEDETAILS FETCH COLUMNS NAME
    #     apinvoicedetails = columnname['apinvoicedetails']
    #     table_key2 = apinvoicedetails['tabel_key']
    #     APinvoicedeltable_param = apinvoicedetails['param']
    #     fetch_tables2 = ParameterTables.objects.get(id=table_key2)
    #     apinvoicedetails = fetch_tables2.name
    #     clm2_arr = []
    #     for k in APinvoicedeltable_param:
    #         clm2_arr.append(k['columnname'])
    #
    #     lenchk_apinvoicedel = len(clm2_arr)
    #     c = 0
    #     apinvoicedel_clms = ''
    #     for c in range(lenchk_apinvoicedel):
    #         if apinvoicedel_clms == '':
    #             apinvoicedel_clms ='c.'+ clm2_arr[c]
    #         else:
    #             apinvoicedel_clms = apinvoicedel_clms + "," +'c.'+ clm2_arr[c]
    #
    #     from django.db import connection
    #     Dynamic_query = (" select "+str(apheader_clms)+","+str(apinvoiceheader_clms)+","+str(apinvoicedel_clms)+""
    #                     " from  napservice. "+str(apheader_table)+" a "
    #                      " inner join napservice. "+str(apinvoiceheader_table)+" b  on a.id=b.apheader_id "
    #                      "inner join napservice. "+str(apinvoicedetails)+" c on b.id=c.apinvoiceheader_id "
    #                                                                      " where crno= '"+str(crno)+"' ")
    #     #print(Dynamic_query)
    #     with connection.cursor() as cursor:
    #         cursor.execute(Dynamic_query)
    #         columns = [x[0] for x in cursor.description]
    #         rows = cursor.fetchall()
    #         rows = list(rows)
    #         df_data = pd.DataFrame(rows, columns=columns)
    #         resp = {"DATA": json.loads(df_data.to_json(orient='records'))}
    #         resp1 = resp['DATA']
    #     return resp1



        # apinvoiceheader = columnname['apinvoiceheader']
        # table_key = apinvoiceheader['tabel_key']

        # fetch_tables = ParameterTables.objects.get(id=table_key)
        # apheader_table=fetch_tables.name
        # cond = Q(apinvoiceheader__apheader__crno=crno)
        # obj = APDebit.objects.using('ap_service').filter(cond)
        #print(apheader_table)
        # for key,value in columnname.items():
        #     if key == 'apheader':
        #         arr=[]
        #         for a in key:
        #             arr.append(a.columname)
        #         print(arr)
        #     print(key)
        #
        #     if isinstance(value,list):
        #         pass
        #     elif isinstance(value,dict):
        #         for i,j in value.items():
        #             if isinstance(j,list):
        #                 for list_item in j:
        #                     print(list_item)

class ConditionsName:

    in_val = 1
    equal_val = 2
    In_VAL = "IN"
    EQUAL_VAL = "EQUAL"

def list_conditionname():
    idarr = [ConditionsName.in_val, ConditionsName.equal_val]
    typearr = [ConditionsName.In_VAL, ConditionsName.EQUAL_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist

class Type:
    PO = 1
    NON_PO = 2
    PETTYCASH = 3
    ADVANCE = 4
    TCF = 8
    NONPOPAYMENT = 9
    NONPORCM = 10
    TCFPAYMENT = 11
    NONPOBLOCKED = 12
    NONPORCMBLOCKED = 13
    ERA = 14
    PPX = 15
    ADV = 16
    ADE = 17

    PO_Type = "PO"
    NON_PO_Type = "NON PO"
    PETTYCASH_Type = "PETTYCASH"
    ADVANCE_Type = "ADVANCE"
    TCF_Type = "TCF"
    NONPO_PAYMENT_Type = "PAYMENT"
    NONPO_RCM_Type = "NON PO RCM"
    TCF_PAYMENT_Type = "TCF PAYMENT"
    NONPO_BLOCKED_Type = "NON PO BLOCKED"
    NONPO_RCM_BLOCKED_Type = "NON PO RCM AND BLOCKED"
    ERA_Type = "EMP REIMP"
    PPX_Type = "PPX"
    ADV_Type = "ADV"
    ADE_Type = "ADE"

def get_Type(number):
    if (number == Type.PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PO'
        return vyslite

    elif (number == Type.NON_PO):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO'
        return vyslite
    elif (number == Type.PETTYCASH):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PETTYCASH'
        return vyslite
    elif (number == Type.ADVANCE):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ADVANCE'
        return vyslite
    elif (number == Type.TCF):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'TCF'
        return vyslite
    elif (number == Type.NONPOPAYMENT):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PAYMENT'
        return vyslite
    elif (number == Type.NONPORCM):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO RCM'
        return vyslite
    elif (number == Type.TCFPAYMENT):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'TCF PAYMENT'
        return vyslite
    elif (number == Type.NONPOBLOCKED):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO BLOCKED'
        return vyslite
    elif (number == Type.NONPO_RCM_BLOCKED_Type):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'NON PO RCM AND BLOCKED'
        return vyslite
    elif (number == Type.ERA_Type):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'EMP REIMP'
        return vyslite
    elif (number == Type.PPX_Type):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'PPX'
        return vyslite
    elif (number == Type.ADE_Type):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ADE'
        return vyslite
    elif (number == Type.ADV_Type):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'ADV'
        return vyslite

def get_entry_list():
    idarr = [Type.PO, Type.NON_PO, Type.PETTYCASH, Type.ADVANCE,Type.TCF,Type.NONPOPAYMENT,Type.NONPORCM,
             Type.TCFPAYMENT,Type.NONPOBLOCKED,Type.NONPORCMBLOCKED,Type.ERA,Type.PPX,Type.ADV,Type.ADE]
    typearr = [Type.PO_Type, Type.NON_PO_Type, Type.PETTYCASH_Type, Type.ADVANCE_Type,Type.TCF_Type,Type.NONPO_PAYMENT_Type,
               Type.NONPO_RCM_Type,Type.TCF_PAYMENT_Type,Type.NONPO_BLOCKED_Type,Type.NONPO_RCM_BLOCKED_Type,
               Type.ERA_Type,Type.PPX_Type,Type.ADE_Type,Type.ADV_Type]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist
class ErrorType:
    SUCCESS = 1
    FAILED = 2
    SUCCESS_Type = "SUCCESS"
    FAILED_Type = "FAILED"
    def get_val(self,data):
        if data==self.SUCCESS:
            return self.SUCCESS_Type
        elif data==self.FAILED:
            return self.FAILED_Type

class ModuleRefType:
    AP= 1
    FA= 2
    JV= 3
    AP_VAL = 'AP'
    FA_VAL='FA'
    JV_VAL='JV'
    def get_val(self,data):
        if data==self.AP_VAL:
            return self.AP
        elif data==self.FA_VAL:
            return self.FA
        elif data==self.JV_VAL:
            return self.JV