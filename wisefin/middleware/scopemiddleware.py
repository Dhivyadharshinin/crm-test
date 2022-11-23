import sys
from userservice.service.vowemployeeservice import VowEmployeeServ
from configservice.service.applicationservice import ApplicationService
from configservice.service.appspaceservice import AppSpaceService
from middleware.nwisefinauth import NWisefinAuth
from userservice.service.userservice import UserService


class ScopeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = NWisefinAuth()
        auth.authenticate(request)
        self.set_scope(request)
        response = self.get_response(request)

        response['Access-Control-Allow-Origin'] = "*"
        return response

    def set_scope(self, request):
        user = request.user
        if user is not None:
            user_id = user.id
            vow_serv = VowEmployeeServ()
            is_staff = vow_serv.get_user_type(user_id)
            if is_staff == 1:
                request.user_id = user_id
                auth = NWisefinAuth()
                token = auth.get_token(request)
                employee_id = auth.get_employee_id(user_id)
                request.employee_id = employee_id
                app_space_service = AppSpaceService()
                userservice = UserService()
                entity_ids = userservice.get_employee_entityids(employee_id)
                default_entity_id = userservice.get_default_entity_id(employee_id)
                entity_info = app_space_service.get_app_info(entity_ids)
                request.entity_info = entity_info
                request.token = token
                path = auth.get_path(request)
                application_service = ApplicationService()
                application_id = application_service.fetch_application_id(path)
                app_space_service = AppSpaceService()
                current_app_info = app_space_service.get_current_app_info(application_id, default_entity_id)
                default_dict = current_app_info.get()
                request.default = default_dict
                is_vow_user = 1
                request.is_user = is_vow_user
                request.scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                                 'employee_id': employee_id, 'user_id': user_id, 'is_user': is_vow_user}
                print(request.scope)
            else:
                self.set_vow_scope(request, user_id)

        else:
            request.user_id = None
            employee_id = None
            token = None
            entity_info = None
            default_dict = None
            user_id = None
            request.employee_id = None
            request.default = {'entity_id': None, 'entity_name': None, 'schema': None}
            request.entity_info = None
            request.token = None
            is_vow_user = 0
            request.is_user = is_vow_user
            request.scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                             'employee_id': employee_id, 'user_id': user_id, 'is_user': is_vow_user}

    # changes for vow(v-0.1)
    def set_vow_scope(self, request, user_id):
        request.user_id = user_id
        vow_serv = VowEmployeeServ()
        auth = NWisefinAuth()
        token = auth.get_token(request)
        vow_user_id = vow_serv.get_vow_user_id(user_id)
        request.employee_id = vow_user_id
        app_space_service = AppSpaceService()
        entity_ids = vow_serv.get_vow_entityids(vow_user_id)
        default_entity_id = vow_serv.get_default_vow_entity(vow_user_id)
        entity_info = app_space_service.get_app_info(entity_ids)
        request.entity_info = entity_info
        request.token = token
        path = auth.get_path(request)
        application_service = ApplicationService()
        application_id = application_service.fetch_application_id(path)
        current_app_info = app_space_service.get_current_app_info(application_id, default_entity_id)
        default_dict = current_app_info.get()
        request.default = default_dict
        is_vow_user = 0
        request.is_user = is_vow_user
        request.scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                         'employee_id': vow_user_id, 'user_id': user_id, 'is_user': is_vow_user}
        print(request.scope)
