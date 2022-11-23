from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from masterservice.controller import ccbsmappingcontroller, ccbscontroller
from userservice.controller import authcontroller, modulecontroller, modulemappingcontroller, rolecontroller, \
rolemodulecontroller, roleemployeecontroller, employeecontroller, employeebranchcontroller, usercontroller, \
    directquery, employeehierarchycontroller, employeeaccountdetailscontroller,\
 employeebranchcontroller, usercontroller, directquery,generalledgercontroller,entitycontroller,employeesynccontroller,sftpcontroller,groupcontroller,deptfileuploadcontroller


urlpatterns = [
    path('signup', authcontroller.signup, name='signup'),
    path('auth_token', authcontroller.auth_token, name='auth_token'),
    path('test', authcontroller.test, name='test'),
    # module
    path('usermodule', modulecontroller.module, name='module'),
    path('usermodule/<module_id>', modulecontroller.fetch_module, name='module_get'),
    # modulemapping
    path('modulemapping/<moduleuser_id>', modulemappingcontroller.modulemapping, name='modulemapping'),
    path('moduleorder', modulemappingcontroller.module_order, name='moduleordering'),

    # role
    path('role', rolecontroller.role, name='role'),
    path('role/<role_id>', rolecontroller.fetch_role, name='get_role'),
    path('role/<role_id>/employee', roleemployeecontroller.fetch_employee, name='get_employee'),
    path('role/<role_id>/module', rolemodulecontroller.fetch_module, name='get_module'),

    # roleemployee
    path('roleemployee', roleemployeecontroller.roleemployee, name='roleemployee'),
    path('roleemployee/<employee_id>', roleemployeecontroller.fetch_role, name='roleemployee_get'),
    # rolemodule
    path('rolemodule', rolemodulecontroller.rolemodule, name='rolemodule'),
    path('rolemodule/<module_id>', rolemodulecontroller.fetch_role, name='rolemodule_get'),

    #role - module -employee
    path('permission', roleemployeecontroller.permission, name='permission'),
    path('user/<employee_id>', roleemployeecontroller.employee_module, name='employee_module'),
    path('module/<module_id>/role/<role_id>/users', roleemployeecontroller.fetch_employee_modulerole, name='fetch_employee_modulerole'),
    # path('start_migrations', roleemployeecontroller.start_migrations, name='start_migrations'),

    #submodule
    path('usermodule/<module_id>/submodule', modulecontroller.fetch_submodule,name='module_get'),
    path('user_modules', roleemployeecontroller.employee_submodule, name='employee_submodule'),
    path('user_modules/<employee_id>', roleemployeecontroller.employee_submodule_empid, name='employee_submodule'),
    path('user_modules/<employee_id>', roleemployeecontroller.employee_submodule_empid, name='employee_submodule'),

    # ADMIN
    path('role_admin', rolecontroller.role_admin, name='role'),
    path('role_admin/<role_id>', rolecontroller.fetch_role_admin,name='get_role'),
    path('usermodule_admin', modulecontroller.module_admin, name='module'),
    path('usermodule_admin/<module_id>', modulecontroller.fetch_module_admin, name='module_get'),
    path('permission_admin', roleemployeecontroller.permission_admin, name='permission'),
    path('permission_all_admin', roleemployeecontroller.permission_all, name='permission'),
    path('user_modules_admin/<employee_id>', roleemployeecontroller.employee_submodule_admin,name='module_get'),
    # path('del_table',rolecontroller.del_table,name='del_table'),
    path('Branch_data',employeecontroller.Branch_data,name='branch_data_get'),
    path('employee_bs_data', employeecontroller.bs_data_get, name='bs_data_get'),
    path('create_employee_account_details', employeeaccountdetailscontroller.create_employee_account,name='create_employee_account'),
    path('employee_modulerole',modulecontroller.employee_modulerole,name='employee_modulerole'),
    # path('premission_remove_category',roleemployeecontroller.permission_remove, name='permission_remove'),
    # path('rems_permission',roleemployeecontroller.rems_permission, name='rems_permission'),
    path('employee', employeecontroller.create_employee, name='employee'),
    path('employeemobileno', employeecontroller.employeemobileno, name='employeemobileno'),
    path('fetch_empmobile', employeecontroller.fetch_empmobile, name='fetch_empmobile'),
    path('employee_account_get', employeeaccountdetailscontroller.employee_get, name='employee_account_get'),
    path('employee_paymode_get', employeeaccountdetailscontroller.employee_paymode_get,name='employee_paymode_get'),
    path('employee_bank', employeeaccountdetailscontroller.employee_bank, name='employee_bank'),
    path('mobileupdation', employeecontroller.mobileupdation, name='mobileupdation'),
    # path('employeemobilenomicro', employeecontroller.employeemobilenomicro, name='employeemobilenomicro'),
    path('employee/<employee_id>', employeecontroller.fetch_employee, name='fetch_employee'),
    path('employee_get_view/<employee_id>', employeecontroller.fetch_employee_id, name='employee_get_view'),
    path('department', employeecontroller.department, name='department'),
    path('department_download',employeecontroller.department_download,name='department_download'),
    path('department/<dept_id>', employeecontroller.fetch_department, name='fetch_department'),
    path('emplist', employeecontroller.employee_info, name='employee_info'),
    path('emplistbyeid', employeecontroller.employee_info_by_id, name='employee_info'),
    path('deplist', employeecontroller.department_info, name='department_info'),
    path('userid', employeecontroller.get_user_id, name='get_user_id'),
    path('user_emp_list', employeecontroller.get_user_emp_list, name='get_user_info'),
    path('filter', employeecontroller.get_list_by_filter, name='get_list_by_liter'),
    path('searchemployee', employeecontroller.search_employee_list, name='search_employee_list'),
    path('searchrm', employeecontroller.searchrm, name='searchrm'),
    path('memosearchemp', employeecontroller.searchemployee_designation, name='search_employee_list'),
    path('employee_get_sync', employeecontroller.employee_get_sync, name='search_employee_list'),
    path('branch_get_sync', employeecontroller.fetch_allbranch_list, name='search_employee_list'),
    path('searchdepartment', employeecontroller.search_department_list, name='search_department_list'),
    path('employee_by_userid/<user_id>', employeecontroller.fetch_employee_by_userid,
                       name='fetch_employee_by_userid'),
    path('employee_get', employeecontroller.employee_get, name='employee_get'),
    path('employee_list', employeecontroller.employee_list, name='employee_list'),
    path('employee_id', employeecontroller.fetch_employee_id, name='fetch_employee_post'),
    path('get_employeename', employeecontroller.get_employeename, name='get_employeename'),
    path('get_employeename_data', employeecontroller.get_employeename_data, name='get_employeename_data'),
    # employee - department get add delete
    path('searchcostcentre', ccbsmappingcontroller.searchcostcentre, name='searchcostcentre'),
    path('searchbusinesssegment', ccbsmappingcontroller.searchbusinesssegment,name='searchbusinesssegment'),
    path('businesssegmentlist', ccbscontroller.businesssegmentlist, name='businesssegmentlist'),
    path('masterbusinesssegment', ccbscontroller.mastersegmentname, name='mastersegmentname'),
    path("employee/<employee_id>/department",employeecontroller.employee_department,name='emp_dep_get_update'),
    # department - employee get add delete
    path('employeehierarchy', employeehierarchycontroller.employeehierarchy, name='EmployeeHierarchy'),
    path('employee_department', employeecontroller.fetch_employee_department,name='fetch_employee_department'),
    path('fetch_emp_dropdown', employeecontroller.fetch_emp_dropdown, name='fetch_emp_dropdown'),
    path("department/<department_id>/employee",employeecontroller.department_employee,name='dep_emp_get_update'),
    path('deldept/<dept_id>',employeecontroller.deldept,name='deldept'),
    path('department_sys', employeecontroller.department_sys, name='department_sys'),
    path('fetch_employee',employeecontroller.fetch_employees,name = 'fetch_employee'),
    path('emp_getbycode', employeecontroller.fetch_emp_get, name='emp_getbycode'),
    path('employee_update', employeecontroller.employee_info_update, name='employee_update'),
    path('department_branch', employeecontroller.department_branch, name='department_branch'),
    path('employeebranch', employeebranchcontroller.employeebranch, name='branch'),
    path('employeebranch_activate_inactivate', employeebranchcontroller.employeebranch_activate_inactivate, name='employeebranch_activate_inactivate'),
    path('employeebranch_download', employeebranchcontroller.employeebranch_download, name='employeebranch_download'),
    path('employeebranch/<employeebranch_id>', employeebranchcontroller.fetch_employeebranch, name='branch_get'),
    path('employeebranch_get/<employeebranch_id>', employeebranchcontroller.fetch_employeebranch_get, name='fetch_employeebranch_get'),
    path('user_branch',employeebranchcontroller.userbranch, name='userbranch'),
    path('search_employeebranch',employeebranchcontroller.searchbranch, name='searchbranch'),
    path('branch_sync_api', employeebranchcontroller.branch_sync_create, name='branch_sync'),
    path('missing_branch', employeebranchcontroller.missing_branch, name='missing_branch'),
    path('branchtype_mapping', employeebranchcontroller.branchmapping, name='branchtype_mapping'),
    path('branch_dept_add', employeebranchcontroller.branch_dept_mapping, name='branch_dept_mapping'),
    path('controlling_office_branch', employeebranchcontroller.ctr_office_branch,
                       name='controlling_office_branch'),
    path('employeebranch_get', employeebranchcontroller.employeebranch_get, name='employeebranch_get'),
    path('fetch_employeebranchdata/<employeebranch_id>', employeebranchcontroller.fetch_employeebranchdata,
                       name='fetch_employeebranchdata'),
    path('fetch_employeebranchdata_code/<employeebranch_id>', employeebranchcontroller.fetch_employeebranchdata_code,
                       name='fetch_employeebranchdata_code'),
    path('search_branch', employeebranchcontroller.search_branch, name='search_branch'),
    path('fetch_ebranchaddressdata/<employeebranch_id>', employeebranchcontroller.fetch_ebranchaddressdata,
                       name='fetch_ebranchaddressdata'),
    path('fetch_ebranchaddress/<employeebranch_id>', employeebranchcontroller.fetch_ebranchaddress,
                       name='fetch_ebranchaddress'),
    # path('gl_summary', generalledgercontroller.gl_summary, name='gl_summary'),

                  # TA Dependents api call
    path('get_emp_details', usercontroller.get_emp_details, name='get_emp_details'),
    path('get_login_emp_details/<userid>', usercontroller.get_login_emp_details,
                       name='get_login_emp_details'),
    path('get_emp_grade1/<emp_id>', usercontroller.get_emp_grade1, name='get_emp_grade1'),
    path('get_branch_details', usercontroller.get_branch_details, name='get_branch_details'),
    path('get_branch_data/<branch>', usercontroller.get_branch_data, name='get_branch_data'),
    path('employee_details_get/<empid>', usercontroller.employee_details_get,
                       name='employee_details_get'),
    path('employee_details_all_get_ta/<empid>', usercontroller.employee_details_all_get_ta,
                       name='employee_details_all_get_ta'),
    path('bank_gst_get', usercontroller.bank_gst_get, name='bank_gst_get'),
    path('role_bh_emp_get/<branch_id>', usercontroller.role_bh_emp_get, name='role_bh_emp_get'),
    path('branchwise_employee_get/<branch>', usercontroller.branch_employee_get,
                       name='branch_employee_get'),
    #update
    path('module_order', modulemappingcontroller.module_order_assinging, name='module_order'),
    path('assign_module', modulemappingcontroller.assign_module, name='assign_module'),

    # entity api
    path('entity', authcontroller.get_entity, name='entity_list'),
    path('emp_entity', authcontroller.get_emp_entity, name='employee_entity'),
    path('entity_change', authcontroller.update_default_entity, name='entity_change'),
                  # entity
    path('create_entity', entitycontroller.create_entity, name='entity'),
    path('entity_activate_inactivate', entitycontroller.entity_activate_inactivate,
       name='entity_activate_inactivate'),

    path('cre_emp_entity', authcontroller.create_emp_entity, name='cre_entity'),
    path('del_emp_entity', authcontroller.delete_emp_entity, name='del_entity'),
    path('logout', authcontroller.nwisefin_logout, name='logout'),
    path('query_get', directquery.query_get, name='query_get'),
    # path('gl_master_scheduler', apscheduler.gl_master_sync, name='gl_master_sync'),

    path('generalledger', generalledgercontroller.general_ledger, name='general_ledger'),
    path('glfiledata_sync', generalledgercontroller.glfiledata_sync, name='glfiledata_sync'),
    path('gl_list_all', generalledgercontroller.fetch_allgl_list, name='general_ledger'),
    path('gl_summary', generalledgercontroller.gl_summary, name='gl_summary'),
    path('gl_no/<gl_no>', generalledgercontroller.gl_no_get, name='gl_no_get'),
    path('gl_activate_inactivate', generalledgercontroller.gl_activate_inactivate,name='gl_activate_inactivate'),
    path('employee_get_apexpense', employeecontroller.fetch_employeedata, name='employee_get_single'),

    path('emp_empbranch/<emp_id>', employeecontroller.emp_empbranch, name='emp_empbranch'),
    path('empbranch', employeebranchcontroller.empbranch, name='empbranch'),
    path('get_empbranch/<empbranch_id>', employeecontroller.fetch_empbranch, name='fetch_empbranch'),
    path('get_emp_empid/<emp_id>', employeecontroller.fetch_empbranch_empid, name='fetch_empbranch'),
    path('employee_bankbranch/<bank_id>',employeeaccountdetailscontroller.employee_bankbranch,name='employee_bankbranch'),
    path('employeeaccount_active_inactivate',employeeaccountdetailscontroller.employeeaccount_active_inactivate,name='employeeaccount_active_inactivate'),

    path('check_permission_ta',employeecontroller.check_permission_ta,name='check_permission_ta'),
    path('employee_synch',employeesynccontroller.employeesynchcontroller_data,name='employee_synch'),
    path('ceo_team_get_ta',employeecontroller.ceo_team_get_ta,name='ceo_team_get_ta'),
    path('ceo_team_get_ta_check',employeecontroller.ceo_team_get_ta_check,name='ceo_team_get_ta_check'),

    path('user_branch_ctrl',employeebranchcontroller.get_user_branch_ctrl, name='user_branch_ctrl'),
    path('controlling_office_branch_do', employeebranchcontroller.ctrl_office_branch, name='controlling_office_branch_do'),
    path('sftp_common_api', sftpcontroller.sftp_common_file_upload, name='sftp_common_file_upload'),

    path('refreshtoken', authcontroller.nwisefin_RefreshToken, name='nwisefin_RefreshToken'),

    # group
    path('employeegroup',groupcontroller.create_employee_group,name='employeegroup'),
    path('mapping_employee_group',groupcontroller.mapping_employee_group,name='mapping_employee_group'),
    path('get_employee_from_grpid/<group_id>',groupcontroller.get_employee_by_groupid,name='get_employee_from_grpid'),
    path('get_group_from_empid/<employee_id>',groupcontroller.get_group_by_empid,name='get_group_from_empid'),
    path('group_role', groupcontroller.get_group_role, name='get_group_role'),
    path('group_employee', groupcontroller.group_employee, name='group_employee'),
    path('group_employeeall', groupcontroller.group_employeeall, name='group_employeeall'),
    path('employeegroup_search', groupcontroller.employee_group_fetch, name='get_group_role'),

    # vow
    path('vow_signup', authcontroller.vow_signup, name='vow_signup'),
    path('vow_auth_token', authcontroller.vow_auth_token, name='vow_auth_token'),
    path('vow_user_insert', authcontroller.vow_user_insert, name='vow_user_insert'),
    path('dept/<dept_id>',deptfileuploadcontroller.create_deptfile, name='deptfileupload'),
    path('change_pass', usercontroller.change_password, name='password_change'),
    path('employee_org_info',employeecontroller.employee_org_info,name='emporgupdate')
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
