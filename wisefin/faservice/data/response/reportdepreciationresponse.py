import json
class DepreciationSettingResponse:
    Asset_ID = Product_Name = Branch_Code = Branch_Name = Dep_Type = Dep_GL = Asset_GL = Dep_From_Date = Dep_To_Date = Class = Cat_No = \
        Sub_Cat_No = Asset_Create_Date = End_Date = Dep_Rate = Purchase_cost = Dep_Yr_Closing_Balance = Additions_After_Last_Dep = \
        Removal = Asset_Val_Before_Dep = Dep_Value = Closing_Balance = acc_branch_code = Assert_Status = ITOD = SOLD = subcat_id =\
        subcat_glno = subcat_no = cat_id = Branch_id = product_id = product_code \
        = product_name = dep_fromdate = dep_todate = yrclosingblnce = deptmp_todate = None

    def get(self):
        return self.__dict__

    def set_Asset_ID(self, Asset_ID):
        self.Asset_ID = Asset_ID
    def set_Product_Name(self, Product_Name):
        self.Product_Name = Product_Name
    def set_Branch_Code(self, Branch_Code):
        self.Branch_Code = Branch_Code
    def set_Branch_Name(self, Branch_Name):
        self.Branch_Name = Branch_Name
    def set_Dep_Type(self, Dep_Type):
        self.Dep_Type = Dep_Type
    def set_Dep_GL(self, Dep_GL):
        self.Dep_GL = Dep_GL
    def set_Asset_GL(self, Asset_GL):
        self.Asset_GL = Asset_GL
    def set_Dep_From_Date(self, Dep_From_Date):
        self.Dep_From_Date = Dep_From_Date
    def set_Dep_To_Date(self, Dep_To_Date):
        self.Dep_To_Date = Dep_To_Date
    def set_Class(self, Class):
        self.Class = Class
    def set_Cat_No(self, Cat_No):
        self.Cat_No = Cat_No
    def set_Sub_Cat_No(self, Sub_Cat_No):
        self.Sub_Cat_No = Sub_Cat_No
    def set_Asset_Create_Date(self, Asset_Create_Date):
        self.Asset_Create_Date = Asset_Create_Date
    def set_Cap_Date(self, Cap_Date):
        self.Cap_Date = Cap_Date
    def set_End_Date(self, End_Date):
        self.End_Date = End_Date
    def set_Dep_Rate(self, Dep_Rate):
        self.Dep_Rate = Dep_Rate
    def set_Purchase_cost(self, Purchase_cost):
        self.Purchase_cost = Purchase_cost
    def set_Dep_Yr_Closing_Balance(self, Dep_Yr_Closing_Balance):
        self.Dep_Yr_Closing_Balance = Dep_Yr_Closing_Balance
    def set_Additions_After_Last_Dep(self, Additions_After_Last_Dep):
        self.Additions_After_Last_Dep = Additions_After_Last_Dep
    def set_Removal(self, Removal):
        self.Removal = Removal
    def set_Asset_Val_Before_Dep(self, Asset_Val_Before_Dep):
        self.Asset_Val_Before_Dep = Asset_Val_Before_Dep
    def set_Dep_Value(self, Dep_Value):
        self.Dep_Value = Dep_Value
    def set_Closing_Balance(self, Closing_Balance):
        self.Closing_Balance = Closing_Balance
    def set_acc_branch_code(self, acc_branch_code):
        self.acc_branch_code = acc_branch_code
    def set_Assert_Status(self, Assert_Status):
        self.Assert_Status = Assert_Status
    def set_ITOD(self, ITOD):
        self.ITOD = ITOD
    def set_SOLD(self, SOLD):
        self.SOLD = SOLD

    def set_sucatdata(self,subcatdata_id,arr):
        for i in arr:
            if i.id == subcatdata_id:
                self.subcat_id = i.id
                self.subcat_glno = i.glno
                self.subcat_no = i.no
                self.cat_id = i.category.id

    def set_branchdata(self,branch_id,arr):
        for i in arr:
            if i.id == branch_id:
                self.Branch_id=i.id
                self.Branch_Code=i.code
                self.Branch_Name=i.name

    def set_productdata(self,product_id,arr):
        for i in arr:
            if i.id == product_id:
                self.product_id=i.id
                self.product_code=i.code
                self.product_name=i.name

    def set_depdata(self,asset_id,arr):
        for i in arr:
            if i.id == asset_id:
                self.dep_fromdate=i.depreciation_fromdate
                self.dep_todate=i.depreciation_todate
                self.yrclosingblnce=i.yrclosingblnce

    def set_deptmpdata(self,asset_id,arr):
        for i in arr:
            if i.id == asset_id:
                self.deptmp_todate=i.depreciation_todate


    def get_dep_fromdate(self):
        return self.dep_fromdate
    def get_dep_todate(self):
        return self.dep_todate
    def get_yrclosingblnce(self):
        return self.yrclosingblnce
    def get_deptmp_todate(self):
        return self.deptmp_todate


