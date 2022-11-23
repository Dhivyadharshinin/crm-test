# import json
#
# from django.db.models import Q
# from datetime import datetime
# from apservice.data.response.apinwardinvoiceresponse import APInwardInvoiceResponse
# from apservice.models import APInwardInvoiceHeader
# from apservice.util.aputil import APDocModule, get_APType, ap_get_api_caller, get_AP_status
# from docservice.service.documentservice import DocumentsService
# from vysfinutility.data.success import Success, SuccessStatus, SuccessMessage
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorDescription, ErrorMessage
# from django.db import transaction
#
# from vysfinutility.data.vysfinlist import VysfinList
# from vysfinutility.service.dbutil import DataBase
#
#
# class APInwardInvoiceService:
#
#     def apinwardinvoice_create(self,request,ap_data,emp_id):
#         # try:
#         #     with transaction.atomic(using=DataBase.AP_DB):
#                 apinwrdinvhdr = APInwardInvoiceHeader.objects.using(DataBase.AP_DB).create(
#                 inwarddetails_id = ap_data.get_inwarddetails_id(),
#                 crno = ap_data.get_crno(),
#                 invoicetype = ap_data.get_invoicetype_id(),
#                 supplier_id = ap_data.get_supplier_id(),
#                 supplierstate_id = ap_data.get_supplierstate_id(),
#                 gst = ap_data.get_gst(),
#                 invoice_date = ap_data.get_invoice_date(),
#                 invoice_no = ap_data.get_invoice_no(),
#                 dedupeinvoice_no = ap_data.get_dedupeinvoice_no(),
#                 amount = ap_data.get_invoice_amount(),
#                 branch_id = ap_data.get_branch_id(),
#                 commodity_id = ap_data.get_commodity_id(),
#                 remarks = ap_data.get_remarks(),
#                 is_dueadjustment=ap_data.get_dueadjustment(),
#                 is_ppx=ap_data.get_ppx(),
#                 created_by=emp_id)
#                 #file upload part
#                 if len(request.FILES.getlist('file')) > 0:
#                     doc_serv=DocumentsService()
#                     doc_params={"module":APDocModule.AP,"ref_id":"-1","ref_type":"-1"}
#                     file_response=doc_serv.upload(request,doc_params)
#                     doc_json=json.loads(file_response.get())['data'][0]['id']
#                     doc_id  = doc_json.split('_')[-1]
#                     apinwrdinvhdr.document_id=doc_id
#                     apinwrdinvhdr.save()
#
#                 apinwardind_resp=APInwardInvoiceResponse()
#                 apinwardind_resp.set_id(apinwrdinvhdr.id)
#                 apinwardind_resp.set_invoicetype_id(apinwrdinvhdr.invoicetype)
#                 apinwardind_resp.set_inwarddetails_id(apinwrdinvhdr.inwarddetails_id)
#                 apinwardind_resp.set_supplier_id(apinwrdinvhdr.supplier_id)
#                 apinwardind_resp.set_supplierstate_id(apinwrdinvhdr.supplierstate_id)
#                 apinwardind_resp.set_gst(apinwrdinvhdr.gst)
#                 apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoice_date)
#                 apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoice_no)
#                 apinwardind_resp.set_dedupeinvoice_no(apinwrdinvhdr.dedupeinvoice_no)
#                 apinwardind_resp.set_invoice_amount(apinwrdinvhdr.amount)
#                 apinwardind_resp.set_branch_id(apinwrdinvhdr.branch_id)
#                 apinwardind_resp.set_remarks(apinwrdinvhdr.remarks)
#                 apinwardind_resp.set_ppx(apinwrdinvhdr.is_ppx)
#                 apinwardind_resp.set_document_id(apinwrdinvhdr.document_id)
#                 return apinwardind_resp
#
#         # except Exception  as excep:
#         #     error_obj = Error()
#         #     error_obj.set_code(ErrorMessage.INVALID_DATA)
#         #     error_obj.set_description(str(excep))
#         #     return error_obj
#
#
#     def get_pocket_apinwardinvoicehdr(self,request,emp_id,inwarddtl_id):
#         try:
#             condition=Q(status=1,inwarddetails_id=inwarddtl_id)
#             apinwrdinvhdr_data = APInwardInvoiceHeader.objects.using(DataBase.AP_DB).filter(condition)
#             resp_list = VysfinList()
#             if len(apinwrdinvhdr_data) > 0:
#                 for apinwrdinvhdr in apinwrdinvhdr_data:
#                     supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
#                     apinwardind_resp = APInwardInvoiceResponse()
#                     apinwardind_resp.set_id(apinwrdinvhdr.id)
#                     apinwardind_resp.set_crno(apinwrdinvhdr.crno)
#                     apinwardind_resp.set_inwarddetails_id(apinwrdinvhdr.inwarddetails_id)
#                     apinwardind_resp.set_invoicetype_id(get_APType(apinwrdinvhdr.invoicetype))
#                     apinwardind_resp.set_supplier(supplier_data)
#                     apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoice_no)
#                     apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoice_date)
#                     apinwardind_resp.set_invoice_amount(apinwrdinvhdr.amount)
#                     apinwardind_resp.set_rmubarcode(apinwrdinvhdr.rmubarcode)
#                     apinwardind_resp.set_remarks(apinwrdinvhdr.remarks)
#                     resp_list.append(apinwardind_resp)
#             return resp_list
#
#         except Exception  as excep:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_DATA)
#             error_obj.set_description(str(excep))
#             return error_obj
#
#     def get_apinwardinvoiceheader(self,request,filter_json,emp_id):
#         try:
#             condition=Q(status=1)
#             if 'crno' in filter_json:
#                 condition&=Q(crno__icontains=filter_json.get('crno'))
#             if 'invoicetype_id' in filter_json:
#                 condition&=Q(invoicetype=filter_json.get('invoicetype_id'))
#             if 'supplier_id' in filter_json:
#                 condition&=Q(supplier_id=filter_json.get('supplier_id'))
#             if 'branch_id' in filter_json:
#                 condition&=Q(branch_id=filter_json.get('branch_id'))
#             if 'invoice_no' in filter_json:
#                 condition&=Q(invoice_no__icontains=filter_json.get('invoice_no'))
#             if 'invoice_amount' in filter_json:
#                 condition&=Q(amount__icontains=filter_json.get('invoice_amount'))
#             if 'invoice_from_date' in filter_json and 'invoice_to_date' in filter_json:
#                 inv_from_date = filter_json.get('invoice_from_date')
#                 inv_to_date =filter_json.get('invoice_to_date')
#                 condition&=Q(invoice_date__gte=inv_from_date,invoice_date__lte=inv_to_date)
#             # if 'inward_from_date' in filter_json and 'inward_to_date' in filter_json:
#             #     inward_from_date = datetime.strptime(filter_json.get('inward_from_date'), '%d-%m-%Y')
#             #     inward_to_date = datetime.strptime(filter_json.get('inward_to_date'), '%d-%m-%Y')
#             #     condition&=Q(invoice_date__gte=inward_from_date,invoice_date__lte=inward_to_date)
#
#
#
#             apinwrdinvhdr_data = APInwardInvoiceHeader.objects.using(DataBase.AP_DB).filter(condition)
#             resp_list = VysfinList()
#             if len(apinwrdinvhdr_data) > 0:
#                 for apinwrdinvhdr in apinwrdinvhdr_data:
#                     supplier_data=ap_get_api_caller(request, {"api_url":'/venserv/get_supplier/'+str(apinwrdinvhdr.supplier_id)})
#                     branch_data=ap_get_api_caller(request, {"api_url":'/usrserv/get_empbranch/'+str(apinwrdinvhdr.branch_id)})
#                     apinwardind_resp = APInwardInvoiceResponse()
#                     apinwardind_resp.set_id(apinwrdinvhdr.id)
#                     apinwardind_resp.set_crno(apinwrdinvhdr.crno)
#                     apinwardind_resp.set_inwarddetails_id(apinwrdinvhdr.inwarddetails_id)
#                     apinwardind_resp.set_invoicetype(get_APType(apinwrdinvhdr.invoicetype))
#                     apinwardind_resp.set_supplier(supplier_data)
#                     apinwardind_resp.set_invoice_no(apinwrdinvhdr.invoice_no)
#                     apinwardind_resp.set_invoice_date(apinwrdinvhdr.invoice_date)
#                     apinwardind_resp.set_branch(branch_data)
#                     apinwardind_resp.set_invoice_amount(apinwrdinvhdr.amount)
#                     apinwardind_resp.set_rmubarcode(apinwrdinvhdr.rmubarcode)
#                     apinwardind_resp.set_barcode(apinwrdinvhdr.barcode)
#                     apinwardind_resp.set_remarks(apinwrdinvhdr.remarks)
#                     apinwardind_resp.set_status(get_AP_status(apinwrdinvhdr.status))
#                     resp_list.append(apinwardind_resp)
#             return resp_list
#
#         except Exception  as excep:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_DATA)
#             error_obj.set_description(str(excep))
#             return error_obj