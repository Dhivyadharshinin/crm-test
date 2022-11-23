import json
#test
class JVDetailEntryresponse:
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
    jedtype_id = None
    jedbranch = None
    EntryType_id = None
    EntryType = None
    Branch = None
    Category = None
    Subcategory = None
    BS = None
    CC = None
    CBSGL = None
    Description = None
    Amount = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_jeentry_id(self,jeentry_id):
        self.jeentry_id=jeentry_id
    def set_jedtype(self, jedtype):
        self.jedtype = jedtype
    def set_jeddescription(self,jeddescription):
        self.jeddescription =jeddescription
    def set_jedamount(self,jedamount):
        self.jedamount =jedamount
    def set_jedcat_code(self,jedcat_code):
        self.jedcat_code =jedcat_code
    def set_jedsubcat_code(self, jedsubcat_code):
        self.jedsubcat_code = jedsubcat_code
    def set_jedglno(self,jedglno):
        self.jedglno =jedglno
    def set_jedcc_code(self,jedcc_code):
        self.jedcc_code =jedcc_code
    def set_jedbs_code(self,jedbs_code):
        self.jedbs_code =jedbs_code
    def set_jedtype_id(self,jedtype_id):
        self.jedtype_id =jedtype_id
    def set_jedbranch(self,jedbranch):
        self.jedbranch =jedbranch
    def set_EntryType_id(self,EntryType_id):
        self.EntryType_id =EntryType_id
    def set_EntryType(self,EntryType):
        self.EntryType =EntryType
    def set_Branch(self, Branch):
        self.Branch = Branch
    def set_Category(self, Category):
        self.Category = Category
    def set_Subcategory(self, Subcategory):
        self.Subcategory = Subcategory
    def set_BS(self, BS):
        self.BS = BS
    def set_CC(self, CC):
        self.CC = CC
    def set_CBSGL(self, CBSGL):
        self.CBSGL = CBSGL
    def set_Description(self, Description):
        self.Description = Description
    def set_Amount(self, Amount):
        self.Amount = Amount