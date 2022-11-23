import json

class AuditCheckListRequest:

    id = None
    type = None
    group = None
    code = None
    question = None
    solution = None
    status = None

    def __init__(self, aud_data):
        if 'id' in aud_data:
            self.id = aud_data['id']
        if 'code' in aud_data:
            self.code = aud_data['code']
        if 'group' in aud_data:
            self.group = aud_data['group']
        if 'question' in aud_data:
            self.question = aud_data['question']
        if 'solution' in aud_data:
            self.solution = aud_data['solution']
        if 'status' in aud_data:
            self.status = aud_data['status']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_group(self):
        return self.group
    def get_question(self):
        return self.question
    def get_solution(self):
        return self.solution
    def get_status(self):
        return self.status
