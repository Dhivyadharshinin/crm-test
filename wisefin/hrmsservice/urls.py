from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from hrmsservice.controller import employeepaycontroller, payrollcontroller,employeedetailscontroller,employeeeducationdetailscontroller,empbankdetailscontroller,hrmspdfcontroller,employeedocumentcontroller

urlpatterns = [      path('employee_pay', employeepaycontroller.create_employeepay, name=' employee'),
                     path('employee_pay/<id>', employeepaycontroller.fetch_employeepay, name=' get'),
                     path('employee_adv', employeepaycontroller.create_employee_advancerequest, name=' get'),
                     path('employee_adv/<id>', employeepaycontroller.fetch_employee_advancerequest, name=' get'),
                     path('emp_approval', employeepaycontroller.create_employee_advanceapproval, name=' get'),
                     path('emp_approval/<id>', employeepaycontroller.fetch_employee_advanceapproval, name=' get'),

                     path('workweek', payrollcontroller.create_workweek, name=' work'),
                     # path('pay/<id>', payrollcontroller.fetch_workweek, name=' pay'),
                     # path('pay-srch/<day>', payrollcontroller.search_workweek, name=' pay'),
                     path('workshift', payrollcontroller.create_WorkShift, name=' pay'),
                     path('workshift/<id>', payrollcontroller.fetch_WorkShift, name=' pay'),
                     path('payday', payrollcontroller.create_payday, name=' pay'),
                     path('payday/<id>', payrollcontroller.fetch_payday, name=' pay'),
                     path('payroll', payrollcontroller.create_payrollconfigstatus, name=' pay'),
                     path('payroll/<id>', payrollcontroller.fetch_payrollconfigstatus, name=' pay'),
                     # employee details info
                     path('employeedetails/<employeeid>',employeedetailscontroller.employeedetails,name='employee'),
                     path('employeefamilyinfo/<employee_id>',employeedetailscontroller.employeefamilyinfo,name='employeefamilyinfo'),
                     path('employeeeducationdetails/<employee_id>',employeeeducationdetailscontroller.employeeeducationdetails,name='employeeeducation info'),
                     path('empemergencycontact/<employee_id>',employeedetailscontroller.empemergencycontact,name='empemergencycontact'),
                     path('employeeexperiences/<employee_id>',employeeeducationdetailscontroller.employeeexperiences,name='employeeexperiences'),
                     path('employeebankdetails/<employee_id>',empbankdetailscontroller.employeebankdetails,name='employeebankdetails'),
                     # common template pdf
                     path('commontemplate_pdf/<employee_id>',hrmspdfcontroller.commontemplate_pdf,name='commontemplate_pdf'),
                     #  employee document
                    path('employeedocument/<employee_id>',employeedocumentcontroller.employee_document,name='commontemplate_pdf'),
                     path('hrms_drop_down',employeedetailscontroller.hrms_drop_down,name='hrms_drop_down'),
                     path('employeeshiftmapping',employeedetailscontroller.employeeshiftmapping,name='employee_shift_mapping')
                     ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
