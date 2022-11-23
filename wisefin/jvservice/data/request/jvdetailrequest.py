#test
class JVDetailEntryrequest:
    id = None
    jeentry_id = None
    jedtype = None
    jeddescription = None
    jedamount = None
    jedcat_code = None
    jedsubcat_code = None
    jedglno = None
    jedcc_code = None
    jedbs_code = None
    jedbranch = None

    def __init__(self,obj_jventry):
        if 'id' in obj_jventry:
            self.id=obj_jventry['id']
        if 'jeentry_id' in obj_jventry:
            self.jeentry_id = obj_jventry['jeentry_id']
        if 'jedtype' in obj_jventry:
            self.jedtype = obj_jventry['jedtype']
        if 'jeddescription' in obj_jventry:
            self.jeddescription=obj_jventry['jeddescription']
        if 'jedamount' in obj_jventry:
            self.jedamount = obj_jventry['jedamount']
        if 'jedcat_code' in obj_jventry:
            self.jedcat_code=obj_jventry['jedcat_code']
        if 'jedsubcat_code' in obj_jventry:
            self.jedsubcat_code = obj_jventry['jedsubcat_code']
        if 'jedglno' in obj_jventry:
            self.jedglno=obj_jventry['jedglno']
        if 'jedcc_code' in obj_jventry:
            self.jedcc_code=obj_jventry['jedcc_code']
        if 'jedbs_code' in obj_jventry:
            self.jedbs_code=obj_jventry['jedbs_code']
        if 'jedbranch' in obj_jventry:
            self.jedbranch=obj_jventry['jedbranch']


    def get_id(self):
        return self.id
    def get_jeentry_id(self):
        return self.jeentry_id
    def get_jedtype(self):
        return self.jedtype
    def get_jeddescription(self):
        return self.jeddescription
    def get_jedamount(self):
        return self.jedamount
    def get_jedcat_code(self):
        return self.jedcat_code
    def get_jedsubcat_code(self):
        return self.jedsubcat_code
    def get_jedglno(self):
        return self.jedglno
    def get_jedcc_code(self):
        return self.jedcc_code
    def get_jedbs_code(self):
        return self.jedbs_code
    def get_jedbranch(self):
        return self.jedbranch

