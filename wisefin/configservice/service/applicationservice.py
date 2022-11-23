from django.db.models import Q

from configservice.data.response.applicationresponse import ApplicationResponse
from configservice.data.response.entityresponse import EntityResponse
from configservice.models import Entity, Application
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess


class ApplicationService:
    def post(self, app_req):
        if app_req.get_id() is not None:
            return self.update(app_req)
        else:
            return self.create(app_req)

    def create(self, app_req):
        app_obj = Application.objects.using('default').create(name=app_req.get_name(), app_path=app_req.get_path(),
                                                              namespace=app_req.get_namespace())
        app_resp = ApplicationResponse(app_obj)
        return app_resp

    def update(self, app_req):
        app_obj = Application.objects.using('default').filter(id=app_req.get_id()).update(
            name=app_req.get_name(), app_path=app_req.get_path(), namespace=app_req.get_namespace())
        app_resp = ApplicationResponse(app_obj)
        return app_resp

    def fetch_application(self, app_id):
        app_arr = Application.objects.using('default').filter(id__exact=app_id)
        app_length = len(app_arr)
        if app_length == 0:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Application ID')
        else:
            resp = ApplicationResponse(app_arr[0])
        return resp

    def fetch_application_list(self):
        app_arr = Application.objects.using('default').all()
        resp_list = NWisefinList()
        for app in app_arr:
            resp = ApplicationResponse(app)
            resp_list.append(resp)
        return resp_list

    def fetch_application_id(self, app_path):
        condition = Q(app_path__exact=app_path)
        app_obj = Application.objects.using('default').filter(condition)
        app_obj = app_obj[0]
        return app_obj.id

    def delete_application(self, app_id):
        if app_id is None:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Application ID')
        else:
            Application.objects.using('default').filter(id=app_id).delete()
            resp = NWisefinSuccess()
            resp.set_status(200)
            resp.set_message('Application Deleted Successfully')
        return resp
