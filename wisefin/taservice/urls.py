from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from taservice.controller import tacontroller
from django.shortcuts import render


urlpatterns = [
    path('tourdata/<tour_id>', tacontroller.tourrequest_get, name='tourrequest_get'),
    # path('tourid_data/<tour_id>', tacontroller.tourid_data, name='tourid_data'),
    # path('tourdata', tacontroller.tour_data, name='tour_data'),
    path('nac_tourdata', tacontroller.nac_tour_data, name='tour_data'),
    # path('all_tour_report', tacontroller.all_tour_report, name='all_tour_report'),
    path('tour', tacontroller.tour_request, name='tour_request'),
    path('tourreason', tacontroller.tour_reason, name='tour_reason'),
    path('tourapprove', tacontroller.tour_approve, name='tour_approve'),
    # path('tourapprove/<type>', tacontroller.approver_data, name='approver_data'),
    path('nac_tourapprove/<type>', tacontroller.nac_approver_data, name='approver_data'),
    path('touradvance', tacontroller.tour_advance, name='tour_advance'),
    path('touradvance/<tour_id>', tacontroller.advance_get, name='advanceget'),
    path('advance_summary', tacontroller.advance_summary, name='advance_summary'),
    path('admin_summary', tacontroller.admin_summary, name='admin_summary'),
    # path('tourid_advance/<tour_id>', tacontroller.tourid_advance, name='tourid_advance'),

    # path('touradvance/tour', tacontroller.tourto_advance, name='tourto_advance'),
    # path('touradvance/tour/<tour_id>', tacontroller.tourto_advance_detail, name='tourto_advance_detail'),
    path('expenselist', tacontroller.expenselist, name='expenselist'),

    path('claimreq/tour/<tour_id>', tacontroller.claimreq_tour_get, name='claimreq_tour_get'),
    path('claim_request/<tour_id>', tacontroller.claimreq_tour_get_mobile, name='claimreq_tour_get'),
    path('get_each_expense/<tour_id>', tacontroller.get_each_expense, name='get_each_expense'),
    # path('claimreq', tacontroller.claimreq_get, name='claimreq_get'),

    path('dailydeim', tacontroller.dailydeim_insert, name='dailydeim_insert'),
    path('dailydeim/<type>', tacontroller.dailydeim_logic, name='dailydeim_logic'),
    path('dailydeim/tour/<tour_id>', tacontroller.dailydeim_tour_get, name='dailydeim_tour_get'),

    path('localdeputation', tacontroller.localdeputation, name='localdeputation'),
    path('localdeputation/<type>', tacontroller.localdeputation_logic, name='localdeputation_logic'),
    path('localdeputation/tour/<tour_id>', tacontroller.localdeputation_get, name='localdeputation_tour_get'),

    path('incidental', tacontroller.incidental_insert, name='incidental_insert'),
    path('incidental/<type>', tacontroller.incidental_logic, name='incidental_logic'),
    path('incidental/tour/<tour_id>', tacontroller.incidental_tour_get, name='incidental_insert'),

    path('localconv', tacontroller.localconv_insert, name='localconv_insert'),
    path('localconv/<type>', tacontroller.localconv_logic, name='localconv_logic'),
    path('localconv/tour/<tour_id>', tacontroller.localconv_tour_get, name='localconv_tour_get'),

    path('lodging', tacontroller.lodging_insert, name='lodging_insert'),
    path('lodging/<type>', tacontroller.lodging_logic, name='lodging_logic'),
    path('lodging/tour/<tour_id>', tacontroller.lodging_tour_get, name='lodging_tour_get'),

    path('misc', tacontroller.misc_insert, name='misc_insert'),
    path('misc/<type>', tacontroller.misc_logic, name='misc_logic'),
    path('misc/tour/<tour_id>', tacontroller.misc_tour_get, name='misc_tour_get'),

    path('packingmvg', tacontroller.packingmvg_insert, name='packingmvg_insert'),
    path('packingmvg/<type>', tacontroller.packingmvg_logic, name='packingmvg_logic'),
    path('packingmvg/tour/<tour_id>', tacontroller.packingmvg_tour_get, name='packingmvg_tour_get'),

    path('travel', tacontroller.travel_insert, name='travel_insert'),
    # path('travel/<type>', tacontroller.travel_logic, name='travel_logic'),
    path('travel/tour/<tour_id>', tacontroller.travel_tour_get, name='travel_tour_get'),

    path('associate', tacontroller.associate_insert, name='associate_insert'),
    path('associate/tour/<tour_id>', tacontroller.associate_tour_get, name='associate_tour_get'),

    # path('autoemail', tacontroller.automate_email, name='automate_email'),

    path('expense/<type>', tacontroller.expense_movetoapprover, name='expense_movetoapprover'),

    # allowance
    path('allowance', tacontroller.allowance_insert, name = 'allowance'),
    path('allowance/<fetch_id>',tacontroller.allowance_fetch, name = 'allowance'),
    path('allowance_get',tacontroller.allowance_get, name = 'allowance_get'),

    #gradeeligibility
    path('grade', tacontroller.grade_insert,name ='grade'),
    path('grade/<fetch_id>', tacontroller.grade_fetch,name ='grade'),

    path('tourforward', tacontroller.approved_forward, name='approved_forward'),
    path('tourreturn', tacontroller.approved_return, name='approved_return'),
    path('tourcancel',tacontroller.tour_cancel, name='tour_cancel'),
    path('tourreject', tacontroller.tour_reject, name='tour_reject'),

    # path('eligibleamount',tacontroller.filter_amount, name ='filter_amount'),

    path('holiday', tacontroller.holiday_insert, name='holiday_insert'),
    path('holiday/<fetch_id>', tacontroller.fetch_holiday, name='fetch_holiday'),
    path('holiday_file', tacontroller.holiday_file, name='holiday_insert'),
    #employeemapping
    path('employeemapping', tacontroller.employeemapping_insert, name='employeemapping_insert'),
    path('employeemapping/<fetch_id>', tacontroller.fetch_employeemapping, name='fetch_employeemapping'),
    path('employee_designation/<designation>', tacontroller.employee_designation, name='employee_designation'),

    # Holidaydeim
    path('holidaydeim', tacontroller.holidaydeim, name='holidaydeim'),
    path('holidaydeim/<id>', tacontroller.fetch_hol_deim, name='fetch_hol_deim'),

    # Glmapping
    path('glmapping', tacontroller.glmapping, name='glmapping'),
    path('glmapping/<id>', tacontroller.fetch_glmapping, name='fetch_glmapping'),
    # elligible amount-lodging
    # path('elligible_lodging_amount', tacontroller.elligible_lodging_amount, name='elligible_lodging'),

    #update amount in expenses table from list of expense
    path('expamount',tacontroller.expense_amount,name = 'expense_amount'),
    path('app_amt_ccbs_update/<tourid>',tacontroller.app_amt_ccbs_update,name = 'app_amt_ccbs_update'),
    #advance adjust
    # path('updateapprove',tacontroller.advance_updamt,name='advance_updamt'),

    # dailydeim amount calculate percentage and holidays and return eligible amount
    # path('dailyeligibleamount',tacontroller.dailydeim_filter,name = 'dailydeim'),
    # total amount packing_moving
    # path('packing_moving_amount', tacontroller.packing_moving_amount, name='packing_moving_amount'),
    # driver bata amount
    # path('driver_bata_amount', tacontroller.driver_bata_amount, name='driver_bata_amount'),

    # approvelist
    path('approverlist', tacontroller.approvelist_insert, name='allowance'),
    path('approverlist/<fetch_id>', tacontroller.approvelist_fetch, name='allowance'),

    #allowance
    # path('singlefare',tacontroller.allowance_elgible,name='allowanceeligible'),

    # breakage amount calculation
    # path('breakage_amount',tacontroller.breakage_amount, name='breakage_amount'),

    # common_dropdown
    path('common_dropdown', tacontroller.common_dropdown, name='common_dropdown'),
    path('common_dropdown_get/<code>', tacontroller.common_dropdown_get, name='common_dropdown_get'),
    path('common_dropdown_search/<code>', tacontroller.common_dropdown_search, name='common_dropdown_search'),#this api only for city dropdown
    path('common_dropdown/<id>', tacontroller.fetch_common_dropdown, name='fetch_common_dropdown'),
    # common_dropdown_details
    path('common_dropdown_details', tacontroller.common_dropdown_details, name='common_dropdown_details'),
    path('common_dropdown_details/<id>', tacontroller.fetch_dropdown_details, name='fetch_dropdown_details'),

    #expense submit
    # path('expense_submit', tacontroller.expense_submit, name= 'expense_submit'),
    # total amount
    # path('total_amount', tacontroller.total_amount, name='total_amount'),

    # ecf entry
    # path('ecf_entry', tacontroller.ecf_entry, name= 'ecf_entry'),
    # path('all_booking_get', tacontroller.all_booking_get, name= 'all_booking_get'),
    # path('ecf1', tacontroller.ecf1, name= 'ecf1'),

    # onbehalfof
    path('onbehalfof', tacontroller.onbehalfof_insert, name='onbehalfof'),
    path('onbehalfof/<fetch_id>', tacontroller.onbehalfof_fetch, name='onbehalfof'),
    path('onbehalf_emp_get', tacontroller.onbehalf_emp_get , name = 'onbehalf_emp_get'),
    path('nac_onbehalf_emp_get', tacontroller.nac_onbehalf_emp_get , name = 'onbehalf_emp_get'),
    path('nac_onbehalf_emp_get_check', tacontroller.nac_onbehalf_emp_get_check , name = 'onbehalf_emp_get_check'),
    path('onbehalf_emp_get/<branch>', tacontroller.onbehalf_emp_get_branch , name = 'onbehalf_emp_get_branch'),
    path('onbehalfof_status_update', tacontroller.onbehalfof_status, name = 'onbehalf_emp_get_branch'),

    # report
    path('report_tour_summary', tacontroller.report_tour_summary , name = 'report_tour_summary'),
    path('report_tourid_summary/<tourid>', tacontroller.report_tourid_summary , name = 'report_tourid_summary'),
    path('report_tour_detail/<tourno>', tacontroller.report_tour_detail , name = 'report_tour_detail'),
    path('report_tour_advance/<tourno>', tacontroller.report_tour_advance , name = 'report_tour_advance'),
    path('report_download_tour_summary', tacontroller.report_download_tour_summary , name = 'report_tour_summary'),
    path('report_download_tourid/<tourid>', tacontroller.report_download_tourid , name = 'report_tourid'),
    path('report_download_tour_detail/<tourno>', tacontroller.report_download_tour_detail , name = 'report_tour_detail'),
    path('report_download_tour_advance/<tourno>', tacontroller.download_tour_advance , name = 'report_tour_advance'),
    path('report_download_tour_expense/<tourno>', tacontroller.report_download_tour_expense , name = 'report_tour_expense'),
    path('consolidate_report/<tourno>', tacontroller.consolidate_report , name = 'consolidate_report'),
    path('branchwise_pending/<empgid>', tacontroller.branchwise_pending, name='branchwise_pending'),
    path('report_tour_requirements', tacontroller.report_tour_requirements, name='branchwise_pending'),
    path('report_tour_requirements_download', tacontroller.report_requirements_download, name='branchwise_pending'),
    # path('report_requirements_download', tacontroller.report_requirements_download, name='branchwise_pending'),

    path('nac_report', tacontroller.nac_report, name='nac_report'),

    # date_relaxation
    path('date_relaxation', tacontroller.date_relaxation, name='date_relaxation'),
    path('date_relaxation/<id>', tacontroller.date_relaxation_fetch, name='date_relaxation'),

    path('approve_international_travel', tacontroller.approve_international_travel, name='approve_international_travel'),
    path('insure_international_travel', tacontroller.insure_international_travel, name='insure_international_travel'),

    # path('cc_get', tacontroller.cc_get, name='cc_get'),
    # path('bs_get', tacontroller.bs_get, name='bs_get'),
    # path('searchbs_cc', tacontroller.searchbs_cc, name='searchbs_cc'),

    # path('search_employee', tacontroller.search_employee, name='search_employee'),
    # path('employeebranch', tacontroller.employeebranch, name='employeebranch'),

    # path('branch_employee_get/<branch>', tacontroller.branch_employee_get, name='branch_employee_get'),
    path('branch_approver_get/<type>/branch/<branch>', tacontroller.branch_approver_get, name='branch_approver_get'),

    path('fetch_documents/<refid>', tacontroller.fetch_documents , name = 'fetch_documents'),
    path('download_documents/<file_id>', tacontroller.download_attachment , name = 'download_documents'),
    # path('pdf_download/<id>', tacontroller.pdf_download , name = 'pdf_download'),
    # path('requirement_file/<id>', tacontroller.requirement_file , name = 'requirement_file'),

    path('expense_summary', tacontroller.expense_summary , name = 'expense_summmary'),
    path('approved_data', tacontroller.approved_data , name = 'approved_data'),
    path('cancelled_data', tacontroller.cancelled_data , name = 'cancelled_data'),
    path('change_approver', tacontroller.change_approver , name = 'change_approver'),
    # path('change_maker_comment', tacontroller.change_maker_comment , name = 'change_maker_comment'),

    path('ccbs_get', tacontroller.ccbs_get , name = 'ccbs_get'),
    path('ccbs_update', tacontroller.ccbs_update , name = 'ccbs_update'),
    path('tourno_grade_get/<tourid>', tacontroller.tourno_grade_get , name = 'tourno_grade_get'),
    path('approval_flow_get', tacontroller.approval_flow_get , name = 'approval_flow_get'),
    path('expense_delete/<tourid>/tour/<type>', tacontroller.expense_delete , name = 'expense_delete'),
    path('dependencies', tacontroller.dependencies , name = 'dependencies'),
    path('travel_dependencies_travelid/<travelid>', tacontroller.travel_dependencies_travelid , name = 'travel_dependencies_travelid'),
    path('dependencies_get', tacontroller.dependencies_get , name = 'dependencies_get'),
    # path('hsn_code_search', tacontroller.hsn_code_search, name='hsn_code_search'),
    path('ongoing_tour', tacontroller.ongoing_tour, name='ongoing_tour'),
    path('forward_data_get', tacontroller.forward_data_get, name='forward_data_get'),
    path('emp_details_get', tacontroller.emp_details_get, name='emp_details_get'),
    path('emp_elig_travel', tacontroller.emp_elig_travel, name='emp_elig_travel'),
    # path('bank_gst_get', tacontroller.bank_gst_get, name='bank_gst_get'),
    path('provision', tacontroller.provision, name='provision'),
    # path('crn_get/<ecf_no>', tacontroller.crn_get, name='crn_get'),
    path('adv_adjust_check/<tourid>', tacontroller.adv_adjust_check, name='adv_adjust_check'),
    path('recovery_summary', tacontroller.recovery_summary, name='recovery_summary'),
    path('recovery_get_jv', tacontroller.recovery_get_jv, name='recovery_get_jv'),
    path('recovery_jv_entry', tacontroller.recovery_jv_entry, name='recovery_jv_entry'),
    path('branch_onbehalf_status/<branch>/emp/<empid>', tacontroller.branch_onbehalf_status, name='branch_onbehalf_status'),

    # delete start used for BE reference
    path('tour_status_get', tacontroller.tour_status_get, name='tour_status_get'),
    path('tourapprovedby_table', tacontroller.tourapprovedby_table, name='tourapprovedby_table'),
    path('update_approvedby', tacontroller.update_approvedby, name='update_approvedby'),
    path('effective_date', tacontroller.effective_date, name='effective_date'),
    path('onbehalf_present', tacontroller.onbehalf_present, name='onbehalf'),
    path('onbehalf_notpresent', tacontroller.onbehalf_notpresent, name='onbehalf'),
    # get approverlist by their branch id and type
    path('approvetype', tacontroller.approvetype, name='approve'),
    path('common_dropdown/detail/<id>', tacontroller.get_dropdown_details, name='get_dropdown_details'),
    path('travel_dependencies', tacontroller.travel_dependencies, name='travel_dependencies'),
    # delete end
    #ALLOWANCE FILE UPLOAD
    path('allowance_file_upload', tacontroller.allowance_file_upload, name='allowance_file_upload'),
    # path('allowance_get_effectiveto', tacontroller.allowance_get_effectiveto, name='allowance_get_effectiveto'),

    # ALLOWANCE FILE UPLOAD
    # path('holiday_file_upload', tacontroller.holiday_file_upload, name='holiday_file_upload'),

    #loding tax ccbs
    # path('lodging_tax_ccbs', tacontroller.lodging_tax_ccbs, name='lodging_tax_ccbs')

    #tourdetail_details
    path('tour_detail_delete/<id>', tacontroller.tour_detail_delete, name='tour_detail_delete'),
    # path('travel_req_delete/<req_id>', tacontroller.travel_req_delete, name='travel_req_delete'),
    path('upload_excel_data', tacontroller.common_excelUpload, name='upload_excel_data'),
    path('role_permission', tacontroller.role_permission, name='role_permission'),

    #chat_box
    path('chat_box', tacontroller.chat_box, name='chat_box'),
    path('chat_box_view', tacontroller.chat_box_view, name='chat_box'),
    path('chat_summary', tacontroller.chat_summary, name='chat_box'),

    path('delete_chat_box', tacontroller.del_chat_box, name='del_chat_box'),
    path('undo_chat_box', tacontroller.undo_chat_box, name='undo_chat_box'),
    path('approved_by_get', tacontroller.approved_by_get, name='approver_chat_box'),
    #doc_master
    # path('insert_documenttype', tacontroller.insert_doctype, name='chat_box'),
    # path('del_documenttype', tacontroller.del_doctype, name='chat_box'),
    # path('booking', tacontroller.booking, name='booking'),

    path('document_insert',tacontroller.doc_insert,name='insert_doc'),
    path('document_get',tacontroller.doc_fetch,name='GET'),
    # path('document_',tacontroller.doc_fetch,name='GET'),
    path('document_view',tacontroller.doc_view,name='GET'),
    path('particular_doc_get/<id>',tacontroller.particulardoc_get,name='GET'),


    #weekend_check
    path('holiday_check', tacontroller.holiday_check, name='holiday_check'),
    #count_get
    path('all_travel_get', tacontroller.all_travel_employee, name='all_travel_employe'),
    path('claim_count', tacontroller.total_claim_count, name='total_claim_count'),
    path('alltravelget_date', tacontroller.alltravelget_date, name='all_travel_employe'),
    path('allclaimget_date', tacontroller.allclaimget_date, name='all_travel_employe'),

#car_requirements
    path('cab_booking',tacontroller.cab_booking,name='cab_booking'),
    path('cab_details/<id>',tacontroller.cab_details,name='cab_details'),
    path('cab_booking_admin',tacontroller.cab_booking_admin,name='cab_booking_admin'),
    path('cab_details_admin/<id>',tacontroller.cab_details_admin,name='cab_details_admin'),

    #Bus_requirements
    path('bus_booking',tacontroller.bus_booking,name='bus_booking'),
    path('bus_details/<id>',tacontroller.bus_details,name='bus_details'),
    path('bus_booking_admin',tacontroller.bus_booking_admin,name='bus_booking_admin'),
    path('bus_details_admin/<id>',tacontroller.bus_details_admin,name='bus_details_admin'),


    #Air_requirements
    path('air_booking',tacontroller.air_booking,name='air_booking'),
    path('sameday_booking',tacontroller.sameday_booking,name='air_booking'),
    path('air_details/<id>',tacontroller.air_details,name='air_details'),
    path('air_booking_admin',tacontroller.air_booking_admin,name='air_booking_admin'),
    path('air_details_admin/<id>',tacontroller.air_details_admin,name='air_details_admin'),

    #Train_requirements
    path('train_booking',tacontroller.train_booking,name='train_booking'),
    path('train_details/<id>',tacontroller.train_details,name='train_details'),
    path('train_booking_admin',tacontroller.train_booking_admin,name='train_booking_admin'),
    path('train_details_admin/<id>',tacontroller.train_details_admin,name='train_details_admin'),

    path('accommodation_booking',tacontroller.accommodation_booking,name='accommodation_booking'),
    path('accommodation/<id>',tacontroller.accommodation_details,name='accommodation'),
    path('accommodation_booking_admin',tacontroller.accommodation_booking_admin,name='accommodation_booking_admin'),
    path('accommodation_details_admin/<id>',tacontroller.accommodation_details_admin,name='accommodation_details_admin'),

    path('get_requirements_admin', tacontroller.get_requirements_admin,name='get_requirements_admin'),

    path('short_term_travel',tacontroller.short_term_travel,name='short_term_travel'),
    path('delete_travel_requirements',tacontroller.delete_travel_requirements,name='delete_travel_requirements'),

    path('popup_five_days',tacontroller.daterelaxation_popup,name='daterelaxation_popup'),
    path('popup_nine_days',tacontroller.popup_nine_days,name='daterelaxation_popup'),

    path('client',tacontroller.client_insert,name='client_insert'),
    path('client/<id>',tacontroller.get_client,name='client_get'),

    path('cancel_booking_request',tacontroller.cancel_booking_request,name='cancel_booking_request'),
    path('req_cancel_approve',tacontroller.req_cancel_approve,name='cancel_approve'),
    path('requirement_reject',tacontroller.requirement_reject,name='requirement_reject'),
    # path('eligible_amount',tacontroller.eligible_amount_popup,name='eligible_amount_popup'),
    path('employee_base_get',tacontroller.employee_base_get,name='cancel_approve'),

    path('personal_official', tacontroller.personal_official,name='personal_official'),
    path('city_dropdown', tacontroller.city_dropdown,name='city_dropdown'),
    path('no_show', tacontroller.no_show,name='no_show'),
    path('admin_reserv', tacontroller.admin_reserv,name='admin_reserv'),
    path('get_emp_rm', tacontroller.get_emp_rm,name='get_emp_rm'),
    path('get_emp_fm', tacontroller.get_emp_fm,name='get_emp_fm'),
    # path('money_conversion', tacontroller.money_conversion,name='city_dropdown'),
    path('insert_ta_city', tacontroller.insert_ta_city,name='insert_ta_city'),
    path('city_file', tacontroller.city_file,name='city_file'),
    path('state_dropdown', tacontroller.state_dropdown,name='state_dropdown'),
    path('citytype_dropdown', tacontroller.citytype_dropdown,name='citytype_dropdown'),
    path('branch_dropdown', tacontroller.branch_dropdown,name='citytype_dropdown'),
    path('city_delete/<id>', tacontroller.city_delete,name='city_delete'),
    path('tour_reason/<id>', tacontroller.tourreason_delete,name='tour_reason'),
    path('tour_expense', tacontroller.tour_expense,name='tour_expense'),
    path('tour_expense/<id>', tacontroller.tourexpense_delete,name='tour_expense'),
    path('frequent_city', tacontroller.frequent_city,name='frequent_city'),
    path('frequent_client', tacontroller.frequent_client,name='frequent_client'),
    path('frequent_data_insert', tacontroller.frequent_data_insert,name='frequent_data_insert'),
    path('edit_history/<id>', tacontroller.edit_history,name='frequent_data_insert'),
    path('edited_difference/<id>', tacontroller.edited_difference,name='frequent_data_insert'),
    path('team_update', tacontroller.team_update,name='team_update'),

    # path('no_show', tacontroller.no_show,name='no_show'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



