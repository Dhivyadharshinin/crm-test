import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from knox.models import AuthToken
from rest_framework import status
from django.db.models import Q
from nwisefin.settings import logger
from userservice.data.response.authresponse import AuthResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from configservice.models.configmodels import Entity
from userservice.service.userservice import UserService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.models.usermodels import Employee, EmployeeEntityMapping,Vow_user, Vow_userEntityMapping
from userservice.data.response.entityresponse import EntityResponse
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
import json
import base64
import traceback


class AuthService:
    def get_user(self, user_name, password):
        user = authenticate(username=user_name, password=password)
        return user

    def nwisefin_authenticate(self, user_name, password, entity_id):
        user = self.get_user(user_name, password)
        entity_obj = Entity.objects.using('default').filter(id=entity_id)
        entity_obj_length = len(entity_obj)
        if (user is None) or (entity_obj_length == 0):
            error_response = NWisefinError()
            error_response.set_code(403)
            error_response.set_description('Invalid user account')
            # error_response.set_http_status(status.HTTP_403_FORBIDDEN)
            print(error_response)
            return error_response
        else:
            token_obj = AuthToken.objects.create(user)
            employee = Employee.objects.filter(code=user_name)
            print(token_obj)
            auth_user = token_obj[0].user
            expiry = token_obj[0].expiry
            expiry_str = str(expiry)
            auth_response = AuthResponse()
            # auth_response.set_id(auth_user.id)
            zeyaly_user = User.objects.get(id=auth_user.id)
            # auth_response.set_name(zeyaly_user.full_name)
            # auth_response.set_email(zeyaly_user.email)
            # auth_response.set_phone(zeyaly_user.phone)
            auth_response.set_token(token_obj[1])
            auth_response.set_expiry(expiry_str)
            auth_response.set_name(employee[0].full_name)
            auth_response.set_code(employee[0].code)
            auth_response.set_employee_id(employee[0].id)
            auth_response.user_id = employee[0].user_id
            # auth_response.set_http_status(status.HTTP_200_OK)
            # entity details
            entity = Entity.objects.get(id=entity_id)
            auth_response.entity_id = entity_id
            auth_response.entity_name = entity.name
            user_serv = UserService()
            user_serv.change_employee_entity_mapping(user_name, entity_id)
            return auth_response

    def user(self,user_arr):
        condition = None
        user_list = None
        for user_id in user_arr:
            if condition is None:
                condition = Q(id__exact=user_id)
            else:
                condition |= Q(id__exact=user_id)
        if condition is not None:
            user_list = User.objects.filter(condition)
        resp_list = NWisefinList()
        if user_list is not None:
            for user in user_list:
                user_obj = NWisefinUser()
                user_obj.set_id(user.id)
                user_obj.set_username(user.username)
                user_obj.set_email(user.email)
                user_obj.set_first_name(user.first_name)
                user_obj.set_last_name(user.last_name)
                user_obj.set_is_active(user.is_active)
                resp_list.append(user_obj)
        return resp_list.get()

    def get_entity(self, vys_page):
        try:
            entity = Entity.objects.all()
            list_length = len(entity)
            entity_list_data = NWisefinList()
            if list_length >= 0:
                for client in entity:
                    ent_data = EntityResponse()
                    ent_data.set_id(client.id)
                    ent_data.set_name(client.name)
                    ent_data.set_namespace(client.namespace)
                    ent_data.set_status(client.status)
                    entity_list_data.append(ent_data)
                vpage = NWisefinPaginator(entity, vys_page.get_index(), 10)
                entity_list_data.set_pagination(vpage)
                return entity_list_data
        except:
            logger.error('ERROR_Entity_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def get_emp_entity(self, vys_page, employee_id):
        emp_entity = EmployeeEntityMapping.objects.filter(employee_id=employee_id)
        list_length = len(emp_entity)
        entity_list_data = NWisefinList()
        if list_length >= 0:
            for client in emp_entity:
                entity = Entity.objects.get(id=client.entity_id)
                ent_data = EntityResponse()
                ent_data.set_id(entity.id)
                ent_data.set_name(entity.name)
                entity_list_data.append(ent_data)
            vpage = NWisefinPaginator(emp_entity, vys_page.get_index(), 10)
            entity_list_data.set_pagination(vpage)
            return entity_list_data

    def update_default_entity(self, entity_id, employee_id):
        if entity_id is not None:
            EmployeeEntityMapping.objects.filter(employee_id=employee_id).update(is_default=0)
            EmployeeEntityMapping.objects.filter(employee_id=employee_id, entity_id=entity_id).update(is_default=1)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def create_emp_entity(self, resp_data):
        entity_id=resp_data['entity_id']
        employee_id=resp_data['employee_id']
        emp_ent = EmployeeEntityMapping.objects.filter(entity_id=entity_id,employee_id=employee_id)
        if len(emp_ent)==0:
            EmployeeEntityMapping.objects.create(entity_id=entity_id,employee_id=employee_id)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def delete_emp_entity(self,resp):
        entity_id = resp['entity_id']
        employee_id = resp['employee_id']
        emp_ent = EmployeeEntityMapping.objects.filter(entity_id=entity_id,employee_id=employee_id)
        if len(emp_ent)>0:
            EmployeeEntityMapping.objects.filter(entity_id=entity_id,employee_id=employee_id).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def auth_welcome(self, result):
        results = result.content.decode("utf-8")
        results_data = json.loads(results)
        user_info = results_data.get('id_token')
        # refresh_token = results_data.get('refresh_token')
        if user_info is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_USER_ID)
            error_obj.set_description(ErrorDescription.INVALID_USER_ID)
            return error_obj
        else:
            user_info = user_info.split('.')
            user_info = user_info[1]
            user_info = base64.b64decode(user_info + "==")
            user_info = json.loads(user_info)
            user_info = user_info.get("upn")
            logger.info('upn : '+str(user_info))
            data = self.get_user_data(user_info)
            return data

    def get_user_data(self,user_info):
        emp_data = Employee.objects.filter(email_id=user_info)
        emp_length = len(emp_data)
        if emp_length == 0:
            logger.info('Employee query not satisfied')
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_USER_ID)
            error_obj.set_description(ErrorDescription.INVALID_USER_ID)
            return error_obj
        else:
            user_name = emp_data[0].code
            # password = '1234'
            user_data = User.objects.filter(username=user_name)
            user_length = len(user_data)
            if user_length == 0:
                try:
                    logger.info('Creating new user for Employee :' + str(user_name))
                    user = User.objects.create_user(username=user_name, password=user_name)
                    user.set_password(user_name)
                    user.save()
                    logger.info('Mapping the User and Employee :' + str(user_name))
                    user_id = user.id
                    emp_data[0].user_id = user_id
                    emp_data[0].save()
                except:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.CANT_ABLE_TO_CREATE)
                    error_obj.set_description(ErrorDescription.CANT_ABLE_TO_CREATE)
                    return error_obj
            emp_entity = EmployeeEntityMapping.objects.filter(employee_id=emp_data[0].id, is_default=1)
            entity_id = emp_entity[0].entity_id
            service = AuthService()
            resp_obj = service.nwisefin_authenticate(user_name, user_name, entity_id)
            return resp_obj

    def vow_user_insert(self,data,employee_id):
        vow_create=Vow_user.objects.using('default').create(entity_id=data["entity_id"],
                                                            code=data["code"],
                                                            full_name=data["full_name"],
                                                            email_id=data["email_id"],
                                                            status=1,
                                                            created_by=employee_id,
                                                            created_date=datetime.datetime.now(),
                                                            user_id=data["user_id"],
                                                            role=data["role"],
                                                            vow_employee_id=data["vow_employee_id"])
        entity_mapping = Vow_userEntityMapping.objects.using('default').create(employee_id=vow_create.id,
                                                                               entity_id=data["entity_id"],
                                                                               is_default=True)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def vow_welcome(self, user_name, password, entity_id):
        user = self.get_user(user_name, password)
        entity_obj = Entity.objects.using('default').filter(id=entity_id)
        entity_obj_length = len(entity_obj)
        if (user is None) or (entity_obj_length == 0):
            error_response = NWisefinError()
            error_response.set_code(403)
            error_response.set_description('Invalid user account')
            # error_response.set_http_status(status.HTTP_403_FORBIDDEN)
            print(error_response)
            return error_response
        else:
            token_obj = AuthToken.objects.create(user)
            employee = Vow_user.objects.filter(code=user_name)
            print(token_obj)
            auth_user = token_obj[0].user
            expiry = token_obj[0].expiry
            expiry_str = str(expiry)
            auth_response = AuthResponse()
            # auth_response.set_id(auth_user.id)
            zeyaly_user = User.objects.get(id=auth_user.id)
            # auth_response.set_name(zeyaly_user.full_name)
            # auth_response.set_email(zeyaly_user.email)
            # auth_response.set_phone(zeyaly_user.phone)
            auth_response.set_token(token_obj[1])
            auth_response.set_expiry(expiry_str)
            auth_response.set_name(employee[0].full_name)
            auth_response.set_code(employee[0].code)
            auth_response.set_employee_id(employee[0].id)
            auth_response.user_id = employee[0].user_id
            auth_response.vow_employee_id = employee[0].vow_employee_id
            # auth_response.set_http_status(status.HTTP_200_OK)
            # entity details
            entity = Entity.objects.get(id=entity_id)
            auth_response.entity_id = entity_id
            auth_response.entity_name = entity.name
            user_serv = UserService()
            user_serv.change_vow_entity_mapping(user_name, entity_id)
            return auth_response

    # changes for ujjivan(v-0.1)
    def nwisefin_authenticate_default(self, user_name, password):
        user = self.get_user(user_name, password)
        if user is None:
            error_response = NWisefinError()
            error_response.set_code(403)
            error_response.set_description('Invalid user account')
            print(error_response)
            return error_response
        else:
            token_obj = AuthToken.objects.create(user)
            employee = Employee.objects.filter(code=user_name)
            emp_ent_map = EmployeeEntityMapping.objects.filter(employee_id=employee[0].id,
                                                               is_default=1)
            entity_id = emp_ent_map[0].entity_id
            print(token_obj)
            expiry = token_obj[0].expiry
            expiry_str = str(expiry)
            auth_response = AuthResponse()
            auth_response.set_token(token_obj[1])
            auth_response.set_expiry(expiry_str)
            auth_response.set_name(employee[0].full_name)
            auth_response.set_code(employee[0].code)
            auth_response.set_employee_id(employee[0].id)
            auth_response.user_id = employee[0].user_id
            entity = Entity.objects.get(id=entity_id)
            auth_response.entity_id = entity_id
            auth_response.entity_name = entity.name
            return auth_response
