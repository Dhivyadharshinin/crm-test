import traceback
from datetime import datetime, date

import pandas as pd
# from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils.timezone import now
# from colorama import Fore, Back, Style
from environs import Env
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule, DocPrefix
from entryservice.models import ModuleEOD
from faservice.util.FaApiService import DictObj
from nwisefin.settings import logger, DATABASES
from reportservice.data.response.reportdownloadrequest import templateDownloadResponse, vendorDownloadResponse
from django.db import connection, connections
from reportservice.models import ReportParameter, ReportDetails
# from reportservice.util.reportutil import bold_color
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
today = date.today()
# from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
# from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
START_TIME_D = datetime.now()
START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
env = Env()
env.read_env()


class APDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def get_ap_schema(self):
        return self._current_app_schema()


class ENTRYDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    def get_entry_schema(self):
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


class INWARDDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)

    def get_inward_schema(self):
        return self._current_app_schema()


class ECFDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def get_ecf_schema(self):
        return self._current_app_schema()


class ENTRY1DBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)
        self.entry_db_serv = self._current_app_schema()
        self.entry_db = DATABASES[self.entry_db_serv]['NAME']

    def insert(self, scope,emp_id,obj,data):
        logger.info('EntryEOD TrailBalance DB Get '+str(START_TIME))
        DB_NAME_nwisefin = env.str('DB_NAME_nwisefindb')
        ap_db = APDBService(scope)
        entry_db = ENTRYDBService(scope)
        master_db = MASTERDBService(scope)

        Ap_Dynamic_schema = ap_db.get_ap_schema()
        Entry_Dynamic_schema = entry_db.get_entry_schema()
        Master_Dynamic_schema = master_db.get_master_schema()

        from nwisefin.settings import DATABASES
        DB_NAME_apdb = DATABASES.get(Ap_Dynamic_schema).get("NAME")
        DB_NAME_entry = DATABASES.get(Entry_Dynamic_schema).get("NAME")
        DB_NAME_master = DATABASES.get(Master_Dynamic_schema).get("NAME")

        act = ModuleEOD.objects.using(self._current_app_schema()).all()
        if len(act)==0:
            # from datetime import date, timedelta
            # def daterange(start_date, end_date):
            #     for n in range(int((end_date - start_date).days)):
            #         yield start_date + timedelta(n)
            #
            # start_date = date(2022, 3, 1)
            # end_date = date.today()
            # for single_date in daterange(start_date, end_date):
            #     date_new=single_date.strftime("%Y-%m-%d")

            insert_files = (
                    "insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                                    "SELECT 1, entry.crno,entry.gl, apsubcat.code AS 'gl_code', apsubcat.name AS 'gl_description', "
                                    "CASE WHEN stamp.opening_balance is null THEN 0 else stamp.closing_balance END as opening_balance, "
                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), 0), 2) AS entry_debitamt, "
                                    "ROUND(IF(entry.type = 2, SUM(entry.amount), 0), 2) AS entry_creditamt,"
                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), sum(-entry.amount)), 2) AS Closing_Balance, "
                                    " apinv.invoiceno AS 'invoice_no', apinv.invoicedate AS 'invoice_date', 1, " + str(
                emp_id) + ", NOW() "
                          "FROM " + str(DB_NAME_entry) + ".entryservice_entry entry "
                                                         "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apheader ap ON entry.crno = ap.crno "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel ON apinv.id = apinvdel.apinvoiceheader_id "
                                "LEFT JOIN " + str(
                DB_NAME_master) + ".masterservice_apsubcategory apsubcat ON apsubcat.glno = entry.gl "
                                "LEFT JOIN " + str(
                DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp on stamp.gl_no = entry.gl "
                                  "WHERE transactiondate between '2022-03-01' AND '2022-05-09' AND entry.entry_status = 1 GROUP BY entry.transactiondate , entry.type , entry.gl;")
            print(insert_files)
            with connections[self.entry_db_serv].cursor() as cursor:
                cursor.execute(insert_files)

            insert_files1 = (
                    "insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                                    "SELECT 1, entry.crno,entry.gl, apsubcat.code AS 'gl_code', apsubcat.name AS 'gl_description', "
                                    "CASE WHEN stamp.opening_balance is null THEN 0 else stamp.closing_balance END as opening_balance, "
                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), 0), 2) AS entry_debitamt, "
                                    "ROUND(IF(entry.type = 2, SUM(entry.amount), 0), 2) AS entry_creditamt,"
                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), sum(-entry.amount)), 2) AS Closing_Balance, "
                                    "apinv.invoiceno AS 'invoice_no', apinv.invoicedate AS 'invoice_date', 1, " + str(
                emp_id) + ", NOW() "
                          "FROM " + str(DB_NAME_entry) + ".entryservice_entry entry "
                                                         "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apheader ap ON entry.crno = ap.crno "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel ON apinv.id = apinvdel.apinvoiceheader_id "
                                "LEFT JOIN " + str(
                DB_NAME_master) + ".masterservice_apsubcategory apsubcat ON apsubcat.glno = entry.gl "
                                  "LEFT JOIN " + str(
                DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp on stamp.gl_no = entry.gl "
                                    "WHERE transactiondate between '2022-05-10' AND '2022-07-30'AND entry.entry_status = 1 GROUP BY entry.transactiondate , entry.type , entry.gl;")
            print(insert_files1)
            with connections[self.entry_db_serv].cursor() as cursor:
                cursor.execute(insert_files1)

            logger.info('EntryEOD TrailBalance Inserted Succesfully ' + str(START_TIME))
            obj_eod = ModuleEOD.objects.using(self._current_app_schema()).create(entity_id=self._entity_id(),
                                                                                 date=today,
                                                                                 eodflag=1,
                                                                                 status=1,
                                                                                 created_by=38,
                                                                                 created_date=now())
            obj_eod.save()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            try:
                case = 1
                obj_eod = ModuleEOD.objects.using(self._current_app_schema()).get(date=today,
                                                                                  eodflag=0)
                if len(obj_eod) == 1:
                    case = 1
                logger.info('EntryEOD TrailBalance Completed ' + str(START_TIME))
            except:
                obj_eod = ModuleEOD.objects.using(self._current_app_schema()).filter(date=today,
                                                                                  eodflag=1)
                if len(obj_eod) == 1:
                    case = 3
                else:
                    case = 2

            if case == 2:
                obj_eod = ModuleEOD.objects.using(self._current_app_schema()).create(entity_id=self._entity_id(),
                                                                                     date=today,
                                                                                     eodflag=0,
                                                                                     status=1,
                                                                                     created_by=38,
                                                                                     created_date=now())
                logger.info('EntryEOD TrailBalance Not Completed ' + str(START_TIME))
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj

            elif case == 1:
                logger.info('EntryEOD TrailBalance Starts ' + str(START_TIME))
                try:
                    if data['module'] == 'TRIAL BALANCE':
                        if obj[0]['master'] == 1:
                            insert_files = (
                                    "insert into " + str(
                                DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                                                    "SELECT 1, entry.crno,entry.gl, apsubcat.code AS 'gl_code', apsubcat.name AS 'gl_description', "
                                                    "CASE WHEN stamp.opening_balance is null THEN 0 else stamp.closing_balance END as opening_balance, "
                                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), 0), 2) AS entry_debitamt, "
                                                    "ROUND(IF(entry.type = 2, SUM(entry.amount), 0), 2) AS entry_creditamt,"
                                                    "ROUND(IF(entry.type = 1, SUM(entry.amount), sum(-entry.amount)), 2) AS Closing_Balance, "
                                                    "apinv.invoiceno AS 'invoice_no', apinv.invoicedate AS 'invoice_date', 1, " + str(
                                emp_id) + ", NOW() "
                                          "FROM " + str(DB_NAME_entry) + ".entryservice_entry entry "
                                                                         "INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apheader ap ON entry.crno = ap.crno "
                                                "INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                                                "INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel ON apinv.id = apinvdel.apinvoiceheader_id "
                                                "LEFT JOIN " + str(
                                DB_NAME_master) + ".masterservice_apsubcategory apsubcat ON apsubcat.glno = entry.gl "
                                                  "LEFT JOIN " + str(
                                DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp on stamp.gl_no = entry.gl "
                                                  "WHERE transactiondate BETWEEN '" + str(
                                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + ""
                                                                                                "' AND entry.entry_status = 1 GROUP BY entry.transactiondate , entry.type , entry.gl;")
                            print(insert_files)
                            with connection.cursor() as cursor:
                                cursor.execute(insert_files)
                            logger.info('EntryEOD TrailBalance Inserted Succesfully ' + str(START_TIME))
                            obj_eod = ModuleEOD.objects.using(self._current_app_schema()).filter(id=obj_eod.id).update(eodflag=1,
                                                                                                                       status=1,
                                                                                                                       updated_by=38,
                                                                                                                       updated_date=now())
                            success_obj = NWisefinSuccess()
                            success_obj.set_status(SuccessStatus.SUCCESS)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                            return success_obj
                except Exception as e:
                    logger.info('EntryEOD TrailBalance Starts ' + str(START_TIME))
                    logger.info('EntryEOD TrailBalance Error ' + str(e))
                    logger.info('EntryEOD TrailBalance Error {}'.format(traceback.format_exc()))
            elif case == 3:
                logger.info('EntryEOD Already Run For The Day')
                return True
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorMessage.ASSET_CREATE_LOCK)
                logger.info('EntryEOD TrailBalance Error Occurs ' + str(START_TIME))
                logger.info('EntryEOD TrailBalance Error {}'.format(traceback.format_exc()))
                return error_obj


class ReportDownloadService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.REPORT_SERVICE)

    def fetch_parameterlist(self, module_id, report_id, emp_id):
        global resp
        condition = Q(status=1) & Q(reportemp_moduleid=module_id, reportemp_empid=emp_id,
                                    reportemp_modulenamedropdownid=report_id)
        # , reportemp_name = emp_name
        try:
            logger.info('Module Parameter List - ' + START_TIME)
            parameter = ReportParameter.objects.using(self._current_app_schema()).filter(condition)
            print(self._current_app_schema())
            list_length = len(parameter)
            # module_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for i in parameter:
                    module_data = templateDownloadResponse()
                    module_data.set_emp_report(i.reportemp_filter)
                    out_data = []
                    for col in module_data.emp_report:
                        out_dict = {'name': col}
                        out_data.append(out_dict.copy())
                    resp = {"data": out_data}
                    logger.info('Module Parameter List - ' + START_TIME)
                return resp
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Module Parameter List - ' + str(e))
            return error_obj

    def generate_report_download(self, param_details, emp_id, scope):
        gl_no="'232100','232101','232102','232103','232104','232104','232105','232200','232201','232202','232203','232204','232205','215000','215101','215102','215103', " \
              "'200000','210000','211000','211101','211102','211103','211104','211105','212000','212101','212102','212103','212104','213000','213101','213102','213103', " \
              "'213104','213105','213106','214000','214101','214102','214103','214104','215000','215101','215102','215103','216000','216101','216102','216103' "
        DB_NAME_nwisefin = env.str('DB_NAME_nwisefindb')
        ap_db = APDBService(scope)
        entry_db = ENTRYDBService(scope)
        master_db = MASTERDBService(scope)
        vendor_db = VENDORDBService(scope)
        # DB_NAME_inward = env.str('DB_NAME_inwdb')
        inward_db = INWARDDBService(scope)
        # DB_NAME_ecf = env.str('DB_NAME_necf')
        ecf_db = ECFDBService(scope)

        Ap_Dynamic_schema = ap_db.get_ap_schema()
        Entry_Dynamic_schema = entry_db.get_entry_schema()
        Master_Dynamic_schema = master_db.get_master_schema()
        Vendor_Dynamic_schema = vendor_db.get_vendor_schema()
        inward_Dynamic_schema = inward_db.get_inward_schema()
        ecf_Dynamic_schema = ecf_db.get_ecf_schema()

        from nwisefin.settings import DATABASES
        DB_NAME_apdb = DATABASES.get(Ap_Dynamic_schema).get("NAME")
        DB_NAME_entry = DATABASES.get(Entry_Dynamic_schema).get("NAME")
        DB_NAME_master = DATABASES.get(Master_Dynamic_schema).get("NAME")
        DB_NAME_vendor = DATABASES.get(Vendor_Dynamic_schema).get("NAME")
        DB_NAME_inward = DATABASES.get(inward_Dynamic_schema).get("NAME")
        DB_NAME_ecf = DATABASES.get(ecf_Dynamic_schema).get("NAME")
        files = ()
        data = param_details['report_id'][0]
        obj = []
        import io
        BytesIO = io.BytesIO()
        if data['operators'] == 'DATE BETWEEN' and data['scheduler'] == 1:
            i = {'value1date': data['value1date'],
                 'value2date': data['value2date'],
                 'master': 1}
            obj.append(i)
            logger.info('Scheduler Starts')
            entrynew = ENTRY1DBService(scope)
            new = entrynew.insert(scope,emp_id,obj,data)
            return new

        if data['operators'] == 'DATE BETWEEN':
            i = {'value1date': data['value1date'],
                 'value2date': data['value2date'],
                 'master': 1}
            obj.append(i)
            logger.info('Date Filter'+str(data['module']))
        elif data['operators'] == 'MONTH BETWEEN':
            i = {'value1month': data['value1month'],
                 # 'value2month': data['value2month'],
                 'master': 4}
            obj.append(i)
            logger.info('Month Filter'+str(data['module']))
        elif data['operators'] == 'RANGE BETWEEN':
            i = {'value1': data['value1'],
                 'value2': data['value2'],
                 'master': 2}
            obj.append(i)
            logger.info('Range Filter'+str(data['module']))
        else:
            i = {'value1': data['value1'],
                 'master': 3}
            obj.append(i)
        try:
            logger.info('Report Generate ID - ' + START_TIME)
            id = ReportDetails.objects.using(self._current_app_schema()).latest('id')
            id = id.id
        except:
            id = 0
        report_id = int(id) + 1
        report = 'REPORT_' + str(report_id)
        logger.info('Report Excel Start - ' + START_TIME)
        if data['module'] == 'TRIAL BALANCE':
            if obj[0]['master'] == 1:
                # truncate_stamp = ("truncate " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport;")
                # with connection.cursor() as cursor:
                #     cursor.execute(truncate_stamp)
                # insert_files = (
                #         "insert into " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                #         "Select 1,entry.crno as 'crno', entry.gl as 'glno',apsubcat.code as 'gl_code', apsubcat.name as 'gl_description', 0 as 'opening_balance', "
                #         "case when entry.type=1 then entry.amount end as 'debit', case when entry.type=2 then entry.amount end as 'credit',0, "
                #         "apinv.invoiceno as 'invoice_no',apinv.invoicedate as 'invoice_date',1," + str(
                #     emp_id) + ",now() "
                #               "from " + str(DB_NAME_entry) + ".entryservice_entry entry inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
                #                     "left join " + str(
                #     DB_NAME_master) + ".masterservice_apsubcategory apsubcat on apsubcat.glno=entry.gl "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
                #                       "where  entry.transactiondate between '" + str(
                #     obj[0]['value1date']) + "' and '" + str(
                #     obj[0]['value2date']) + "' and entry.entry_status=1 group by apsubcat.glno;")
                # insert_files = (
                #         "insert into " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                #         "SELECT 1, entry.crno,entry.gl, apsubcat.code AS 'gl_code', apsubcat.name AS 'gl_description', 0 AS 'opening_balance', "
                #         "ROUND(IF(entry.type = 1, SUM(entry.amount), 0), 2) AS entry_debitamt, "
                #         "ROUND(IF(entry.type = 2, SUM(entry.amount), 0), 2) AS entry_creditamt, "
                #         "0, apinv.invoiceno AS 'invoice_no', apinv.invoicedate AS 'invoice_date', 1, " + str(emp_id) + ", NOW() "
                #         "FROM " + str(DB_NAME_entry) + ".entryservice_entry entry "
                #         "INNER JOIN " + str(DB_NAME_apdb) + ".apservice_apheader ap ON entry.crno = ap.crno "
                #         "INNER JOIN " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                #         "INNER JOIN " + str(DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel ON apinv.id = apinvdel.apinvoiceheader_id "
                #         "LEFT JOIN " + str(DB_NAME_master) + ".masterservice_apsubcategory apsubcat ON apsubcat.glno = entry.gl "
                #         "WHERE transactiondate BETWEEN '" + str(obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + ""
                #         "' AND entry.entry_status = 1 GROUP BY entry.transactiondate , entry.type , entry.gl;")
                # with connection.cursor() as cursor:
                #     cursor.execute(insert_files)
                # files = (
                #         "Select stamp.gl_no as 'GL No',stamp.gl_code as 'GL Code',stamp.gl_description as 'GL Description', "
                #         "0 as 'Opening Balance', stamp.debit as'Debit',-(stamp.credit) as 'Credit', "
                #         "case when stamp.closing_balance = 0 then ((stamp.debit) - (stamp.credit)) end as 'Closing Balance' "
                #         "from " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp "
                #                                           "where stamp.invoice_date between '" + str(
                #     obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' "
                #                                                                     "order by stamp.invoice_date;")

                files = (
                        "Select stamp.gl_no as 'GL No',stamp.gl_code as 'GL Code',stamp.gl_description as 'GL Description', "
                        "sum(stamp.closing_balance) as 'Opening Balance', sum(stamp.debit) as'Debit',sum(-stamp.credit) as 'Credit', "
                        "((stamp.debit) - (stamp.credit)  + sum(stamp.closing_balance)) as 'Closing Balance' "
                        "from " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp "
                                                          "where stamp.invoice_date between '" + str(
                    obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' "
                                                                                    "group by stamp.gl_no order by stamp.invoice_date;")
            if obj[0]['master'] == 4:
                # truncate_stamp = ("truncate " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport;")
                # with connection.cursor() as cursor:
                #     cursor.execute(truncate_stamp)
                # insert_files = (
                #         "insert into " + str(
                #     DB_NAME_nwisefin) + ".reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
                #                         "Select 1,entry.crno as 'crno', entry.gl as 'glno',apsubcat.code as 'gl_code', apsubcat.name as 'gl_description', 0 as 'opening_balance', "
                #                         "case when entry.type=1 then entry.amount end as 'debit', case when entry.type=2 then entry.amount end as 'credit',0, "
                #                         "apinv.invoiceno as 'invoice_no',apinv.invoicedate as 'invoice_date',1," + str(
                #     emp_id) + ",now() "
                #               "from " + str(DB_NAME_entry) + ".entryservice_entry entry inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
                #                     "left join " + str(
                #     DB_NAME_master) + ".masterservice_apsubcategory apsubcat on apsubcat.glno=entry.gl "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
                #                       "where  entry.transactiondate between  '" + str(
                #     obj[0]['value1month']) + "-01' and '" + str(
                #     obj[0]['value1month']) + "-30' and entry.entry_status=1 group by apsubcat.glno;")
                # with connection.cursor() as cursor:
                #     cursor.execute(insert_files)

                # files = ("Select stamp.gl_no as 'GL No',stamp.gl_code as 'GL Code',stamp.gl_description as 'GL Description', "
                #          "(sum(stamp.debit) - sum(stamp.credit)) as 'Opening Balance', stamp.debit as'Debit',-(stamp.credit) as 'Credit', "
                #          "case when stamp.closing_balance = 0 then (sum(stamp.debit) - (stamp.credit))-stamp.debit+stamp.credit end as 'Closing Balance' "
                #          "from "+ str(DB_NAME_nwisefin) +".reportservice_stamptrailreport stamp where stamp.invoice_date between '"+ str(obj[0]['value1month']) +"-01' and '"+ str(obj[0]['value1month']) +"-30' group by stamp.gl_no order by stamp.invoice_date;")

                files = (
                        "Select stamp.gl_no as 'GL No',stamp.gl_code as 'GL Code',stamp.gl_description as 'GL Description', "
                        "sum(stamp.closing_balance) as 'Opening Balance', stamp.debit as'Debit',-(stamp.credit) as 'Credit', "
                        "((stamp.debit) - (stamp.credit)  + sum(stamp.closing_balance)) as 'Closing Balance' "
                        "from " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp "
                                                          "where stamp.invoice_date between '" + str(
                    obj[0]['value1month']) + "-01' and '" + str(
                    obj[0]['value1month']) + "-30' " "group by stamp.gl_no order by stamp.invoice_date;")

            # if obj[0]['master']==1:
            #     files = ("Select ven.code as 'Vendor Code', ven.name as 'Vendor Name',apinv.invoicedate as 'Voucher Date', 0 as 'Opening Balance', "
            #              "case when entry.type=1 then sum(entry.amount) end as'Debit' when entry.type=2 then sum(entry.amount) end as 'Credit' "
            #              "apinv.invoiceno as 'Invoice No',apinv.invoicedate as 'Invoice Date' "
            #              "from "+ str(DB_NAME_entry) +".entryservice_entry entry "
            #              "inner join "+ str(DB_NAME_apdb) +".apservice_apheader ap on entry.crno = ap.crno "
            #              "inner join "+ str(DB_NAME_apdb) +".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
            #              "inner join "+ str(DB_NAME_apdb) +".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
            #              "inner join "+ str(DB_NAME_vendor) +".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
            #              "inner join "+ str(DB_NAME_vendor) +".vendorservice_vendor ven on ven.id=supp.vendor_id "
            #              "where  entry.transactiondate between '"+ str(obj[0]['value1date']) +"' and '"+ str(obj[0]['value2date']) +"' group by entry.type;")
            print(files)
        elif data['module'] == 'SUPPLIER MASTER':
            if obj[0]['master'] == 1:
                files = (
                        "select ven.code as 'Vendor Code',ven.name as 'Vendor Name',supp.panno as 'PAN',supp.gstno as 'GSTIN', "
                        "venadd.line1 as 'Address 1',venadd.line2 as 'Address 2',venadd.line3 as 'Address 3', mcity.name as 'City',"
                        "pay.account_no as 'Bank Account No.',banbr.ifsccode as 'IFSC Code',ban.name as 'Bank Name',banbr.name as 'Bank Branch', "
                        "case when tax.msme = 1 then 'YES' when tax.msme = 2 then 'NO' end as 'MSME Flag', "
                        "tax.msme_reg_no as 'MSME Registration No.' from " + str(
                    DB_NAME_vendor) + ".vendorservice_vendor ven "
                                      "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                      "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierpayment pay on supp.id=pay.supplierbranch_id "
                                      "inner join " + str(
                    DB_NAME_master) + ".masterservice_bank ban on ban.id=pay.bank_id "
                                      "inner join " + str(
                    DB_NAME_master) + ".masterservice_bankbranch banbr on banbr.id=pay.branch_id "
                                      "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_suppliertax tax on ven.id=tax.vendor_id "
                                      "left join " + str(
                    DB_NAME_vendor) + ".vendorservice_vendoraddress venadd on ven.id=venadd.vendor_id "
                                      "left join nmaster.masterservice_city mcity on mcity.id=venadd.city_id "
                                      "where ven.created_date between '" + str(
                    obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' group by ven.code;")
            # if obj[0]['master'] == 4:
            #     files = (
            #             "select ven.code as 'Vendor Code',ven.name as 'Vendor Name',supp.panno as 'PAN',supp.gstno as 'GSTIN', "
            #             "venadd.line1 as 'Address 1',venadd.line2 as 'Address 2',venadd.line3 as 'Address 3', mcity.name as 'City',"
            #             "pay.account_no as 'Bank Account No.',banbr.ifsccode as 'IFSC Code',ban.name as 'Bank Name',banbr.name as 'Bank Branch', "
            #             "case when tax.msme = 1 then 'YES' when tax.msme = 2 then 'NO' end as 'MSME Flag', "
            #             "tax.msme_reg_no as 'MSME Registration No.' from " + str(
            #         DB_NAME_vendor) + ".vendorservice_vendor ven "
            #                           "inner join " + str(
            #         DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
            #                           "inner join " + str(
            #         DB_NAME_vendor) + ".vendorservice_supplierpayment pay on supp.id=pay.supplierbranch_id "
            #                           "inner join " + str(
            #         DB_NAME_master) + ".masterservice_bank ban on ban.id=pay.bank_id "
            #                           "inner join " + str(
            #         DB_NAME_master) + ".masterservice_bankbranch banbr on banbr.id=pay.branch_id "
            #                           "inner join " + str(
            #         DB_NAME_vendor) + ".vendorservice_suppliertax tax on ven.id=tax.vendor_id "
            #                           "left join " + str(
            #         DB_NAME_vendor) + ".vendorservice_vendoraddress venadd on ven.id=venadd.vendor_id "
            #                           "left join nmaster.masterservice_city mcity on mcity.id=venadd.city_id "
            #                           "where ven.created_date between '" + str(
            #         obj[0]['value1month']) + "-01' and '" + str(obj[0]['value1month']) + "-30'  group by ven.code;")
            print(files)
        elif data['module'] == 'JOURNAL VOUCHER':
            files = (
                    "Select date_format(apinv.invoicedate,'%d-%M-%Y') as 'Creation Date', date_format(entry.transactiondate,'%d-%M-%Y') as 'Payment Date', "
                    "entry.crno As 'ECF No', ven.code as 'Vendor Code', supp.name as 'Supplier Name', usrserv.full_name as 'AP Maker Name', "
                    " entry.gl as 'GL Code', entry.glnodescription as 'GL Description', "
                    "case when entry.type=1 then entry.amount end as 'Debit', case when entry.type=2 then -(entry.amount) end as 'Credit', "
                    "case when entry.type=1 then entry.amount else -(entry.amount) end as Net, case when ap.aptype=1 then 'PO' when ap.aptype=2 then 'NON PO' when ap.aptype=3 then 'PETTYCASH' "
                    "when ap.aptype=4 then 'ADVANCE' when ap.aptype=8 then 'TCF' end as 'Invoice Type', "
                    "case when apinv.status=1 then 'NEW' when apinv.status=2 then 'PENDING FOR APPROVAL' when apinv.status=3 then 'BOUNCE' "
                    "when apinv.status=4 then 'RE-AUDIT' when apinv.status=5 then 'REJECTED' when apinv.status=6 then 'PAYMENT INITIATED' "
                    "when apinv.status=7 then 'APPROVED' when apinv.status=8 then 'PAID' when apinv.status=9 then 'FILE INITIATED' when apinv.status=10 then 'AP INITIATED' "
                    "when apinv.status=11 then 'PAY INITIATED' end as 'AP Status', "
                    "ab.description AS 'Text(Narration/Nature_of_transaction)' from " + str(
                DB_NAME_entry) + ".entryservice_entry entry "
                                 "inner join " + str(
                DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
                                "INNER JOIN (select apinvdel.id,apinvdel.apinvoiceheader_id,apinvdel.description,b.apheader_id from  " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel "
                                "INNER JOIN  " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader  b ON b.id = apinvdel.apinvoiceheader_id group by b.id ) as ab ON ap.id = ab.apheader_id "
                                "left join " + str(
                DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
                                  "left join " + str(
                DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
                                  "inner join " + str(
                DB_NAME_nwisefin) + ".userservice_employee usrserv on usrserv.id = ap.created_by "
                                    "where apinv.status in (7,8,6,9,11) and entry.transactiondate between '" + str(
                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "';")
            # files = ("select apinv.invoicedate as Voucher_Date, entry.transactiondate as Value_Date, "
            #         "apinv.invoiceno as Voucher_No, ven.code as Vendor_Code, apheader.raisername as User_Name, "
            #         "entry.gl as GL_Code, subcat.name as GL_Description, entry.amount, apinv.totalamount as Net, "
            #         "case when entry.type=1 then 'Dr' when entry.type=2 then 'Cr' end as Nature_Of_Transaction "
            #         "from "+ str(DB_NAME_vendor) +".vendorservice_vendor ven "
            #         "inner join "+ str(DB_NAME_vendor) +".vendorservice_supplierbranch supp on ven.id =supp.vendor_id "
            #         "inner join "+ str(DB_NAME_apdb) +".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
            #         "inner join "+ str(DB_NAME_apdb) +".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
            #         "inner join "+ str(DB_NAME_apdb) +".apservice_apheader ap on ap.id=apinv.apheader_id "
            #         "inner join "+ str(DB_NAME_entry) +".entryservice_entry entry on entry.crno = ap.crno "
            #         "inner join "+ str(DB_NAME_master) +".masterservice_apsubcategory subcat on subcat.glno = entry.gl "
            #         "inner join "+ str(DB_NAME_apdb) +".apservice_apheader apheader on apheader.id = apinv.apheader_id "
            #         "where ven.status=1  and supp.status=1 and apinvdel.status=1 and ap.crno='"+ str(obj[0]['value1']) +"';")
            print(files)

        elif data['module'] == 'TDS REPORT':
            if obj[0]['master'] == 1:
                # files = (
                #         "Select apinv.invoiceno as 'Invoice No',date_format(apinv.created_date,'%d-%M-%Y') as 'Payment Date', date_format(apinv.invoicedate,'%d-%M-%Y') as 'Invoice Date', "
                #         "ven.name as 'Vendor Name',ven.code as 'Vendor Code',ecfhead.crno as 'ECF Number',supp.panno as 'Vendor PAN', "
                #         "entry.gl as 'GL Code',entry.glnodescription as 'GL Description',case when ven.orgtype = 1 then 'SOLE PROPERTIERS' when ven.orgtype = 2 then 'PARTERNSHIP' "
                #         "when ven.orgtype = 3 then 'PRIVATE LTD' when ven.orgtype = 4 then 'PUBLIC LTD' when ven.orgtype = 5 then 'INDIVIDUAL' "
                #         "when ven.orgtype = 6 then 'TRUST' when ven.orgtype = 7 then 'OTHERS' when ven.orgtype = 8 then 'GOVERNMENT ENTITY' "
                #         "end as 'Venodr Org Type', case when substring(supp.panno, 4, 1) = 'C' then 'Company' when substring(supp.panno, 4, 1) != 'C' then 'Non Company' end as 'Category', "
                #         "msub.name as 'TAX RATE NAME',mrate.rate as 'TAX RATE', "
                #         "apinv.totalamount as 'INV LINE AMOUNT',apinv.totalamount*(mrate.rate)/100 as 'INV LINE TAX VAL', "
                #         "(apinv.totalamount -apinv.totalamount*(mrate.rate)/100) as 'INV LINE AMT PAYABLE', apcre.category_code as 'AP Category'  "
                #         "from " + str(DB_NAME_entry) + ".entryservice_entry entry "
                #                                        "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
                #                     "inner join " + str(
                #     DB_NAME_apdb) + ".apservice_apcredit apcre on apcre.apinvoiceheader_id=apinv.id "
                #                     "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
                #                       "inner join " + str(
                #     DB_NAME_vendor) + ".vendorservice_suppliertax tax on apcre.suppliertax_id=tax.vendor_id "
                #                       "inner join " + str(
                #     DB_NAME_master) + ".masterservice_tax mtax on mtax.id=tax.tax_id "
                #                       "inner join " + str(
                #     DB_NAME_master) + ".masterservice_subtax msub on msub.id=tax.subtax_id "
                #                       "inner join " + str(
                #     DB_NAME_master) + ".masterservice_taxrate mrate on mrate.subtax_id=msub.id "
                #                       "inner join " + str(
                #     DB_NAME_nwisefin) + ".userservice_general_ledger ngl on ngl.no = msub.glno "
                #                         "left join " + str(
                #     DB_NAME_ecf) + ".ecfservice_ecfheader ecfhead on ecfhead.crno=ap.crno "
                #                    "where (entry.gl in ("+(gl_no)+") or entry.gl like '4%') and entry.transactiondate between '" + str(
                #     obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "'"
                #                                                                     " and mtax.name='TDS' group by entry.gl;")
                # files = (
                #         "Select b.invoiceno as 'Invoice No',DATE_FORMAT(k.created_date, '%d-%M-%Y') as 'Payment Date', "
                #         "DATE_FORMAT(b.invoicedate,'%d-%M-%Y') as 'Invoice Date',g.name as 'Vendor Name', "
                #         "g.code as 'Vendor Code',a.crno as 'ECF Number',f.panno as 'Vendor Pan', "
                #         "e.creditglno as 'Credit GL No',i.description as 'GL Desc', "
                #         "CASE WHEN SUBSTRING(f.panno, 4, 1) = 'C' THEN 'Company' WHEN SUBSTRING(f.panno, 4, 1) != 'C' THEN 'Non Company' "
                #         "END AS 'Category', e.suppliertaxtype as 'TAX RATE NAME', e.suppliertaxrate as 'TAX RATE', "
                #         "b.invoiceamount as 'INV Line Amount',(-e.amount) as 'INV LINE TAX VAL', "
                #         "b.invoiceamount - e.amount as 'INV LINE AMT PAYABLE', e.category_code as 'AP Category' "
                #         "from " + str(DB_NAME_apdb) + ".apservice_apheader as a "
                #         "INNER JOIN " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader as b  ON a.id = b.apheader_id "
                #         "INNER JOIN " + str(DB_NAME_apdb) + ".apservice_apcredit as e ON e.apinvoiceheader_id = b.id AND e.paymode_id = 7 and e.is_delete = 0 "
                #         "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_supplierbranch as f ON b.supplier_id = f.id "
                #         "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_vendor as g  ON g.id = f.vendor_id "
                #         "inner join " + str(DB_NAME_apdb) + ".apservice_paymentdetails as k on k.apinvoiceheader_id = b.id "
                #         "inner join "+ str(DB_NAME_nwisefin) + ".userservice_general_ledger i on e.creditglno = i.no "
                #         "where e.paymode_id = 7 and e.is_entry=0 and b.invoicedate between '" + str(obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "';")
                files = ("Select b.invoiceno as 'Invoice No',DATE_FORMAT(k.created_date, '%d-%M-%Y') as 'Payment Date', "
                        "DATE_FORMAT(b.invoicedate,'%d-%M-%Y') as 'Invoice Date',g.name as 'Vendor Name', "
                        "g.code as 'Vendor Code',c.crno as 'ECF Number',f.panno as 'Vendor Pan', "
                        "gl.creditglno as 'Credit GL No',gl.description as 'GL Desc', "
                        "CASE WHEN SUBSTRING(f.panno, 4, 1) = 'C' THEN 'Company' WHEN SUBSTRING(f.panno, 4, 1) != 'C' THEN 'Non Company' "
                        "END AS 'Category', gl.suppliertaxtype as 'TAX RATE NAME', gl.suppliertaxrate as 'TAX RATE', "
                        "b.invoiceamount as 'INV Line Amount',(-gl.amount) as 'INV LINE TAX VAL', "
                        "b.invoiceamount - gl.amount as 'INV LINE AMT PAYABLE', gl.category_code as 'AP Category' "
                        "from (select a.ref_id, date_format(min(a.created_date), '%Y-%m-%d') as Trn_date "
                        "from " + str(DB_NAME_apdb) + ".apservice_apqueue as a where a.ref_type = 2 and a.status = 7 group by ref_id) as m1 "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader as b on m1.ref_id = b.id "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apheader as c on b.apheader_id = c.id "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apcredit as d on b.id = d.apinvoiceheader_id "
                        "and d.paymode_id = 7 and d.is_delete = 0 "
                        "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_supplierbranch as f ON b.supplier_id = f.id "
                        "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_vendor as g  ON g.id = f.vendor_id "
                        "left join " + str(DB_NAME_apdb) + ".apservice_paymentdetails as k on k.apinvoiceheader_id = b.id "
                        "inner join "
                        "(select e.apinvoiceheader_id,e.creditglno,e.amount,e.suppliertaxtype,e.suppliertaxrate,e.category_code,i.description from " + str(DB_NAME_apdb) + ".apservice_apcredit e "
                        "inner join " + str(DB_NAME_nwisefin) + ".userservice_general_ledger i on e.creditglno = i.no "
                        "where e.paymode_id = 7 and e.is_delete = 0 and e.is_entry=0 ) as gl on gl.apinvoiceheader_id =b.id "
                        "where b.status in (7,8,6,9,11) and Trn_date between '" + str(obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "';")

                # queryyyjv = files
                # print(files)
            if obj[0]['master'] == 4:
                files = (
                        "Select b.invoiceno as 'Invoice No',DATE_FORMAT(k.created_date, '%d-%M-%Y') as 'Payment Date', "
                        "DATE_FORMAT(b.invoicedate,'%d-%M-%Y') as 'Invoice Date',g.name as 'Vendor Name', "
                        "g.code as 'Vendor Code',c.crno as 'ECF Number',f.panno as 'Vendor Pan', "
                        "gl.creditglno as 'Credit GL No',gl.description as 'GL Desc', "
                        "CASE WHEN SUBSTRING(f.panno, 4, 1) = 'C' THEN 'Company' WHEN SUBSTRING(f.panno, 4, 1) != 'C' THEN 'Non Company' "
                        "END AS 'Category', gl.suppliertaxtype as 'TAX RATE NAME', gl.suppliertaxrate as 'TAX RATE', "
                        "b.invoiceamount as 'INV Line Amount',(-gl.amount) as 'INV LINE TAX VAL', "
                        "b.invoiceamount - gl.amount as 'INV LINE AMT PAYABLE', gl.category_code as 'AP Category' "
                        "from (select a.ref_id, date_format(min(a.created_date), '%Y-%m-%d') as Trn_date "
                        "from " + str(DB_NAME_apdb) + ".apservice_apqueue as a where a.ref_type = 2 and a.status = 7 group by ref_id) as m1 "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader as b on m1.ref_id = b.id "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apheader as c on b.apheader_id = c.id "
                        "inner join " + str(DB_NAME_apdb) + ".apservice_apcredit as d on b.id = d.apinvoiceheader_id "
                        "and d.paymode_id = 7 and d.is_delete = 0 "
                        "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_supplierbranch as f ON b.supplier_id = f.id "
                        "INNER JOIN " + str(DB_NAME_vendor) + ".vendorservice_vendor as g  ON g.id = f.vendor_id "
                        "left join " + str(DB_NAME_apdb) + ".apservice_paymentdetails as k on k.apinvoiceheader_id = b.id "
                        "inner join "
                        "(select e.apinvoiceheader_id,e.creditglno,e.amount,e.suppliertaxtype,e.suppliertaxrate,e.category_code,i.description from " + str(DB_NAME_apdb) + ".apservice_apcredit e "
                        "inner join " + str(DB_NAME_nwisefin) + ".userservice_general_ledger i on e.creditglno = i.no "
                        "where e.paymode_id = 7 and e.is_delete = 0 and e.is_entry=0 ) as gl on gl.apinvoiceheader_id =b.id "
                        "where b.status in (7,8,6,9,11) and Trn_date between '" + str(obj[0]['value1month']) + "-01' and '" + str(obj[0]['value1month']) + "-30';")
            print(files)
        # elif(data['module'] == 'TRIAL BALANCE'):
        #     files = ("select entry.gl as 'GL Code', entry.glnodescription as 'GL Description', 0 as OpeningBalance, "
        #              "case when entry.type = 1 then entry.amount end as 'Debit',case when entry.type=2 then -(entry.amount) end as 'Credit', "
        #              "case when entry.type = 1 then entry.amount when entry.type=2 then -(entry.amount) end as 'Closing Blanace' "
        #              "from "+ str(DB_NAME_entry) +".entryservice_entry entry "
        #              "where entry.transactiondate between '"+ str(obj[0]['value1date']) +"' and '"+ str(obj[0]['value2date']) +"'")
        #     print(files)
        elif data['module'] == 'GSTR 2 INPUT RECORD':
            if obj[0]['master'] == 1:
                files = (
                        "select ven.code as 'Vendor Code',ven.name as 'Vendor Name',apinv.suppliergst as 'GSTIN Of Supplier',apinv.raisorbranchgst as 'GSTIN Of Reciver', "
                        "date_format(invoicedate,'%d-%M-%Y') as 'Invoice Date',date_format(appaydet.created_date,'%d-%M-%Y') as 'Payment Date',apinv.invoiceno As 'Invoice No.', ap.crno as 'ECF No', "
                        "apdetail.unitprice as 'Taxable Value', apdetail.igst as 'IGST', apdetail.cgst as 'CGST', apdetail.sgst as 'SGST', "
                        "apdetail.taxamount as 'Total GST', apdetail.totalamount as 'Gross', apdetail.taxamount/2 as '50% Reversal', mstate.name as 'Place Of Supply(State)', "
                        "entry.gl as 'GL Code', entry.glnodescription as 'GL Description', apdetail.hsn as 'HSN/SAC Code', apdetail.description as 'Description/Narration' , "
                        "case when apinv.status=1 then 'NEW' when apinv.status=2 then 'PENDING FOR APPROVAL' when apinv.status=3 then 'BOUNCE' "
                    "when apinv.status=4 then 'RE-AUDIT' when apinv.status=5 then 'REJECTED' when apinv.status=6 then 'PAYMENT INITIATED' "
                    "when apinv.status=7 then 'APPROVED' when apinv.status=8 then 'PAID' when apinv.status=9 then 'FILE INITIATED' when apinv.status=10 then 'AP INITIATED' "
                    "when apinv.status=11 then 'PAY INITIATED' end as 'AP Status' "
                        "from " + str(DB_NAME_vendor) + ".vendorservice_vendor ven "
                                                        "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                      "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierpayment pay on supp.id=pay.supplierbranch_id "
                                      "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apheader ap on apinv.apheader_id = ap.id "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apcredit apcre on apcre.apinvoiceheader_id=apinv.id and apcre.is_delete=0 "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail on apdetail.apinvoiceheader_id = apinv.id "
                                    "left join " + str(
                    DB_NAME_apdb) + ".apservice_paymentdetails appaydet on appaydet.apinvoiceheader_id = apinv.id "
                                      "inner join " + str(
                    DB_NAME_entry) + ".entryservice_entry entry on entry.crno = ap.crno "
                                     "left join " + str(
                    DB_NAME_master) + ".masterservice_address madd on madd.id = supp.address_id "
                                      "left join " + str(
                    DB_NAME_master) + ".masterservice_state mstate on mstate.id = madd.state_id "
                                      "where apinv.status in (7,8,6,9,11) and entry.transactiondate between '" + str(
                    obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' and (entry.gl in ("+(gl_no)+") or entry.gl like '4%') group by entry.crno;")
            if obj[0]['master'] == 4:
                files = (
                        "select ven.code as 'Vendor Code',ven.name as 'Vendor Name',apinv.suppliergst as 'GSTIN Of Supplier',apinv.raisorbranchgst as 'GSTIN Of Reciver', "
                        "date_format(invoicedate,'%d-%M-%Y') as 'Invoice Date',date_format(appaydet.created_date,'%d-%M-%Y') as 'Payment Date',apinv.invoiceno As 'Invoice No.', ap.crno as 'ECF No', "
                        "apdetail.unitprice as 'Taxable Value', apdetail.igst as 'IGST', apdetail.cgst as 'CGST', apdetail.sgst as 'SGST', "
                        "apdetail.taxamount as 'Total GST', apdetail.totalamount as 'Gross', apdetail.taxamount/2 as '50% Reversal', mstate.name as 'Place Of Supply(State)', "
                        "entry.gl as 'GL Code', entry.glnodescription as 'GL Description', apdetail.hsn as 'HSN/SAC Code', apdetail.description as 'Description/Narration' , "
                        "case when apinv.status=1 then 'NEW' when apinv.status=2 then 'PENDING FOR APPROVAL' when apinv.status=3 then 'BOUNCE' "
                    "when apinv.status=4 then 'RE-AUDIT' when apinv.status=5 then 'REJECTED' when apinv.status=6 then 'PAYMENT INITIATED' "
                    "when apinv.status=7 then 'APPROVED' when apinv.status=8 then 'PAID' when apinv.status=9 then 'FILE INITIATED' when apinv.status=10 then 'AP INITIATED' "
                    "when apinv.status=11 then 'PAY INITIATED' end as 'AP Status' "
                        "from " + str(DB_NAME_vendor) + ".vendorservice_vendor ven "
                                                        "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                      "inner join " + str(
                    DB_NAME_vendor) + ".vendorservice_supplierpayment pay on supp.id=pay.supplierbranch_id "
                                      "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apheader ap on apinv.apheader_id = ap.id "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apcredit apcre on apcre.apinvoiceheader_id=apinv.id and apcre.is_delete=0 "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail on apdetail.apinvoiceheader_id = apinv.id "
                                    "inner join " + str(
                    DB_NAME_apdb) + ".apservice_paymentdetails appaydet on appaydet.apinvoiceheader_id = apinv.id "
                                      "inner join " + str(
                    DB_NAME_entry) + ".entryservice_entry entry on entry.crno = ap.crno "
                                     "left join " + str(
                    DB_NAME_master) + ".masterservice_address madd on madd.id = supp.address_id "
                                      "left join " + str(
                    DB_NAME_master) + ".masterservice_state mstate on mstate.id = madd.state_id "
                                      "where entry.transactiondate between '" + str(
                    obj[0]['value1month']) + "-01' and '" + str(
                    obj[0]['value1month']) + "-30' and  (entry.gl in ("+(gl_no)+") or entry.gl like '4%') group by entry.crno;")

            print(files)
        elif data['module'] == 'LIST OF INVOICES NOT PAID':
            files = (
                    "select ven.code as 'Vendor Code',ven.name as 'Vendor Name',entry.gl as 'Expense GL Code', entry.glnodescription as 'Expense GL Description', "
                    "ecfhead.crno as 'ECF No',apinv.invoiceno as 'Invoice No',date_format(invoicedate,'%d-%M-%Y') as 'Invoice Date',date_format(ap.apdate,'%d-%M-%Y') as 'Creation Date', "
                    "apdetail.amount as 'Taxable Value', apdetail.igst as 'IGST', apdetail.cgst as 'CGST', apdetail.sgst as 'SGST', 0 as 'UGST', "
                    "0 as 'Cess',apdetail.totalamount as 'Invoice Value', " 
                    "case when apinv.status=1 then 'NEW' when apinv.status=2 then 'PENDING FOR APPROVAL' when apinv.status=3 then 'BOUNCE' "
                    "when apinv.status=4 then 'RE-AUDIT' when apinv.status=5 then 'REJECTED' when apinv.status=6 then 'PAYMENT INITIATED' "
                    "when apinv.status=7 then 'APPROVED' when apinv.status=8 then 'PAID' when apinv.status=9 then 'FILE INITIATED' when apinv.status=10 then 'AP INITIATED' "
                    "when apinv.status=11 then 'PAY INITIATED' end as 'AP Status' "
                    " from " + str(
                DB_NAME_apdb) + ".apservice_apheader ap INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail ON apdetail.apinvoiceheader_id = apinv.id "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + " "
                ".apservice_apcredit apcre ON apcre.apinvoiceheader_id = apinv.id left JOIN " + str(
                DB_NAME_vendor) +
                ".vendorservice_supplierbranch supp ON supp.id = apinv.supplier_id left JOIN " + str(
                DB_NAME_vendor) + "."
                "vendorservice_vendor ven ON ven.id = supp.vendor_id left JOIN " + str(
                DB_NAME_vendor) + ""
                ".vendorservice_suppliertax tax ON ven.id = tax.vendor_id INNER JOIN " + str(
                DB_NAME_ecf) + ".ecfservice_ecfheader ecfhead ON ecfhead.crno = ap.crno INNER JOIN " + str(
                DB_NAME_entry) + " .entryservice_entry entry on entry.crno = ap.crno "
                                 " where (entry.gl in ("+(gl_no)+") or entry.gl like '4%')  and apinv.status !=8 "
                                 " and apinv.status in (1,10,2,7) "                                
                                 " and entry.transactiondate between '" + str(
                obj[0]['value1date']) + "' and '" + str(
                obj[0]['value2date']) + "' group by ap.crno;")
            print(files)
        # elif data['module'] == 'EXPENSE CLAIM REPORT':
        #     files = (
        #             "SELECT a.crno as 'CR No', case when a.ecftype=1 then 'PO' when a.ecftype=2 then 'NON PO' when a.ecftype=3 "
        #             "then 'ERA' when a.ecftype=4 then 'ADVANCE' when a.ecftype=8 then 'TCF' end as 'Invoice Type', "
        #             "date_format(a.ecfdate,'%d-%M-%Y') as 'ECF Date', a.ecfamount as 'ECF Amount', case when a.ecfstatus = 1 then 'DRAFT' when a.ecfstatus = 2 then 'PENDING FOR APPROVAL'  "
        #             "when a.ecfstatus = 3 then 'APPROVED' when a.ecfstatus = 4 then 'REJECT' when a.ecfstatus = 5 then 'PENDING FOR APPROVAL MODIFICATION' "
        #             "when a.ecfstatus = 6 then 'DELETE' end as 'ECF Status', uempbra.name as 'Branch Name', mclient.client_name as 'Client Name',  "
        #             "uemp.full_name as 'Raised By',uempapp.full_name as 'Approved By',b.invoiceno as 'Invoice No', date_format(b.invoicedate,'%d-%M-%Y') as 'Invoice Date', "
        #             "b.invoiceamount as 'Invoice Amount', b.taxamount as 'Tax Amount', b.totalamount as 'Total Amount', b.inv_crno as 'Invoice CR No', "
        #             "supp.name as 'Supplier Name' FROM " + str(DB_NAME_ecf) + ".ecfservice_ecfheader AS a "
        #                                                                       "INNER JOIN " + str(
        #         DB_NAME_ecf) + ".ecfservice_invoiceheader AS b ON a.id = b.ecfheader_id "
        #                        "LEFT JOIN " + str(
        #         DB_NAME_vendor) + ".vendorservice_supplierbranch supp ON supp.id = b.supplier_id "
        #                           "LEFT JOIN " + str(
        #         DB_NAME_nwisefin) + ".userservice_employee uemp on uemp.id = a.raisedby "
        #                             "LEFT JOIN " + str(
        #         DB_NAME_nwisefin) + ".userservice_employee uempapp on uempapp.id = a.approvedby "
        #                             "LEFT JOIN " + str(
        #         DB_NAME_nwisefin) + ".userservice_employeebranch uempbra on uempbra.id = a.branch "
        #                             "LEFT JOIN " + str(
        #         DB_NAME_master) + ".masterservice_clientcode mclient on mclient.id = a.client_code "
        #                           "WHERE a.ecfstatus in (2,3,4,5) and a.ecfdate between '" + str(
        #         obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' group by a.crno;")
        #     print(files)
        # elif data['module'] == 'DEBIT REPORT':
        #     files = ("Select apinv.invoiceno as 'Invoice No',ecfhead.crno as 'ECF Number',ven.code as 'Vendor Code', "
        #              "supp.name as 'Supplier Name',user.full_name as 'AP Maker Name',apdeb.amount as 'Debit Amount',apinvdel.totalamount as 'Gross Amount', "
        #              "case when ap.aptype=1 then 'PO' when ap.aptype=2 then 'NON PO' when ap.aptype=3 then 'PETTYCASH' "
        #              "when ap.aptype=4 then 'ADVANCE' when ap.aptype=8 then 'TCF' end as 'Invoice Type', entry.gl as 'GL No', "
        #              "entry.glnodescription as 'Oracle GL Name',apsubcat.name as 'AP Subcategory',apcat.name as 'AP Category', "
        #              "apinvdel.productname as 'Product Name',bs.name as 'BS Name', cc.name as 'CC Name', apinv.updated_date as 'AP Approved Date', "
        #              "case when apinv.status=1 then 'NEW' when apinv.status=2 then 'PENDING FOR APPROVAL' when apinv.status=3 then 'BOUNCE' "
        #              "when apinv.status=4 then 'APPROVED ' when apinv.status=5 then 'RE-AUDIT' when apinv.status=6 then 'PAYMENT INITIATED' "
        #              "when apinv.status=7 then 'PAID' when apinv.status=8 then 'FILE INITIATED' when apinv.status=9 then 'AP INITIATED' "
        #              "when apinv.status=10 then 'PAY INITIATED' end as 'AP Status' "
        #              "from " + str(
        #         DB_NAME_entry) + ".entryservice_entry entry inner join napservice.apservice_apheader ap on entry.crno = ap.crno "
        #                          "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apdebit apdeb on apdeb.apinvoicedetail_id = apinvdel.id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apccbsdetails apccbs on apccbs.apdebit_id = apdeb.id "
        #                         "inner join " + str(
        #         DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
        #                           "inner join " + str(
        #         DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
        #                           "left join " + str(
        #         DB_NAME_ecf) + ".ecfservice_ecfheader ecfhead on ecfhead.crno=ap.crno "
        #                        "left join " + str(
        #         DB_NAME_master) + ".masterservice_apsubcategory apsubcat on apsubcat.glno=entry.gl "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_apcategory apcat on apcat.id=apsubcat.category_id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_businesssegment bs on bs.code = apccbs.bs_code "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_costcentre cc on cc.code = apccbs.cc_code "
        #                           "left join " + str(
        #         DB_NAME_nwisefin) + ".userservice_employee user on user.id = apinv.created_by "
        #                             "where entry.transactiondate between '" + str(
        #         obj[0]['value1date']) + "' and '" + str(
        #         obj[0]['value2date']) + "' and entry.type=1 group by entry.crno order by entry.created_date;")
        #     print(files)
        # elif data['module'] == 'CREDIT REPORT':
        #     files = (
        #             "Select date_format(inwhead.date,'%d-%M-%Y') as 'Inward Date', ap.crno as 'CR No',case when ap.aptype=1 then 'PO' when ap.aptype=2 then 'NON PO' when ap.aptype=3 "
        #             "then 'PETTYCASH' when ap.aptype=4 then 'ADVANCE' when ap.aptype=8 then 'TCF' end as 'Invoice Type', "
        #             "supp.code as 'Supplier Code', supp.name as 'Supplier Name', supp.panno as 'Supplier Pan No', "
        #             "supp.gstno as 'Supplier GST No',mcomm.name as 'Commodity Name',apinv.invoiceno as 'Invoice No',date_format(apinv.invoicedate,'%d-%M-%Y') as 'Invoice Date', "
        #             "apinv.invoiceamount as 'Bill Amount', apinv.taxamount as 'GST_AMOUNT',apinv.otheramount as'Other Amount',apinv.roundoffamt as'Roundoff Amount', "
        #             "apinv.totalamount as 'Invoice Amount',apdeb.deductionamount as 'TDS Amount', apinv.totalamount as 'Amount Payable',ecfcr.creditrefno as 'Credit AC', "
        #             "mpay.name as 'Paymode Name', ap.raisername as 'AP Maker', ap.approvername as 'AP Approver', appayhead.pvno as 'Payment PVNo', "
        #             "date_format(appayhead.paymentheader_date,'%d-%M-%Y') as 'Transaction Date', case when ecfhead.ecfstatus = 1 then 'DRAFT' when ecfhead.ecfstatus = 2 then 'PENDING FOR APPROVAL'  "
        #             "when ecfhead.ecfstatus = 3 then 'APPROVED' when ecfhead.ecfstatus = 4 then 'REJECT' when ecfhead.ecfstatus = 5 then 'PENDING FOR APPROVAL MODIFICATION' "
        #             "when ecfhead.ecfstatus = 6 then 'DELETE' end as 'ECF Status', ecfhead.remark as 'ECF Purpose' from " + str(
        #         DB_NAME_entry) + ".entryservice_entry entry "
        #                          "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apcredit apcre on apcre.apinvoiceheader_id=apinv.id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_apdebit apdeb on apdeb.apinvoiceheader_id=apinv.id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_paymentdetails appaydetail on appaydetail.apinvoiceheader_id=apinv.id "
        #                         "inner join " + str(
        #         DB_NAME_apdb) + ".apservice_paymentheader appayhead on appayhead.id=appaydetail.paymentheader_id "
        #                         "left join " + str(
        #         DB_NAME_ecf) + ".ecfservice_ecfheader ecfhead on ecfhead.crno=ap.crno "
        #                        "left join " + str(
        #         DB_NAME_ecf) + ".ecfservice_invoiceheader ecfinvhead on ecfinvhead.ecfheader_id=ecfhead.id "
        #                        "left join " + str(
        #         DB_NAME_ecf) + ".ecfservice_credit ecfcr on ecfcr.invoiceheader_id=ecfinvhead.id "
        #                        "left join " + str(
        #         DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
        #                           "left join " + str(
        #         DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
        #                           "left join " + str(
        #         DB_NAME_vendor) + ".vendorservice_suppliertax tax on ven.id=tax.vendor_id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_tax mtax on mtax.id=tax.tax_id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_subtax msub on msub.id=tax.subtax_id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_taxrate mrate on mrate.subtax_id=msub.id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_commodity mcomm on mcomm.id = ap.commodity_id "
        #                           "left join " + str(
        #         DB_NAME_master) + ".masterservice_paymode mpay on mpay.id = apcre.paymode_id "
        #                           "inner join " + str(
        #         DB_NAME_inward) + ".inwardservice_inwarddetails inwdet on inwdet.id = ap.inwarddetails_id "
        #                           "inner join " + str(
        #         DB_NAME_inward) + ".inwardservice_inwardheader inwhead on inwhead.id = inwdet.inwardheader_id "
        #                           "where entry.transactiondate between '" + str(
        #         obj[0]['value1date']) + "' and '" + str(
        #         obj[0]['value2date']) + "' and entry.type=2 group by entry.crno order by entry.created_date;")
        #     print(files)
        # elif (data['module'] == 'VENDOR STATEMENT OF ACCOUNT'):
        #     if obj[0]['master'] == 1:
        #         truncate_stamp = ("truncate nwisefin.reportservice_stamptrailreport;")
        #         with connection.cursor() as cursor:
        #             cursor.execute(truncate_stamp)
        #         insert_files = (
        #                 "insert into nwisefin.reportservice_stamptrailreport (entity_id,crno,gl_no,gl_code,gl_description,opening_balance,debit,credit,closing_balance,invoice_no,invoice_date,status,created_by,created_date) "
        #                 "Select 1,entry.crno as 'crno', entry.gl as 'glno',supp.code as 'gl_code', supp.name as 'gl_description', 0 as 'opening_balance', "
        #                 "case when entry.type=1 then entry.amount end as 'debit', case when entry.type=2 then entry.amount end as 'credit',0, "
        #                 "apinv.invoiceno as 'invoice_no',apinv.invoicedate as 'invoice_date',1," + str(
        #             emp_id) + ",now() "
        #                       "from " + str(DB_NAME_entry) + ".entryservice_entry entry inner join " + str(
        #             DB_NAME_apdb) + ".apservice_apheader ap on entry.crno = ap.crno "
        #                             "inner join " + str(
        #             DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on ap.id =apinv.apheader_id "
        #                             "inner join " + str(
        #             DB_NAME_apdb) + ".apservice_apinvoicedetail apinvdel on apinv.id =apinvdel.apinvoiceheader_id "
        #                             "left join " + str(
        #             DB_NAME_master) + ".masterservice_apsubcategory apsubcat on apsubcat.glno=entry.gl "
        #                               "inner join " + str(
        #             DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
        #                               "inner join " + str(
        #             DB_NAME_vendor) + ".vendorservice_vendor ven on ven.id=supp.vendor_id "
        #                               "where  entry.transactiondate between '" + str(
        #             obj[0]['value1date']) + "' and '" + str(
        #             obj[0]['value2date']) + "' and entry.entry_status=1 group by supp.code;")
        #         with connection.cursor() as cursor:
        #             cursor.execute(insert_files)
        #         files = (
        #                 "Select stamp.gl_code as 'Vendor Code', stamp.gl_description as 'Vendor Name', date_format(entry.transactiondate,'%d-%M-%Y') as 'Creation Date', "
        #                 "(sum(stamp.debit) - sum(stamp.credit)) as 'Opening Balance', stamp.debit as'Debit',-(stamp.credit) as 'Credit', "
        #                 "case when stamp.closing_balance = 0 then (sum(stamp.debit) - sum(stamp.credit))-stamp.debit+stamp.credit end as 'Closing Balance', "
        #                 "supp.remarks as 'Text', stamp.invoice_no as 'Invoice No', date_format(stamp.invoice_date,'%d-%M-%Y') as 'Invoice Date' "
        #                 "from " + str(DB_NAME_nwisefin) + ".reportservice_stamptrailreport stamp "
        #                                                   "inner join " + str(
        #             DB_NAME_entry) + ".entryservice_entry entry on entry.crno = stamp.crno "
        #                              "inner join " + str(
        #             DB_NAME_apdb) + ".apservice_apheader ap on ap.crno = stamp.crno "
        #                             "inner join " + str(
        #             DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.apheader_id = ap.id "
        #                             "inner join " + str(
        #             DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on apinv.supplier_id=supp.id "
        #                               "where stamp.invoice_date between '" + str(
        #             obj[0]['value1date']) + "' and '" + str(
        #             obj[0]['value2date']) + "' group by stamp.gl_no order by stamp.invoice_date;")
        #     print(files)
            # case when apcre.paymode_id = 7 then apcre.amount else 0 end as 'TDS'
        elif (data['module'] == 'PAYMENT REPORT'):
            files = (
                    "select date_format(payhed.paymentheader_date,'%d-%M-%Y') as 'Payment Requested Date',ven.code as 'Vendor Code',ven.name as 'Vendor Name', case when ap.aptype=1 then 'PO' when ap.aptype=2 then 'NON PO' "
                    "when ap.aptype=3 then 'PETTYCASH' when ap.aptype=4 then 'ADVANCE' when ap.aptype=8 then 'TCF' end as 'Nature of Invoice', "
                    "entry.gl as 'Expense GL Code', entry.glnodescription as 'Expense GL Description', "
                    "entry.crno As 'ECF No.', apinv.invoiceno as 'Invoice No',date_format(apinv.invoicedate,'%d-%M-%Y') as 'Invoice Date', "
                    "apdetail.amount as 'Taxable Value', apdetail.igst as 'IGST', apdetail.cgst as 'CGST', apdetail.sgst as 'SGST', 0 as 'UGST', "
                    "0 as 'Cess',apdetail.totalamount as 'Invoice Value',ifnull(y.amount,0) as 'TDS', apcre.amount as 'Amount Paid', 0 as 'UTR No.', "
                    "date_format(ecfhead.ecfdate,'%d-%M-%Y') as 'Date of Payment',ecfhead.raisername as 'Payment Raised By', date_format(ecfinvhead.invoicedate,'%d-%M-%Y') as 'Request Raised on',  "
                    " datediff(ecfhead.ecfdate,ecfinvhead.invoicedate) as 'Actual TAT', 0 as 'TAT As Per Policy', "
                    "0 as 'Payment delayed by', 0 as 'Ageing (Days)' from  " + str(DB_NAME_apdb) + ".apservice_apheader ap INNER JOIN """ + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail ON apdetail.apinvoiceheader_id = apinv.id "
                                "INNER JOIN " + str(DB_NAME_apdb) + " "
                ".apservice_apcredit apcre ON apcre.apinvoiceheader_id = apinv.id left JOIN " + str(DB_NAME_vendor) +
                ".vendorservice_supplierbranch supp ON supp.id = apinv.supplier_id left JOIN " + str(DB_NAME_vendor) + "."
                "vendorservice_vendor ven ON ven.id = supp.vendor_id left JOIN " + str(DB_NAME_vendor) + ""
                ".vendorservice_suppliertax tax ON ven.id = tax.vendor_id INNER JOIN " + str(DB_NAME_entry) + ""
                ".entryservice_entry entry ON entry.crno = ap.crno INNER JOIN " + str(DB_NAME_ecf) + ""
                ".ecfservice_ecfheader ecfhead ON ecfhead.crno = ap.crno INNER JOIN " + str( DB_NAME_ecf) +
                ".ecfservice_invoiceheader ecfinvhead ON ecfinvhead.ecfheader_id = ecfhead.id INNER JOIN "
                + str(DB_NAME_apdb) + ".apservice_paymentdetails appaydel ON apinv.id = appaydel.apinvoiceheader_id "
                " INNER JOIN " + str(DB_NAME_apdb) + ".apservice_paymentheader payhed ON payhed.id = appaydel.paymentheader_id "
                " LEFT JOIN (SELECT z.id, z.apinvoiceheader_id, z.amount FROM " + str(DB_NAME_apdb) + ".apservice_apcredit AS z "
                " WHERE z.paymode_id = 7) AS y ON y.apinvoiceheader_id = apinv.id "
                               " where apinv.status=8 and date_format(appaydel.created_date,'%Y-%m-%d') between '" + str(
                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' group by entry.crno;")
            # and (entry.gl in ("+(gl_no)+") or entry.gl like '4%')
            print(files)
        elif (data['module'] == 'PAYMENT COUNT MOVEMENT'):
            truncate_stamp = ("truncate nwisefin.reportservice_stamppaycount;")
            with connection.cursor() as cursor:
                cursor.execute(truncate_stamp)
                date_mod = obj[0]['value1date'][:-3]
            insert_1 = ("insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamppaycount (entity_id,particular,vendor_payment,travel_claim,rcm_payment,statutory_payment,foreign_payment,total,created_by) "
                                    "select 1,'Opening Balance (at the beginning of the month)',case when ap.aptype=1 or 2 or 3 or 4 or 5 or 6  then count(*) else 0 end as 'Vendor Payment', "
                                    "case when ap.aptype=8 then count(*) else 0 end as 'Travel Claim', "
                                    "case when ap.aptype=2  and mprod.product_isrcm = 'Y' then count(*) else 0 end as 'RCM Payment',  "
                                    "0 as 'Statutory Payment',0 as 'Foreign Currency Payment',count(*) as 'Total'," + str(
                emp_id) + " "
                          "from " + str(DB_NAME_vendor) + ".vendorservice_vendor ven inner join " + str(
                DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                  "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
                                "inner join  " + str(
                DB_NAME_apdb) + ".apservice_apheader ap on apinv.apheader_id = ap.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail on apdetail.apinvoiceheader_id = apinv.id "
                                "left join " + str(
                DB_NAME_apdb) + ".apservice_paymentdetails appaydet on appaydet.apinvoiceheader_id = apinv.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_paymentheader appayhead on appayhead.id = appaydet.paymentheader_id "
                                "left join " + str(
                DB_NAME_master) + ".masterservice_product mprod on mprod.code = apdetail.productcode "
                                  "where appayhead.paymentheader_date='" + str(date_mod) + "-01' and apinv.status=1;")
            with connection.cursor() as cursor:
                cursor.execute(insert_1)

            insert_2 = (
                    "insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamppaycount (entity_id,particular,vendor_payment,travel_claim,rcm_payment,statutory_payment,foreign_payment,total,created_by) "
                                    "select 1,'Opening Balance (at the beginning of the month)',case when ap.aptype=1 or 2 or 3 or 4 or 5 or 6  then count(*) else 0 end as 'Vendor Payment', "
                                    "case when ap.aptype=8 then count(*) else 0 end as 'Travel Claim', "
                                    "case when ap.aptype=2  and mprod.product_isrcm = 'Y' then count(*) else 0 end as 'RCM Payment',  "
                                    "0 as 'Statutory Payment',0 as 'Foreign Currency Payment',count(*) as 'Total'," + str(
                emp_id) + " "
                          "from " + str(DB_NAME_vendor) + ".vendorservice_vendor ven inner join " + str(
                DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                  "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
                                "inner join  " + str(
                DB_NAME_apdb) + ".apservice_apheader ap on apinv.apheader_id = ap.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail on apdetail.apinvoiceheader_id = apinv.id "
                                "left join " + str(
                DB_NAME_apdb) + ".apservice_paymentdetails appaydet on appaydet.apinvoiceheader_id = apinv.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_paymentheader appayhead on appayhead.id = appaydet.paymentheader_id "
                                "left join " + str(
                DB_NAME_master) + ".masterservice_product mprod on mprod.code = apdetail.productcode "
                                  "where appayhead.paymentheader_date between '" + str(
                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' and apinv.status=6;")
            with connection.cursor() as cursor:
                cursor.execute(insert_2)

            insert_3 = (
                    "insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamppaycount (entity_id,particular,vendor_payment,travel_claim,rcm_payment,statutory_payment,foreign_payment,total,created_by) "
                                    "select 1,'Opening Balance (at the beginning of the month)',case when ap.aptype=1 or 2 or 3 or 4 or 5 or 6  then count(*) else 0 end as 'Vendor Payment', "
                                    "case when ap.aptype=8 then count(*) else 0 end as 'Travel Claim', "
                                    "case when ap.aptype=2  and mprod.product_isrcm = 'Y' then count(*) else 0 end as 'RCM Payment',  "
                                    "0 as 'Statutory Payment',0 as 'Foreign Currency Payment',count(*) as 'Total'," + str(
                emp_id) + " "
                          "from " + str(DB_NAME_vendor) + ".vendorservice_vendor ven inner join " + str(
                DB_NAME_vendor) + ".vendorservice_supplierbranch supp  on ven.id=supp.vendor_id "
                                  "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader apinv on apinv.supplier_id=supp.id "
                                "inner join  " + str(
                DB_NAME_apdb) + ".apservice_apheader ap on apinv.apheader_id = ap.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_apinvoicedetail apdetail on apdetail.apinvoiceheader_id = apinv.id "
                                "left join " + str(
                DB_NAME_apdb) + ".apservice_paymentdetails appaydet on appaydet.apinvoiceheader_id = apinv.id "
                                "inner join " + str(
                DB_NAME_apdb) + ".apservice_paymentheader appayhead on appayhead.id = appaydet.paymentheader_id "
                                "left join " + str(
                DB_NAME_master) + ".masterservice_product mprod on mprod.code = apdetail.productcode "
                                  "where appayhead.paymentheader_date between '" + str(
                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + "' and apinv.status=8;")
            with connection.cursor() as cursor:
                cursor.execute(insert_3)

            insert_4 = ("insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stamppaycount(entity_id,particular,vendor_payment,travel_claim,rcm_payment,statutory_payment,foreign_payment,total,created_by) "
                                    "select 1,'Closing Balance (at the end of the month)', "
                                    "(json_extract(concat('[',group_concat(vendor_payment),']'),'$[0]')) + (json_extract(concat('[',group_concat(vendor_payment),']'),'$[1]')) - (json_extract(concat('[',group_concat(vendor_payment),']'),'$[2]')) as 'vendor_payment', "
                                    "(json_extract(concat('[',group_concat(travel_claim),']'),'$[0]')) + (json_extract(concat('[',group_concat(travel_claim),']'),'$[1]')) - (json_extract(concat('[',group_concat(travel_claim),']'),'$[2]')) as 'travel_claim', "
                                    "(json_extract(concat('[',group_concat(rcm_payment),']'),'$[0]')) + (json_extract(concat('[',group_concat(rcm_payment),']'),'$[1]')) - (json_extract(concat('[',group_concat(rcm_payment),']'),'$[2]')) as 'travel_claim', "
                                    "0 as statutory_payment, 0 as foreign_payment, (sum(vendor_payment)) + (sum(travel_claim)) + (sum(rcm_payment)) as total," + str(
                emp_id) + " from " + str(DB_NAME_nwisefin) + ".reportservice_stamppaycount;")
            with connection.cursor() as cursor:
                cursor.execute(insert_4)

            files = (
                "select particular,vendor_payment,travel_claim,rcm_payment,statutory_payment,foreign_payment,total from nwisefin.reportservice_stamppaycount;")
        with connection.cursor() as cursor:
            cursor.execute(files)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            # if data['module'] == 'JOURNAL VOUCHER':
            #     df_data['Voucher Date'] = datetime.strftime()
            #     df_data['Value Date'] = datetime.now().strftime("%d-%m-%Y")
            # elif data['module'] == 'ACCOUNT PAYABLE':
            #     df_data['Voucher Date'] = datetime.now().strftime("%d-%m-%Y")
            # elif (data['module'] == 'TDS REPORT'):
            #     df_data['Creation Date'] = datetime.now().strftime("%d-%m-%Y")
            #     df_data['Invoice Date'] = datetime.now().strftime("%d-%m-%Y")
            # elif (data['module'] == 'EXPENSE CLAIM REPORT'):
            #     df_data['ECF Date'] = datetime.now().strftime("%d-%m-%Y")
            #     df_data['Invoice Date'] = datetime.now().strftime("%d-%m-%Y")
            # elif (data['module'] == 'DEBIT REPORT'):
            #     df_data['Invoice Date'] = datetime.now().strftime("%d-%m-%Y")
            #     df_data['AP Approved Date'] = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            #     df_data['Payment Date'] = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        output = BytesIO
        output.name = 'REPORT-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        if data['module'] == 'TRIAL BALANCE':
            df_data.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=7)
        else:
            df_data.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
        worksheet = writer.sheets['Sheet1']
        # def highlight_cells():
        # provide your criteria for highlighting the cells here
        # return ['background-color: yellow']
        # df_data.style.apply(highlight_cells)
        # if data['module'] == 'ACCOUNT PAYABLE':
        #     worksheet.write_string(2, 5, 'ACCOUNT PAYABLE')
        if data['module'] == 'JOURNAL VOUCHER':
            worksheet.write_string(2, 5, 'JOURNAL VOUCHER')
        elif data['module'] == 'SUPPLIER MASTER':
            worksheet.write_string(2, 5, 'SUPPLIER MASTER')
        elif data['module'] == 'TDS REPORT':
            worksheet.write_string(2, 5, 'TDS REPORT')
        elif data['module'] == 'TRIAL BALANCE':
            if obj[0]['master'] == 1:
                worksheet.write_string(0, 2, 'TRIAL BALANCE')
                worksheet.write_string(2, 0, "Trial Balance for the period '" + str(obj[0]['value1date']) + "' to "
                                                                                                            "'" + str(
                    obj[0]['value2date']) + "'")
                worksheet.write_string(3, 0, 'Generated on')
                worksheet.write_string(3, 1, datetime.now().strftime("%d-%m-%Y"))
                worksheet.write_string(4, 0, 'Generated by')
                emp_name = ("select full_name from " + str(
                    DB_NAME_nwisefin) + ".userservice_employee where id ='" + str(emp_id) + "';")
                with connection.cursor() as cursor:
                    cursor.execute(emp_name)
                    rows = cursor.fetchall()
                    rows = list(rows)
                    emp_name_data = rows[0]
                worksheet.write_string(4, 1, str(emp_name_data[0]))
            elif obj[0]['master'] == 4:
                worksheet.write_string(0, 2, 'TRIAL BALANCE')
                worksheet.write_string(2, 0, "Trial Balance for the period '" + str(obj[0]['value1month']) + "-01' to "
                                                                                                             "'" + str(
                    obj[0]['value1month']) + "-30'")
                worksheet.write_string(3, 0, 'Generated on')
                worksheet.write_string(3, 1, datetime.now().strftime("%d-%m-%Y"))
                worksheet.write_string(4, 0, 'Generated by')
                emp_name = ("select full_name from " + str(
                    DB_NAME_nwisefin) + ".userservice_employee where id ='" + str(emp_id) + "';")
                with connection.cursor() as cursor:
                    cursor.execute(emp_name)
                    rows = cursor.fetchall()
                    rows = list(rows)
                    emp_name_data = rows[0]
                worksheet.write_string(4, 1, str(emp_name_data[0]))
            # worksheet.write_string(6, 4, str(df_data['Total_Closing_Balance']))
        elif data['module'] == 'GSTR 2 INPUT RECORD':
            worksheet.write_string(2, 5, 'GST Input Report for GSTR 2B')
        elif data['module'] == 'LIST OF INVOICES NOT PAID':
            worksheet.write_string(2, 5, 'LIST OF INVOICES NOT PAID')
        # elif data['module'] == 'EXPENSE CLAIM REPORT':
        #     worksheet.write_string(2, 5, 'EXPENSE CLAIM REPORT')
        # elif data['module'] == 'DEBIT REPORT':
        #     worksheet.write_string(2, 7, 'DEBIT REPORT')
        # elif data['module'] == 'CREDIT REPORT':
        #     worksheet.write_string(2, 11, 'CREDIT REPORT')
        # elif data['module'] == 'VENDOR STATEMENT OF ACCOUNT':
        #     worksheet.write_string(2, 5, 'VENDOR STATEMENT OF ACCOUNT')
        elif data['module'] == 'PAYMENT REPORT':
            worksheet.write_string(2, 11, 'PAYMENT REPORT')
        elif data['module'] == 'PAYMENT COUNT MOVEMENT':
            worksheet.write_string(1, 3, 'PAYMENT COUNT MOVEMENT')
            worksheet.write_string(3, 0, "Movement of Vendor Payment Count for the period '" + str(
                obj[0]['value1date']) + "' to "
                                        "'" + str(obj[0]['value2date']) + "'")
        writer.save()
        output.seek(0)
        output.size = BytesIO.__sizeof__()
        writer.name = report + '_demo.xlsx'
        writer.size = df_data.size
        mod_obj = DocModule()
        doc_pref = DocPrefix()
        doc_param = {"module": mod_obj.REPORT, "ref_type": mod_obj.REPORT,
                     "ref_id": id}
        # file = ContentFile(BytesIO.read())
        # file.name = BytesIO.name
        doc_serv = DocumentsService(scope)
        upload_serv = doc_serv.upload_single_Doc_Report(BytesIO, doc_param)
        reportdownload = ReportDetails.objects.using(self._current_app_schema()). \
            create(reportdetails_modulenamedropdownid=report_id, reportdetails_reportemp_id=emp_id,
                   reportdetails_id=upload_serv.id,
                   reportdetails_path=upload_serv.gen_file_name, reportdetails_status='COMPLETED',
                   entity_id=self._entity_id(), status=1,
                   created_by=emp_id, created_date=now())
        reportdownload.save()
        logger.info('Report Excel Created - ' + START_TIME)
        # obj = ReportDocuments.objects.using(self._current_app_schema()).get(file_name=upload_serv.id)
        # generated_id = upload_serv.file_name
        # success_obj = NWisefinSuccess()
        # success_obj.set_status(SuccessStatus.SUCCESS)
        # success_obj.set_message(generated_id)
        return output

    def fetch_downloadlist(self):
        condition = Q(status=1)
        try:
            logger.info('Report Download List - ' + START_TIME)
            parameter = ReportDetails.objects.using(self._current_app_schema()).filter(condition)
            print(self._current_app_schema())
            list_length = len(parameter)
            module_list_data = NWisefinList()
            if list_length <= 0:
                return module_list_data
            else:
                for i in parameter:
                    module_data = templateDownloadResponse()
                    module_data.set_id(i.id)
                    module_data.set_module_name(i.entity_id)
                    module_data.set_report_template_name(i.reportdetails_modulenamedropdownid)
                    module_data.set_report_id(i.reportdetails_id)
                    module_data.set_file_name(i.reportdetails_path)
                    module_data.set_status(i.reportdetails_status)
                    module_list_data.append(module_data)
                    logger.info('Report Download List - ' + START_TIME)
                    # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                    # entry_list_data.set_pagination(vpage)
                return module_list_data
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Report Download List - ' + str(e))
            return error_obj

    def fetch_reportdownload(self, id):
        condition = Q(status=1, id=id)
        try:
            logger.info('Report Download - ' + START_TIME)
            parameter = ReportDetails.objects.using(self._current_app_schema()).filter(condition)
            list_length = len(parameter)
            module_list_data = NWisefinList()
            if list_length <= 0:
                return module_list_data
            else:
                for i in parameter:
                    logger.info('Report Download - ' + START_TIME)
                    return i.reportdetails_path
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Report Download - ' + str(e))
            return error_obj

    def fetch_vendor(self,vendor_id):
        try:
            vendor = ("SELECT apinv.invoicedate AS 'invoice_date', apsubcat.name as 'Description', apinv.invoiceno AS 'invoice_no', "
                      "CASE WHEN entry.type = 1 THEN entry.amount else 0 END AS 'debit', "
                      "CASE WHEN entry.type = 2 THEN entry.amount else 0 END AS 'credit' "
                      "FROM nentry.entryservice_entry entry "
                      "INNER JOIN napservice.apservice_apheader ap ON entry.crno = ap.crno "
                      "INNER JOIN napservice.apservice_apinvoiceheader apinv ON ap.id = apinv.apheader_id "
                      "INNER JOIN napservice.apservice_apinvoicedetail apinvdel ON apinv.id = apinvdel.apinvoiceheader_id "
                      "LEFT JOIN nmaster.masterservice_apsubcategory apsubcat ON apsubcat.glno = entry.gl  "
                      "INNER JOIN nvendor.vendorservice_supplierbranch supp ON apinv.supplier_id = supp.id "
                      "INNER JOIN nvendor.vendorservice_vendor ven ON ven.id = supp.vendor_id  "
                      "WHERE apinv.supplier_id='"+str(vendor_id)+"'"
                      # "entry.transactiondate BETWEEN '2022-03-01' AND '2022-05-17' "
                      "AND entry.entry_status = 1 GROUP BY supp.code,apsubcat.name,apinv.invoicedate order by apinv.invoicedate;")
            with connection.cursor() as cursor:
                cursor.execute(vendor)
                columns = [x[0] for x in cursor.description]
                rows = cursor.fetchall()
                rows = list(rows)
                df_data = pd.DataFrame(rows, columns=columns)
            df = df_data.to_dict('records')
            print('df', df)
            module_list_data = NWisefinList()
            if len(df) > 0:
                for data in df:
                    asset = DictObj()
                    i = asset.get_obj(data)
                    module_data = vendorDownloadResponse()
                    module_data.set_invoice_date(i.invoice_date)
                    module_data.set_description(i.Description)
                    module_data.set_invoice_no(i.invoice_no)
                    module_data.set_debit(i.debit)
                    module_data.set_credit(i.credit)
                    module_list_data.append(module_data)
                    logger.info('Report Download List - ' + START_TIME)
                return module_list_data
            else:
                return module_list_data
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Report Download List - ' + str(e))
            return error_obj