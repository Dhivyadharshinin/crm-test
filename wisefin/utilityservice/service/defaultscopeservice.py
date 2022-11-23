from configservice.service.applicationservice import ApplicationService
from configservice.service.appspaceservice import AppSpaceService
from middleware.nwisefinauth import NWisefinAuth
from userservice.service.userservice import UserService


class DefaultScopeService:
    def set_default_scope(self, request):
        user_id = 20
        request.user_id = user_id
        auth = NWisefinAuth()
        token = ''
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
        request.scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                         'employee_id': employee_id, 'user_id': user_id}
        scope_resp = request.scope
        print(scope_resp)
        return scope_resp


class DefaultScopeScheduler:
    def create_default_scope(self):
        user_id = 20
        auth = NWisefinAuth()
        token = ''
        employee_id = auth.get_employee_id(user_id)
        app_space_service = AppSpaceService()
        user_service = UserService()
        entity_ids = user_service.get_employee_entityids(employee_id)
        default_entity_id = user_service.get_default_entity_id(employee_id)
        entity_info = app_space_service.get_app_info(entity_ids)
        application_service = ApplicationService()
        application_id = application_service.fetch_application_id('/usrserv')
        app_space_service = AppSpaceService()
        current_app_info = app_space_service.get_current_app_info(application_id, default_entity_id)
        default_dict = current_app_info.get()
        scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                 'employee_id': employee_id, 'user_id': user_id}
        return scope

    def scope_for_multiple_entity(self, entity_id):
        user_id = None
        employee_id = None
        token = ''
        app_space_service = AppSpaceService()
        entity_info = app_space_service.get_app_space_by_entity(entity_id)
        app_space_service = AppSpaceService()
        current_app_info = app_space_service.get_current_app_by_entity(entity_id)
        default_dict = current_app_info
        scope = {'token': token, 'entity_info': entity_info, 'default': default_dict,
                 'employee_id': employee_id, 'user_id': user_id, "is_user": 1}
        print(scope)
        return scope