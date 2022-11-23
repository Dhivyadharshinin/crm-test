from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now
from masterservice.data.response.bsproductresponse import BusinessProductResponse
from masterservice.models import Businessproductcode
from django.utils import timezone

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
#test
# businessproduct
class BsproductService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bsproduct(self, bsproduct_obj, emp_id):
        if not bsproduct_obj.get_id() is None:
            # try:
                logger.error('BUSINESSPRODUCTCODE: Businessproductcode Update Started')
                bsproduct = Businessproductcode.objects.using(self._current_app_schema()).filter(id=bsproduct_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                 bsproduct_code=bsproduct_obj.get_bsproduct_code(),
                                                                                 bsproduct_name=bsproduct_obj.get_bsproduct_name(),
                                                                                 updated_by=emp_id,
                                                                                 updated_date=timezone.now())
                bsproduct = Businessproductcode.objects.using(self._current_app_schema()).get(id=bsproduct_obj.get_id(),entity_id=self._entity_id())
                logger.error('BUSINESSPRODUCTCODE: Businessproductcode Update Success' + str(bsproduct))
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except Businessproductcode.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        else:
            # try:
                logger.error('BUSINESSPRODUCTCODE: Businessproductcode Creation Started')
                bsproduct = Businessproductcode.objects.using(self._current_app_schema()).create(
                                                     bsproduct_code=bsproduct_obj.get_bsproduct_code(),
                                                     bsproduct_name=bsproduct_obj.get_bsproduct_name(),
                                                     created_by=emp_id,
                                                     created_date=timezone.now(),
                                                     entity_id=self._entity_id()
                                                     )
                logger.error('BUSINESSPRODUCTCODE: Businessproductcode Creation Success' + str(bsproduct))
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
        data_obj = BusinessProductResponse()
        data_obj.set_id(bsproduct.id)
        data_obj.set_bsproduct_code(bsproduct.bsproduct_code)
        data_obj.set_bsproduct_name(bsproduct.bsproduct_name)
        return data_obj

    def fetch_bsproductlist(self,vys_page,query):
        conditions = Q(status=1)&Q(entity_id=self._entity_id())
        if query is not None:
            conditions &= Q(bsproduct_name__icontains=query)
        bsproductlist = Businessproductcode.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(bsproductlist)
        if list_length >= 0:
            bsproduct_data = NWisefinList()
            for bsproductobj in bsproductlist:
                bsprod_data = BusinessProductResponse()
                bsprod_data.set_id(bsproductobj.id)
                bsprod_data.set_bsproduct_code(bsproductobj.bsproduct_code)
                bsprod_data.set_bsproduct_name(bsproductobj.bsproduct_name)
                bsproduct_data.append(bsprod_data)
            vpage = NWisefinPaginator(bsproductlist, vys_page.get_index(), 10)
            bsproduct_data.set_pagination(vpage)
            return bsproduct_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid_Client_id")
            error_obj.set_description("Invalid client id or code")
            return error_obj

    def fetch_bsproductcode(self, client_id):
        try:
            client_var = Businessproductcode.objects.using(self._current_app_schema()).get(id=client_id,entity_id=self._entity_id())
            client_data = BusinessProductResponse()
            client_data.set_id(client_var.id)
            client_data.set_bsproduct_code(client_var.bsproduct_code)
            client_data.set_bsproduct_name(client_var.bsproduct_name)
            return client_data
        except Businessproductcode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid data")
            error_obj.set_description("Invalid client id")
            return error_obj
