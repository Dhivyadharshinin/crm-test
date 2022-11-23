import json
#test
class JVEntryresponse:
    id = None
    jecrno = None
    jemode = None
    jebranch = None
    jetype = None
    jerefno = None
    jedescription = None
    jetransactiondate = None
    jeamount = None
    jestatus = None
    jestatus_id = None
    jetype_id = None
    journaldetails = None
    jventry = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_jecrno(self,jecrno):
        self.jecrno=jecrno
    def set_jemode(self, jemode):
        self.jemode = jemode
    def set_jebranch(self,jebranch):
        self.jebranch =jebranch
    def set_jetype(self,jetype):
        self.jetype =jetype
    def set_jerefno(self,jerefno):
        self.jerefno =jerefno
    def set_jedescription(self, jedescription):
        self.jedescription = jedescription
    def set_jetransactiondate(self,jetransactiondate):
        jetransactiondate = str(jetransactiondate)
        self.jetransactiondate =jetransactiondate
    def set_jeamount(self,jeamount):
        self.jeamount =jeamount
    def set_jestatus(self,jestatus):
        self.jestatus =jestatus
    def set_jestatus_id(self, jestatus_id):
        self.jestatus_id = jestatus_id
    def set_jetype_id(self, jetype_id):
        self.jetype_id = jetype_id
    def set_journaldetails(self,journaldetails):
        self.journaldetails =journaldetails
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_jventry(self, jventry):
        self.jventry = jventry
    def set_file_data(self, file_data):
        self.file_data = file_data