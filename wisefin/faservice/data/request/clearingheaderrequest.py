import json

class ClearingHeaderRequest:

    id =  assettype = invoicecount =  totinvoiceamount =  tottaxamount =  totamount = \
    balanceamount =  groupno  =  remarks = None
    capitalizedamount = 0

    def __init__(self, clearing_data):
        if 'id' in clearing_data:
            self.id = clearing_data['id']
        if 'assettype' in clearing_data:
            self.assettype = clearing_data['assettype']
        if 'invoicecount' in clearing_data:
            self.invoicecount = clearing_data['invoicecount']
        if 'totinvoiceamount' in clearing_data:
            self.totinvoiceamount = clearing_data['totinvoiceamount']
        if 'tottaxamount' in clearing_data:
            self.tottaxamount = clearing_data['tottaxamount']
        if 'totamount' in clearing_data:
            self.totamount = clearing_data['totamount']
        if 'capitalizedamount' in clearing_data:
            self.capitalizedamount = clearing_data['capitalizedamount']
        if 'balanceamount' in clearing_data:
            self.balanceamount = clearing_data['balanceamount']
        if 'groupno' in clearing_data:
            self.groupno = clearing_data['groupno']
        if 'remarks' in clearing_data:
            self.remarks = clearing_data['remarks']



    def get_id(self):
        return self.id
    def get_assettype(self):
        return self.assettype
    def get_invoicecount(self):
        return self.invoicecount
    def get_totinvoiceamount(self):
        return self.totinvoiceamount
    def get_tottaxamount(self):
        return self.tottaxamount
    def get_totamount(self):
        return self.totamount
    def get_capitalizedamount(self):
        return self.capitalizedamount
    def get_balanceamount(self):
        return self.balanceamount
    def get_groupno(self):
        return self.groupno
    def get_remarks(self):
        return self.remarks


class ClearanceBucketRequest:

    ClrHeader_Updateids = ClrHeader_Gid  = Tot_Tax = Tot_Amount = Tot_InvAmount = Inv_Count =\
    FaClrance_GrpName = Tot_BalanceAmount =None

    def __init__(self, clringdatas):
        for clearing_data in clringdatas:
            if 'FA_ClrHeader_Updateids' in clearing_data:
                self.ClrHeader_Updateids = clearing_data['FA_ClrHeader_Updateids']
            if 'FA_ClrHeader_Gid' in clearing_data:
                self.ClrHeader_Gid = clearing_data['FA_CltHeader_Gid']
            if 'Tot_Tax' in clearing_data:
                self.Tot_Tax = clearing_data['Tot_Tax']
            if 'Tot_Amount' in clearing_data:
                self.Tot_Amount = clearing_data['Tot_Amount']
            if 'Tot_InvAmount' in clearing_data:
                self.Tot_InvAmount = clearing_data['Tot_InvAmount']
            if 'Inv_Count' in clearing_data:
                self.Inv_Count = clearing_data['Inv_Count']
            if 'FaClrance_GrpName' in clearing_data:
                self.FaClrance_GrpName = clearing_data['FaClrance_GrpName']
            if 'Tot_BalanceAmount' in clearing_data:
                self.Tot_BalanceAmount = clearing_data['Tot_BalanceAmount']


class BucketRequest:
    code = name = doctype = status = created_by = created_date = updated_by = updated_date = None
    def __init__(self, bucket_data):
        if ("code" in bucket_data):
            self.code = bucket_data["code"]
        if ("name" in bucket_data):
            self.name = bucket_data["name"]
        if ("doctype" in bucket_data):
            self.doctype = bucket_data["doctype"]
        if ("status" in bucket_data):
            self.status = bucket_data["status"]
        if ("created_by" in bucket_data):
            self.created_by = bucket_data["created_by"]
        if ("created_date" in bucket_data):
            self.created_date = bucket_data["created_date"]
        if ("updated_by" in bucket_data):
            self.updated_by = bucket_data["updated_by"]
        if ("updated_date" in bucket_data):
            self.updated_date = bucket_data["updated_date"]