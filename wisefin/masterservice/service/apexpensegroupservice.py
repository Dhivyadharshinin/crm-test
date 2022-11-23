import traceback

from django.db import IntegrityError

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.models.mastermodels import APexpensegroup
from django.utils import timezone
from django.db.models import Q
from masterservice.data.response.expensegroupresponse import ExpenseGroupresponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class ExpenseGroupservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_expensegrp(self, expensegrp_obj, user_id):
        if not expensegrp_obj.get_id() is None:
            try:
                logger.error('APEXPENSEGROUP: APexpensegroup Update Started')
                expensegrp_update = APexpensegroup.objects.using(self._current_app_schema()).filter(
                    id=expensegrp_obj.get_id(), entity_id=self._entity_id()).update(name=expensegrp_obj.get_name(),
                                                                                    description=expensegrp_obj.get_description(),
                                                                                    updated_by=user_id,
                                                                                    updated_date=timezone.now())
                expensegrp = APexpensegroup.objects.using(self._current_app_schema()).get(id=expensegrp_obj.get_id(),
                                                                                          entity_id=self._entity_id())
                logger.error('APEXPENSEGROUP: APexpensegroup Update Success' + str(expensegrp_update))
                expensegrp_auditdata = {'id': expensegrp_obj.get_id(), 'name': expensegrp_obj.get_name(),
                                        'description': expensegrp_obj.get_description(), 'updated_by': user_id,
                                        'updated_date': timezone.now()}
                self.audit_function(expensegrp_auditdata, user_id, expensegrp.id, ModifyStatus.update)


            except IntegrityError as error:
                logger.error('ERROR_APexpensegroup_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except APexpensegroup.DoesNotExist:
                logger.error('ERROR_APexpensegroup_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APexpenseGroup_ID)
                error_obj.set_description(ErrorDescription.INVALID_APexpenseGroup_ID)
                return error_obj
            except:
                logger.error('ERROR_APexpensegroup_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('APEXPENSEGROUP: APexpensegroup Creation Started')
                data_len = APexpensegroup.objects.using(self._current_app_schema()).filter(
                    name=expensegrp_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                expensegrp = APexpensegroup.objects.using(self._current_app_schema()).create(
                    name=expensegrp_obj.get_name(), description=expensegrp_obj.get_description(),
                    created_by=user_id, entity_id=self._entity_id())
                expensegrp.save()
                self.audit_function(expensegrp, user_id, expensegrp.id, ModifyStatus.create)
                logger.error('APEXPENSEGROUP: APexpensegroup Creation Success' + str(expensegrp))
            except IntegrityError as error:
                logger.error('ERROR_APexpensegroup_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_APexpensegroup_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        expensegrp_data = ExpenseGroupresponse()
        expensegrp_data.set_id(expensegrp.id)
        expensegrp_data.set_name(expensegrp.name)
        expensegrp_data.set_description(expensegrp.description)

        return expensegrp_data

    def fetch_expensegrp_search_list(self, query, vys_page):
        try:
            condition =  Q(entity_id=self._entity_id())
            if query != None:
                condition &= Q(name__icontains=query)
            expensegrp_obj = APexpensegroup.objects.using(self._current_app_schema()).filter(condition).values('id', 'name',
                                                                                                               'description','status')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(expensegrp_obj)
            pro_list = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for i in expensegrp_obj:
                    expensegrp_response = ExpenseGroupresponse()
                    expensegrp_response.set_id(i["id"])
                    expensegrp_response.set_name(i["name"])
                    expensegrp_response.set_description(i['description'])
                    expensegrp_response.set_status(i['status'])
                    pro_list.append(expensegrp_response)
            vpage = NWisefinPaginator(expensegrp_obj, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
            return pro_list
        except:
            logger.error('ERROR_APexpensegroup_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_APexpenseGroup_ID)
            error_obj.set_description(ErrorDescription.INVALID_APexpenseGroup_ID)
            return error_obj

    def apexpense_activate_inactivate(self, request, apsec_obj):

        if (int(apsec_obj.status) == 0):

            apsector_data = APexpensegroup.objects.using(self._current_app_schema()).filter(id=apsec_obj.id).update(
                status=1)
        else:
            apsector_data = APexpensegroup.objects.using(self._current_app_schema()).filter(id=apsec_obj.id).update(
                status=0)
        apsector_var = APexpensegroup.objects.using(self._current_app_schema()).get(id=apsec_obj.id)
        data = ExpenseGroupresponse()
        data.set_status(apsector_var.status)
        status = apsector_var.status
        data.set_id(apsector_var.id)

        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
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
        audit_obj.set_relreftype(MasterRefType.CATEGORY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
