from django.db import IntegrityError
from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import ECFAudit
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from datetime import datetime

from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import ModuleList, RoleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now=str(now)

class ECFAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def create_audit(self, audit_obj):
        try:
            audit_var = ECFAudit.objects.using(self._current_app_schema()).create(ref_id=audit_obj.ref_id,
                                               ref_type=audit_obj.ref_type,
                                               data=audit_obj.data,
                                               user_id=audit_obj.user_id,
                                               date=now,
                                               req_status=audit_obj.req_status,
                                               rel_refid=audit_obj.rel_refid,
                                               rel_reftype=audit_obj.rel_reftype,
                                               action=audit_obj.action,entity_id=self._entity_id())
        except IntegrityError as error:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

        audit_data = ECFAuditResponse()
        audit_data.set_id(audit_var.id)
        audit_data.set_refid(audit_var.ref_id)
        audit_data.set_reftype(audit_var.ref_type)
        audit_data.set_data(audit_var.data)
        audit_data.set_userid(audit_var.user_id)
        audit_data.set_date(audit_var.date)
        audit_data.set_relrefid(audit_var.rel_refid)
        audit_data.set_reqstatus(audit_var.req_status)
        audit_data.set_relrefid(audit_var.rel_refid)
        audit_data.set_relreftype(audit_var.rel_reftype)
        audit_data.set_action(audit_var.action)
        return audit_data

    def fetch_audit_list(self, user_id):
        auditlist = ECFAudit.objects.using(self._current_app_schema()).all()
        list_length = len(auditlist)
        # print(list_length)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            audit_list_data = NWisefinList()
            for auditobj in auditlist:
                audit_data = ECFAuditResponse()
                audit_data.set_id(auditobj.id)
                audit_list_data.append(audit_data)
            return audit_list_data

    def fetch_audit(self, audit_id, user_id):
        try:
            audit_var = ECFAudit.objects.using(self._current_app_schema()).get(id=audit_id,entity_id=self._entity_id())
            audit_data = ECFAuditResponse()
            audit_data.set_id(audit_var.id)

            return audit_data
        except ECFAudit.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj

    def delete_audit(self, audit_id, user_id):
        audit = ECFAudit.objects.using(self._current_app_schema()).filter(id=audit_id,entity_id=self._entity_id()).delete()
        if audit[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def employee_role(self, request, user_id):
        api_serv = ModulePermission(self._scope())
        role_arr = api_serv.employee_modulerole(user_id,ModuleList.ECF)
        rolelist = RoleList.ONBEHALFOFF
        if rolelist in role_arr:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            # empp = api_serv.get_emp_id(request, user_id)
            # emp_id = empp['id']
            emppp = api_serv.get_empsingle_id(request, user_id)
            emp_id = emppp['id']
            emp_bid = emppp['employee_branch']
            empppp = api_serv.get_empbranch_id(request, emp_bid)
            emp_bname = empppp['name']
            print(emp_bname)
            emp = api_serv.get_emp_grade(request, emp_id)
            data = {}
            data["enable_ddl"] = True
            data["branch_name"] = emp_bname
            data["id"] = empppp['id']
            data["code"] = empppp['code']
            return data
        else:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            # empp = api_serv.get_emp_id(request, user_id)
            # emp_id = empp['id']
            emppp = api_serv.get_empsingle_id(request, user_id)
            emp_id = emppp['id']
            emp_bid = emppp['employee_branch']
            empppp = api_serv.get_empbranch_id(request, emp_bid)
            emp_bname = empppp['name']
            print(emp_bname)
            emp = api_serv.get_emp_grade(request, emp_id)
            data = {}
            data["enable_ddl"] = False
            data["branch_name"] = emp_bname
            data["id"] = empppp['id']
            data["code"] = empppp['code']
            return data