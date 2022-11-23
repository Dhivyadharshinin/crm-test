from django.db import IntegrityError

from masterservice.models import Country
from masterservice.data.response.countryresponse import CountryResponse
from masterservice.service.Codegenerator import CodeGen
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CountryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_country(self, country_obj, user_id):
        if not country_obj.get_id() is None:
            try:
                country_update = Country.objects.using(self._current_app_schema()).filter(id=country_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    # code =country_obj.get_code (),
                    name=country_obj.get_name(),
                    updated_by=user_id, updated_date=timezone.now())

                country = Country.objects.using(self._current_app_schema()).get(id=country_obj.get_id(),
                                                                                entity_id=self._entity_id())

                country_auditdata = {'id': country_obj.get_id(),
                                     # 'code': country_obj.get_code(),
                                     'name': country_obj.get_name(),
                                     'updated_date': timezone.now(),
                                     'updated_by': user_id}
                self.audit_function(country_auditdata, user_id, country.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Country.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_country_ID)
                error_obj.set_description(ErrorDescription.INVALID_country_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                country = Country.objects.using(self._current_app_schema()).create(  # code =country_obj.get_code (),
                    name=country_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id())

                try:
                    max_cat_code = Country.objects.using(self._current_app_schema()).filter(code__icontains='CO').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CO" + str(new_rnsl).zfill(3)# code = "ISCT" + str(country.id)
                country.code = code
                country.save()

                self.audit_function(country, user_id, country.id, ModifyStatus.create)

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

        country_data = CountryResponse()
        country_data.set_id(country.id)
        country_data.set_code(country.code)
        country_data.set_name(country.name)

        return country_data

    def fetch_country_list(self, user_id, vys_page):
        countrylist = Country.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
            'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(countrylist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_country_ID)
            error_obj.set_description(ErrorDescription.INVALID_country_ID)
            return error_obj
        else:
            country_list_data = NWisefinList()
            for country in countrylist:
                country_data = CountryResponse()
                country_data.set_id(country.id)
                country_data.set_code(country.code)
                country_data.set_name(country.name)
                country_list_data.append(country_data)
                vpage = NWisefinPaginator(countrylist, vys_page.get_index(), 10)
                country_list_data.set_pagination(vpage)
            return country_list_data

    def fetch_country(self, country_id, user_id):
        try:
            country = Country.objects.using(self._current_app_schema()).get(id=country_id, entity_id=self._entity_id())
            country_data = CountryResponse()
            country_data.set_id(country.id)
            country_data.set_code(country.code)
            country_data.set_name(country.name)
            return country_data

        except country.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_country_ID)
            error_obj.set_description(ErrorDescription.INVALID_country_ID)
            return error_obj

    def delete_country(self, country_id, user_id):
        country = Country.objects.using(self._current_app_schema()).filter(id=country_id,
                                                                           entity_id=self._entity_id()).delete()
        self.audit_function(country, user_id, country_id, ModifyStatus.delete)

        if country[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_country_ID)
            error_obj.set_description(ErrorDescription.INVALID_country_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

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
        audit_obj.set_relreftype(MasterRefType.COUNTRY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def country_sync_create(self,country_name,Entity):
        ctry = Country.objects.using(self._current_app_schema()).filter(entity_id=Entity,name__iexact=country_name)
        if len(ctry) > 0:
            ctry_id = ctry[0].id
            return ctry_id
        else:
            return 0