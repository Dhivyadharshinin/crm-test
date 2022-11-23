import json



class AuditCheckListResponse:
    id = None
    type = None
    group = None
    code = None
    question = None
    solution = None
    status = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type(self, type):
        self.type = type

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def set_question(self, question):
        self.question = question

    def set_solution(self, solution):
        self.solution = solution

    def set_status(self, status):
        self.status = status