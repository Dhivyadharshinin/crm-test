import json
import traceback
from django.db import transaction
from apservice.models import PaymentHeader, PaymentDetails, APQueue, APInvoiceHeader
from apservice.service.apauditservice import APAuditService
from apservice.util.aputil import APModifyStatus, APRefType, APRequestStatusUtil, AP_Status
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now
from entryservice.service.entryservice import EntryService
import pandas as pd
from nwisefin.settings import logger
import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
import json
import os
from entryservice.util import entryutil

Is_Bulk_Works="Y"
Oracle_Client_Base_URL =entryutil.ORACLE_CLIENT_BASE_URL
Oracle_Client_Basic_Auth_User_Name = entryutil.ORACLE_CLIENT_AUTH_USER_NAME
Oracle_Client_Basic_Auth_User_Password = entryutil.ORACLE_CLIENT_AUTH_PASSWORD

JournalImportService_API = "fscmService/JournalImportService"
ErpIntegrationService="fscmService/ErpIntegrationService"

class EntryOracleService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    def journal_entry_api(self, orcle_obj, emp_id):
        try:
            AP_Type=orcle_obj.get_AP_Type()
            CR_Number=orcle_obj.get_CR_Number()
            Entry_Failed_Response_Data=[]
            Bulk_Entry_Failed_Response_Data=[]
            data=""
            entry_all_data_array=[]
            if(AP_Type):
                try:
                    ap_data={}
                    cr_number_against_entry=EntryService.oracle_fetch_commonentry(self,CR_Number,AP_Type,ap_data,emp_id)
                    data=json.loads(cr_number_against_entry.get())
                    if(len(data.get("data"))!=0):
                        entry_all_data_array=data.get('data')
                        segment_validation=entry_all_data_array[0].get("Message")
                        if(segment_validation=="FAIL"):
                            response_msg = entry_all_data_array[0]
                            return response_msg
                        entry_data_log = [{"CR_Number": CR_Number, "Data": entry_all_data_array}]
                        logger.info(entry_data_log)
                        orginal_data_frame = pd.DataFrame(entry_all_data_array)
                        orginal_data_frame['amount'] = orginal_data_frame['amount'].astype(float)
                        orginal_data_frame['EnteredDrAmount'] = orginal_data_frame['EnteredDrAmount'].astype(float)
                        orginal_data_frame['EnteredCrAmount'] = orginal_data_frame['EnteredCrAmount'].astype(float)
                        Credit_amount = orginal_data_frame.loc[orginal_data_frame['type'] == 'DEBIT', 'amount'].sum()
                        Debit_amount = orginal_data_frame.loc[orginal_data_frame['type'] == 'CREDIT', 'amount'].sum()
                        Credit_amount = str(round(float(Credit_amount), 2))
                        Debit_amount = str(round(float(Debit_amount), 2))
                        if (Credit_amount == Debit_amount):
                            single_entry_success_count=0
                            single_entry_fail_count=0
                            single_entry_total_count=len(entry_all_data_array)
                            for single_entry in entry_all_data_array:
                                entry_staus=int(single_entry.get("entry_status"))
                                if(entry_staus==1):
                                    single_entry_success_count += 1
                                else:
                                    entry_id=single_entry['id']
                                    script_dir = os.path.dirname(__file__)
                                    xml_input = script_dir+"/oracle_request_xml/journal_input_file.xml"
                                    xml_out = script_dir + "/oracle_request_xml/journal_output_file.xml"
                                    f = open(xml_out, 'r+')
                                    f.truncate(0)
                                    xmlTree = ET.parse(xml_input)
                                    rootElement = xmlTree.getroot()
                                    for child_root in rootElement:
                                        if(child_root.tag=="{http://schemas.xmlsoap.org/soap/envelope/}Body"):
                                            for body_child in child_root:
                                                if(body_child.tag=="{http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/types/}importJournals"):
                                                    for importjournals in body_child:
                                                        if(importjournals.tag=="{http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/types/}interfaceRows"):
                                                            for interface_child in importjournals:
                                                                #print(interface_child)
                                                                interface_child_str = interface_child.tag.rsplit('}', 1)
                                                                interface_child_str_last = interface_child_str[-1]
                                                                is_in_list_interface_child_value=single_entry.get(interface_child_str_last)
                                                                if(is_in_list_interface_child_value!=None):
                                                                    interface_child.text = str(is_in_list_interface_child_value)
                                                                if(interface_child.tag=="{http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/}GlInterface"):
                                                                    for GlInterface_child in interface_child:
                                                                        gl_interface_str=GlInterface_child.tag.rsplit('}', 1)
                                                                        gl_interface_str_last = gl_interface_str[-1]
                                                                        gl_interface_str_last_value = single_entry.get(gl_interface_str_last)
                                                                        if (gl_interface_str_last_value != None):
                                                                            GlInterface_child.text = str(gl_interface_str_last_value)
                                                                        if(GlInterface_child.tag=="{http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/}JournalLineGdf"):
                                                                            for gl_interface_child in GlInterface_child:
                                                                                gl_interface_child_sub_str = gl_interface_child.tag.rsplit('}',1)
                                                                                gl_interface_child_sub_str_last = gl_interface_child_sub_str[-1]
                                                                                gl_interface_child_sub_str_last_value = single_entry.get(gl_interface_child_sub_str_last)
                                                                                if (gl_interface_child_sub_str_last_value != None):
                                                                                    GlInterface_child.text = str(gl_interface_child_sub_str_last_value)

                                    xmlTree.write(xml_out)
                                    xmlTree = ET.parse(xml_out)
                                    rootElement1 = xmlTree.getroot()
                                    request_xml = ET.tostring(rootElement1, encoding='utf8').decode('utf8')
                                    #print(request_xml)
                                    single_entry_data_log = [{"BEFORE_IMPORT_JOURNAL_API": CR_Number, "Data": request_xml}]
                                    logger.info(single_entry_data_log)
                                    headers = {
                                        'Content-Type': 'text/xml; charset=utf-8',
                                        'SOAPAction': 'http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/getEntityList'
                                    }
                                    response = requests.request("POST", Oracle_Client_Base_URL+JournalImportService_API, headers=headers, data=request_xml,
                                                                auth=HTTPBasicAuth(Oracle_Client_Basic_Auth_User_Name, Oracle_Client_Basic_Auth_User_Password))
                                    Oracle_API_Response_JSON = (response.content.decode('utf-8'))
                                    Response_Status_Code=response.status_code
                                    single_entry_data_output_log = [{"AFTER_IMPORT_JOURNAL_API": CR_Number, "Data": Oracle_API_Response_JSON}]
                                    logger.info(single_entry_data_output_log)
                                    if (Response_Status_Code== 200):
                                        myxml = ET.fromstring(response.content)
                                        for child in myxml.iter('*'):
                                            if(child.tag == '{http://xmlns.oracle.com/apps/financials/generalLedger/journals/desktopEntry/journalImportService/types/}result'):
                                                if(child.text=='0'):
                                                    entry_update_data_200={"id":entry_id,"entry_status":1,"is_error":0,"errordescription":"success"}
                                                    entry_update_result_200 = EntryService.update_oracelstatus(self, entry_update_data_200,emp_id)
                                                    entry_update_result_data_200=json.loads(entry_update_result_200.get())
                                                    if(entry_update_result_data_200.get("status")=="success"):
                                                        single_entry_success_count += 1
                                                    else:
                                                        update_response_data_200={"CR_Number":CR_Number,
                                                                                  "Response_Status_Code": Response_Status_Code,
                                                                                  "Message":"Oracle API Success, Entry Status Update Failed",
                                                                                  "Entry_Message":entry_update_result_data_200}
                                                        Entry_Failed_Response_Data.append(update_response_data_200)
                                    elif (Response_Status_Code == 500):
                                        entry_update_data_500 = {"id": entry_id, "entry_status": 0, "is_error": 1,
                                                             "errordescription": Oracle_API_Response_JSON}
                                        entry_update_result_500 = EntryService.update_oracelstatus(self, entry_update_data_500, emp_id)
                                        entry_update_result_data_500 = json.loads(entry_update_result_500.get())
                                        single_entry_fail_count += 1
                                        if (entry_update_result_data_500.get("status") == "success"):
                                            update_response_data_500 = {"CR_Number": CR_Number,
                                                                        "Message": "Oracle API Failed, Entry Status Update Success",
                                                                        "Response_Status_Code":Response_Status_Code,
                                                                        "Oracle_Message": Oracle_API_Response_JSON,
                                                                        "Entry_Message": entry_update_result_data_500}
                                            Entry_Failed_Response_Data.append(update_response_data_500)
                                        else:
                                            update_response_data_500 = {"CR_Number": CR_Number,
                                                                    "Message": "Oracle API Failed, Entry Status Update Failed",
                                                                    "Response_Status_Code": Response_Status_Code,
                                                                    "Oracle_Message":Oracle_API_Response_JSON,
                                                                    "Entry_Message": entry_update_result_data_500}
                                            Entry_Failed_Response_Data.append(update_response_data_500)
                                    else:
                                        entry_update_data_other = {"id": entry_id, "entry_status": 0, "is_error": 1,
                                                                 "errordescription": Oracle_API_Response_JSON}
                                        entry_update_result_other = EntryService.update_oracelstatus(self, entry_update_data_other,emp_id)
                                        entry_update_result_data_other = json.loads(entry_update_result_other.get())
                                        single_entry_fail_count += 1
                                        if (entry_update_result_data_other.get("status") == "success"):
                                            update_response_data_other = {"CR_Number": CR_Number,
                                                                        "Message": "Oracle API Failed, Entry Status Update Success",
                                                                        "Response_Status_Code": Response_Status_Code,
                                                                        "Oracle_Message": Oracle_API_Response_JSON,
                                                                        "Entry_Message": entry_update_result_data_other}
                                            Entry_Failed_Response_Data.append(update_response_data_other)
                                        else:
                                            update_response_data_other = {"CR_Number": CR_Number,
                                                                    "Message": "Oracle API Failed, Entry Status Update Failed",
                                                                    "Response_Status_Code": Response_Status_Code,
                                                                    "Oracle_Message": Oracle_API_Response_JSON,
                                                                    "Entry_Message": entry_update_result_data_other}
                                            Entry_Failed_Response_Data.append(update_response_data_other)
                                        #myxml = ET.fromstring(response.content)
                                        #for child in myxml.iter('*'):
                                        #    pass
                            if(single_entry_total_count==single_entry_success_count):
                                if(Is_Bulk_Works=="Y" and (AP_Type=="AP_PAYMENT" or AP_Type=="JV_PAYMENT")):
                                    try:
                                        GroupId=entry_all_data_array[0].get("GroupId")
                                        script_dir = os.path.dirname(__file__)
                                        bulk_xml_input = script_dir + "/oracle_request_xml/ErpIntegrationService_input_file.xml"
                                        bulk_xml_out = script_dir + "/oracle_request_xml/ErpIntegrationService_out_put_file.xml"
                                        f = open(bulk_xml_out, 'r+')
                                        f.truncate(0)
                                        xmlTree = ET.parse(bulk_xml_input)
                                        rootElement = xmlTree.getroot()
                                        paramList_count=0
                                        for child_root in rootElement:
                                            if (child_root.tag == "{http://schemas.xmlsoap.org/soap/envelope/}Body"):
                                                for body_child in child_root:
                                                    if (body_child.tag == "{http://xmlns.oracle.com/apps/financials/commonModules/shared/model/erpIntegrationService/types/}submitESSJobRequest"):
                                                        for interface_child in body_child:
                                                            interface_child_str = interface_child.tag.rsplit('}', 1)
                                                            interface_child_str_last = interface_child_str[-1]
                                                            if (interface_child_str_last=="paramList"):
                                                                paramList_count+=1
                                                                if(paramList_count==4):
                                                                    interface_child.text = str(GroupId)
                                        xmlTree.write(bulk_xml_out)
                                        xmlTree = ET.parse(bulk_xml_out)
                                        rootElement1 = xmlTree.getroot()
                                        erp_request_xml = ET.tostring(rootElement1, encoding='utf8').decode('utf8')
                                        #print(erp_request_xml)
                                        entry_data_log = [
                                            {"BEFORE_IMPORT_BULK_DATA_API": CR_Number, "Data": erp_request_xml}]
                                        logger.info(entry_data_log)
                                        headers = {
                                            'Content-Type': 'text/xml; charset=utf-8',
                                            'SOAPAction': 'http://xmlns.oracle.com/apps/financials/commonModules/shared/model/erpIntegrationService/importBulkData'
                                        }
                                        response_bulk = requests.request("POST",
                                                                    Oracle_Client_Base_URL + ErpIntegrationService,
                                                                    headers=headers, data=erp_request_xml,
                                                                    auth=HTTPBasicAuth(Oracle_Client_Basic_Auth_User_Name,
                                                                                       Oracle_Client_Basic_Auth_User_Password))
                                        Bulk_Oracle_API_Response_JSON = response_bulk.content.decode('utf-8')
                                        Response_Status_Code_Bulk = response_bulk.status_code
                                        entry_data_output_log = [{"AFTER_IMPORT_BULK_DATA_API": CR_Number,"Data": Bulk_Oracle_API_Response_JSON}]
                                        logger.info(entry_data_output_log)
                                        Process_id=0
                                        if (Response_Status_Code_Bulk == 200):
                                            string_split_all=Bulk_Oracle_API_Response_JSON.split('--')
                                            split_data_4=string_split_all[3]
                                            split_data_4_1 = split_data_4.split('\n')
                                            for bulks in split_data_4_1:
                                                split_data_6_find=bulks[0:13]
                                                if(split_data_6_find=='<env:Envelope'):
                                                    split_data_6=bulks
                                            #split_data_6=split_data_4_1[5]
                                            myxml = ET.fromstring(split_data_6)
                                            for child in myxml.iter('*'):
                                                if (child.tag == "{http://xmlns.oracle.com/apps/financials/commonModules/shared/model/erpIntegrationService/types/}result"):
                                                    Process_id=child.text
                                            if(Process_id!="" and Process_id!=None and Process_id!=0):
                                                update_response_data_200 = {"CR_Number": CR_Number,"Process_id": Process_id,
                                                                            "bulk_status": 1,"bulk_is_error":0,"bulk_errordescription":"success"}
                                                entry_bulk_update_result_200 = EntryService.update_oracle_bulk_status(self,update_response_data_200,emp_id)
                                                entry_bulk_update_result_200_data = json.loads(entry_bulk_update_result_200.get())
                                                if (entry_bulk_update_result_200_data.get("status") == "success"):
                                                    response_msg = {"Message": "SUCCESS"}
                                                    return response_msg
                                                else:
                                                    update_response_data_other = {"CR_Number": CR_Number,
                                                                                  "Message": "Oracle API Bulk Success, Entry Status Update Failed",
                                                                                  "Response_Status_Code": Response_Status_Code_Bulk,
                                                                                  "Oracle_Message": Bulk_Oracle_API_Response_JSON,
                                                                                  "Entry_Message": entry_bulk_update_result_200_data}
                                                    Bulk_Entry_Failed_Response_Data.append(update_response_data_other)
                                            else:
                                                update_response_data_200 = {"CR_Number": CR_Number,"Process_id": Process_id,
                                                                            "bulk_status": 0,"bulk_is_error": 1,
                                                                            "bulk_errordescription":Bulk_Oracle_API_Response_JSON}
                                                entry_bulk_update_result_200 = EntryService.update_oracle_bulk_status(self,update_response_data_200,emp_id)
                                                entry_bulk_update_result_200_data = json.loads(entry_bulk_update_result_200.get())
                                                if (entry_bulk_update_result_200_data.get("status") == "success"):
                                                    response_msg = {"Message": "Bulk Entry Failed","Data":entry_bulk_update_result_200_data,
                                                                    "Entry_Update_Status":"Success"}
                                                    return response_msg
                                        else:
                                            update_response_data_500 = {"CR_Number": CR_Number,"bulk_status": 0, "bulk_is_error": 1,"Process_id": Process_id,
                                                                        "bulk_errordescription": Bulk_Oracle_API_Response_JSON}
                                            entry_bulk_update_result_500 = EntryService.update_oracle_bulk_status(self,update_response_data_500,emp_id)
                                            entry_bulk_update_result_500_data = json.loads(
                                                entry_bulk_update_result_500.get())
                                            if (entry_bulk_update_result_500_data.get("status") == "success"):
                                                response_msg = {"Message": "Bulk Entry Failed,Import Journal Success",
                                                                "Data": Bulk_Oracle_API_Response_JSON,
                                                                "Entry_Update_Status": "Success"}
                                                return response_msg
                                            else:
                                                response_msg = {"Message": "Bulk Entry Failed,Import Journal Success",
                                                                "Data": Bulk_Oracle_API_Response_JSON,
                                                                "Entry_Update_Status": "Failed"}
                                                return response_msg

                                    except Exception as e:
                                        return {"Message": "ERROR_OCCURED_ON_ORACLE_BULK_API_","DATA": str(e)}
                                else:
                                    response_msg = {"Message": "SUCCESS"}
                                    return response_msg
                            else:
                                response_msg = {"Message": "FAIL","Data":Entry_Failed_Response_Data}
                                return response_msg
                        else:
                            response_msg={"Message":"Debit Amount and Credit Amount Not Equal."}
                            return response_msg
                    else:
                        not_found_response = {"Message": "Entry Records Not Found"}
                        return not_found_response
                except Exception as e:
                    return {"Message": "ERROR_OCCURED_ON_ORACLE_COMMON_API_SERVICE_", "Data": str(e)}
            else:
                return {"Message": "ERROR_OCCURED_ON_ORACLE_COMMON_API", "Data":"Type Missing"}
        except Exception as e:
            return {"Message": "ERROR_OCCURED_ON_JOUNAL_ENTRY_LOCAL_API_", "Data": str(e)}