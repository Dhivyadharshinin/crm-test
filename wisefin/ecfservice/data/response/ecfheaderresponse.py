import json

class ECFHeaderresponse:
    id = None
    supplier_type = None
    # supplierstate_id = None
    commodity_id = None
    file_id = None
    crno = None
    ecftype = None
    ecfdate = None
    ecfamount = None
    ecfstatus = None
    ppx = None
    dueadjustment = None
    notename = None
    remark = None
    payto = None
    raisedby = None
    raiserbranch = None
    raisername = None
    approvedby = None
    approvername = None
    created_by = None
    branchgst = None
    gsttype =None
    supgstno=None
    branchname =None
    Invheader = None
    branch=None
    count = None
    file_data = None
    tds = None
    approver_name = None
    invoiceheader = None
    rmcode = None
    client_code = None
    raiserbranchgst = None
    ap_status = None
    status = None
    raisercode = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


    def set_id(self,id):
        self.id = id
    def set_supplier_type_id(self,supplier_type_id):
        self.supplier_type_id=supplier_type_id

    def set_supplier_type(self, supplier_type):
        self.supplier_type = supplier_type
    # def set_supplier_id(self, supplier_id, arr):
    #     if supplier_id != None:
    #         for i in arr:
    #             if i['id'] == supplier_id:
    #                 self.supplier_id = i
    #                 break
    # def set_supplierstate(self,supplierstate_id):
    #     self.supplierstate_id =supplierstate_id
    # def set_supplierstate_id(self, supplierstate_id, arr):
    #     if supplierstate_id != None:
    #         for i in arr:
    #             if i['id'] == supplierstate_id:
    #                 self.supplierstate_id = i
    #                 break
    def set_commodity(self,commodity_id):
        self.commodity_id =commodity_id

    def set_commodity_id(self, commodity_id, arr):
        if commodity_id != None:
            for i in arr:
                if i['id'] == commodity_id:
                    self.commodity_id = i
                    break
    def set_file_id(self,file_id):
        self.file_id =file_id
    def set_ecftype(self,ecftype):
        self.ecftype =ecftype
    def set_ecftype_id(self, ecftype_id):
        self.ecftype_id = ecftype_id
    def set_ecfdate(self,ecfdate):
        ecfdate = str(ecfdate)
        self.ecfdate =ecfdate
    def set_ecfamount(self,ecfamount):
        self.ecfamount =ecfamount
    def set_ecfstatus(self,ecfstatus):
        self.ecfstatus =ecfstatus
    def set_ecfstatus_id(self,ecfstatus_id):
        self.ecfstatus_id =ecfstatus_id
    def set_crno(self,crno):
        self.crno =crno
    def set_ppx(self,ppx):
        self.ppx =ppx
    def set_ppx_id(self,ppx_id):
        self.ppx_id =ppx_id
    def set_dueadjustment(self,dueadjustment):
        self.dueadjustment =dueadjustment
    def set_notename(self,notename):
        self.notename =notename
    def set_remark(self,remark):
        self.remark =remark
    def set_payto(self,payto):
        self.payto = payto
    def set_payto_id(self,payto_id):
        self.payto_id = payto_id
    def set_raisedby(self,raisedby):
        self.raisedby = raisedby
    def set_raiserbranch(self,raiserbranch_id):
        self.raiserbranch = raiserbranch_id
    def set_raiserbranchgst(self,raiserbranchgst):
        self.raiserbranchgst = raiserbranchgst
    def set_raisername(self,raisername):
        self.raisername = raisername
    def set_approvedby(self,approvedby_id):
        self.approvedby = approvedby_id
    def set_approvername(self,approvername):
        self.approvername = approvername
    def set_approverbranch(self,approverbranch):
        self.approverbranch = approverbranch
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_branchgst(self, branchgst):
        self.branchgst = branchgst
    def set_gsttype(self, gsttype):
        self.gsttype = gsttype
    def set_branchname(self, branchname):
        self.branchname = branchname
    def set_branch(self, branch):
        self.branch = branch
    def set_supgstno(self, supgstno):
        self.supgstno = supgstno
    def set_Invheader(self, Invheader):
        self.Invheader = Invheader
    def set_count(self, count):
        self.count = count
    def set_file_data(self, file_data):
        self.file_data = file_data
    def set_data(self, data):
        self.data =  data
    def set_tds(self, tds):
        self.tds =  tds
    def set_approver_branch(self, approver_branch):
        self.approver_branch =  approver_branch
    def set_invoiceheader(self, invoiceheader):
        self.invoiceheader =  invoiceheader
    def set_rmcode(self, rmcode):
        self.rmcode =  rmcode
    def set_client_code(self, client_code):
        self.client_code =  client_code
    def set_ap_status(self, ap_status):
        self.ap_status =  ap_status
    def set_status(self, status):
        self.status =  status
    def set_raisercode(self, raisercode):
        self.raisercode =  raisercode




