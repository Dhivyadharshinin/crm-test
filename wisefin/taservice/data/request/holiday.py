import json
from taservice.util.ta_util import Status

class HolidayRequest:
    id = None
    date = None
    holidayname = None
    state = 1
    status = Status.REQUESTED
    entity = 1


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, get_obj):

        if 'id' in get_obj:
            self.id = get_obj['id']
        if 'Date' in get_obj:
            self.date= get_obj['Date']
        if 'Holiday Name' in get_obj:
            self.holidayname= get_obj['Holiday Name']
        if 'State' in get_obj:
            self.state= get_obj['State']
        if 'entity' in get_obj:
            self.entity= get_obj['entity']
        if 'status' in get_obj:
            self.status = get_obj['status']

    def get_id(self):
        return self.id

    def get_date(self):
        return self.date

    def get_holidayname(self):
        return self.holidayname

    def get_state(self):
        return self.state

    def get_entity(self):
        return self.entity

    def get_status(self):
        return self.status
