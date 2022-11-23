import json
from datetime import datetime


class AssetUpdateResponse:
    def common_get(self,parameter):
        return json.dumps(parameter, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,input_id):
        self.id=input_id
    def set_asset_id(self,asset_id):
        self.asset_id=asset_id
    def set_assetdetails_id(self,assetdetails_id):
        self.assetdetails_id=assetdetails_id
    def set_asset_details_id(self,asset_details_id):
        self.asset_details_id=asset_details_id
    def set_assetdetails_gid(self,assetdetails_gid):
        self.assetdetails_gid=assetdetails_gid
    def set_assetdetails_productgid(self,assetdetails_productgid):
        self.assetdetails_productgid=assetdetails_productgid
    def set_assetdetails_branchgid(self,assetdetails_branchgid):
        self.assetdetails_branchgid=assetdetails_branchgid
    def set_assetdetails_value(self,assetdetails_value):
        self.assetdetails_value=str(assetdetails_value)
    def set_assetdetails_cost(self,assetdetails_cost):
        self.assetdetails_cost=str(assetdetails_cost)
    def set_branch_name(self,branch_name):
        self.branch_name=branch_name
    def set_product_name(self,product_name):
        self.product_name=product_name
    def set_product_id(self,product_id):
        self.product_id=product_id
    def set_branch_id(self,branch_id):
        self.branch_id=branch_id
    def set_barcode(self,barcode):
        self.barcode=barcode
    def set_document_id(self,document_id):
        self.barcode=document_id
    def set_asset_value(self, asset_value):
        self.asset_value = str(asset_value)
    def set_asset_cost(self, asset_cost):
        self.asset_cost = str(asset_cost)
    def set_asset_tag(self,asset_tag):
        self.asset_tag=asset_tag
    def set_make(self,make):
        self.make=make
    def set_serial_no(self,serial_no):
        self.serial_no=serial_no
    def set_cr_number(self,cr_number):
        self.cr_number=cr_number
    def set_kvb_asset_id(self,kvb_asset_id):
        self.kvb_asset_id=kvb_asset_id
    def set_condition(self,condition):
        self.condition=condition
    def set_status(self,status):
        self.status=status
    def set_remarks(self,remarks):
        self.remarks=remarks
    def set_update_record(self,update_record):
        self.update_record=update_record
    def set_pv_done(self,pv_done):
        self.pv_done=pv_done
    def set_maker_date(self,maker_date):
        # split_todate = datetime.strptime(str(maker_date), '%Y-%m-%d %H:%M:%f:').date()
        self.maker_date=str(maker_date)
    def set_checker_date(self, checker_date):
        self.checker_date = str(checker_date)
    def set_completed_date(self,completed_date):
        self.completed_date=str(completed_date)
    # def set_assetdetails_branch_name(self,assetdetails_branch_name):
    #     self.assetdetails_branch_name=assetdetails_branch_name
    def set_branch_code(self,branch_code):
        self.branch_code=branch_code
    def set_control_office_branch(self,control_office_branch):
        self.control_office_branch=control_office_branch
    def set_assetdetails_barcode(self,assetdetails_barcode):
        self.assetdetails_barcode=assetdetails_barcode

class Asset_Details_Response:
    def common_get(self,parameter):
        return json.dumps(parameter, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,input_id):
        self.id=input_id
    def set_assetdetails_gid(self,assetdetails_gid):
        self.assetdetails_gid=assetdetails_gid
    def set_assetdetails_barcode(self,assetdetails_barcode):
        self.assetdetails_barcode=assetdetails_barcode
    def set_assetdetails_productgid(self,assetdetails_productgid):
        self.assetdetails_productgid=assetdetails_productgid
    def set_assetdetails_branchgid(self,assetdetails_branchgid):
        self.assetdetails_branchgid=assetdetails_branchgid
    def set_assetdetails_poductname(self,assetdetails_poductname):
        self.assetdetails_poductname=assetdetails_poductname
    def set_assetdetails_value(self,assetdetails_value):
        self.assetdetails_value=str(assetdetails_value)
    def set_assetdetails_cost(self,assetdetails_cost):
        self.assetdetails_cost=str(assetdetails_cost)











