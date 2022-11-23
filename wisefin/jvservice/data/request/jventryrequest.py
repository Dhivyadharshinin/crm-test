class JVEntryrequest:
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

    def __init__(self,obj_jventry):
        if 'id' in obj_jventry:
            self.id=obj_jventry['id']
        if 'jecrno' in obj_jventry:
            self.jecrno = obj_jventry['jecrno']
        if 'jemode' in obj_jventry:
            self.jemode = obj_jventry['jemode']
        if 'jebranch' in obj_jventry:
            self.jebranch=obj_jventry['jebranch']
        if 'jetype' in obj_jventry:
            self.jetype = obj_jventry['jetype']
        if 'jerefno' in obj_jventry:
            self.jerefno=obj_jventry['jerefno']
        if 'jedescription' in obj_jventry:
            self.jedescription = obj_jventry['jedescription']
        if 'jetransactiondate' in obj_jventry:
            self.jetransactiondate=obj_jventry['jetransactiondate']
        if 'jeamount' in obj_jventry:
            self.jeamount=obj_jventry['jeamount']
        if 'jestatus' in obj_jventry:
            self.jestatus=obj_jventry['jestatus']

    def get_id(self):
        return self.id
    def get_jecrno(self):
        return self.jecrno
    def get_jemode(self):
        return self.jemode
    def get_jebranch(self):
        return self.jebranch
    def get_jetype(self):
        return self.jetype
    def get_jerefno(self):
        return self.jerefno
    def get_jedescription(self):
        return self.jedescription
    def get_jetransactiondate(self):
        return self.jetransactiondate
    def get_jeamount(self):
        return self.jeamount
    def get_jestatus(self):
        return self.jestatus