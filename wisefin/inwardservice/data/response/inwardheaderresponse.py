import json

class InwardHeaderResponse:
    id = None
    no = None
    date = None
    channel = None
    channel_id = None
    courier = None
    courier_id = None
    awbno = None
    noofpockets = None
    status = None
    inwardfrom = None
    inwardstatus = None
    # receivedby = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_no(self, no):
        self.no = no

    def set_date(self, date):
        date = str(date.date())
        self.date = date

    def set_channel(self, channel_id):
        self.channel_id = channel_id

    def set_courier(self, courier_id):
        self.courier_id = courier_id

    def set_branch(self, branch_id):
        self.branch_id = branch_id

    def set_awbno(self, awbno):
        self.awbno = awbno

    def set_noofpockets(self, noofpockets):
        self.noofpockets = noofpockets

    def set_status(self, status):
        self.status = status

    def set_inwardfrom(self, inwardfrom):
        self.inwardfrom = inwardfrom
    def set_inwardstatus(self, inwardstatus):
        self.inwardstatus = inwardstatus

    # def set_receivedby(self, receivedby):
    #     self.receivedby = receivedby

    def set_channel_id(self, channel_id, arr):
        if channel_id != None:
            for i in arr:
                if i['id'] == channel_id:
                    self.channel_id = i
                    break

    def set_courier_id(self, courier_id, arr):
        if courier_id != None:
            for i in arr:
                if i['id'] == courier_id:
                    self.courier_id = i
                    break

    def set_created_by(self, created_by, arr):
        if created_by != None:
            for i in arr:
                if i['id'] == created_by:
                    self.created_by = i
                    break

    def set_branch_id(self, branch_id, arr):
        if branch_id != None:
            for i in arr:
                if i['id'] == branch_id:
                    self.branch_id = i
                    break