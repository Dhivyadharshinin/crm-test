from django.utils import timezone

from cmsservice.models.cmsmodels import CMS_MailScheduler,CMSProjectInvitation
from userservice.models.usermodels import Employee,EmployeeGroupMapping,Vow_user
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from cmsservice.util.cmsutil import Mail_Reltype,Mail_ToType,Mail_TranType,Mail_Is_user, Mailtotypeutil
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

def cms_mail(type,data,employee_id):
    arr=[]
    if type==Mail_TranType.CREATED:
        for i in data:
            obj=CMS_MailScheduler(rel_id=i.rel_id,rel_type=i.rel_type,tran_type=Mail_TranType.CREATED,to_mail=i.to_mail,is_user=Mail_Is_user.CMS,created_date=timezone.now(),to_type=Mail_ToType.MAKER,created_by=employee_id)
            arr.append(obj)
    elif type==Mail_TranType.APPROVED:
        for i in data:
            obj = CMS_MailScheduler(rel_id=i.rel_id, rel_type=i.rel_type, tran_type=Mail_TranType.APPROVED,
                                    to_mail=i.to_mail, is_user=Mail_Is_user.CMS, created_date=timezone.now(),
                                    to_type=Mail_ToType.APPROVER, created_by=employee_id)
            arr.append(obj)
    elif type==Mail_TranType.REJECTED:
        for i in data:
            obj = CMS_MailScheduler(rel_id=i.rel_id, rel_type=i.rel_type, tran_type=Mail_TranType.REJECTED,
                                    to_mail=i.to_mail, is_user=Mail_Is_user.CMS, created_date=timezone.now(),
                                    to_type=Mail_ToType.APPROVER, created_by=employee_id)
            arr.append(obj)
    elif type ==Mail_TranType.RETURNED:
        for i in data:
            obj = CMS_MailScheduler(rel_id=i.rel_id, rel_type=i.rel_type, tran_type=Mail_TranType.RETURNED,
                                    to_mail=i.to_mail, is_user=Mail_Is_user.CMS, created_date=timezone.now(),
                                    to_type=Mail_ToType.APPROVER, created_by=employee_id)
            arr.append(obj)
    elif type==Mail_TranType.FORWARDED:
        for i in data:
            obj = CMS_MailScheduler(rel_id=i.rel_id, rel_type=i.rel_type, tran_type=Mail_TranType.FORWARDED,
                                    to_mail=i.to_mail, is_user=Mail_Is_user.CMS, created_date=timezone.now(),
                                    to_type=Mail_ToType.APPROVER, created_by=employee_id)
            arr.append(obj)

    CMS_MailScheduler.objects.bulk_create(arr)


class EmailService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)
    def cmsemail(self):
        data1 = CMS_MailScheduler.objects.using(self._current_app_schema()).filter(is_send=False)
        arr = []
        for i in data1:
            if i.is_user == Mail_Is_user.CMS:
                if i.to_type == Mailtotypeutil.employee:
                    emp1 = Employee.objects.using(self._current_app_schema()).get(id=i.to_mail)
                    arr.append(emp1.email_id)
                elif i.to_type == Mailtotypeutil.group:
                    grpemp = EmployeeGroupMapping.objects.using(self._current_app_schema()).filter(group_id=i.to_mail)
                    for emp in grpemp:
                        arr.append(emp.employee.email_id)

            else:
                if i.to_type == Mailtotypeutil.vendor:
                    grpemp1 = CMSProjectInvitation.objects.using(self._current_app_schema()).get(id=i.to_mail)
                    for emp1 in grpemp1:
                        arr.append(emp1.email_id)
                else:
                    data2 = Vow_user.objects.using(self._current_app_schema()).get(id=i.to_mail)
                    arr.append(data2.email_id)
        return arr

    def createmailcms(self,arr,emp_id):
        for data in arr :
            rel_id = data['rel_id']
            rel_type = data['rel_type']
            to_mail = data['to_mail']
            tran_type = data['tran_type']
            is_user = data['is_user']
            to_type = data['to_type']
            v_obj = CMS_MailScheduler.objects.using(self._current_app_schema()).create(rel_id=rel_id, rel_type=rel_type, tran_type=tran_type,
                                        to_mail=to_mail, is_user=is_user,
                                        to_type=to_type, created_by=emp_id)

        return