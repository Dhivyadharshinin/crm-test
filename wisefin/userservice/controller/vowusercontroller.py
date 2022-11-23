from configservice.models import AppSpace, Application, Schema
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class VowUser:

    # def __init__(self):
    #     self.is_user =False
    #     self.emp_id =None
    #     self.entity_id =None

    def get_user(self, request):
        d = {}
        d['user_id'] = request.GET.get('user_id')
        d['entity_id'] = int(request.GET.get('entity_id'))
        d['schema'] = 'default'
        d['is_user'] = False
        # sev = NWisefinThread(request.scope)
        # sev._set_namespace(ApplicationNamespace.CMS_SERVICE)
        # d['user_id'] = request.employee_id
        # d['entity_id'] = sev._entity_id()
        # d['schema'] = sev._current_app_schema()
        # d['is_user'] = request.scope['is_user']
        # print(d)
        return d

    def get_user1(self, request, app_name):
        entity_id = int(request.GET.get('entity_id'))
        appspace = AppSpace.objects.get(entity_id=entity_id,
                                        application__namespace__iexact=app_name,
                                        application__status=1)
        schema = appspace.schema.name

        d = {}
        d['user_id'] = request.GET.get('user_id')
        d['entity_id'] = entity_id
        d['schema'] = schema
        d['is_user'] = False
        return d