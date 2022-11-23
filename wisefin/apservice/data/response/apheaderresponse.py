import json

class APHeaderResponse:
    id = None
    supplier_type = None
    commodity_id = None
    file_id = None
    crno = None
    aptype = None
    apdate = None
    apamount = None
    apstatus = None
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
    apinvheader = None
    apinvoiceheader = None
    apinvdetail_id = None
    apinvdetails = None
    Apinvoiceheader =None
    rmubarcode =None
    branch = None
    approver_branch = None
    tds = None
    is_originalinvoice = None
    client_code = None
    rmcode = None

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
    def set_aptype(self,aptype):
        self.aptype =aptype
    def set_aptype_id(self, aptype_id):
        self.aptype_id = aptype_id
    def set_apdate(self,apdate):
        apdate = str(apdate)
        self.apdate =apdate
    def set_apamount(self,apamount):
        self.apamount =apamount
    def set_apstatus(self,apstatus):
        self.apstatus =apstatus
    def set_apstatus_id(self,apstatus_id):
        self.apecfstatus_id =apstatus_id
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
    def set_raisername(self,raisername):
        self.raisername = raisername
    def set_approvedby(self,approvedby_id):
        self.approvedby = approvedby_id
    def set_approvername(self,approvername):
        self.approvername = approvername
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_branchgst(self, branchgst):
        self.branchgst = branchgst
    def set_gsttype(self, gsttype):
        self.gsttype = gsttype
    def set_branchname(self, branchname):
        self.branchname = branchname
    def set_supgstno(self, supgstno):
        self.supgstno = supgstno
    def set_apinvheader(self, apnvheader):
        self.apinvoiceheader = apnvheader
    def set_apinvdetails_id(self, apinvdetail_id):
        self.apinvdetail_id = apinvdetail_id
    def set_rmubarcode(self, rmubarcode):
        self.rmubarcode = rmubarcode
    def set_apinvdetails(self, apinvdetails):
        self.apinvdetails = apinvdetails
    def set_Apinvoiceheader(self, Apinvoiceheader):
        self.Apinvoiceheader = Apinvoiceheader
    def set_branch(self, branch):
        self.branch = branch
    def set_approver_branch(self, approver_branch):
        self.approver_branch = approver_branch
    def set_tds(self, tds):
        self.tds = tds

    def set_is_originalinvoice(self, is_originalinvoice):
        self.is_originalinvoice = is_originalinvoice

    def set_client_code(self, client_code):
        self.client_code = client_code

    def set_rmcode(self, rmcode):
        self.rmcode = rmcode











        #APHeaderResponse******END





class APQueueResponse:
    id = None
    from_user_id = None
    from_user = None
    to_user_id = None
    to_user = None
    status = None
    created_date = None
    comments = None
    remarks = None
    from_user_branch=None
    to_user_branch=None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


    def set_id(self,id):
        self.id = id
    def set_from_user_id(self,from_user_id):
        self.from_user_id=from_user_id
    def set_from_user(self, from_user):
        self.from_user = from_user
    def set_to_user_id(self,to_user_id):
        self.to_user_id=to_user_id
    def set_to_user(self, to_user):
        self.to_user = to_user
    def set_status(self,status):
        self.status=status
    def set_created_date(self, created_date):
        self.created_date = created_date
    def set_comments(self,comments):
        self.comments=comments
    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_from_user_branch(self, from_user_branch):
        self.from_user_branch = from_user_branch
    def set_to_user_branch(self, to_user_branch):
        self.to_user_branch = to_user_branch


    #-******APQueueResponse******END---------
