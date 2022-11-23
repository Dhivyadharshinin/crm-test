import json


class InwardListResponse:
    id = None
    no = None
    date = None
    channel = None
    courier = None
    awbno = None
    noofpockets = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_no(self, no):
        self.no = no

    def set_date(self, date):
        date = str(date)
        self.date = date

    def set_channel(self, channel):
        self.channel = channel

    def set_courier(self, courier):
        self.courier = courier

    def set_awbno(self, awbno):
        self.awbno = awbno

    def set_noofpockets(self, noofpockets):
        self.noofpockets = noofpockets