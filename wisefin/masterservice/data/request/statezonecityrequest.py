class StateZoneRequest:

    id = None
    statemap_id = None
    statename = None
    zone = None
    effectivefrom = None
    count = None


    def __init__(self, state_zone_data):
        if 'id' in state_zone_data:
            self.id = state_zone_data['id']
        if 'statemap_id' in state_zone_data:
            self.statemap_id = state_zone_data['statemap_id']
        if 'zone' in state_zone_data:
            self.zone = state_zone_data['zone']
        if 'effectivefrom' in state_zone_data:
            self.effectivefrom = state_zone_data['effectivefrom']
        if 'count' in state_zone_data:
            self.effectiveto = state_zone_data['count']



    def get_id(self):
        return self.id
    def get_statemap_id(self):
        return self.statemap_id
    def get_zone(self):
        return self.zone
    def get_effectivefrom(self):
        return self.effectivefrom
    def get_count(self):
        return self.count


class StateAndZoneRequest:
    id = None
    state_id = None
    zone = None
    effectivefrom = None
    count = None
    code=None
    name=None


    def __init__(self, state_zone_data):
        if 'id' in state_zone_data:
            self.id = state_zone_data['id']
        if 'state_id' in state_zone_data:
            self.state_id = state_zone_data['state_id']
        if 'zone' in state_zone_data:
            self.zone = state_zone_data['zone']
        if 'effectivefrom' in state_zone_data:
            self.effectivefrom = state_zone_data['effectivefrom']
        if 'count' in state_zone_data:
            self.count = state_zone_data['count']
        if 'name' in state_zone_data:
            self.name = state_zone_data['name']
        if 'code' in state_zone_data:
            self.code = state_zone_data['code']



    def get_id(self):
        return self.id
    def get_state_id(self):
        return self.state_id
    def get_zone(self):
        return self.zone
    def get_effectivefrom(self):
        return self.effectivefrom
    def get_count(self):
        return self.count
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
