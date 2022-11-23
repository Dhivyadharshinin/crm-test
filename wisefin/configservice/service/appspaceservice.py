from django.db.models import Q

from configservice.data.response.appspaceresponse import AppSpaceResponse
from configservice.models import AppSpace


class AppSpaceService:
    def get_app_info(self, entity_ids):
        app_space_arr = AppSpace.objects.filter(entity_id__in=entity_ids)
        resp_arr = []
        for app_space in app_space_arr:
            app_obj = AppSpaceResponse(app_space)
            resp_arr.append(app_obj.get())
        return resp_arr

    def get_current_app_info(self, app_id, entity_id):
        print(app_id,entity_id)
        condition = Q(application_id__exact=app_id) & Q(entity_id__exact=entity_id)
        app_arr = AppSpace.objects.filter(condition)
        app_resp = None
        if len(app_arr) > 0:
            app_resp = AppSpaceResponse(app_arr[0])
        return app_resp

    def get_app_space_by_entity(self, entity_id):
        app_space_arr = AppSpace.objects.filter(entity_id=entity_id)
        resp_arr = []
        for app_space in app_space_arr:
            app_obj = AppSpaceResponse(app_space)
            resp_arr.append(app_obj.get())
        return resp_arr

    def get_current_app_by_entity(self, entity_id):
        app_arr = AppSpace.objects.filter(entity_id__exact=entity_id)
        app_resp = None
        if len(app_arr) > 0:
            app_resp = AppSpaceResponse(app_arr[0]).get()
        return app_resp

