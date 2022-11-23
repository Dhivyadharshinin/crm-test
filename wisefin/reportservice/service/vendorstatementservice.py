import os
import tempfile
import traceback
from datetime import datetime, date

import pdfkit
from django.http import HttpResponse
from django.template import loader
import io
from xhtml2pdf import pisa
from django.utils.timezone import now
from nwisefin.settings import logger, env
from reportservice.data.response.reportresponse import VendorReportResponse
from reportservice.models import StampVendorStatement, VendorModuleEOD
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
today = date.today()
START_TIME_D = datetime.now()
START_TIME = START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
from django.db import IntegrityError, connection
import json
import pandas as pd
out_data1 = []

class APDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def get_ap_schema(self):
        return self._current_app_schema()

class VENDORDBService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def get_vendor_schema(self):
        return self._current_app_schema()

class VendorstatementService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.REPORT_SERVICE)

    def fetch_vendorstatementservice(self,supplier_id,from_date,limit,offset,Type,scope):
        #condition = Q(status=1)
        from nwisefin.settings import DATABASES
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")
        DB_NAME_nwisefin = env.str('DB_NAME_nwisefindb')
        vendor_db = VENDORDBService(scope)
        Dynamicven_schema = vendor_db.get_vendor_schema()
        DB_NAME_vendordb = DATABASES.get(Dynamicven_schema).get("NAME")


        try:
            if Type=='Name':
                Dynamic_query = (
                            " select sum(c.amount) as 'Base Amount',sum(c.taxamount) "
                            " as 'Tax Amount',sum(d.amount) as 'TDS Amount',sum(d.amount) as 'LIQ Amount',p.paymentdetails_amount as 'Bank Payment' "
                            "from " + str(DB_NAME_apdb) + ".apservice_apheader a inner join " + str(
                        DB_NAME_apdb) + " .apservice_apinvoiceheader"
                                        " b on a.id=b.apheader_id and b.is_delete=0 "
                                        "inner join " + str(DB_NAME_apdb) + " .apservice_apinvoicedetail c "
                                                                            "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                                                            " left join " + str(
                        DB_NAME_apdb) + ".apservice_apcredit d on d.apinvoiceheader_id=b.id"
                                        " and d.is_delete=0 and d.status=1 inner join " + str(
                        DB_NAME_vendordb) + ".vendorservice_supplierbranch g"
                                            " on g.id=b.supplier_id inner join napservice.apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "
                                            "where a.id=0 ")
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
            else:
                Query_columns = ''
                if supplier_id != "":
                    Query_columns = "(b.supplier_id = " + "'" + str(supplier_id) + "'" + ")"
                if from_date != "":
                    Query_columns = "(b.invoicedate BETWEEN " + "'" + str(from_date) + "'" + " AND " + "'" + str(
                        from_date) + "'" + ")"
                Query_limit = " LIMIT " + str(limit) + " OFFSET " + str(offset)

                Dynamic_query = (" select b.id as Invoiceheader_id,c.id as Invoicedetails_id,a.crno AS Crno,b.invoiceno AS Invoiceno,date_format(b.invoicedate,'%Y-%m-%d') as Invoice_Date,"
                                 "CONVERT( SUM(c.amount) , DECIMAL (10 , 2 )) AS Base_Amount,"
                                 "CONVERT( SUM(c.taxamount) , DECIMAL (10 , 2 )) AS Tax_Amount,"
                                 " ifnull(CONVERT( ad.tds_amount , DECIMAL (10 , 2 )),0) AS TDS_Amount,"
                                 " ifnull(CONVERT( ae.liq_amount , DECIMAL (10 , 2 )),0) AS LIQ_Amount,g.name as supplier_name, "
                                 "CONVERT( -(ab.credit_amount) , DECIMAL (10 , 2 )) AS credit_amount,CONVERT( ac.debit_amount , DECIMAL (10 , 2 )) AS debit_amount "
                                 " ,p.paymentdetails_amount as Bank_Payment,date_format(p.created_date,'%Y-%m-%d') as payment_Date, "
                                 # " case when count(a.crno) > 1 then sum(p.paymentdetails_amount) else 0 end as  opening_balance, "
                                 "venstamp.closingbalance as opening_balance, (venstamp.closingbalance + CONVERT( ac.debit_amount , DECIMAL (10 , 2 )) - "
                                 "CONVERT( ab.credit_amount , DECIMAL (10 , 2 ))) as closing_balance, ifnull(callbackrefno,0) as UTRNO "
                                 "from "+str(DB_NAME_apdb)+".apservice_apheader a inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader"
                                 " b on a.id=b.apheader_id and b.is_delete=0 "
                                 "inner join "+str(DB_NAME_apdb)+" .apservice_apinvoicedetail c "
                                 "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                 " inner join "+str(DB_NAME_vendordb)+".vendorservice_supplierbranch g"
                                 " on g.id=b.supplier_id INNER JOIN (SELECT z.id, SUM(y.amount) AS credit_amount FROM "
                                 " "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader z INNER JOIN "+str(DB_NAME_apdb)+".apservice_apcredit y "
                                 "ON z.id = y.apinvoiceheader_id WHERE y.is_delete = 0 AND y.status = 1 GROUP BY z.id) "
                                 "AS ab ON ab.id = b.id INNER JOIN (SELECT m.id, SUM(n.amount) AS debit_amount FROM "+str(DB_NAME_apdb)+".apservice_apinvoiceheader m "
                                "INNER JOIN "+str(DB_NAME_apdb)+".apservice_apdebit n ON m.id = n.apinvoiceheader_id WHERE n.is_delete = 0 AND n.status = 1 "
                                "GROUP BY m.id) AS ac ON ac.id = b.id  inner join "+str(DB_NAME_apdb)+".apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "                                                                  
                                " left join (SELECT k.id, SUM(d.amount) AS tds_amount FROM  "+str(DB_NAME_apdb)+".apservice_apinvoiceheader k "
                                " INNER JOIN "+str(DB_NAME_apdb)+".apservice_apcredit d ON k.id = d.apinvoiceheader_id "
                                " WHERE d.paymode_id=7 and d.is_delete = 0 AND d.status = 1 GROUP BY k.id) AS ad ON ad.id = b.id "
                                "left join (select max(s.id),s.openingbalance,s.closingbalance,s.supplier_id from "
                                ""+str(DB_NAME_nwisefin)+".reportservice_stampvendorstatement s where s.supplier_id='"+str(supplier_id)+"') as venstamp on venstamp.supplier_id = b.supplier_id"
                                " left join (SELECT g.id, SUM(h.amount) AS liq_amount FROM "
                                " "+str(DB_NAME_apdb)+".apservice_apinvoiceheader g INNER JOIN "+str(DB_NAME_apdb)+".apservice_apcredit h ON g.id = h.apinvoiceheader_id"
                                " WHERE h.paymode_id=6 and h.is_delete = 0 AND h.status = 1 GROUP BY g.id) AS ae ON ae.id = b.id "
                                "left join "+str(DB_NAME_apdb)+".apservice_paymentdetails r on r.apinvoiceheader_id=g.id "
                                "left join "+str(DB_NAME_apdb)+".apservice_paymentheader payh on payh.id = r.paymentheader_id "
                                "where a.is_delete=0  and "
                                "  "+Query_columns+"  group by b.id  "+Query_limit+" ")
                print(Dynamic_query)
                logger.info('REPORT_VENDOR_LOGGER - ' + str(Dynamic_query))
                #print(Dynamic_query)
                with connection.cursor() as cursor:
                    cursor.execute(Dynamic_query)
                    columns = [x[0] for x in cursor.description]
                    rows = cursor.fetchall()
                    rows = list(rows)
                    df_data = pd.DataFrame(rows, columns=columns)
                    resp = json.loads(df_data.to_json(orient='records'))
                return resp
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Vendor Statement Error - ' + str(e))
            return error_obj


    def download_vendorstatementservice(self,supplier_id,from_date,scope):
        #condition = Q(status=1)
        from nwisefin.settings import DATABASES
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")
        DB_NAME_nwisefin = env.str('DB_NAME_nwisefindb')
        vendor_db = VENDORDBService(scope)
        Dynamicven_schema = vendor_db.get_vendor_schema()
        DB_NAME_vendordb = DATABASES.get(Dynamicven_schema).get("NAME")


        try:
                Dynamic_query = (
                            " select sum(c.amount) as 'Base Amount',sum(c.taxamount) "
                            " as 'Tax Amount',sum(d.amount) as 'TDS Amount',p.paymentdetails_amount as 'Bank Payment',sum(d.amount) as 'LIQ Amount' "
                            "from " + str(DB_NAME_apdb) + ".apservice_apheader a inner join " + str(
                        DB_NAME_apdb) + " .apservice_apinvoiceheader"
                                        " b on a.id=b.apheader_id and b.is_delete=0 "
                                        "inner join " + str(DB_NAME_apdb) + " .apservice_apinvoicedetail c "
                                                                            "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                                                            " left join " + str(
                        DB_NAME_apdb) + ".apservice_apcredit d on d.apinvoiceheader_id=b.id"
                                        " and d.is_delete=0 and d.status=1 inner join " + str(
                        DB_NAME_vendordb) + ".vendorservice_supplierbranch g"
                                            " on g.id=b.supplier_id inner join napservice.apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "
                                            "where a.id=0 ")
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
                    # resp = {"DATA": out_data}

                Query_columns = ''
                if supplier_id != "" and supplier_id != None:
                    Query_columns = "(b.supplier_id = " + "'" + str(supplier_id) + "'" + ")"
                if from_date != "" and from_date != None:
                    Query_columns += (" and (b.invoicedate BETWEEN " + "'" + str(from_date) + "'" + " AND " + "'" + str(
                        from_date) + "'" + ")")
                    # Query_columns = "(b.invoicedate BETWEEN " + "'" + str(from_date) + "'" + " AND " + "'" + str(
                    #     from_date) + "'" + ")"

                Dynamic_query = (
                            " select b.id as Invoiceheader_id,c.id as Invoicedetails_id,a.crno AS Crno,b.invoiceno AS Invoiceno,date_format(b.invoicedate,'%Y-%m-%d') as Invoice_Date,"
                            "CONVERT( SUM(c.amount) , DECIMAL (10 , 2 )) AS Base_Amount,"
                            "CONVERT( SUM(c.taxamount) , DECIMAL (10 , 2 )) AS Tax_Amount,"
                            " ifnull(CONVERT( ad.tds_amount , DECIMAL (10 , 2 )),0) AS TDS_Amount,"
                            " ifnull(CONVERT( ae.liq_amount , DECIMAL (10 , 2 )),0) AS LIQ_Amount,g.name as supplier_name, "
                            "CONVERT( -(ab.credit_amount) , DECIMAL (10 , 2 )) AS credit_amount,CONVERT( ac.debit_amount , DECIMAL (10 , 2 )) AS debit_amount "
                            " ,p.paymentdetails_amount as Bank_Payment,date_format(p.created_date,'%Y-%m-%d') as payment_Date, "
                            # " case when count(a.crno) > 1 then sum(p.paymentdetails_amount) else 0 end as  opening_balance, "
                            "venstamp.closingbalance as opening_balance, (venstamp.closingbalance + CONVERT( ac.debit_amount , DECIMAL (10 , 2 )) - "
                            "CONVERT( ab.credit_amount , DECIMAL (10 , 2 ))) as closing_balance, ifnull(callbackrefno,0) as UTRNO "
                            "from " + str(DB_NAME_apdb) + ".apservice_apheader a inner join " + str(
                        DB_NAME_apdb) + " .apservice_apinvoiceheader"
                                        " b on a.id=b.apheader_id and b.is_delete=0 "
                                        "inner join " + str(DB_NAME_apdb) + " .apservice_apinvoicedetail c "
                                                                            "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                                                            " inner join " + str(
                        DB_NAME_vendordb) + ".vendorservice_supplierbranch g"
                                            " on g.id=b.supplier_id INNER JOIN (SELECT z.id, SUM(y.amount) AS credit_amount FROM "
                                            " " + str(DB_NAME_apdb) + " .apservice_apinvoiceheader z INNER JOIN " + str(
                        DB_NAME_apdb) + ".apservice_apcredit y "
                                        "ON z.id = y.apinvoiceheader_id WHERE y.is_delete = 0 AND y.status = 1 GROUP BY z.id) "
                                        "AS ab ON ab.id = b.id INNER JOIN (SELECT m.id, SUM(n.amount) AS debit_amount FROM " + str(
                        DB_NAME_apdb) + ".apservice_apinvoiceheader m "
                                        "INNER JOIN " + str(
                        DB_NAME_apdb) + ".apservice_apdebit n ON m.id = n.apinvoiceheader_id WHERE n.is_delete = 0 AND n.status = 1 "
                                        "GROUP BY m.id) AS ac ON ac.id = b.id  inner join " + str(
                        DB_NAME_apdb) + ".apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "
                                        " left join (SELECT k.id, SUM(d.amount) AS tds_amount FROM  " + str(
                        DB_NAME_apdb) + ".apservice_apinvoiceheader k "
                                        " INNER JOIN " + str(
                        DB_NAME_apdb) + ".apservice_apcredit d ON k.id = d.apinvoiceheader_id "
                                        " WHERE d.paymode_id=7 and d.is_delete = 0 AND d.status = 1 GROUP BY k.id) AS ad ON ad.id = b.id "
                                        "left join (select max(s.id),s.openingbalance,s.closingbalance,s.supplier_id from "
                                        "" + str(
                        DB_NAME_nwisefin) + ".reportservice_stampvendorstatement s where s.supplier_id='" + str(
                        supplier_id) + "') as venstamp on venstamp.supplier_id = b.supplier_id"
                                       " left join (SELECT g.id, SUM(h.amount) AS liq_amount FROM "
                                       " " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader g INNER JOIN " + str(
                        DB_NAME_apdb) + ".apservice_apcredit h ON g.id = h.apinvoiceheader_id"
                                        " WHERE h.paymode_id=6 and h.is_delete = 0 AND h.status = 1 GROUP BY g.id) AS ae ON ae.id = b.id "
                                        "left join " + str(
                        DB_NAME_apdb) + ".apservice_paymentdetails r on r.apinvoiceheader_id=g.id "
                                        "left join " + str(
                        DB_NAME_apdb) + ".apservice_paymentheader payh on payh.id = r.paymentheader_id "
                                        "where a.is_delete=0  and "
                                        "  " + Query_columns + "  group by b.id ")
                print(Dynamic_query)
                logger.info('REPORT_LOGGER - ' + str(Dynamic_query))
                #print(Dynamic_query)
                with connection.cursor() as cursor:
                    cursor.execute(Dynamic_query)
                    columns = [x[0] for x in cursor.description]
                    rows = cursor.fetchall()
                    rows = list(rows)
                    df_data = pd.DataFrame(rows, columns=columns)
                    resp = json.loads(df_data.to_json(orient='records'))
                    resp_data = []
                    count = 0
                    counter = 1
                    module_list_data = NWisefinList()
                    for i in resp:
                        val = self.cal(zip(resp[count].keys(), resp[count].values()))
                        for j, q in zip(out_data, val):
                            module_data = VendorReportResponse()
                            module_data.set_ID(counter)
                            if j['name'] == 'Base Amount':
                                module_data.set_Invoice_Date(i['Invoice_Date'])
                            else:
                                module_data.set_Invoice_Date('')
                            if j['name'] == 'Bank Payment':
                                module_data.set_payment_Date(i['payment_Date'])
                            else:
                                module_data.set_payment_Date('')
                            # if j['name']=='Total_Amount':
                            #     module_data.set_opening_balance(i['opening_balance'])
                            # else:
                            #     module_data.set_opening_balance('')
                            if j['name'] == 'Base Amount':
                                module_data.set_closing_balance(i['closing_balance'])
                            else:
                                module_data.set_closing_balance('')
                            if j['name'] == 'Base Amount':
                                module_data.set_payment_Date(i['payment_Date'])
                            else:
                                module_data.set_payment_Date('')
                            module_data.set_tax_name(j)
                            if j['name'] == 'Base Amount':
                                module_data.set_Invoiceno(i['Invoiceno'])
                            else:
                                module_data.set_payment_Date('')
                            if j['name'] == 'Base Amount':
                                module_data.set_UTRNO(i['UTRNO'])
                            else:
                                module_data.set_UTRNO('')
                            module_data.set_Amount(q)
                            if j['name'] == 'Base Amount':
                                module_data.set_debit_amount(i['debit_amount'])
                            else:
                                module_data.set_debit_amount('')
                            if j['name'] == 'Base Amount':
                                module_data.set_credit_amount(i['credit_amount'])
                            else:
                                module_data.set_credit_amount('')
                            if j['name'] == 'Base Amount':
                                count += 1
                                counter += 1
                            module_list_data.append(module_data)
                    #     data = {"Invoice_Date":i['Invoice_Date'],
                    #             "payment_Date":i['payment_Date'],
                    #             "tax_name":out_data,
                    #             "Invoiceno":i['Invoiceno'],
                    #             # "tax_name":{"name":i.Total_Amount,
                    #             #     "name":i.Base_Amount,
                    #             #     "name":i.Tax_Amount,
                    #             #     "name":i.TDS_Amount,
                    #             #     "name":i.Bank_Payment,
                    #             #     "name":i.LIQ_Amount}
                    #             "Total_Amount":i['Total_Amount'],
                    #             "Base_Amount":i['Base_Amount'],
                    #             "Tax_Amount":i['Tax_Amount'],
                    #             "TDS_Amount":i['TDS_Amount'],
                    #             "Bank_Payment":i['Bank_Payment'],
                    #             "LIQ_Amount":i['LIQ_Amount'],
                    #             "debit_amount":i['debit_amount'],
                    #             "credit_amount":i['credit_amount']}
                    #     resp_data.append(data)
                    #     obj_data = {"data":resp_data}
                    # templates = loader.get_template("Report_Template_Vendor.html")
                    # html = templates.render(obj_data)
                    # options = {
                    #     'margin-top': '0.25in',
                    #     'margin-right': '0.5in',
                    #     'margin-bottom': '0.75in',
                    #     'margin-left': '0.5in',
                    #     'enable-local-file-access': None,
                    #     'encoding': 'UTF-8'}
                    # pdf = pdfkit.from_string(html, False, options)
                    # return pdf
                    ven = ("select name from nvendor.vendorservice_supplierbranch where id = " + "'" + str(supplier_id) + "'" )
                    with connection.cursor() as cursor:
                        cursor.execute(ven)
                        rows = cursor.fetchall()
                        rows = list(rows)
                        emp_name_data = rows[0]
                    import io
                    BytesIO = io.BytesIO()
                    output = BytesIO
                    output.name = 'VENDOR-REPORT-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
                    writer = pd.ExcelWriter(output, engine='xlsxwriter')
                    data = json.loads(module_list_data.get())
                    col = columns.append('Description')
                    df = pd.DataFrame(data['data'], columns=col)
                    df = df.reindex(columns=['Invoice_Date', 'Description', 'Invoiceno', 'Amount', 'UTRNO', 'debit', 'credit', 'Txn Balance', 'closing_balance'])
                    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
                    worksheet = writer.sheets['Sheet1']
                    workbook = writer.book
                    header_format = workbook.add_format()
                    header_format.set_align('center')
                    header_format.set_bold()
                    # def highlight_cells():
                    # provide your criteria for highlighting the cells here
                    # return ['background-color: yellow']
                    # df_data.style.apply(highlight_cells)
                    worksheet.write_string(1, 2, 'Vendor Report')
                    worksheet.write_string(3, 0, "Vendor Name: ")
                    worksheet.write_string(3, 1, str(emp_name_data[0]))
                    writer.save()
                    output.seek(0)
                    output.size = BytesIO.__sizeof__()
                    writer.name = 'Vendor_Report_demo.xlsx'
                    writer.size = df_data.size
                    logger.info('Vendor Report Excel Created - ' + START_TIME)
                    return output
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            logger.info('Vendor Report Error - ' + str(e))
            return error_obj


    def cal(self,resp):
        out_data1 = []
        for i, o in resp:
            out_dict1 = {}
            if i == 'Base_Amount':
                out_dict1['name'] = o
            elif i == 'Tax_Amount':
                out_dict1['name'] = o
            elif i == 'TDS_Amount':
                out_dict1['name'] = o
            elif i == 'Bank_Payment':
                out_dict1['name'] = o
            elif i == 'LIQ_Amount':
                out_dict1['name'] = o
            if out_dict1 != {} or '' or None:
                out_data1.append(out_dict1.copy())
        return out_data1

    def vendoreod(self,scope,emp_id,obj,data):
        from nwisefin.settings import DATABASES
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")
        DB_NAME_nwisefin = env.str('DB_NAME_nwisefindb')
        vendor_db = VENDORDBService(scope)
        Dynamicven_schema = vendor_db.get_vendor_schema()
        DB_NAME_vendordb = DATABASES.get(Dynamicven_schema).get("NAME")

        act = StampVendorStatement.objects.using(self._current_app_schema()).all()
        if len(act) == 0:
            Dynamic_Insert = ("insert into " + str(
                DB_NAME_nwisefin) + ".reportservice_stampvendorstatement (entity_id,supplier_id,closingbalance,openingbalance,date,status,created_by,created_date) "
                                    "select 1,b.supplier_id,((sum(b.totalamount) - sum(p.paymentdetails_amount)) -  ifnull(CONVERT( sum(ad.tds_amount) , DECIMAL (10 , 2 )),0) - ifnull(CONVERT( sum(ae.liq_amount) , DECIMAL (10 , 2 )),0)) as closing_balance, "
                                    "ifnull(CONVERT(sum(venstamp.closingbalance),DECIMAL(10,2)),0),date_format(p.created_date,'%Y-%m-%d') as payment_Date,1,"+str(emp_id)+",now() "
                                    "from " + str(DB_NAME_apdb) + ".apservice_apheader a inner join " + str(
                DB_NAME_apdb) + " .apservice_apinvoiceheader"
                                " b on a.id=b.apheader_id and b.is_delete=0 "
                                "inner join " + str(DB_NAME_apdb) + " .apservice_apinvoicedetail c "
                                                                    "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                                                    " inner join " + str(
                DB_NAME_vendordb) + ".vendorservice_supplierbranch g"
                                    " on g.id=b.supplier_id INNER JOIN (SELECT z.id, SUM(y.amount) AS credit_amount FROM "
                                    " " + str(DB_NAME_apdb) + " .apservice_apinvoiceheader z INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apcredit y "
                                "ON z.id = y.apinvoiceheader_id WHERE y.is_delete = 0 AND y.status = 1 GROUP BY z.id) "
                                "AS ab ON ab.id = b.id INNER JOIN (SELECT m.id, SUM(n.amount) AS debit_amount FROM " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader m "
                                "INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apdebit n ON m.id = n.apinvoiceheader_id WHERE n.is_delete = 0 AND n.status = 1 "
                                "GROUP BY m.id) AS ac ON ac.id = b.id  inner join " + str(
                DB_NAME_apdb) + ".apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "
                                " left join (SELECT k.id, SUM(d.amount) AS tds_amount FROM  " + str(
                DB_NAME_apdb) + ".apservice_apinvoiceheader k "
                                " INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apcredit d ON k.id = d.apinvoiceheader_id "
                                " WHERE d.paymode_id=7 and d.is_delete = 0 AND d.status = 1 GROUP BY k.id) AS ad ON ad.id = b.id "
                                "left join (select max(s.id),s.openingbalance,s.closingbalance,s.supplier_id from "
                                "" + str(
                DB_NAME_nwisefin) + ".reportservice_stampvendorstatement s) as venstamp on venstamp.supplier_id = b.supplier_id"
                               " left join (SELECT g.id, SUM(h.amount) AS liq_amount FROM "
                               " " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader g INNER JOIN " + str(
                DB_NAME_apdb) + ".apservice_apcredit h ON g.id = h.apinvoiceheader_id"
                                " WHERE h.paymode_id=6 and h.is_delete = 0 AND h.status = 1 GROUP BY g.id) AS ae ON ae.id = b.id "
                                "left join " + str(
                DB_NAME_apdb) + ".apservice_paymentdetails r on r.apinvoiceheader_id=g.id "
                                "left join " + str(
                DB_NAME_apdb) + ".apservice_paymentheader payh on payh.id = r.paymentheader_id "
                                "where a.is_delete=0 group by b.id")

            with connection.cursor() as cursor:
                cursor.execute(Dynamic_Insert)

            logger.info('VendorEOD TrailBalance Inserted Succesfully ' + str(START_TIME))
            obj_eod = VendorModuleEOD.objects.using(self._current_app_schema()).create(entity_id=self._entity_id(),
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
                obj_eod = VendorModuleEOD.objects.using(self._current_app_schema()).get(date=today,
                                                                                  eodflag=0)
                if len(obj_eod) == 1:
                    case = 1
                logger.info('VendorEOD TrailBalance Completed ' + str(START_TIME))
            except:
                obj_eod = VendorModuleEOD.objects.using(self._current_app_schema()).filter(date=today,
                                                                                     eodflag=1)
                if len(obj_eod) == 1:
                    case = 3
                else:
                    case = 2

            if case == 2:
                obj_eod = VendorModuleEOD.objects.using(self._current_app_schema()).create(entity_id=self._entity_id(),
                                                                                     date=today,
                                                                                     eodflag=0,
                                                                                     status=1,
                                                                                     created_by=38,
                                                                                     created_date=now())
                logger.info('VendorEOD TrailBalance Not Completed ' + str(START_TIME))
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj

            elif case == 1:
                logger.info('VendorEOD TrailBalance Starts ' + str(START_TIME))
                try:
                    if data['module'] == 'Vendor Statement':
                        if obj[0]['master'] == 1:
                            Dynamic_Insert = ("insert into " + str(
                                DB_NAME_nwisefin) + ".reportservice_stampvendorstatement (entity_id,supplier_id,closingbalance,openingbalance,date,status,created_by,created_date) "
                                                    "select 1,b.supplier_id,((sum(b.totalamount) - sum(p.paymentdetails_amount)) -  ifnull(CONVERT( sum(ad.tds_amount) , DECIMAL (10 , 2 )),0) - ifnull(CONVERT( sum(ae.liq_amount) , DECIMAL (10 , 2 )),0)) as closing_balance, "
                                                    "ifnull(CONVERT(sum(venstamp.closingbalance),DECIMAL(10,2)),0),date_format(p.created_date,'%Y-%m-%d') as payment_Date,1,"+str(emp_id)+",now() "
                                                    "from " + str(DB_NAME_apdb) + ".apservice_apheader a inner join " + str(
                                DB_NAME_apdb) + " .apservice_apinvoiceheader"
                                                " b on a.id=b.apheader_id and b.is_delete=0 "
                                                "inner join " + str(DB_NAME_apdb) + " .apservice_apinvoicedetail c "
                                                                                    "on b.id=c.apinvoiceheader_id and  c.is_delete=0 "
                                                                                    " inner join " + str(
                                DB_NAME_vendordb) + ".vendorservice_supplierbranch g"
                                                    " on g.id=b.supplier_id INNER JOIN (SELECT z.id, SUM(y.amount) AS credit_amount FROM "
                                                    " " + str(DB_NAME_apdb) + " .apservice_apinvoiceheader z INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apcredit y "
                                                "ON z.id = y.apinvoiceheader_id WHERE y.is_delete = 0 AND y.status = 1 GROUP BY z.id) "
                                                "AS ab ON ab.id = b.id INNER JOIN (SELECT m.id, SUM(n.amount) AS debit_amount FROM " + str(
                                DB_NAME_apdb) + ".apservice_apinvoiceheader m "
                                                "INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apdebit n ON m.id = n.apinvoiceheader_id WHERE n.is_delete = 0 AND n.status = 1 "
                                                "GROUP BY m.id) AS ac ON ac.id = b.id  inner join " + str(
                                DB_NAME_apdb) + ".apservice_paymentdetails p on p.apinvoiceheader_id=b.id and p.is_delete=0 "
                                                " left join (SELECT k.id, SUM(d.amount) AS tds_amount FROM  " + str(
                                DB_NAME_apdb) + ".apservice_apinvoiceheader k "
                                                " INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apcredit d ON k.id = d.apinvoiceheader_id "
                                                " WHERE d.paymode_id=7 and d.is_delete = 0 AND d.status = 1 GROUP BY k.id) AS ad ON ad.id = b.id "
                                                "left join (select max(s.id),s.openingbalance,s.closingbalance,s.supplier_id from "
                                                "" + str(
                                DB_NAME_nwisefin) + ".reportservice_stampvendorstatement s) as venstamp on venstamp.supplier_id = b.supplier_id"
                                                    " left join (SELECT g.id, SUM(h.amount) AS liq_amount FROM "
                                                    " " + str(DB_NAME_apdb) + ".apservice_apinvoiceheader g INNER JOIN " + str(
                                DB_NAME_apdb) + ".apservice_apcredit h ON g.id = h.apinvoiceheader_id"
                                                " WHERE h.paymode_id=6 and h.is_delete = 0 AND h.status = 1 GROUP BY g.id) AS ae ON ae.id = b.id "
                                                "left join " + str(
                                DB_NAME_apdb) + ".apservice_paymentdetails r on r.apinvoiceheader_id=g.id "
                                                "left join " + str(
                                DB_NAME_apdb) + ".apservice_paymentheader payh on payh.id = r.paymentheader_id "
                                                "where date_format(a.created_date,'%Y-%m-%d')=BETWEEN '" + str(
                                obj[0]['value1date']) + "' and '" + str(obj[0]['value2date']) + ""
                                                                                                "' and a.is_delete=0 group by b.id")

                            with connection.cursor() as cursor:
                                cursor.execute(Dynamic_Insert)
                            logger.info('EntryEOD TrailBalance Inserted Succesfully ' + str(START_TIME))
                            obj_eod = VendorModuleEOD.objects.using(self._current_app_schema()).filter(id=obj_eod.id).update(eodflag=1,
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

