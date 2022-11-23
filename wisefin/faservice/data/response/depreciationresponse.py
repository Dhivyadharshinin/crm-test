import json
from datetime import datetime


class DepreciationResponse:
    depreciation_gid = assetdetails_id = assetdetails_gid = asst_id = depreciation_fromdate = depreciation_todate = \
        depreciation_month = \
        assetdetails_cost = assetcat_subcatname = asset_cap_date = depreciation_year = depreciation_itcvalue = \
        depreciation_cavalue = depreciation_mgmtvalue = depreciation_gl = depreciation_resgl = depreciation_value = \
        depreciation_type = asset_branch_name = It_Catname = Opening_WDV =Additions_GreaterThan_180Days = Additions_LessThan_180Days =\
        Sale_Value= Closing_Balance = Value_Before_Depreciation= None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_depreciation_gid(self, depreciation_gid):
        self.depreciation_gid = depreciation_gid
    def set_assetdetails_gid(self, assetdetails_gid):
        self.assetdetails_gid = assetdetails_gid
    def set_asst_id(self, asst_id):
        self.asst_id = asst_id
    def set_depreciation_fromdate(self, depreciation_fromdate):
        split_fromdate = datetime.strptime(str(depreciation_fromdate), '%Y-%m-%d').date()
        self.depreciation_fromdate = str(split_fromdate)
    def set_depreciation_todate(self, depreciation_todate):
        split_todate = datetime.strptime(str(depreciation_todate), '%Y-%m-%d').date()
        self.depreciation_todate = str(split_todate)
    def set_depreciation_month(self, depreciation_month):
        self.depreciation_month = depreciation_month
    def set_assetcat_subcatname(self, assetcat_subcatname):
        self.assetcat_subcatname = assetcat_subcatname
    def set_asset_cap_date(self, asset_cap_date):
        split_capdate = datetime.strptime(str(asset_cap_date), '%Y-%m-%d').date()
        self.asset_cap_date = str(split_capdate)
    def set_depreciation_year(self, depreciation_year):
        self.depreciation_year = depreciation_year
    def set_depreciation_itcvalue(self, depreciation_itcvalue):
        self.depreciation_itcvalue = str(depreciation_itcvalue)
    def set_depreciation_cavalue(self, depreciation_cavalue):
        self.depreciation_cavalue = str(depreciation_cavalue)
    def set_depreciation_mgmtvalue(self, depreciation_mgmtvalue):
        self.depreciation_mgmtvalue = str(depreciation_mgmtvalue)
    def set_depreciation_gl(self, depreciation_gl):
        self.depreciation_gl = str(depreciation_gl)
    def set_depreciation_resgl(self, depreciation_resgl):
        self.depreciation_resgl = str(depreciation_resgl)
    def set_depreciation_value(self, depreciation_value):
        self.depreciation_value = str(depreciation_value)
    def set_depreciation_type(self, depreciation_type):
        self.depreciation_type = depreciation_type
    def set_asset_branch_name(self, asset_branch_name):
        self.asset_branch_name = asset_branch_name
    def set_assetcat_deptype(self, assetcat_deptype):
        self.assetcat_deptype = assetcat_deptype
    def set_assetdetails_id(self, assetdetails_id):
        self.assetdetails_id = assetdetails_id
    def set_assetdetails_cost(self, assetdetails_cost):
        self.assetdetails_cost = str(assetdetails_cost)
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_It_Catname(self, itcatname):
        self.It_Catname = itcatname
    def set_Opening_WDV(self, dep_itopening):
        self.Opening_WDV = int(dep_itopening)
    def set_Additions_GreaterThan_180Days(self, revadditions_1):
        self.Additions_GreaterThan_180Days = int(revadditions_1)
    def set_Additions_LessThan_180Days(self, revadditions_2):
        self.Additions_LessThan_180Days = int(revadditions_2)
    def set_Sale_Value(self, dep_deletion):
        self.Sale_Value = int(dep_deletion)
    def set_Closing_Balance(self, dep_closingblnce):
        self.Closing_Balance = int(dep_closingblnce)
    def set_Value_Before_Depreciation(self, dep_value_before_depreciation):
        self.Value_Before_Depreciation = int(dep_value_before_depreciation)
