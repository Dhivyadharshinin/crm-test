import json
import traceback

import django

from django.db import IntegrityError
from django.db.models import Q
from masterservice.models import Courier
from masterservice.data.response.courierresponse import CourierResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.addressservice import AddressService
from masterservice.service.contactservice import ContactService
from masterservice.util.masterutil import ModifyStatus, Code_Gen_Type, Code_Gen_Value
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList

from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from datetime import datetime

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()


class CourierService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_courier(self, courier_obj, add_id, cont_id, user_id):
        if not courier_obj.get_id() is None:
            try:
                logger.error('COURIER: Courier Update Started')

                Courier_var = Courier.objects.using(self._current_app_schema()).filter(id=courier_obj.get_id(),
                                                                                       entity_id=self._entity_id()).update(
                    # code=courier_obj.get_code(),
                    name=courier_obj.get_name(),
                    type=courier_obj.get_type(),
                    contactperson=courier_obj.get_contactperson(),
                    address_id=add_id,
                    contact_id=cont_id,
                    updated_date=now,
                    updated_by=user_id)

                Courier_var = Courier.objects.using(self._current_app_schema()).get(id=courier_obj.get_id(),
                                                                                    entity_id=self._entity_id())
                logger.error('COURIER: Courier Update Success' + str(Courier_var))
            except IntegrityError as error:
                logger.error('ERROR_Courier_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Courier.DoesNotExist:
                logger.error('ERROR_Courier_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_Courier_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            condition = Q(name__exact=courier_obj.get_name()) & Q(entity_id=self._entity_id())
            courier = Courier.objects.using(self._current_app_schema()).filter(condition)
            if len(courier) > 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                return error_obj
            try:
                logger.error('COURIER: Courier Creation Started')
                Courier_var = Courier.objects.using(self._current_app_schema()).create(  # code=courier_obj.get_code(),
                    name=courier_obj.get_name(),
                    type=courier_obj.get_type(),
                    contactperson=courier_obj.get_contactperson(),
                    address_id=add_id, all_branch=courier_obj.get_all_branch(),
                    contact_id=cont_id, created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = Courier.objects.using(self._current_app_schema()).filter(code__icontains='COU').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "COU" + str(new_rnsl).zfill(3)# code = "ISCT" + str(Courier_res)
                Courier_var.code = code
                Courier_var.save()
                logger.error('COURIER: Courier Creation Success' + str(Courier_var))
            except IntegrityError as error:
                logger.error('ERROR_Courier_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Courier_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        courier_data = CourierResponse()
        courier_data.set_id(Courier_var.id)
        courier_data.set_code(Courier_var.code)
        courier_data.set_name(Courier_var.name)
        courier_data.set_type(Courier_var.type)
        courier_data.set_contactperson(Courier_var.contactperson)
        return courier_data

    def fetch_courier_list(self, vys_page, user_id, query):

        if query is None:
            courierlist = Courier.objects.using(self._current_app_schema()).filter(status=1,
                                                                                   entity_id=self._entity_id()).select_related(
                'contact')[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(status=1) & Q(entity_id=self._entity_id())
            courierlist = Courier.objects.using(self._current_app_schema()).filter(condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(courierlist)
        courier_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for courierobj in courierlist:
                address_service = AddressService(self._scope())  # changed
                contact_service = ContactService(self._scope())  # changed
                courier_data = CourierResponse()
                courier_data.set_id(courierobj.id)
                courier_data.set_code(courierobj.code)
                courier_data.set_name(courierobj.name)
                courier_data.set_type(courierobj.type)
                courier_data.set_contactperson(courierobj.contactperson)
                if courierobj.contact_id == None:
                    courier_data.set_contact_id(None)
                elif courierobj.contact_id != None:
                    courier_data.set_contact_id(contact_service.fetchcontact(courierobj.contact_id))
                if courierobj.address_id == None:
                    courier_data.set_address_id(None)
                elif courierobj.address_id != None:
                    courier_data.set_address_id(address_service.fetch_address(courierobj.address_id, user_id))
                courier_list_data.append(courier_data)

            vpage = NWisefinPaginator(courierlist, vys_page.get_index(), 10)
            courier_list_data.set_pagination(vpage)
        return courier_list_data

    def fetchcourier(self, courier_id, user_id):
        try:
            courier_var = Courier.objects.using(self._current_app_schema()).get(id=courier_id,
                                                                                entity_id=self._entity_id())
            courier_data = CourierResponse()
            addre_serv = AddressService(self._scope())  # changed
            contact_serv = ContactService(self._scope())  # changed
            courier_data.set_id(courier_var.id)
            courier_data.set_code(courier_var.code)
            courier_data.set_name(courier_var.name)
            courier_data.set_type(courier_var.type)
            courier_data.set_contactperson(courier_var.contactperson)
            if courier_var.contact_id == None:
                courier_data.set_contact_id(None)
            elif courier_var.contact_id != None:
                courier_data.set_contact_id(contact_serv.fetchcontact(courier_var.contact_id))
            if courier_var.address_id == None:
                courier_data.set_address_id(None)
            elif courier_var.address_id != None:
                courier_data.set_address_id(addre_serv.fetch_address(courier_var.address_id, user_id))
            return courier_data
        except Courier.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COURIER_ID)
            error_obj.set_description(ErrorDescription.INVALID_COURIER_ID)
            return error_obj

    def deletecourier(self, courier_id, user_id):
        Courier_var = Courier.objects.using(self._current_app_schema()).filter(id=courier_id,
                                                                               entity_id=self._entity_id()).update(
            status=ModifyStatus.delete,
            updated_by=user_id,
            updated_date=now)
        if Courier_var == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_COURIER_ID)
            error_obj.set_description(ErrorDescription.INVALID_COURIER_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_courier(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = (Q(name__icontains=query) | Q(code__icontains=query)) & Q(entity_id=self._entity_id())
        courierList = None
        if condition is not None:
            courierList = Courier.objects.using(self._current_app_schema()).filter(
                condition).values('id', 'name', 'code')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            courierList = Courier.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).values('id', 'name', 'code')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for cou in courierList:
            courier_res = CourierResponse()
            disp_name = '(' + cou['code'] + ') ' + cou['name']
            courier_res.set_name(disp_name)
            courier_res.set_id(cou['id'])
            courier_res.set_name(cou['name'])
            vlist.append(courier_res)
        vpage = NWisefinPaginator(courierList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    # dropdown inward
    def courier_search(self, query, vys_page):
        if query is None:
            condition = Q(status=1)
        else:
            condition = Q(name__icontains=query) & Q(status=1)
        courierList = Courier.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
                      vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        list_length = len(courierList)
        if list_length > 0:
            for cou in courierList:
                courier_res = CourierResponse()
                courier_res.set_id(cou['id'])
                courier_res.set_name(cou['name'])
                courier_res.set_code(cou['code'])
                vlist.append(courier_res)
            vpage = NWisefinPaginator(courierList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

    def fetch_courierdata(self, courier_id):
        courier = Courier.objects.using(self._current_app_schema()).get(id=courier_id)
        cou_data = {"id": courier.id, "code": courier.code, "name": courier.name}
        return cou_data


    #summarysearch inward
    def courier_summarysearch(self, query, vys_page):
        if query is None:
            condition = Q(status=1)
        else:
            print(query)
            condition = Q(name__icontains=query["name"]) \
                        & Q(code__icontains=query["code"]) \
                        & Q(contactperson__icontains=query["contact_person"]) \
                        & Q(status=1)
        courierlist = Courier.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                      vys_page.get_offset(): vys_page.get_query_limit()]
        list_length = len(courierlist)
        courier_list_data = NWisefinList()
        if list_length > 0:
            for courierobj in courierlist:
                courier_data = CourierResponse()
                courier_data.set_id(courierobj.id)
                courier_data.set_code(courierobj.code)
                courier_data.set_name(courierobj.name)
                courier_data.set_contactperson(courierobj.contactperson)
                courier_list_data.append(courier_data)
            vpage = NWisefinPaginator(courierlist, vys_page.get_index(), 10)
            courier_list_data.set_pagination(vpage)
        return courier_list_data


    def get_courier(self, courier_data):
        courierIdarr = courier_data.get('courier_id')
        courier = Courier.objects.using(self._current_app_schema()).filter(id__in=courierIdarr).values('id', 'code', 'name')
        courier_list_data = NWisefinList()
        for i in courier:
            data = {"id": i['id'],
                    "code": i['code'],
                    "name": i['name']}
            courier_list_data.append(data)
        return courier_list_data.get()