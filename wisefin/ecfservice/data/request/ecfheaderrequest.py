import json

class ECFHeaderrequest:
    id = None
    supplier_type = None
    # supplierstate = None
    commodity = None
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
    branch = None
    tds = None
    approver_branch = None
    rmcode = None
    client_code = None
    ap_status = None

    def __init__(self,obj_ecfhdr):
        if 'id' in obj_ecfhdr:
            self.id=obj_ecfhdr['id']
        if 'supplier_type' in obj_ecfhdr:
            self.supplier_type = obj_ecfhdr['supplier_type']
        # if 'supplierstate_id' in obj_ecfhdr:
        #     self.supplierstate=obj_ecfhdr['supplierstate_id']
        if 'commodity_id' in obj_ecfhdr:
            self.commodity = obj_ecfhdr['commodity_id']
        if 'file_id' in obj_ecfhdr:
            self.file_id=obj_ecfhdr['file_id']
        if 'crno' in obj_ecfhdr:
            self.crno = obj_ecfhdr['crno']
        if 'ecftype' in obj_ecfhdr:
            self.ecftype=obj_ecfhdr['ecftype']
        if 'ecfdate' in obj_ecfhdr:
            self.ecfdate = obj_ecfhdr['ecfdate']
        if 'ecfamount' in obj_ecfhdr:
            self.ecfamount=obj_ecfhdr['ecfamount']
        if 'ecfstatus' in obj_ecfhdr:
            self.ecfstatus = obj_ecfhdr['ecfstatus']
        if 'ppx' in obj_ecfhdr:
            self.ppx=obj_ecfhdr['ppx']
        if 'dueadjustment' in obj_ecfhdr:
            self.dueadjustment = obj_ecfhdr['dueadjustment']
        if 'notename' in obj_ecfhdr:
            self.notename=obj_ecfhdr['notename']
        if 'remark' in obj_ecfhdr:
            self.remark = obj_ecfhdr['remark']
        if 'payto' in obj_ecfhdr:
            self.payto=obj_ecfhdr['payto']
        if 'raisedby' in obj_ecfhdr:
            self.raisedby = obj_ecfhdr['raisedby']
        if 'raiserbranch' in obj_ecfhdr:
            self.raiserbranch=obj_ecfhdr['raiserbranch']
        if 'raisername' in obj_ecfhdr:
            self.raisername = obj_ecfhdr['raisername']
        if 'approvedby_id' in obj_ecfhdr:
            self.approvedby=obj_ecfhdr['approvedby_id']
        if 'approvername' in obj_ecfhdr:
            self.approvername = obj_ecfhdr['approvername']
        if 'approver_branch' in obj_ecfhdr:
            self.approver_branch = obj_ecfhdr['approver_branch']
        if 'created_by' in obj_ecfhdr:
            self.created_by = obj_ecfhdr['created_by']
        if 'branch' in obj_ecfhdr:
            self.branch = obj_ecfhdr['branch']
        if 'tds' in obj_ecfhdr:
            self.tds = obj_ecfhdr['tds']
        if 'rmcode' in obj_ecfhdr:
            self.rmcode = obj_ecfhdr['rmcode']
        if 'client_code' in obj_ecfhdr:
            self.client_code = obj_ecfhdr['client_code']
        if 'ap_status' in obj_ecfhdr:
            self.ap_status = obj_ecfhdr['ap_status']

    def get_id(self):
        return self.id
    def get_supplier_type(self):
        return self.supplier_type
    # def get_supplierstate_id(self):
    #     return self.supplierstate
    def get_commodity_id(self):
        return self.commodity
    def get_file_id(self):
        return self.file_id
    def get_ecftype(self):
        return self.ecftype
    def get_ecfdate(self):
        return self.ecfdate
    def get_ecfamount(self):
        return self.ecfamount
    def get_ecfstatus(self):
        return self.ecfstatus
    def get_crno(self):
        return self.crno
    def get_ppx(self):
        return self.ppx
    def get_dueadjustment(self):
        return self.dueadjustment
    def get_notename(self):
        return self.notename
    def get_remark(self):
        return self.remark
    def get_payto(self):
        return self.payto
    def get_raisedby(self):
        return self.raisedby
    def get_raiserbranch(self):
        return self.raiserbranch
    def get_raisername(self):
        return self.raisername
    def get_approvedby(self):
        return self.approvedby
    def get_approvername(self):
        return self.approvername
    def get_created_by(self):
        return self.created_by
    def get_branch(self):
        return self.branch
    def get_tds(self):
        return self.tds
    def get_approver_branch(self):
        return self.approver_branch
    def get_rmcode(self):
        return self.rmcode
    def get_client_code(self):
        return self.client_code
    def get_ap_status(self):
        return self.ap_status



