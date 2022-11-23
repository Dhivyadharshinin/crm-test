import traceback
from django.db import IntegrityError
from django.db.models import Q

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.data.response.apexpenseresponse import APexpenseResponse
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now=str(now)
from masterservice.models import APexpense


class APexpenseService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_expense(self, expense_obj, emp_id):
        if not expense_obj.get_id() is None:
            try:
                logger.error('APEXPENSE: APexpense Update Started')
                expense_var = APexpense.objects.using(self._current_app_schema()).filter(id=expense_obj.get_id(),
                                                                                         entity_id=self._entity_id()).update(
                    head=expense_obj.get_head(),
                    linedesc=expense_obj.get_linedesc(),
                    sch16=expense_obj.get_sch16(),
                    sch16desc=expense_obj.get_sch16desc(),
                    group=expense_obj.get_group(),
                    exp_grp_id=expense_obj.get_exp_grp_id(),
                    # code=expense_obj.get_code(),
                    updated_by=emp_id,
                    updated_date=now)
                expense = APexpense.objects.using(self._current_app_schema()).get(id=expense_obj.get_id(),
                                                                                  entity_id=self._entity_id())
                logger.error('APEXPENSE: APexpense Update Success' + str(expense_var))
                expense_auditdata = {'id': expense_obj.get_id(), "code": expense_obj.get_code(),
                                     'head': expense_obj.get_head(),
                                     'linedesc': expense_obj.get_linedesc(),
                                     'sch16': expense_obj.get_sch16(),
                                     'sch16desc': expense_obj.get_sch16desc(),
                                     'group': expense_obj.get_group(),
                                     'updated_date': now,
                                     'updated_by': emp_id}
                self.audit_function(expense_auditdata, emp_id, expense.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_APexpense_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except APexpense.DoesNotExist:
                logger.error('ERROR_APexpense_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APexpense_ID)
                error_obj.set_description(ErrorDescription.INVALID_APexpense_ID)
                return error_obj
            except:
                logger.error('ERROR_APexpense_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            condition = Q(head__exact=expense_obj.get_head()) & Q(entity_id=self._entity_id())
            expense = APexpense.objects.using(self._current_app_schema()).filter(condition)
            if len(expense) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('APEXPENSE: APexpense Creation Started')
                expense = APexpense.objects.using(self._current_app_schema()).create(head=expense_obj.get_head(),
                                                                                     # code=expense_obj.get_code(),
                                                                                     exp_grp_id=expense_obj.get_exp_grp_id(),
                                                                                     linedesc=expense_obj.get_linedesc(),
                                                                                     sch16=expense_obj.get_sch16(),
                                                                                     sch16desc=expense_obj.get_sch16desc(),
                                                                                     group=expense_obj.get_group(),
                                                                                     created_by=emp_id,
                                                                                     entity_id=self._entity_id())
                try:
                    max_cat_code = APexpense.objects.using(self._current_app_schema()).filter(code__icontains='EXP').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl=0
                new_rnsl = rnsl + 1
                code = "EXP" + str(new_rnsl).zfill(3)
                expense.code=code
                expense.save()
                self.audit_function(expense, emp_id, expense.id, ModifyStatus.create)
                logger.error('APEXPENSE: APexpense Creation Success' + str(expense))
            except IntegrityError as error:
                logger.error('ERROR_APexpense_Create_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_APexpense_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        expensedata = APexpenseResponse()
        expensedata.set_id(expense.id)
        expensedata.set_head(expense.head)
        expensedata.set_linedesc(expense.linedesc)
        expensedata.set_group(expense.group)
        expensedata.set_sch16(expense.sch16)
        expensedata.set_sch16desc(expense.sch16desc)
        expensedata.set_code(expense.code)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def delete_expense(self, expense_id, emp_id):
        expense = APexpense.objects.using(self._current_app_schema()).filter(id=expense_id,
                                                                             entity_id=self._entity_id()).delete()
        self.audit_function(expense, emp_id, expense_id, ModifyStatus.delete)
        if expense[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_APexpense_ID)
            error_obj.set_description(ErrorDescription.INVALID_APexpense_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_expense(self, expense_id):
        try:
            print("fdsa")
            expense = APexpense.objects.using(self._current_app_schema()).get(id=expense_id,
                                                                              entity_id=self._entity_id())
            expensedata = APexpenseResponse()
            expensedata.set_id(expense.id)
            expensedata.set_head(expense.head)
            expensedata.set_linedesc(expense.linedesc)
            expensedata.set_group(expense.group)
            expensedata.set_sch16(expense.sch16)
            expensedata.set_sch16desc(expense.sch16desc)
            expensedata.set_code(expense.code)
            return expensedata
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_APexpense_ID)
            error_obj.set_description(ErrorDescription.INVALID_APexpense_ID)
            return error_obj

    def fetch_expense_list(self, vys_page):
        expense_list = APexpense.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
            'created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(expense_list)
        expense_list_data = NWisefinList()
        if list_length > 0:
            for expense in expense_list:
                expensedata = APexpenseResponse()
                expensedata.set_id(expense.id)
                expensedata.set_head(expense.head)
                expensedata.set_linedesc(expense.linedesc)
                expensedata.set_group(expense.group)
                expensedata.set_sch16(expense.sch16)
                expensedata.set_sch16desc(expense.sch16desc)
                expensedata.set_code(expense.code)
                expense_list_data.append(expensedata)
            vpage = NWisefinPaginator(expense_list, vys_page.get_index(), 10)
            expense_list_data.set_pagination(vpage)
        return expense_list_data

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
        audit_obj.set_relreftype(MasterRefType.Apexpense)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def search_expense(self, query, vys_page):
        condition = Q(entity_id=self._entity_id())
        if query is None:
            condition &= Q(status=1)
        else:
            condition &= Q(head__icontains=query)
        expenselist = APexpense.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(expenselist)
        vlist_data = NWisefinList()
        if list_length > 0:
            for expense in expenselist:
                expense_data = APexpenseResponse()
                expense_data.set_id(expense.id)
                expense_data.set_head(expense.head)
                vlist_data.append(expense_data)
            vpage = NWisefinPaginator(expenselist, vys_page.get_index(), 10)
            vlist_data.set_pagination(vpage)
        return vlist_data

    def apexpence_code_update(self, json_data):
        codition = (Q(head=json_data['expense_head'],
                      linedesc=json_data['expense_linedesc'],
                      sch16=json_data['expense_sch16'],
                      sch16desc=json_data['expense_sch16desc'],
                      group=json_data['expense_group'])) & Q(entity_id=self._entity_id())
        expense_var = APexpense.objects.using(self._current_app_schema()).filter(codition).update(
            code=json_data['expense_code'])

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj
