from django.db.models import Q

from configservice.data.response.configresponse import SchemaResponse
from configservice.models import Schema, AppSpace
from configservice.service.applicationservice import ApplicationService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess


class ConfigService:
    def post_schema(self, schema_json):
        schema = Schema.objects.using('default').create(name=schema_json['name'])
        resp = SchemaResponse(schema)
        return resp

    def fetch_schema(self):
        schema_arr = Schema.objects.using('default').all()
        resp_list = NWisefinList()
        for schema in schema_arr:
            resp = SchemaResponse(schema)
            resp_list.append(resp)
        return resp_list

    def delete_schema(self, schema_id):
        if schema_id is None:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Schema ID')
        else:
            Schema.objects.using('default').filter(id=schema_id).delete()
            resp = NWisefinSuccess()
            resp.set_status(200)
            resp.set_message('Schema Deleted Successfully')
        return resp

    def reserve(self, app_id, entity_id, schema_id):
        condition = Q(application_id__exact=app_id) & Q(entity_id__exact=entity_id) & Q(schema_id__exact=schema_id)
        app_arr = AppSpace.objects.using('default').filter(condition)
        app_len = len(app_arr)
        if app_len > 0 :
            resp = NWisefinError()
            resp.set_code(302)
            resp.set_description('Schema Already exists')
        else:
            AppSpace.objects.using('default').create(application_id= app_id, entity_id=entity_id, schema_id=schema_id)
            resp = NWisefinSuccess()
            resp.set_status(200)
            resp.set_message('Schema Created Successfully')
        return resp

    def get_schema(self, app_id, entity_id):
        condition = Q(application_id__exact=app_id) & Q(entity_id__exact=entity_id)
        app_arr = AppSpace.objects.using('default').filter(condition)
        app_len = len(app_arr)
        if app_len > 0:
            return app_arr[0].schema.name
        else:
            return None

    def set_config(self, request):
        req_path = request.path
        path_arr = req_path.split('/')
        app_path = '/'+ path_arr[1]
        app_service = ApplicationService()
        app_id = app_service.fetch_application_id(app_path)
        req_entity = request.default.entity
        entity_id = req_entity.id
        schema_name = self.get_schema(app_id, entity_id)
        print(request.path)
        print(app_path)
        resp = NWisefinSuccess()
        resp.set_status(200)
        resp.set_message('Config Fetch Successful '+str(app_id) + ' '+schema_name)
        return resp
