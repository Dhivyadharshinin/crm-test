from django.db import IntegrityError
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.data.response.securityguardresponse import SecurityguardResponse, EmployeementtypeResponse
from masterservice.service.masterauditservice import MasterAuditService
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import ContactType, Employeementcatgorymaster, EmployeementTypemaster
from django.utils import timezone

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class SecurityguardService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_employeementcat(self, exuom_obj, user_id):
        if not exuom_obj.get_id() is None:
            try:
                exuom = Employeementcatgorymaster.objects.using(self._current_app_schema()).filter(
                    id=exuom_obj.get_id(), entity_id=self._entity_id()).update(
                    empcat=exuom_obj.get_empcat(),
                    empcatdesc=exuom_obj.get_empcatdesc())
                exuom = Employeementcatgorymaster.objects.using(self._current_app_schema()).get(id=exuom_obj.get_id(),
                                                                                                entity_id=self._entity_id())
                employeementcat_auditdata = {'id': exuom_obj.get_id(),

                                             'empcat': exuom_obj.get_empcat(),
                                             'empcatdesc': exuom_obj.get_empcatdesc(),
                                             }
                self.audit_function(employeementcat_auditdata, user_id, exuom.id, ModifyStatus.update)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except ContactType.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
                error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                exuom = Employeementcatgorymaster.objects.using(self._current_app_schema()).create(
                    empcat=exuom_obj.get_empcat(),
                    empcatdesc=exuom_obj.get_empcatdesc(), entity_id=self._entity_id())

                self.audit_function(exuom, user_id, exuom.id, ModifyStatus.create)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def employeementcat_list(self,  vys_page,user_id):
        employeecatlist = Employeementcatgorymaster.objects.using(self._current_app_schema()).all()[
                  vys_page.get_offset():vys_page.get_query_limit()]
        employeecat_list_data = NWisefinList()
        for employeecat in employeecatlist:
            employeecat_data = SecurityguardResponse()
            employeecat_data.set_id(employeecat.id)
            employeecat_data.set_empcat(employeecat.empcat)
            employeecat_data.set_empcatdesc(employeecat.empcatdesc)
            employeecat_list_data.append(employeecat_data)
            vpage = NWisefinPaginator(employeecatlist, vys_page.get_index(), 10)
            employeecat_list_data.set_pagination(vpage)
        return employeecat_list_data

    def delete_employeementcat(self, exuom_id,emp_id):
        emptype=EmployeementTypemaster.objects.using(self._current_app_schema()).filter(empcat_id=exuom_id)

        if len(emptype)>0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DELETE)
            error_obj.set_description(ErrorDescription.INVALID_DELETE)
            return error_obj
        else:
            exuom = Employeementcatgorymaster.objects.using(self._current_app_schema()).filter(id=exuom_id).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_empcatdesc(self, vys_page,query):
        employeecatlist = Employeementcatgorymaster.objects.using(self._current_app_schema()).filter(empcat__icontains=query)[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(employeecatlist)
        #print(list_length)
        employeecat_list = NWisefinList()
        if list_length > 0:
            for employeecat in employeecatlist:
                employeecat_data = SecurityguardResponse()
                employeecat_data.set_id(employeecat.id)
                disp_name = employeecat.empcat + "-" + employeecat.empcatdesc
                employeecat_data.set_empcat(employeecat.empcat)
                employeecat_data.set_empcatdesc(employeecat.empcatdesc)
                employeecat_data.set_empdesc(disp_name)
                employeecat_list.append(employeecat_data)
                vpage = NWisefinPaginator(employeecatlist, vys_page.get_index(), 10)
                employeecat_list.set_pagination(vpage)
            return employeecat_list
        return employeecat_list

    def create_employeementtypecat(self, stu_obj, user_id):
        if stu_obj.get_empcat_id() == None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

        if not stu_obj.get_id() is None:
            # try:
               studentupdate=EmployeementTypemaster.objects.using(self._current_app_schema()).filter(id=stu_obj.get_id()).update(

                            emptype=stu_obj.get_emptype(),
                            emptypedesc=stu_obj.get_emptypedesc(),
                            empcat_id=stu_obj.get_empcat_id())
               stud = EmployeementTypemaster.objects.using(self._current_app_schema()).get(id=stu_obj.get_id())
               employeetype_auditdata = {'id': stu_obj.get_id(),

                                     'emptype': stu_obj.get_emptype(),
                                     'emptypedesc': stu_obj.get_emptypedesc(),
                                     'empcat_id' : stu_obj.get_empcat_id()
                                     }
               self.audit_function(employeetype_auditdata, user_id, stud.id, ModifyStatus.update)
               success_obj = NWisefinSuccess()
               success_obj.set_status(SuccessStatus.SUCCESS)
               success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
               return success_obj
        else:
            stud = EmployeementTypemaster.objects.using(self._current_app_schema()).create(
                emptype=stu_obj.get_emptype(),
                emptypedesc=stu_obj.get_emptypedesc(),
                empcat_id=stu_obj.get_empcat_id(), entity_id=self._entity_id())
            self.audit_function(stud, user_id, stud.id, ModifyStatus.create)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def employeetypemaster_list(self, vys_page, emp_cat, query):
        if query != None:
            employeetypelist = EmployeementTypemaster.objects.using(self._current_app_schema()).filter(
                empcat__empcat=query, entity_id=self._entity_id()).order_by('created_date')[
                               vys_page.get_offset():vys_page.get_query_limit()]
        elif emp_cat != None:
            employeetypelist = EmployeementTypemaster.objects.using(self._current_app_schema()).filter(
                empcat_id=emp_cat, entity_id=self._entity_id()).order_by('created_date')[
                               vys_page.get_offset():vys_page.get_query_limit()]
        else:
            employeetypelist = EmployeementTypemaster.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                               vys_page.get_offset():vys_page.get_query_limit()]

        employeetype_list_data = NWisefinList()
        for sub in employeetypelist:
            employeetypedata = EmployeementtypeResponse()
            employeetypedata.set_id(sub.id)
            employeetypedata.set_emptype(sub.emptype)
            employeetypedata.set_emptypedesc(sub.emptypedesc)
            employeetypedata.set_empcat_id(sub.empcat_id)
            employeetypedata.set_empcat(sub.empcat)
            employeetypedata.name=sub.empcat.empcat+"-"+sub.emptype
            employeetype_list_data.append(employeetypedata)

            vpage = NWisefinPaginator(employeetypelist, vys_page.get_index(), 10)
            employeetype_list_data.set_pagination(vpage)
        return employeetype_list_data

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changed
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.DESIGNATION)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
