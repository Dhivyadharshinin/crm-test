import json

class InwardResponse:
    id = None
    no = None
    date = None
    channel = None
    courier = None
    awbno = None
    noofpockets = None
    inwardfrom = None
    details = []


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

    def set_status(self, status):
        self.status = status

    def set_awbno(self, awbno):
        self.awbno = awbno

    def set_noofpockets(self, noofpockets):
        self.noofpockets = noofpockets

    def set_details(self, details):
        self.details = details

    def get_details(self):
        return self.details

    def set_inwardfrom(self, inwardfrom):
        self.inwardfrom = inwardfrom

    def set_branch(self, branch):
        self.branch = branch