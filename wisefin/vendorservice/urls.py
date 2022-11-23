from django.conf import settings
from django.urls import path

from django.conf.urls.static import static

from vendorservice.controller import vendorcontroller, activitycontroller, directorcontroller, profilecontroller, \
    paymentcontroller, suppliercontroller, productcontroller, branchcontroller, suppliertaxcontroller, \
    vendoraddresscontroller, activitydetailscontroller, vendorhistorycontroller, documentcontroller, \
    vendorauditcontroller, catelogcontroller, vendorattactments, modicationcontroller, riskcontroller, kyc_controller, \
    questionnairecontroller,questionscontroller,questionanswercontroller, suboptionanswercontroller, vowcontroller, \
    questionvendormappingcontroller

urlpatterns = [
                  path('vendor', vendorcontroller.vendor, name='vendor'),
                  path('getip', vendorcontroller.getip, name='getip'),
                  path('getoldatmadata/<vendor_id>', vendorcontroller.getoldatmadata, name='getoldatmadata'),
                  path('evaluate_vendor/<vendor_id>', questionscontroller.evaluate_vendor, name='evaluate_vendor'),
                  path('evaluate_supplier/<vendor_id>', questionscontroller.evaluate_suppliermapping, name='Based on activity'),
                  path('evalute_venodor_doc/<vendor_id>', questionscontroller.evaluate_vendor_doc,name='evalute_vendor_doc'),
                  path('vendor/<vendor_id>', vendorcontroller.fetch_vendor, name='fetch_vendor'),
                  path('vendor_code/<vendor_code>', vendorcontroller.fetch_vendor_code, name='fetch_vendor'),
                  path('vendor_supplier_address', vendorcontroller.vendor_supplier_address, name='vendor_supplier_address'),
                  path('vendor_queuefilter', vendorcontroller.vendor_queuefilter, name='vendor_queuefilter'),
                  path('modificationvendor/<vendor_id>', vendorcontroller.fetch_modificationvendor, name='fetch_vendor'),
                  path('vendor/<vendor_id>/director', directorcontroller.director, name='director'),
                  path('vendor/<vendor_id>/director/<director_id>', directorcontroller.fetch_director, name='director'),
                  path('vendor/<activity_id>', activitycontroller.fetch_activity, name='fetch_activity'),
                  #micro new one api
                  path('commonvendor', vendorcontroller.get_vendor, name='post_vendor'),
                  # vendor address
                  path('vendor/<vendor_id>/vendoraddress', vendoraddresscontroller.vendoraddress, name='profile'),

                  # supplier rel address
                  path('address', suppliercontroller.address, name='address'),
                  path('address/<address_id>', suppliercontroller.fetch_address, name='address_get'),
                  # supplier rel contact
                  path('contact', suppliercontroller.contact, name='conatct'),
                  path('contact/<contact_id>', suppliercontroller.fetch_contact, name='fetch_contact'),
                  path('fetch_suppliercode/<supplier_code>', suppliercontroller.get_supplier_using_code, name='fetch_contact'),
                  path('fetch_supplier_code/<supplier_code>', suppliercontroller.fetch_supplier_using_code, name='fetch_supplier'),

                  # vendor profile
                  path('vendor/<vendor_id>/profile', profilecontroller.profile, name='profile'),
                  path('vendor/<vendor_id>/profile/<profile_id>', profilecontroller.fetch_profile,
                       name='fetch_profile'),
                  # branch
                  path('vendor/<vendor_id>/branch', branchcontroller.branch, name='branch'),
                  path('landlordbranch_list', branchcontroller.landlordbranch_list, name='landlordbranch_list'),
                  path('vendor/<vendor_id>/pendingbranch', branchcontroller.pendingbranch, name='pendingbranch'),
                  path('vendor/<vendor_id>/branch/<branch_id>', branchcontroller.fetch_branch, name='branch_get'),
                  path('vendor/<vendor_id>/gstnumbercheck',branchcontroller.gstnumbercontroller,name='gstnumbercheck'),
                  # path('brachactive',branchcontroller.brachactive,name='brachactive'),
                  path('supplieractive',branchcontroller.supplieractive,name='supplieractive'),
                  # product
                  path('vendor/<vendor_id>/product', productcontroller.product, name='product'),
                  path('vendor/<vendor_id>/product/<product_id>', productcontroller.fetch_product, name='product_get'),
                  # client
                  path('vendor/<vendor_id>/client', suppliercontroller.client, name='client'),
                  path('vendor/<vendor_id>/client/<client_id>', suppliercontroller.fetch_client, name='client_get'),
                  # subcontractor
                  path('vendor/<vendor_id>/contractor', suppliercontroller.contractor, name='contractor'),
                  path('vendor/<vendor_id>/contractor/<contractor_id>', suppliercontroller.fetch_contractor,
                       name='contractor_get'),

                  # payment
                  path('branch/<branch_id>/payment', paymentcontroller.payment, name='payment'),
                  path('branch/<branch_id>/payment/<payment_id>', paymentcontroller.fetch_payment, name='payment_get'),
                  path('supplier_payment/<branch_id>', paymentcontroller.supplier_payment, name='supplier_payment'),
                  path('payment_activeflag', paymentcontroller.payment_activeflag, name='payment_activeflag'),

                  # supplier tax
                  path('branch/<branch_id>/suppliertax', suppliertaxcontroller.suppliertax, name='suppliertax'),
                  path('branch/<branch_id>/suppliertax/<tax_id>', suppliertaxcontroller.fetch_suppliertax,
                       name='fetch_suppliertax'),
                  path('supplier_tax/<vendor_id>', suppliertaxcontroller.supplier_tax, name='supplier_tax'),

                  # activity
                  path('branch/<branch_id>/activity', activitycontroller.activity, name='supplieractivity'),
                  path('branch/<branch_id>/activity/<activity_id>', activitycontroller.fetch_activity,
                       name='fetch_activity'),

                  # activitydetails
                  path('activity/<activity_id>/supplieractivitydtl', activitydetailscontroller.supplieractivitydtl,
                       name='supplieractivtydtl'),
                  path('activity/<activity_id>/supplieractivitydtl/<id>', activitydetailscontroller.fetch_activitydtl,
                       name='fetch_activitydtl'),
                  path('activity_search',activitydetailscontroller.fetch_activity_search,name='fetch_activity_search'),
                  # catelog
                  path('supplieractivitydtl/<activitydetail_id>/catelog', catelogcontroller.suppliercatelog,
                       name='suppliercatelog'),
                  path('supplieractivitydtl/<activitydetail_id>/catelog/<catelog_id>', catelogcontroller.fetch_catelog,
                       name='fetch_catelog'),

                  path('catelogdataforrcn', catelogcontroller.catelogdataforrcn,
                       name='catelogdataforrcn'),

                  # VendorAudit
                  path('vendoraudit', vendorauditcontroller.vendoraudit, name='creat_vendoraudit'),
                  path('fetch_vendoraudit/<vendoraudit_id>', vendorauditcontroller.fetch_vendoraudit,
                       name='fetch_vendoraudit'),

                  path('vendor/<vendor_id>/status', vendorcontroller.status_update, name='status_vendor'),
                  path('vendor/<vendor_id>/reject', vendorcontroller.status_update, name='status_vendor'),
                  path('vendor/<vendor_id>/history', vendorhistorycontroller.fetch_vendor_history,
                       name='vendor_history'),
                  path('validate', vendorcontroller.do_validation, name='vendor_validation'),

                  # VendorDocument
                  path('vendor/<vendor_id>/vendordocument', documentcontroller.document, name='vendordocument'),
                    path('vendor/<vendor_id>/document', documentcontroller.single_document, name='vendordocument'),
                  path('vendor/<vendor_id>/vendordocument/<document_id>', documentcontroller.fetch_document,
                       name='fetch_vendordocument'),
                  # path('vendordocument/download/<file_id>', documentcontroller.download_attachment, name='download'),

                  # search
                  path('search', vendorcontroller.get_vendor_searchlist, name='vendor_list'),

                  # Q validation
                  path('vendor/<vendor_id>/q_validation', vendorcontroller.q_validation, name='q_validation'),
                  path('vendor/<vendor_id>/modication_view', modicationcontroller.modication_view, name='modication_view'),
                  path('vendor/<vendor_id>/modification_approve', modicationcontroller.modication_approve,
                       name='modication_approve'),

                  # modification summary
                  path('modification_summary', vendorcontroller.modification_summary, name='modification_summary'),
                  path('vendor/<vendor_id>/modification_request', vendorcontroller.modification_request,
                       name='modification_request'),
                  path('vendor/<vendor_id>/modification_reject', vendorcontroller.modification_reject,
                       name='modification_reject'),

                  path('vendor_attactments/<file_id>', vendorattactments.vendor_download_file,
                       name='vendorattactments'),
                path('view_attactments/<file_id>', vendorattactments.vendor_view_file, name='vendorattactments'),

                  path('vendor/<vendor_id>/vendorrm_validation', vendorcontroller.vendorrm_validation,
                       name='vendorrm_validation'),
                  path('unitprice',vendorcontroller.unitprice,name='unitprice'),
                  path('product_supplier',vendorcontroller.product_supplier,name='product_supplier'),
                  path('get_product',vendorcontroller.get_product),
                  path('getvendor_name',vendorcontroller.getvendor_name,name='getvendor_name'),
                  path('landlord_tax',vendorcontroller.landlord_tax,name='landlord_tax'),
                  path('vendor_payment',vendorcontroller.vendor_payment,name='vendor_payment'),
                  path('report',vendorcontroller.report,name='report'),
                  path('product_dts',branchcontroller.product_dts,name='product_dts'),
                  path('supplier_catalog',catelogcontroller.supplier_catalog,name='supplier_catalog'),
                  path('product_catalog',catelogcontroller.product_catalog,name='product_catalog'),
                  path('catalog_supplier',branchcontroller.catalog_supplier,name='catalog_supplier'),
                  path('catalogproduct_supplier',branchcontroller.catalogproduct_supplier,name='catalogproduct_supplier'),
                  path('catalog_unitprice',catelogcontroller.catalog_unitprice,name='catalog_unitprice'),
                  path('fetch_unitprice', catelogcontroller.fetch_unitprice, name='fetch_unitprice'),
                  path('search_suppliername', branchcontroller.search_suppliername, name='search_suppliername'),
                  # prpo-micro to micro
                  path('supplierbranch_get',branchcontroller.supplierbranch_get,name='supplierbranch_get'),
                  path('fetch_supplierbranchdata/<supplierbranch_id>', branchcontroller.fetch_supplierbranchdata, name='fetch_supplierbranchdata'),
                  path('fetch_catelogdata/<catelog_id>', catelogcontroller.fetch_catelogdata, name='fetch_catelogdata'),
                  path('supplierbranch/<sup_id>', branchcontroller.supplierbranch, name='supplierbranch'),
                  path('search_supplier', branchcontroller.search_supplier, name='search_supplier'),
                  path('search_supplier_name', branchcontroller.search_supplier_name, name='search_supplier_name'),
                  path('fetch_vendoraddress/<address_id>',vendoraddresscontroller.fetch_vendoraddress,name='fetch_vendoraddress'),
                  # micro to micro ecf
                  path('get_supplier/<supplier_id>', vendorcontroller.fetch_supplier, name='get_supplier'),
                  path('get_supplierlist', vendorcontroller.fetch_supplierlist, name='fetch_supplierlist'),
                  path('catelog_productdts/<dts>',catelogcontroller.catelog_productdts,name='catelog_productdts'),
                  path('supplierpaymode/<branch_id>/<paymode_id>', paymentcontroller.getcreditgl, name='getcreditgl'),
                  #ecf
                  path('supplier_tds', suppliertaxcontroller.fetch_subtaxlist, name='fetch_subtaxlist'),
                  #report
                  path('search_suppliername_dropdown', branchcontroller.search_suppliername_dropdown,
                       name='search_suppliername'),
                  path('vendor/<vendor_id>/risk', riskcontroller.create_vendor_risk, name='vendor_risk'),
        path('vendor/<vendor_id>/risk/<risk_id>', riskcontroller.fetch_risk, name='fetch risk'),
        path('vendor/<vendor_id>/branch_count', branchcontroller.branch_count, name='branch count'),
        path('activity/<activity_id>/activitydtl_dd', activitydetailscontroller.activitydtl_list,name='activtydetail'),
        path('branch/<branch_id>/activity_dd', activitycontroller.activity_list, name='activity'),
        path('vendor/<vendor_id>/kyc', kyc_controller.kyc_create, name='kyc'),
        path('vendor/<vendor_id>/kyc/<kyc_id>', kyc_controller.fetch_kyc, name=' fetch kyc'),
        path('vendor/<vendor_id>/vendor_kyc', kyc_controller.kyc, name='vendor kyc'),
        path('vendor/<vendor_id>/bcp_question', questionnairecontroller.bcp_quesitons, name='BCP questionnaire'),
        path('vendor/<vendor_id>/due_question', questionnairecontroller.due_quesitons, name='DUE questionnaire'),
        path('vendor/<vendor_id>/modication_view_type', modicationcontroller.modication_view_type, name='modication_view_type'),
        path('dept_rm', vendorcontroller.search_dept_rm, name='Search dept RM'),
        path('vendor_by_code', vendorcontroller.fetch_vendor_by_code, name='Search vendor'),
        path('branch_by_code', branchcontroller.fetch_branch_by_code, name='Search branch'),
        path('search_contact', vendorcontroller.get_contact_details, name='Search contact'),

        #QUESTION_ANSWER_URL
        path('question_answer_create', questionanswercontroller.question_answer_create, name='question_answer'),
        path('doc/<vendor_id>', questionanswercontroller.create_upload, name='create_upload'),
        path('question_answer_mapping', questionvendormappingcontroller.question_vendor_mapping, name='question_answer'),
        path('question_answer_get/<id>', questionanswercontroller.question_answer_get, name='question_answer'),
        path('quesfile/<file_id>', questionanswercontroller.fetch_file, name='download'),
        path('fileview/<file_id>', questionanswercontroller.view_file, name='view_file'),
        path('deletefile/<file_id>', questionanswercontroller.delete_file, name='deletefile'),
        path('ques_trans/<No>',questionanswercontroller.get_questransget,name='questransaction'),
        #QUESTION_SUBOPTION_API
        path('suboption_create', suboptionanswercontroller.suboption_create,name='suboption'),
        path('suboption_get/<id>', suboptionanswercontroller.suboption_get, name='suboption'),
        path('question_answer_create/<question_id>/question_suboption_get',questionanswercontroller.questioin_suboption_get, name='question'),
        path('get_periodicity', questionscontroller.get_periodcity, name='get_periodicity'),
        path('approve_vendor', vendorcontroller.approve_vendor, name='Approved Vendor'),
        path('approval_dropdown_val', questionanswercontroller.approval_dropdown_val, name='approval_dropdown'),
        path('vow_pan_check', vowcontroller.pan_exist_check, name='PAN check'),
        path('branch_summary', vowcontroller.branch_summary, name='Branch Summary'),
        path('branch_drpdwn', vowcontroller.branch_details, name='Branch dropdown'),
        path('portal_flag_update/<vendor_id>', vendorcontroller.portal_flag_update, name='portal_flag'),
        path('fileview/<file_id>', questionanswercontroller.view_file, name='view_file'),
        path('question_answer_create1', questionanswercontroller.question_answer_create1,name='question_answer'),
        path('activity_trans/<No>', questionanswercontroller.get_activitytransget, name='activitytransaction'),
        path('activity_answer_create', questionanswercontroller.activity_answer_create, name='activity_answer_create'),
        path('activity_answer_create1', questionanswercontroller.activity_answer_create1, name='activity_answer_create'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
