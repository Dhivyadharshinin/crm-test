from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from apservice.controller import apcontroller, apheadercontroller, apinvoiceheadercontroller, employeequerycontroller, \
    paymentheadercontroller, apinvoicedetailscontroller, apcreditcontroller, apdebitcontroller, apccbscontroller, \
    invoicepomapcontroller, ppxcontroller

urlpatterns = [
    path('inwdinvheader', apinvoiceheadercontroller.create_apinwardinvhdr, name='make_inwdinvhdr'),
    path('get_apheader/<apheader_id>', apheadercontroller.get_apheader, name='get_apheader'),
    #apheader
    path('apheader', apheadercontroller.create_apheader, name='apheader'),
    path('apheader/<apheader_id>', apheadercontroller.fetch_apheader_single, name='fetch_apheader_single'),
    path('get_apinwardinvoicehdr/<inwarddtl_id>', apheadercontroller.get_pocket_apheader, name='get_pocket_apheader'),
    #Invoice Header Summary*
    path('get_apinvoiceheader', apinvoiceheadercontroller.fetch_apinvoiceheader, name='get_apinvoiceheader'),
    path('supplierpaymentacctno_val', apinvoiceheadercontroller.supplierpaymentacctno_validation, name='supplierpaymentacctno_validation'),
    #apinvoice header
    path('apinvoiceheader/<apinvheader_id>', apinvoiceheadercontroller.fetch_apinvoicehdr_single, name='apinvoiceheader'),
    path('apinvoicehdr/<apheader_id>', apinvoiceheadercontroller.create_apinvoiceheader, name='apinvoiceheader_create'),
    path('supplier_report/<supplier_id>/apinvoiceheader/<apinvheader_id>', apinvoiceheadercontroller.fetch_supplierreport, name='supplier_report'),
    #invoice_details
    path('apinvoicedetails/<apinvoicehdr_id>', apinvoicedetailscontroller.apinvoicedetails, name='apinvoicedetails'),
    path('get_apinvdetails/<apinvoicedetails_id>', apinvoicedetailscontroller.fetch_apinvoicedetails_single, name='apinvoicedetails'),
    #ap_credit
    path('apcredit/<apinvoiceheader_id>',apcreditcontroller.apcredit, name='apcredit'),
    path('get_apcredit/<apcredit_id>',apcreditcontroller.fetch_apcredit_single, name='get_apcredit'),
    #ap_debit
    path('apdebit/<apinvoicehdr_id>',apdebitcontroller.apdebit, name='apdebit'),
    path('apdebit_invheader/<apinvoicedetails_id>',apdebitcontroller.fetch_apdebit_invhdetails_list, name='fetch_apdebit_invhdetails_list'),
    path('get_apdebit/<apdebit_id>',apdebitcontroller.fetch_apdebit_single, name='get_apdebit'),
    #ap_ccbs
    path('apdebitccbs/<apdebit_id>',apccbscontroller.apdebit_ccbs, name='apdebitccbs'),
    path('get_apdebitccbs/<ccbs_id>',apccbscontroller.fetch_apdebit_ccbs_single, name='fetch_apdebit_ccbs_single'),

    #apauditchecklist API
    path('get_apauditchecklist/<aptype_id>', apcontroller.get_apauditchecklist, name='get_apauditchecklist'),
    path('get_bounceauditchecklist/<apinvoiceheader_id>', apcontroller.get_bounce_apauditchecklist, name='get_bounce_apauditchecklist'),
    path('auditchecklist_map', apcontroller.create_apauditchecklist_mapping, name='auditchecklist_map'),
    path('apauditchecklist_make', apcontroller.create_apauditchecklist, name='apauditchecklist_make'),
    #dedupe check
    path('dedupe_check/<apinvoiveheader_id>', apinvoiceheadercontroller.apdedupe_check, name='dedupe_check'),
    #Yes-or-No dropdown API
    path('get_yes_or_no', apinvoiceheadercontroller.get_yes_ror_no_dropdown, name='get_yes_ror_no_dropdown'),
    #employee query
    path('get_empquery', employeequerycontroller.empq_list, name='overallforempquery'),
    path('get_crno/<crno>', employeequerycontroller.fetch_crno, name='fetch_crno'),
    path('get_crnoo/<crnoo>', employeequerycontroller.fetch_pay, name='fetch_pay'),
    path('searchempquery', employeequerycontroller.search_empquery, name='searchloanappno'),
    path('get_aptype', employeequerycontroller.fetch_aptype_list, name='dropdown'),
    path('get_trans/<No>',apheadercontroller.get_aptransget,name='aptrans'),
    path('get_apstatus', employeequerycontroller.fetch_apstatus_list, name='dropdown'),
    #ap common summary
    path('get_dropdown_list', employeequerycontroller.fetch_dropdown_list, name='get_dropdown_list'),
    #preparepayment
    path('get_preparepayment', apinvoiceheadercontroller.get_preparepayment, name='get_preparepayment'),
    path('get_paymentfile', apinvoiceheadercontroller.fetch_paymentfile, name='get_paymentfile'),
    path('preparepayment', paymentheadercontroller.create_preparepayment, name='create_preparepayment'),
    path('paymentdtlsdownload/<bankdetails_id>', apinvoiceheadercontroller.paymentdetails_download,name='paymentdtlsdownload'),
    #all_table_delete_api
    path('aptables_delete', apheadercontroller.aptables_delete, name='aptables_delete'),
    path('aptables_delete/<apheader_id>', apheadercontroller.aptables_single_delete, name='aptables_single_delete'),
    #upload payment status update
    path('payment_upload', apinvoiceheadercontroller.upload_payment, name='payment_upload'),
    #Bounce API & #REJECT -- Bounce API also Use for REJECT API
    path('apstatus_update', apinvoiceheadercontroller.apstatus_update, name='apstatus_update'),
    path('bounce_get', apinvoiceheadercontroller.get_bounce_summary, name='get_bounce_summary'),
    path('bounce_get/<apinvheader_id>', apinvoiceheadercontroller.fetch_apbounce_single, name='fetch_apbounce_single'),
    #AP Map Invoice PO
    path('apinvoicehdr/<apinvoicehdr_id>/apinvoicedtls/<apinvoicedtls_id>/apmapinvoicepo',invoicepomapcontroller.create_apmap_invoicepo, name='create_apmapinvoicepo'),
    path('apmapinvoicepo/<apinvoicepomap_id>',invoicepomapcontroller.get_apmapinvoicepo, name='get_apmapinvoicepo'),
    #tds calculation
    path('aptds_calculation/<creditamount>/<tds_persent>', apcreditcontroller.fetch_aptds, name='aptds_calculation'),
    path('apfinal_submit', apcontroller.ap_finalsubmit,name='ap_finalsubmit'),
    path('apstatus_history/<apinvoicehdr_id>', apcontroller.apstatus_history,name='apstatus_history'),
    path('get_apraiseraccountdtls/<raiseremp_id>', apcontroller.get_apraiser_accntdtls,name='get_apraiser_accntdtls'),
    #ap common summary
    path('ap_common_summary', apinvoiceheadercontroller.ap_common_summary, name='ap_common_summary'),
    #entry module debit
    path('ap_entrydebit', apdebitcontroller.ap_entrydebit, name='ap_entrydebit'),
    #get_approved_apcrno for jv module
    path('get_approved_apcrno/<apcrno>', apinvoiceheadercontroller.get_approved_apcrno, name='get_approved_apcrno'),
    # ap ppxheader and ap_ppxdetails
    path('ap_ppxheader', ppxcontroller.ap_ppxheader, name='get_approved_apcrno'),
    path('ap_ppxdetails', ppxcontroller.ap_ppxdetails, name='ap_ppxdetails'),
    path('ppxheader_and_dtls', ppxcontroller.create_ap_ppxheader_and_details, name='ap_ppxheader_and_details'),
    # AP lock and AP maker Approver Validation
    path('approverview_validation/<apinvoicehdr_id>', apinvoiceheadercontroller.view_validation, name='approverview_validation'),
    path('fetch_payment_inwarddtls/<crno>', paymentheadercontroller.fetch_payment_and_inward_details, name='fetch_payment_and_inward_details'),
    #File View and dwonload
    path('apfiledownload/<file_id>', apcontroller.apfile_download_and_view,name='apfile_download_and_view'),

              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)