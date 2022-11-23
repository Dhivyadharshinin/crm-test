import json

class  TemplateRequest:
    id = None
    template_name = None
    template_content = None
    escalationsubtype_id = None

    def __init__(self, template_obj):
        if 'id' in template_obj:
            self.id = template_obj['id']
        if 'template_name' in template_obj:
            self.template_name = template_obj['template_name']
        if 'template_content' in template_obj:
            self.template_content = template_obj['template_content']
        if 'escalationsubtype_id' in template_obj:
            self.escalationsubtype_id = template_obj['escalationsubtype_id']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

    def set_template_name(self, template_name):
        self.template_name = template_name

    def set_template_content(self, template_content):
        self.template_content = template_content

    def set_escalationsubtype_id(self, escalationsubtype_id):
        self.escalationsubtype_id = escalationsubtype_id

    def get_id(self):
        return self.id

    def get_template_name(self):
        return self.template_name

    def get_template_content(self):
        return self.template_content

    def get_escalationsubtype_id(self):
        return self.escalationsubtype_id

