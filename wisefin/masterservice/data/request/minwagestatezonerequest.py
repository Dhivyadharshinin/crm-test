import json


class MinwageRequest:
    id = None
    state_id = None
    noofzones = None


    def __init__(self, bank_data):
        if 'id' in bank_data:
            self.id = bank_data['id']
        if 'state_id' in bank_data:
            self.state_id = bank_data['state_id']
        if 'noofzones' in bank_data:
            self.noofzones = bank_data['noofzones']


    def get_id(self):
        return self.id

    def get_state_id(self):
        return self.state_id

    def get_noofzones(self):
        return self.noofzones



