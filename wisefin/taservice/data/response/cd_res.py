import json
class Cd_res:
    id= None
    name= None
    status= None
    entity= 1
    code=None
    common_drop_down_id=None
    reason=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    state=None
    def set_id(self,id):
        self.id=id
    def set_name(self,name):
        self.name=name
    def set_state(self,state):
        self.state=state
    def set_state_type(self,state_type):
        self.state_type=state_type
    def set_metro_non(self,metro_non):
        self.metro_non=metro_non
    def set_status(self,status):
        self.status=status
    def set_entity(self,entity):
        self.entity=entity
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id
    def set_common_id(self,common_id):
        self.common_id=common_id
    def set_common_drop_down_id(self,common_drop_down_id):
        self.common_drop_down_id=common_drop_down_id

    def set_common_drop_down(self,common_drop_down):
        response=Cd_res()
        response.set_name(common_drop_down.name)
        response.set_entity(common_drop_down.entity)
        response.set_id(common_drop_down.id)
        response.set_code(common_drop_down.code)
        self.common_drop_down=response

    def set_value(self,value):
        self.value=value
    def set_updated_by(self,updated_by):
        self.updated_by=updated_by
    def set_created_by(self,created_by):
        self.created_by=created_by
    def set_created_date(self,created_date):
        self.created_date=created_date.strftime("%d-%b-%Y")
        self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        self.updated_date = updated_date
    def set_code(self,code):
        self.code = code

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


