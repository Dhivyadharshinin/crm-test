import json

from inwardservice.data.response.escalatontyperesponse import EscalationSubTypeResponse
from inwardservice.data.response.escalatontyperesponse import EscalationTypeResponse

class InwardTemplateResponse:
    id = None
    template_name = None
    template_content = None
    escalationsubtype = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_template_name(self, template_name):
        self.template_name = template_name

    def set_template_content(self, template_content):
        self.template_content = template_content


    def set_escalationsubtype(self, escalation):
        escalation_data = EscalationSubTypeResponse()
        #escal_service = EscalationTypeService()
        escalation_data.set_id(escalation.id)
        escalation_data.set_name(escalation.name)
        escalation_data.set_escalationtype(self.escalationtype_response(escalation.escalationtype))
        self.escalationsubtype = escalation_data


    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name


    def escalationtype_response(self, escalation):
        escalation_data = EscalationTypeResponse()
        escalation_data.set_id(escalation.id)
        escalation_data.set_name(escalation.name)
        return escalation_data

