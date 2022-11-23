import json


class ClearingHeaderResponse:

    id = assettype = invoicecount = totinvoiceamount = tottaxamount = totamount = capitalizedamount = \
        balanceamount = groupno = remarks = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_assettype(self, assettype):
        self.assettype = assettype
    def set_invoicecount(self, invoicecount):
        self.invoicecount = invoicecount
    def set_totinvoiceamount(self, totinvoiceamount):
        self.totinvoiceamount =str(totinvoiceamount)
    def set_tottaxamount(self, tottaxamount):
        self.tottaxamount = str(tottaxamount)
    def set_totamount(self, totamount):
        self.totamount = str(totamount)
    def set_capitalizedamount(self, capitalizedamount):
        self.capitalizedamount = str(capitalizedamount)
    def set_balanceamount(self, balanceamount):
        self.balanceamount =str(balanceamount)
    def set_groupno(self, groupno):
        self.groupno = groupno
    def set_remarks(self, remarks):
        self.remarks = remarks


class BucketResponse:
    bucket_list=[]
    def add_bucket(self,bucketname,id,code):
        self.bucket_list.append({"name":bucketname,"id":id,"code":code})
    def get(self):
        return json.dumps({"data":self.bucket_list})

class SearchBucketResponce:
    id=code=name=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self,data):
        self.id=data
    def set_code(self,data):
        self.code=data
    def set_name(self,data):
        self.name=data
