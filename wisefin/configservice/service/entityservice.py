from configservice.data.response.entityresponse import EntityResponse
from configservice.models import Entity
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess


class EntityService:
    def post(self, entity_req):
        if entity_req.get_id() is not None:
            return self.update(entity_req)
        else:
            return self.create(entity_req)

    def create(self, entity_req):
        entity_obj = Entity.objects.using('default').create(name=entity_req.get_name())
        entity_resp = EntityResponse(entity_obj)
        return entity_resp

    def update(self, entity_req):
        entity_obj = Entity.objects.using('default').filter(id=entity_req.get_id()).update(name=entity_req.get_name())
        entity_resp = EntityResponse(entity_obj)
        return entity_resp

    def fetch_entity(self, entity_id):
        entity_arr = Entity.objects.using('default').filter(id__exact=entity_id)
        entity_length = len(entity_arr)
        if entity_length == 0:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Entity ID')
        else:
            resp = EntityResponse(entity_arr[0])
        return resp

    def fetch_entity_list(self):
        entity_arr = Entity.objects.using('default').all()
        resp_list = NWisefinList()
        for entity in entity_arr:
            resp = EntityResponse(entity)
            resp_list.append(resp)
        return resp_list

    def delete_entity(self, entity_id):
        if entity_id is None:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Entity ID')
        else:
            Entity.objects.using('default').filter(id=entity_id).delete()
            resp = NWisefinSuccess()
            resp.set_status(200)
            resp.set_message('Entity Deleted Successfully')
        return resp

    def search_entity(self, name):
        if name is None:
            entity_list = Entity.objects.using('default').all()
        else:
            entity_list = Entity.objects.using('default').filter(name__icontains=name)
        resp_list = NWisefinList()
        for entity in entity_list:
            resp = EntityResponse(entity)
            resp_list.append(resp)
        return resp_list
