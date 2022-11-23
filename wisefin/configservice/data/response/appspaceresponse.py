import json

from configservice.data.response.applicationresponse import ApplicationResponse
from configservice.data.response.entityresponse import EntityResponse
from configservice.data.response.configresponse import SchemaResponse


class AppSpaceResponse:
    entity = None
    schema = None
    application = None

    def __init__(self, app_obj):
        self.application = {'id':app_obj.application.id, 'name': app_obj.application.name, 'namespace': app_obj.application.namespace}
        # self.application = ApplicationResponse(app_obj.application)
        self.entity = {'id':app_obj.entity.id, 'name': app_obj.entity.name}
        # self.entity = EntityResponse(app_obj.entity)
        self.schema = {'id': app_obj.schema.id, 'name': app_obj.schema.name}
        # self.schema = SchemaResponse(app_obj.schema)

    def get(self):
        return self.__dict__
        # return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
