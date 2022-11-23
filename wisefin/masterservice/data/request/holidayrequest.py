import json

class HolidayRequest:
    id = None
    holidayname = None
    validfrom = None
    validto = None
    state = None
    date=None


    def __init__(self, folio_dtls):
        if 'id' in folio_dtls:
            self.id = folio_dtls['id']
        if 'Holidayname' in folio_dtls:
            self.holidayname = folio_dtls['Holidayname']
        if 'validfrom' in folio_dtls:
            self.name = folio_dtls['validfrom']
        if 'validto' in folio_dtls:
            self.validto = folio_dtls['validto']
        if 'State' in folio_dtls:
            self.state = folio_dtls['State']
        if 'Date' in folio_dtls:
            self.date = folio_dtls['Date']




    def get_id(self):
        return self.id
    def get_holidayname(self):
        return self.holidayname
    def get_validfrom(self):
        return self.validfrom
    def get_validto(self):
        return self.validto
    def get_state(self):
        return self.state
    def get_date(self):
        return self.date
