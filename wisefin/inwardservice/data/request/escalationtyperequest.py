import json

class EscalatonTypeRequest:

    id = None
    name = None


    def __init__(self, escalation_data):
        if 'id' in escalation_data:
            self.id = escalation_data['id']
        if 'name' in escalation_data:
            self.name = escalation_data['name']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name

class EscalatonSubTypeRequest:

    id = None
    name = None
    escalationtype_id=None


    def __init__(self, escalation_data):
        if 'id' in escalation_data:
            self.id = escalation_data['id']
        if 'name' in escalation_data:
            self.name = escalation_data['name']
        if 'escalationtype_id' in escalation_data:
            self.escalationtype_id = escalation_data['escalationtype_id']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_escalationtype_id(self):
        return self.escalationtype_id



