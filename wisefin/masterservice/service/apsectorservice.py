import traceback

from django.db import IntegrityError

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from masterservice.models.mastermodels import Apsector
from django.utils import timezone
from django.db.models import Q
from masterservice.data.response.apsectorresponse import Sectorresponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus


class SectorService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_sector(self, Sector_obj, user_id):
        if not Sector_obj.get_id() is None:
            try:
                logger.error('APSECTOR: Apsector Update Started')
                sector_update = Apsector.objects.using(self._current_app_schema()).filter(id=Sector_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    name=Sector_obj.get_name(),
                    description=Sector_obj.get_description(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                sector = Apsector.objects.using(self._current_app_schema()).get(id=Sector_obj.get_id(),
                                                                                entity_id=self._entity_id())
                logger.error('APSECTOR: Apsector Update Success' + str(sector_update))
                sector_auditdata = {'id': Sector_obj.get_id(), 'name': Sector_obj.get_name(),
                                    'description': Sector_obj.get_description(), 'updated_by': user_id,
                                    'updated_date': timezone.now()}
                self.audit_function(sector_auditdata, user_id, sector.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_Apsector_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Apsector.DoesNotExist:
                logger.error('ERROR_Apsector_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APSECTOR_ID)
                error_obj.set_description(ErrorDescription.INVALID_APSECTOR_ID)
                return error_obj
            except:
                logger.error('ERROR_Apsector_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('APSECTOR: Apsector Creation Started')
                sector = Apsector.objects.using(self._current_app_schema()).create(name=Sector_obj.get_name(),
                                                                                   description=Sector_obj.get_description(),
                                                                                   created_by=user_id,
                                                                                   entity_id=self._entity_id())
                sector.save()
                self.audit_function(sector, user_id, sector.id, ModifyStatus.create)
                logger.error('APSECTOR: Apsector Creation Success' + str(sector))

            except IntegrityError as error:
                logger.error('ERROR_Apsector_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Apsector_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        sector_data = Sectorresponse()
        sector_data.set_id(sector.id)
        sector_data.set_name(sector.name)
        sector_data.set_description(sector.description)

        # return sector_data
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data

    def fetch_sector_search_list(self, query, vys_page):
        try:
            condition = Q(entity_id=self._entity_id())
            if query != None:
                condition &= Q(name__icontains=query)
            sector_obj = Apsector.objects.using(self._current_app_schema()).filter(condition).values('id', 'name',
                                                                                                     'description','status')[
                         vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(sector_obj)
            pro_list = NWisefinList()

            for i in sector_obj:
                sector_response = Sectorresponse()
                sector_response.set_id(i["id"])
                sector_response.set_name(i["name"])
                sector_response.set_description(i['description'])
                sector_response.set_status(i['status'])
                pro_list.append(sector_response)
            vpage = NWisefinPaginator(sector_obj, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
            return pro_list
        except:
            logger.error('ERROR_Apsector_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_APSECTOR_ID)
            error_obj.set_description(ErrorDescription.INVALID_APSECTOR_ID)
            return error_obj


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

    def apsector_activate_inactivate(self, request, apsec_obj):

        if (int(apsec_obj.status) == 0):

            apsector_data = Apsector.objects.using(self._current_app_schema()).filter(id=apsec_obj.id).update(
                status=1)
        else:
            apsector_data = Apsector.objects.using(self._current_app_schema()).filter(id=apsec_obj.id).update(
                status=0)
        apsector_var = Apsector.objects.using(self._current_app_schema()).get(id=apsec_obj.id)
        data = Sectorresponse()
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
