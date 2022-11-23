import json

class APHeaderRequest:

    id = None
    supplier_type_id = None
    supplier_type = None
    commodity = None
    file_id = None
    crno = None
    aptype = None
    apdate = None
    apamount = None
    apstatus = None
    ecftype_id = None
    ecfdate = None
    ecfamount = None
    ecfstatus = None
    ppx_id = "S"
    dueadjustment = None
    notename = None
    remark = None
    payto = 'S'
    raisedby = None
    raiserbranch = None
    raisername = None
    approvedby = None
    approvername = None
    created_by = None
    inwarddetails_id = None
    ecfstatus_id = None
    tds_id = None
    approver_branch_id=None
    choseapprover_branch_id=None
    client_code_id=None
    rmcode_id=None


    def __init__(self,obj_aphdr,direct_entry):
        if 'id' in obj_aphdr:
            self.id=obj_aphdr['id']
        if 'supplier_type_id' in obj_aphdr:
            self.supplier_type_id = obj_aphdr['supplier_type_id']
        if 'commodity_id' in obj_aphdr:
            self.commodity = obj_aphdr['commodity_id']['id']
        if 'file_id' in obj_aphdr:
            self.file_id=obj_aphdr['file_id']
        if 'crno' in obj_aphdr:
            self.crno = obj_aphdr['crno']
        if 'aptype' in obj_aphdr:
            self.aptype=obj_aphdr['aptype']
        if 'apdate' in obj_aphdr:
            self.apdate = obj_aphdr['apdate']
        if 'apamount' in obj_aphdr:
            self.apamount=obj_aphdr['apamount']
        if 'apstatus' in obj_aphdr:
            self.apstatus = obj_aphdr['apstatus']
        if 'ecftype_id' in obj_aphdr:
            self.ecftype_id=obj_aphdr['ecftype_id']
        if 'ecfdate' in obj_aphdr:
            self.ecfdate = obj_aphdr['ecfdate']
        if 'ecfamount' in obj_aphdr:
           self.ecfamount=obj_aphdr['ecfamount']
        if 'ecfstatus' in obj_aphdr:
            self.ecfstatus = obj_aphdr['ecfstatus']
        if 'ecfstatus_id' in obj_aphdr:
            self.ecfstatus_id = obj_aphdr['ecfstatus_id']
        if 'ppx_id' in obj_aphdr:
            if obj_aphdr['ppx_id'] is not None:
                if 'id' in obj_aphdr['ppx_id']:
                    self.ppx_id=obj_aphdr['ppx_id']['id']
        if 'dueadjustment' in obj_aphdr:
            self.dueadjustment = obj_aphdr['dueadjustment']
        if 'notename' in obj_aphdr:
            self.notename=obj_aphdr['notename']
        if 'remark' in obj_aphdr:
            self.remark = obj_aphdr['remark']
        if 'payto_id' in obj_aphdr:
            if obj_aphdr['payto_id'] is not None:
                if 'id' in obj_aphdr['payto_id']:
                    self.payto=obj_aphdr['payto_id']['id']
        if 'raisedby' in obj_aphdr:
            self.raisedby = obj_aphdr['raisedby']
        if 'raiserbranch' in obj_aphdr:
            self.raiserbranch=obj_aphdr['raiserbranch']['id']
        if 'raisername' in obj_aphdr:
            self.raisername = obj_aphdr['raisername']
        if 'approvedby' in obj_aphdr:
            self.approvedby=obj_aphdr['approvedby']
        if 'approvername' in obj_aphdr:
            self.approvername = obj_aphdr['approvername']
        if 'created_by' in obj_aphdr:
            self.created_by = obj_aphdr['created_by']
        if 'inwarddetails_id' in obj_aphdr:
            self.inwarddetails_id = obj_aphdr['inwarddetails_id']
        if 'data' in obj_aphdr:
            if 'tds' in obj_aphdr['data']:
                if 'id' in obj_aphdr['data']['tds']:
                    self.tds_id = obj_aphdr['data']['tds']['id']
            if 'approverbranch' in obj_aphdr['data']:
                self.approver_branch_id= obj_aphdr['data']['approverbranch']['id']
        if 'branch' in obj_aphdr:
            if obj_aphdr['branch'] is not None :
                if 'id' in obj_aphdr['branch']:
                    self.choseapprover_branch_id= obj_aphdr['branch']['id']
        #here validation for it is direct entry
        if direct_entry:
            if 'client_code_id' in obj_aphdr:
                self.client_code_id = obj_aphdr['client_code_id']
            if 'rmcode_id' in obj_aphdr:
                self.rmcode_id = obj_aphdr['rmcode_id']
        else:
            if 'client_code' in obj_aphdr:
                if obj_aphdr['client_code'] is not None:
                    if  'id' in obj_aphdr['client_code']:
                        self.client_code_id = obj_aphdr['client_code']['id']
            if 'rmcode' in obj_aphdr:
                if obj_aphdr['rmcode'] is not None:
                    if  'id' in obj_aphdr['rmcode']:
                        self.rmcode_id = obj_aphdr['rmcode']['id']



    def get_id(self):
        return self.id
    def get_supplier_type(self):
        return self.supplier_type_id
    def get_commodity_id(self):
        return self.commodity
    def get_file_id(self):
        return self.file_id
    def get_aptype(self):
        return self.aptype
    def get_apdate(self):
        return self.apdate
    def get_apamount(self):
        return self.apamount
    def get_apstatus(self):
        return self.apstatus

    def get_ecftype(self):
        return self.ecftype_id
    def get_ecfdate(self):
        return self.ecfdate
    def get_ecfamount(self):
        return self.ecfamount
    def get_ecfstatus(self):
        return self.ecfstatus

    def get_crno(self):
        return self.crno
    def get_ppx_id(self):
        return self.ppx_id
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
    def get_inwarddetails_id(self):
        return self.inwarddetails_id
    def get_ecfstatus_id(self):
        return self.ecfstatus_id
    def get_tds_id(self):
        return self.tds_id
    def get_approver_branch_id(self):
        return self.approver_branch_id
    def get_choseapprover_branch_id(self):
        return self.choseapprover_branch_id
    def get_client_code(self):
        return self.client_code_id
    def get_rmcode(self):
        return self.rmcode_id



#**************--------------APHeaderRequest---------------***************




class APppxHeaderRequest:

    id = None
    apinvoiceheader_id = None
    crno = None
    ppxheader_date = None
    ppxheader_amount = None
    ppxheader_balance = None


    def __init__(self,obj_aphdr):
        if 'id' in obj_aphdr:
            self.id=obj_aphdr['id']
        if 'apinvoiceheader_id' in obj_aphdr:
            self.apinvoiceheader_id = obj_aphdr['apinvoiceheader_id']
        if 'crno' in obj_aphdr:
            self.crno = obj_aphdr['crno']
        if 'ppxheader_date' in obj_aphdr:
            self.ppxheader_date=obj_aphdr['ppxheader_date']
        if 'ppxheader_amount' in obj_aphdr:
            self.ppxheader_amount=obj_aphdr['ppxheader_amount']
        if 'ppxheader_balance' in obj_aphdr:
            self.ppxheader_balance = obj_aphdr['ppxheader_balance']



    def get_id(self):
        return self.id
    def get_apinvoiceheader_id(self):
        return self.apinvoiceheader_id
    def get_crno(self):
        return self.crno
    def get_ppxheader_date(self):
        return self.ppxheader_date
    def get_ppxheader_amount(self):
        return self.ppxheader_amount
    def get_ppxheader_balance(self):
        return self.ppxheader_balance


#***********-------APppxHeaderRequest----------***************


class APppxDetailsRequest:

    id = None
    apppxheader_id = None
    apinvoiceheader_id = None
    apcredit_id = None
    ppxdetails_amount =None
    ppxdetails_adjusted = None
    ppxdetails_balance = None
    is_closed = None
    ecf_amount = 0
    ap_amount = 0
    process_amount = 0
    ecfheader_id = None
    ppxlique_crno = None


    def __init__(self,obj_aphdr):
        if 'id' in obj_aphdr:
            self.id=obj_aphdr['id']
        if 'apppxheader_id' in obj_aphdr:
            self.apppxheader_id = obj_aphdr['apppxheader_id']
        if 'apinvoiceheader_id' in obj_aphdr:
            self.apinvoiceheader_id = obj_aphdr['apinvoiceheader_id']
        if 'apcredit_id' in obj_aphdr:
            self.apcredit_id = obj_aphdr['apcredit_id']
        if 'ppxdetails_amount' in obj_aphdr:
            self.ppxdetails_amount=obj_aphdr['ppxdetails_amount']
        if 'ppxdetails_adjusted' in obj_aphdr:
            self.ppxdetails_adjusted=obj_aphdr['ppxdetails_adjusted']
        if 'ppxdetails_balance' in obj_aphdr:
            self.ppxdetails_balance = obj_aphdr['ppxdetails_balance']
        if 'is_closed' in obj_aphdr:
            self.is_closed = obj_aphdr['is_closed']
        if 'ecf_amount' in obj_aphdr:
            self.ecf_amount = obj_aphdr['ecf_amount']
        if 'ecfheader_id' in obj_aphdr:
            self.ecfheader_id = obj_aphdr['ecfheader_id']

        if 'process_amount' in obj_aphdr:
            self.process_amount = obj_aphdr['process_amount']

        if 'ap_amount' in obj_aphdr:
            self.ap_amount = obj_aphdr['ap_amount']

        if 'ppxlique_crno' in obj_aphdr:
            self.ppxlique_crno = obj_aphdr['ppxlique_crno']



    def get_id(self):
        return self.id
    def get_apinvoiceheader_id(self):
        return self.apinvoiceheader_id
    def get_apppxheader_id(self):
        return self.apppxheader_id
    def get_apcredit_id(self):
        return self.apcredit_id
    def get_ppxdetails_amount(self):
        return self.ppxdetails_amount
    def get_ppxdetails_adjusted(self):
        return self.ppxdetails_adjusted
    def get_ppxdetails_balance(self):
        return self.ppxdetails_balance
    def get_is_closed(self):
        return self.is_closed
    def get_ecf_amount(self):
        return self.ecf_amount

    def get_ecfheader_id(self):
        return self.ecfheader_id

    def get_process_amount(self):
        return self.process_amount

    def get_ap_amount(self):
        return self.ap_amount

    def get_ppxlique_crno(self):
        return self.ppxlique_crno


#***********-------APppxDetailsRequest----------***************
