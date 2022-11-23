import traceback
from django.db import IntegrityError
from django.utils.timezone import now

from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.models import TaxRate, SubTax, AuditChecklist
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.taxrateresponse import TaxRateResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q

class AuditChecklistService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_audit_check_list(self, checklist_obj, user_id):
        if not checklist_obj.get_id() is None:
            try:
                logger.error('AUDITCHECKLIST: Audit_check_list Update Started')
                audit_check_update = AuditChecklist.objects.using(self._current_app_schema()).filter(id=checklist_obj.get_id()).update(
                    type=checklist_obj.get_type(),
                    name=checklist_obj.get_name(),
                    group=checklist_obj.get_group(),
                    question=checklist_obj.get_question(),
                    solution=checklist_obj.get_solution(),
                    updated_by=user_id,updated_date=now())

                audit_check_list = AuditChecklist.objects.using(self._current_app_schema()).get(id=checklist_obj.get_id())
                check_list_auditdata = {'id': checklist_obj.get_id(),
                                   'type': checklist_obj.get_type(),
                                   'name': checklist_obj.get_name(),
                                   'question': checklist_obj.get_question(),
                                   'solution': checklist_obj.get_solution(),
                                   'group': checklist_obj.get_group(),
                                   'updated_date': now(),
                                   'updated_by': user_id}
                self.audit_function(check_list_auditdata, user_id, audit_check_list.id, ModifyStatus.update)
                logger.error('AUDITCHECKLIST: Audit_Check_list Update Success' + str(audit_check_update))

            except IntegrityError as error:
                logger.error('ERROR_Audit_Check_list_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except AuditChecklist.DoesNotExist:
                logger.error('ERROR_Audit_Check_list_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code('INVALID_Audit_check_list_ID')
                error_obj.set_description('INVALID_Audit_check_list_ID')
                return error_obj
            except:
                logger.error('ERROR_Audit_Check_list_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('AUDITCHECKLIST: Audit_check_list Creation Started')
                check_list = AuditChecklist.objects.using(self._current_app_schema()).create(
                    type=checklist_obj.get_rate(),
                    name=checklist_obj.get_name(),
                    group=checklist_obj.get_group(),
                    question=checklist_obj.get_question(),
                    solution=checklist_obj.get_solution(),
                    updated_by=user_id, updated_date=now())


                try:
                    audit_check_list = AuditChecklist.objects.using(self._current_app_schema()).filter(code__icontains='CH').order_by('-code')[0].code
                    rnsl = int(audit_check_list[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CH" + str(new_rnsl).zfill(3)
                check_list.code = code
                check_list.save()
                self.audit_function(check_list, user_id, check_list.id, ModifyStatus.create)
                logger.error('AUDITCHECKLIST: Audit_check_list Creation Success' + str(check_list))
            except IntegrityError as error:
                logger.error('ERROR_Audit_check_list_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Audit_check_list_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj



        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.AUDITCHECKLIST)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
