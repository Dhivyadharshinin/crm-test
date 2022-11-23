import json

class statezonecityRequest:

    id = None
    state_id = None
    city_id = None
    zone=None


    def __init__(self, bank_data):
        if 'id' in bank_data:
            self.id = bank_data['id']
        if 'state_id' in bank_data:
            self.state_id = bank_data['state_id']
        if 'city_id' in bank_data:
            self.city_id = bank_data['city_id']
        if 'zone' in bank_data:
            self.zone = bank_data['zone']




    def get_id(self):
        return self.id
    def get_state_id(self):
        return self.state_id
    def get_city_id(self):
        return self.city_id
    def get_zone(self):
        return self.zone


