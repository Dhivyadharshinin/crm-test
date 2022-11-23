import json


class Finyearresponse:
    finyer = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_finyear(self, finyear):
        self.finyer = finyear


class PprSupplierresponse:
    supplier_id = None
    supplier_name = None
    supplier_code = None
    quarter = None
    transactionmonth = None
    transactiondate = None
    supplier_branchname = None
    supplier_panno = None
    supplier_gstno = None
    pprdata_id = None
    totamount = None
    ecf_count = None
    apexpense_id = None
    apsubcat_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_apexpense_id(self,apexpense_id):
        self.apexpense_id = apexpense_id

    def set_apsubcat_id(self,apsubcat_id):
        self.apsubcat_id = apsubcat_id

    def set_suppliergid(self, supplier_id):
        self.supplier_id = supplier_id

    def set_supplier_name(self, supplier_name):
        self.supplier_name = supplier_name

    def set_supplier_code(self, supplier_code):
        self.supplier_code = supplier_code

    def set_quarter(self, quarter):
        self.quarter = quarter

    def set_transactionmonth(self, transactionmonth):
        self.transactionmonth = transactionmonth

    def set_transactiondate(self, transactiondate):
        self.transactiondate = transactiondate

    def set_supplier_branchname(self, supplier_branchname):
        self.supplier_branchname = supplier_branchname

    def set_supplier_panno(self, supplier_panno):
        self.supplier_panno = supplier_panno

    def set_supplier_gstno(self, supplier_gstno):
        self.supplier_gstno = supplier_gstno

    def set_pprdata_id(self, pprdata_id):
        self.pprdata_id = pprdata_id

    def set_totamount(self, totamount):
        self.totamount = totamount

    def set_ecf_count(self,ecf_count):
        self.ecf_count = ecf_count

    def set_supplier_detial(self,supplier_detial,ppr_supplier_id):
        if ppr_supplier_id == 0:
            self.supplier_id = 0
            self.supplier_name = "OTHERS"
            self.supplier_code = ""
            self.supplier_branchname = ""
            self.supplier_panno = ""
            self.supplier_gstno = ""
        elif int(ppr_supplier_id) == -1:
            self.supplier_id = -1
            self.supplier_name = "TASK"
            self.supplier_code = ""
            self.supplier_branchname = ""
            self.supplier_panno = ""
            self.supplier_gstno = ""
        else:
            for i in supplier_detial:
                if ppr_supplier_id == i['supplier_id']:
                    self.supplier_id = i['supplier_id']
                    self.supplier_name = i['supplier_name']
                    self.supplier_code = i['supplier_code']
                    self.supplier_branchname = i['supplier_branchname']
                    self.supplier_panno = i['supplier_panno']
                    self.supplier_gstno = i['supplier_gstno']


class Ppr_MBS_BS_CCresponse:
    id = None
    name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name
