import traceback

from django.db import IntegrityError
from django.db.models import Q
from masterservice.data.response.clientcoderesponse import ClientcodeResponse
from masterservice.models import Businessproductcode, Clientcode
from django.utils import timezone

from masterservice.util.masterutil import MasterStatus
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
#test
# businessproduct
class ClientcodeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_clientcode(self, client_obj, emp_id):
        if not client_obj.get_id() is None:
            try:
                logger.error('CLIENTCODE: Clientcode Update Started')
                client = Clientcode.objects.using(self._current_app_schema()).filter(id=client_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                 client_code=client_obj.get_client_code(),
                                                                                 client_name=client_obj.get_client_name(),
                                                                                 rm_name=client_obj.get_rm_name(),
                                                                                 entity=client_obj.get_entity(),
                                                                                 updated_by=emp_id,
                                                                                 updated_date=timezone.now())
                client = Clientcode.objects.using(self._current_app_schema()).get(id=client_obj.get_id(),entity_id=self._entity_id())
                logger.error('CLIENTCODE: Clientcode Update Success' + str(client))
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.UPDATE_MESSAGE)
                return data
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Clientcode.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
                error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('CLIENTCODE: Clientcode Creation Started')
                data_len = Clientcode.objects.using(self._current_app_schema()).filter(
                    client_name=client_obj.get_client_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                data_len = Clientcode.objects.using(self._current_app_schema()).filter(
                    client_code=client_obj.get_client_code()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_CODE)
                    return error_obj

                client = Clientcode.objects.using(self._current_app_schema()).create(
                                                     # client_code=client_obj.get_client_code(),
                                                     client_name=client_obj.get_client_name(),
                                                     rm_name=client_obj.get_rm_name(),
                                                     entity=client_obj.get_entity(),
                                                     created_by=emp_id,
                                                     created_date=timezone.now(),
                                                     entity_id=self._entity_id()
                                                     )
                try:
                    max_cat_code = Clientcode.objects.using(self._current_app_schema()).filter(client_code__icontains='BCC').order_by('-client_code')[
                        0].client_code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "BCC" + str(new_rnsl).zfill(1)
                client.client_code = code
                client.save()
                logger.error('CLIENTCODE: Clientcode Creation Success' + str(client))
                data = NWisefinSuccess()
                data.set_status(SuccessStatus.SUCCESS)
                data.set_message(SuccessMessage.CREATE_MESSAGE)
                return data
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
        # data_obj = ClientcodeResponse()
        # data_obj.set_id(client.id)
        # data_obj.set_client_code(client.client_code)
        # data_obj.set_client_name(client.client_name)
        # return data_obj


    def fetch_clientlist(self,request,vys_page):

        conditions = Q(entity_id=self._entity_id())
        if "code" in request.GET:
            conditions &= Q(client_code__icontains=request.GET.get("code"))
        if "name" in request.GET:
            conditions &= Q(client_name__icontains=request.GET.get("name"))

        clientlist = Clientcode.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(clientlist)
        if list_length >= 0:
            clientcode_data = NWisefinList()
            for clientobj in clientlist:
                client_data = ClientcodeResponse()
                client_data.set_id(clientobj.id)
                client_data.set_client_code(clientobj.client_code)
                client_data.set_client_name(clientobj.client_name)
                client_data.set_status(clientobj.status)
                client_data.Entity = clientobj.entity
                try:
                    from utilityservice.service.api_service import ApiService
                    common_serv = ApiService(self._scope())
                    client_name = common_serv.get_emp_id(request, clientobj.rm_name)
                    client_data.RM_Name = client_name['name']
                except:
                    client_data.RM_Name = ""
                clientcode_data.append(client_data)
            vpage = NWisefinPaginator(clientlist, vys_page.get_index(), 10)
            clientcode_data.set_pagination(vpage)
            return clientcode_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid_Client_id")
            error_obj.set_description("Invalid client id or code")
            return error_obj
    def fetch_clientcode_download(self,request):
        clientlist = Clientcode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
        list_length = len(clientlist)
        if list_length >= 0:
            clientcode_data = NWisefinList()
            for clientobj in clientlist:
                client_data = ClientcodeResponse()

                client_data.Client_Code = clientobj.client_code
                client_data.Client_Name = clientobj.client_name
                status = MasterStatus()
                if clientobj.status == status.Active:
                    client_data.Status = status.Active_VALUE
                if clientobj.status == status.Inactive:
                    client_data.Status = status.Inactive_VALUE
                client_data.Entity = clientobj.entity
                try:
                    from utilityservice.service.api_service import ApiService
                    common_serv = ApiService(self._scope())
                    client_name = common_serv.get_emp_id(request,clientobj.rm_name)
                    client_data.RM_Name = client_name['name']
                except:
                    client_data.RM_Name = ""
                clientcode_data.append(client_data)
            return clientcode_data
        else:
            logger.error('ERROR_Client_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code("Invalid_Client_id")
            error_obj.set_description("Invalid client id or code")
            return error_obj

    def frequent_clientlist_ta(self,vys_page,query,frequent_client_data):
        from itertools import chain
        frequent_clientlist=None
        if frequent_client_data is not None:
            frequent_clientlist = Clientcode.objects.using(self._current_app_schema()).filter(id__in=frequent_client_data).exclude(client_name="NOT APPLICABLE")
            frq_cli_len=len(frequent_clientlist)
        else:
            frq_cli_len=0
            frequent_client_data=[]



        conditions = Q(status=1)&Q(entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(client_name__icontains=query)
        clientlist = Clientcode.objects.using(self._current_app_schema()).filter(conditions).exclude(Q(id__in=frequent_client_data)|Q(client_name="NOT APPLICABLE"))[
                         max(0,(vys_page.get_offset()-frq_cli_len)):(vys_page.get_query_limit())]
        list_length = len(clientlist)
        if list_length >= 0:
            clientcode_data = NWisefinList()
            # if frq_cli_len>0 :
            #     # if len(frequent_clientlist) > 0:
            #     for each_client in frequent_clientlist:
            #         clientcode_data.append(each_client)
            if frequent_clientlist is not None:
                clientlist_combined=list(chain(frequent_clientlist,clientlist))
            else:
                clientlist_combined=clientlist
            for clientobj in clientlist_combined:
                client_data = ClientcodeResponse()
                client_data.set_id(clientobj.id)
                client_data.set_client_code(clientobj.client_code)
                client_data.set_client_name(clientobj.client_name)
                clientcode_data.append(client_data)
            vpage = NWisefinPaginator(clientlist, vys_page.get_index(), 10)
            while len(clientcode_data.data) > vpage.limit:
                clientcode_data.set_pagination(vpage)
            clientcode_data.set_pagination(vpage)
            return clientcode_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid_Client_id")
            error_obj.set_description("Invalid client id or code")
            return error_obj

    def fetch_clientcode(self, client_id):
        try:
            client_var = Clientcode.objects.using(self._current_app_schema()).get(id=client_id,entity_id=self._entity_id())
            client_data = ClientcodeResponse()
            client_data.set_id(client_var.id)
            client_data.set_client_code(client_var.client_code)
            client_data.set_client_name(client_var.client_name)
            return client_data
        except Clientcode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid data")
            error_obj.set_description("Invalid client id")
            return error_obj
    def fetch_clientcode_arr(self, client_id):
        try:
            client_var = Clientcode.objects.using(self._current_app_schema()).filter(id__in=client_id,entity_id=self._entity_id()).values("client_name","client_code","id")
            return client_var
        except Clientcode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid data")
            error_obj.set_description("Invalid client id")
            return error_obj

    def clientcode_activate_inactivate(self, request,client_obj):

        if (int(client_obj.status) == 0):

            clientcode_data = Clientcode.objects.using(self._current_app_schema()).filter(id=client_obj.id).update(
                status=1)
        else:
            clientcode_data = Clientcode.objects.using(self._current_app_schema()).filter(id=client_obj.id).update(
                status=0)
        clientcode_var = Clientcode.objects.using(self._current_app_schema()).get(id=client_obj.id)
        data = ClientcodeResponse()
        data.set_status(clientcode_var.status)
        status = clientcode_var.status

        data.set_id(clientcode_var.id)

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
