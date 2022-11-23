import json


class minwageResponse:
    id = None
    state_id = None
    noofzones = None
    z_list = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_state_id(self, state):
        if state != None:
            state ={"id":state.id ,"name":state.name}
        self.state_id = state

    def set_noofzones(self, noofzones):
        self.noofzones = noofzones
    def set_z_list(self, z_list):
        self.z_list = z_list



