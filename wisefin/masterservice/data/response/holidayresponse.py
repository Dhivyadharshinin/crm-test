import json
import time
class HolidayResponse:

    id = None
    holidayname = None
    validfrom = None
    validto = None
    state = None
    date = None
    year = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_holidayname(self, holidayname):
        self.holidayname = holidayname
    def set_validfrom(self, validfrom):
        if validfrom != None:
            self.validfrom = (validfrom.timestamp() * 1000)
        else:
            self.validfrom = validfrom
    def set_validto(self, validto):
        if validto != None:
            self.validto = (validto.timestamp() * 1000)
        else:
            self.validto = validto
    def set_state(self, state):
        self.state = {"name":state.name,"id":state.id,"code":state.code}

    def set_year(self, year):
        self.year = year

    def set_date(self, date):
        if date != None:
            self.date=int(time.mktime(date.timetuple())*1000)
        else:
            self.date=date
