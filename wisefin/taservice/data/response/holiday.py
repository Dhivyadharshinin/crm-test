import json

class HolidayResponse:
    
    date = None
    holidayname = None
    state = None
    status = 1
    entity = 1
    data = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_date(self, date):
        self.date = str(date)

    def set_holidayname(self, holidayname):
        self.holidayname = holidayname

    def set_state(self, state):
        self.state = state

    def set_entity(self, entity):
        self.entity = entity

    def set_status(self, status):
        self.status = status

    def set_data(self, data):
        self.data = data


