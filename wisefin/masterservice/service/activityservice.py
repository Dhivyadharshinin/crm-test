import traceback
from django.db import IntegrityError
from django.db.models import Q
from masterservice.models import Activity
from  masterservice.data.response.questionresponse import ActivityResponse
from datetime import datetime

from masterservice.util.masterutil import ModifyStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus

now = datetime.now()

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
import json
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
class Activityservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_activity(self, act_obj, user_id):
        if not act_obj.get_id() is None:
                activity_update = Activity.objects.using(self._current_app_schema()).filter(id=act_obj.get_id(),
                    entity_id=self._entity_id()).update(
                    # code=act_obj.get_bankcode(),
                    name=act_obj.get_name(),
                    description=act_obj.get_description(),
                    updated_date=now,
                    updated_by=user_id)

                activity_var = Activity.objects.using(self._current_app_schema()).get(id=act_obj.get_id(), entity_id=self._entity_id())
        else:
                activity_var = Activity.objects.using(self._current_app_schema()).create(
                    name=act_obj.get_name(),description=act_obj.get_description(),
                    created_by=user_id, entity_id=self._entity_id())
        activity_var.code = 'ACT' + str(activity_var.id)
        activity_var.save()
        resp=ActivityResponse()
        resp.set_id(activity_var.id)
        resp.set_name(activity_var.name)
        resp.set_description(activity_var.description)
        return resp


    def Activityget(self,request,vys_page):
        query = request.GET.get('query')
        condtion=Q(entity_id=self._entity_id(), status=ModifyStatus.create)
        if query is not None and query!='':
            condtion &= Q(name__icontains=query)
        activity_var = Activity.objects.using(self._current_app_schema()).filter(condtion).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for obj in activity_var:
            data_resp = ActivityResponse()
            data_resp.set_id(obj.id)
            data_resp.set_name(obj.name)
            data_resp.set_description(obj.description)

            list_data.append(data_resp)
        vpage = NWisefinPaginator(activity_var, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def get_activity(self,id):
        obj = Activity.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = ActivityResponse()
        data_resp.set_id(obj.id)
        data_resp.set_name(obj.name)
        # data_resp.set_description(obj.description)
        # data_resp.set_code(obj.code)
        return data_resp

    def del_activity(self,id):
        obj = Activity.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def activity(self, activity_id):
        obj = Activity.objects.using(self._current_app_schema()).filter(id__in=activity_id)
        arr = []
        for i in obj:
            data_resp = ActivityResponse()
            data_resp.set_id(i.id)
            data_resp.set_name(i.name)
            data_resp.set_description(i.description)
            arr.append(data_resp)
        return arr

