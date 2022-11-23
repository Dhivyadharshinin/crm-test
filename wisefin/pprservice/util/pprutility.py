from masterservice.models.mastermodels import Apcategory, APexpense, APsubcategory,APexpensegroup
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from pprservice.data.response.pprfilterresponse import Ppr_MBS_BS_CCresponse
from userservice.models import EmployeeBranch, Employee,BusinessSegment,CostCentre,MasterBusinessSegment,CostCentreBusinessSegmentMaping
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.supplierresponse import BranchResponse
from vendorservice.models import SupplierBranch
from pprservice.util.fasDB import DataBase
# from userservice.models.usermodels import Employee,EmployeeBranch,BusinessSegment,CostCentre,MasterBusinessSegment,CostCentreBusinessSegmentMaping
from pprservice.models.pprmodel import AllocationLevel, bscc_maping, CostDriver, PPR_history, Allocation_meta
from django.db.models import Q, Sum
from masterservice.models.mastermodels import MasterBusinessSegment as master

class VENDOR_SERVICE(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)


    def get_pprsupplier(self, arr, query):
        condition = Q(id__in=arr, entity_id=self._entity_id())
        if query != None:
            condition &= Q(vendor__name__icontains=query)
        supplier_detial = SupplierBranch.objects.using(self._current_app_schema()).filter(condition)
        final_arr = []
        for i in supplier_detial:
            final_arr.append({"supplier_id": i.id, "supplier_name": i.vendor.name,
                              "supplier_code": i.code,
                              "supplier_branchname": i.name, "supplier_panno": i.panno,
                              "supplier_gstno": i.gstno})
        return final_arr

    def get_supplier(self, arr):
        supplier_detial = SupplierBranch.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                          entity_id=self._entity_id())
        final_arr = []
        for i in supplier_detial:
            final_arr.append({"supplier_id": i.id, "supplier_name": i.vendor.name,
                              "supplier_code": i.code,
                              "supplier_branchname": i.name, "supplier_panno": i.panno,
                              "supplier_gstno": i.gstno})

        return final_arr

    def supplier_list(self, vys_page, query):
        condition = Q(modify_status=-1)
        if query != None:
            condition &= (Q(name__icontains=query) | Q(code__icontains=query))
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).filter(condition).order_by(
                'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            branchlist = SupplierBranch.objects.using(self._current_app_schema()).all().order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        if len(branchlist) != 0:
            for branch in branchlist:
                branch_data = BranchResponse()
                branch_name = branch.name
                branch_code = branch.code
                branch_id = branch.id
                print("barcnh", branch_id)
                city_id = branch.address.city_id

                print("city_id", city_id)
                state_id = branch.address.state_id
                comm_ser = CityService(self._scope())
                city = comm_ser.fetch_cityone(city_id)
                city_name = city['name']
                pos_ser = StateService(self._scope())
                state = pos_ser.fetch_stateone(state_id)
                state_name = state['name']
                code_name = '(' + branch_code + ') ' + branch_name + ' - ' + city_name + ' - ' + state_name
                branch_data.set_id(branch.id)
                branch_data.set_vendor_id(branch.vendor_id)
                branch_data.set_name(code_name)
                branch_data.set_code(branch.code)
                vlist.data.append(branch_data)
            vpage = NWisefinPaginator(branchlist, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
        return vlist

class MASTER_SERVICE(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def get_subcat(self, arr):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(id__in=arr,entity_id=self._entity_id())
        finall_all = []
        for i in obj:
            finall_all.append({"subcat_id": i.id,"subcat_name": i.name, "category_id": i.category.id,
                               "category_name": i.category.name})

        return finall_all

    def get_subcat_expgrp(self,arr):
        exp_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=arr,entity_id=self._entity_id()).values("glno","category__expense__exp_grp_id","category__expense__head","category__expense__id",
                                                                    "category__id","category__name","id", "name")
        return exp_dtls

    def get_subcat_exp(self,arr,id):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(glno=arr,entity_id=self._entity_id(),category__expense__exp_grp_id=id).values('category__expense__id','glno','category__expense__head','category__expense__exp_grp_id')
        return obj

    def get_expense(self, arr):
        final_arr = []
        obj = APexpense.objects.using(self._current_app_schema()).filter(id__in=arr,entity_id=self._entity_id())
        for i in obj:
            final_arr.append({'expense_id': i.id, 'expense_head': i.head, 'expense_group': i.group})

        return final_arr

    def get_expense_expensegrp(self, arr):
        final_arr = []
        expense_id = APexpense.objects.using(self._current_app_schema()).filter(group=arr,entity_id=self._entity_id())
        for i in expense_id:
            final_arr.append(i.id)
        return final_arr
    def get_expense_expensegrp_id(self, arr):
        final_arr = []
        expense_id = APexpense.objects.using(self._current_app_schema()).filter(exp_grp_id=arr,entity_id=self._entity_id())
        for i in expense_id:
            final_arr.append(i.id)
        return final_arr

    def get_new_expense_expensegrp(self,name):
        final_arr = []
        expense_id = APexpense.objects.using(self._current_app_schema()).filter(group=name,entity_id=self._entity_id())
        for i in expense_id:
            final_arr.append(i.id)
        return final_arr

    def get_cat_dtls(self, arr):
        cat_data = Apcategory.objects.using(self._current_app_schema()).filter(id__in=arr,entity_id=self._entity_id()).values('id', 'code', 'name')
        return cat_data

    def get_category(self, arr):
        final_arr = []
        obj = Apcategory.objects.using(self._current_app_schema()).filter(id__in=arr, entity_id=self._entity_id())
        for i in obj:
            final_arr.append({'expense_id': i.expense_id, 'cat_id': i.id, 'categoryname': i.name})

        return final_arr

    def get_cat_subcat(self, arr):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(id__in=arr, entity_id=self._entity_id())
        finall_all = []
        for i in obj:
            finall_all.append({"subcat_id": i.id, "subcat_name": i.name, "expense_id": i.category.expense_id,
                               "category_id": i.category_id,"glno":i.glno})
        return finall_all

    def get_all_expgrp(self):
        expense_id = APexpensegroup.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).all().values('id', 'name')
        return expense_id

    def get_new_expgrp_exp(self, arr):
        expense_id = APexpense.objects.using(self._current_app_schema()).filter(exp_grp_id__in=arr,
                                                                                entity_id=self._entity_id())
        final_arr = []
        for i in expense_id:
            final_arr.append(i.id)
        return final_arr

    def get_subcat_cat(self, arr,id):
        obj = APsubcategory.objects.using(self._current_app_schema()).filter(glno=arr, entity_id=self._entity_id(),
                                                                             category__expense__id=id).values(
            'category__id', 'category__name', 'category__expense__id', 'glno', 'category__expense__head',
            'category__expense__exp_grp_id')
        return obj

    def costcentre(self, businessid, query, vys_page):
        condition = Q(status=1, entity_id=self._entity_id())
        if query != None:
            condition &= Q(name__icontains=query)
        if businessid != None:
            condition &= Q(businesssegment_id=businessid)

        costcentre = CostCentre.objects.using(self._current_app_schema()).filter(condition)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(costcentre) <= 0:
            pass
        else:
            for i in costcentre:
                ppr_response = Ppr_MBS_BS_CCresponse()
                ppr_response.set_id(i.id)
                ppr_response.set_name(i.name)
                pro_list.data.append(ppr_response)
            vpage = NWisefinPaginator(costcentre, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list

    def get_expense_grp(self, data):
        expgrp_dtls = APexpensegroup.objects.using(self._current_app_schema()).filter(
            id=data).values("id", "name")
        return expgrp_dtls
    def get_expense_head(self,data):
        expgrp_dtls = APexpense.objects.using(self._current_app_schema()).filter(
            id=data).values("id", "head")
        return expgrp_dtls

    def get_subcat_glno(self, arr, id):
        subcat_dtls = APsubcategory.objects.using(self._current_app_schema()).filter(glno=arr, category__id=id,entity_id=self._entity_id()).values("glno","category__expense__exp_grp_id","category__expense__head","category__expense__id","category__id","category__name","id", "name")
        return subcat_dtls

    def get_mstbissegment(self, arr):
        final_arr = []
        bscc_data = master.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                           entity_id=self._entity_id())
        for i in bscc_data:
            final_arr.append({"id": i.id, "name": i.name})
        return final_arr

    def get_mstsegment(self, arr):
        final_arr = []
        bscc_data = master.objects.using(self._current_app_schema()).filter(name__in=arr,
                                                                                           entity_id=self._entity_id()).values(
            "id", "code", "name")

        for i in bscc_data:
            final_arr.append({"id": i["id"], "code": i['code'], "name": i['name']})
        return final_arr

    def ppr_mstbusinesssegement(self, query, vys_page):  #
        condition = Q(status=1)
        if query != None:
            condition &= Q(name__icontains=query)
        mstbusiness = master.objects.using(self._current_app_schema()).filter(condition)[
                      vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(mstbusiness) <= 0:
            pass
        else:
            for i in mstbusiness:
                ppr_response = Ppr_MBS_BS_CCresponse()
                ppr_response.set_id(i.id)
                ppr_response.set_name(i.name)
                pro_list.append(ppr_response)
        vpage = NWisefinPaginator(mstbusiness, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

    def get_subcatgl_exphead(self,obj):
        gl_condition = APsubcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),category__expense__exp_grp_id=obj).values_list('glno',flat=True).distinct()
        return gl_condition

    def get_subcatgl_cat(self,expgrp,exphead):
        gl_condition = APsubcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),category__expense__exp_grp_id=expgrp,category__expense__id=exphead).values_list('glno',flat=True).distinct()
        return gl_condition

    def get_subcatgl_subcat(self,expgrp,exphead,cat_id):
        gl_condition = APsubcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),category__expense__exp_grp_id=expgrp,category__expense__id=exphead,category__id=cat_id).values_list('glno',flat=True).distinct()
        return gl_condition

    def get_subcat_expense(self):
        subcat_obj=APsubcategory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),glno__startswith='4').values_list('id',flat=True).distinct()
        return subcat_obj

    def get_BS_id(self, arr):
        from masterservice.models.mastermodels import BusinessSegment
        BS_data = BusinessSegment.objects.using(self._current_app_schema()).filter(id__in=arr, entity_id=self._entity_id()).values('id', 'code', 'name')
        return BS_data

    def get_BS(self, arr):
        from masterservice.models.mastermodels import BusinessSegment
        BS_data = BusinessSegment.objects.using(self._current_app_schema()).filter(name__in=arr, entity_id=self._entity_id()).values('id', 'code', 'name')
        return BS_data

    def get_CC_id(self, arr):
        from masterservice.models.mastermodels import CostCentre
        CC_data = CostCentre.objects.using(self._current_app_schema()).filter(id__in=arr,entity_id=self._entity_id()).values(
            'id', 'code', 'name')
        return CC_data

    def get_mstsegment_id(self, arr):
        final_arr = []
        bscc_data = master.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                           entity_id=self._entity_id()).values(
            "id", "code", "name")

        for i in bscc_data:
            final_arr.append({"id": i["id"], "code": i['code'], "name": i['name']})
        return final_arr

    def businesssegement(self, query, vys_page):  #
        condition = Q(status=1)
        if query != None:
            condition &= Q(name__icontains=query)
        from masterservice.models.mastermodels import BusinessSegment
        mstbusiness = BusinessSegment.objects.using(self._current_app_schema()).filter(condition,entity_id=self._entity_id())[
                      vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(mstbusiness) <= 0:
            pass
        else:
            for i in mstbusiness:
                ppr_response = Ppr_MBS_BS_CCresponse()
                ppr_response.set_id(i.id)
                ppr_response.set_name(i.name)
                pro_list.append(ppr_response)
        vpage = NWisefinPaginator(mstbusiness, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

    def cc(self, query, vys_page):  #
        condition = Q(status=1)
        if query != None:
            condition &= Q(name__icontains=query)
        from masterservice.models.mastermodels import CostCentre
        mstbusiness = CostCentre.objects.using(self._current_app_schema()).filter(condition,entity_id=self._entity_id())[
                      vys_page.get_offset():vys_page.get_query_limit()]
        pro_list = NWisefinList()
        if len(mstbusiness) <= 0:
            pass
        else:
            for i in mstbusiness:
                ppr_response = Ppr_MBS_BS_CCresponse()
                ppr_response.set_id(i.id)
                ppr_response.set_name(i.name)
                pro_list.append(ppr_response)
        vpage = NWisefinPaginator(mstbusiness, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list

class USER_SERVICE(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def get_branch_code(self,arr):
        branch_id = EmployeeBranch.objects.using(self._current_app_schema()).filter(code__in=arr)
        return branch_id


    def get_mst_segment(self, arr):
        final_arr = []
        bscc_data = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                           entity_id=self._entity_id())
        for i in bscc_data:
            final_arr.append({"id": i.id, "code": i.code, "name": i.name})
        return final_arr



    def get_CC(self, arr):
        CC_data = CostCentre.objects.using(self._current_app_schema()).filter(id__in=arr,entity_id=self._entity_id()).values(
            'id', 'code', 'name')
        return CC_data

    def get_CC_Code(self, arr):
        CC_data = CostCentre.objects.filter(code__in=arr, entity_id=self._entity_id()).values('id', 'code', 'name')
        return CC_data


    def get_BS_Code(self, arr):
        BS_data = BusinessSegment.objects.filter(code__in=arr, entity_id=self._entity_id()).values('id', 'code', 'name')
        return BS_data

    def get_finyear_quter_transationmonth(self, date):
        date_split = date.split("-")
        if int(date_split[1]) >= 1 and int(date_split[1]) <= 3:
            finyear = f"FY{int(date_split[0][-2:]) - 1}-{int(date_split[0][-2:])}"
            quater = 4
            transationmonth = date_split[1]
        elif int(date_split[1]) >= 4 and int(date_split[1]) <= 12:
            finyear = f"FY{int(date_split[0][-2:])}-{int(date_split[0][-2:]) + 1}"
            if int(date_split[1]) >= 4 and int(date_split[1]) <= 6:
                quater = 1
            elif int(date_split[1]) >= 7 and int(date_split[1]) <= 9:
                quater = 2
            elif int(date_split[1]) >= 10 and int(date_split[1]) <= 12:
                quater = 3
            transationmonth = date_split[1]
        outdate = {"finyear": finyear, "quater": quater, "transationmonth": transationmonth, "year": date_split[0],
                   "date": date}
        return outdate

    def get_ccbs(self,bsARR,ccARR):
        ccbs_data = CostCentreBusinessSegmentMaping.objects.using(self._current_app_schema()).filter(businesssegment__in=bsARR,costcentre__in=ccARR,entity_id=self._entity_id()).values('id','name','code','costcentre','businesssegment')
        return ccbs_data

    def get_employee_data(self, arr):
        emp_obj = Employee.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                            entity_id=self._entity_id()).values('id',
                                                                                                                'code',
                                                                                                                'full_name',
                                                                                                                'designation',
                                                                                                                'employee_branch__name')
        return emp_obj

    def get_uniqarr(self,arr):
        final_arr = []
        for i in arr:
            if i not in final_arr:
                final_arr.append(i)
        return final_arr

    def code_id_fields(self,arr):
        userservice=USER_SERVICE(self._scope())
        masterservice=MASTER_SERVICE(self._scope())
        vendorservice=VENDOR_SERVICE(self._scope())
        expense_code = []
        category_code = []
        subcategory_code = []
        invoiceheader_suppliergid = []
        branch = []
        bs_code = []
        cc_code = []
        for i in arr:
            expense_code.append(i["expense_gid"])
            category_code.append(i["category_code"])
            subcategory_code.append(i["subcategory_code"])
            invoiceheader_suppliergid.append(i["invoiceheader_suppliergid"])
            branch.append(i["invoiceheader_branchgid"])
            bs_code.append(i["tbs_code"])
            cc_code.append(i["tcc_code"])
        # expense_id = APexpense.objects.using(self._current_app_schema()).filter(code__in=expense_code,entity_id=self._entity_id())
        expense_id =masterservice.get_expense(expense_code)
        # cat_id = Apcategory.objects.using(self._current_app_schema()).filter(code__in=category_code,entity_id=self._entity_id())
        cat_id =masterservice.get_cat_data(category_code)
        # subcat_id = APsubcategory.objects.using(self._current_app_schema()).filter(code__in=subcategory_code,category_id__in=self.get_cat(cat_id),entity_id=self._entity_id())
        subcat_id = masterservice.get_subcat(subcategory_code)
        # supplier_id = SupplierBranch.objects.using(self._current_app_schema()).filter(code__in=invoiceheader_suppliergid,entity_id=self._entity_id())
        supplier_id =vendorservice.get_supplier(invoiceheader_suppliergid)
        # branch_id = EmployeeBranch.objects.using(self._current_app_schema()).filter(code__in=branch,entity_id=self._entity_id())
        branch_id =userservice.get_branch_code(branch)
        # bs_id = BusinessSegment.objects.using(self._current_app_schema()).filter(code__in=bs_code,entity_id=self._entity_id())
        bs_id = userservice.get_BS_Code(bs_code)
        # cc_id = CostCentre.objects.using(self._current_app_schema()).filter(code__in=cc_code,entity_id=self._entity_id())
        cc_id = userservice.get_CC_Code(cc_code)
        out_data = {"expense":expense_id,"category":cat_id,"subcategory":subcat_id,"supplier":supplier_id,"branch":branch_id,"bs":bs_id,"cc":cc_id}
        return out_data

    def get_bs(self, arr):
        BS_data = BusinessSegment.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                   entity_id=self._entity_id()).values(
            'id', 'code', 'name')
        return BS_data

    def get_cc(self, arr):
        CC_data = CostCentre.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                              entity_id=self._entity_id()).values(
            'id', 'code', 'name')
        return CC_data

    def get_branch_id(self,arr):
        branch_id = EmployeeBranch.objects.using(self._current_app_schema()).filter(code__in=arr).values("id","name","code")
        return branch_id

    def get_asset_name(self, arr):
        final_arr = []
        asset_data = BusinessSegment.objects.using(self._current_app_schema()).filter(id=arr,
                                                                                      entity_id=self._entity_id())
        for i in asset_data:
            final_arr.append({"id": i.id, "code": i.code, "name": i.name})
        return final_arr

class Ppr_utilityservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)

    def mantain_history(self,emp_id,module_,json_data,created_status_,remark_key=None,remark=None):
        history = PPR_history.objects.using(self._current_app_schema()).create(user_id=emp_id,modulec=module_,data=json_data,created_status=created_status_,remark_key=remark_key,remark=remark,entity_id=self._entity_id())
        history.save()

    def get_finyear_quter_transationmonth(self, date):
        date_split = date.split("-")
        if int(date_split[1]) >= 1 and int(date_split[1]) <= 3:
            finyear = f"FY{int(date_split[0][-2:]) - 1}-{int(date_split[0][-2:])}"
            quater = 4
            transationmonth = date_split[1]
        elif int(date_split[1]) >= 4 and int(date_split[1]) <= 12:
            finyear = f"FY{int(date_split[0][-2:])}-{int(date_split[0][-2:]) + 1}"
            if int(date_split[1]) >= 4 and int(date_split[1]) <= 6:
                quater = 1
            elif int(date_split[1]) >= 7 and int(date_split[1]) <= 9:
                quater = 2
            elif int(date_split[1]) >= 10 and int(date_split[1]) <= 12:
                quater = 3
            transationmonth = date_split[1]
        outdate = {"finyear": finyear, "quater": quater, "transationmonth": transationmonth, "year": date_split[0],
                   "date": date}
        return outdate


    def get_level(self, arr):
        level_data = AllocationLevel.objects.filter(id__in=arr).values('id', 'code', 'name')
        return level_data


    def get_costderiver(self, arr):
        costdriver_data = CostDriver.objects.filter(id__in=arr).values('id', 'code', 'name')
        return costdriver_data

    def get_bscc_maping(self, arr):
        final_arr = []
        bscc_data = bscc_maping.objects.using(self._current_app_schema()).filter(id__in=arr,
                                                                                 entity_id=self._entity_id())
        for i in bscc_data:
            final_arr.append({"id": i.id, "bscc_code": i.code, "bscc_name": i.name})
        return final_arr

    def get_ratio(self, id):
        final_arr = []
        ratio_data = Allocation_meta.objects.filter(source_bscc_code=id).values('source_bscc_code').annotate(
            amount=Sum("ratio"))
        for i in ratio_data:
            if i['source_bscc_code'] == id:
                data = float(i['amount'])
            return data

class Pprutility_keys:
    name = 'name'
    finyear = 'finyear'
    quarter = 'quarter'
    transactionmonth = 'transactionmonth'
    transactionyear = 'transactionyear'
    transactiondate = 'transactiondate'
    valuedate = 'valuedate'
    apinvoice_id = 'apinvoice_id'
    apinvoicebranch_id = 'apinvoicebranch_id'
    apinvoicesupplier_id = 'apinvoicesupplier_id'
    apinvoicedetails_id = 'apinvoicedetails_id'
    cc_code = 'cc_code'
    bs_code = 'bs_code'
    bsname = 'bsname'
    ccname = 'ccname'
    bizname = 'bizname'
    sectorname = 'sectorname'
    amount = 'amount'
    taxamount = 'taxamount'
    otheramount = 'otheramount'
    totalamount = 'totalamount'
    cat_id = 'cat_id'
    cat_name = 'cat_name'
    subcat_id = 'subcat_id'
    subcat_name = 'subcat_name'
    expense_id = 'expense_id'
    apexpense_id = 'apexpense_id'
    apsubcat_id = 'apsubcat_id'
    apcat_id = 'apcat_id'
    categoryname = 'categoryname'
    expensename = 'expensename'
    expensegrpname = 'expensegrpname'
    subcategoryname = 'subcategoryname'
    YTD = 'YTD'
    Padding_left = 'Padding_left'
    Padding = 'Padding'
    supplier_id = 'supplier_id'
    supplier_name = 'supplier_name'
    supplier_code = 'supplier_code'
    supplier_branchname = 'supplier_branchname'
    supplier_panno = 'supplier_panno'
    supplier_gstno = 'supplier_gstno'
    pprdata_id = 'pprdata_id'
    totamount = 'totamount'
    ecf_count = 'ecf_count'
    is_supplier_in = 'is_supplier_in'
    level_id = 'level_id'
    level_name = 'level_name'
    income_amount = 'income_amount'
    ccbs_code = 'ccbs_code'
    ccbs_name = 'ccbs_name'
    status = 'status'
    Budget_draft = "Budget Draft"
    Budget_maker = "Budget Maker"
    Budget_checker = "Budget Checker"
    Budget_approver = "Budget Approver"
    Budget_reject = "Budget Reject"
    remark_key = "remark_key"
    expensegrp_id = "expensegrp_id"



class ReftableType:
    BudgetDraft = 1
    BudgetBuilder = 2
    BudgetChecker = 3
    BudgetReviewer = 4
    BudgetApproval = 5
    BudgetReject = 6
    wisefin = 1

class CRUDstatus:
    create = 1
    update = 2
    delete = 0

class Activestatus:
    Active = 1
    Inactive = 0

class Client_name:
    ASHIRWAD = 1
    AAA = 2
    XYZ = 3
    ABC = 4
    LMK = 5
    IMK = 6
    LYK = 7

    ASHIRWAD_VAL = "ASHIRWAD"
    AAA_VAL = "AAA"
    XYZ_VAL = "XYZ"
    ABC_VAL = "ABC"
    LMK_VAL = "LMK"
    LYK_VAL = "LYK"
    IMK_VAL = "IMK"


class Product_name:
     TL = 1
     WL = 2
     AB = 3
     CD = 4
     ML = 5
     NCD = 6
     TL_VAL = "TL"
     WL_VAL = "WL"
     AB_VAL = "AB"
     CD_VAL = "CD"
     ML_VA = "ML"
     NCD_VAL = "NCD"


class Asset_class:
    AGRI = 1
    AHF = 2
    BD = 3
    CF = 4
    CONS = 5
    CORP = 6
    INTER_COMPANY = 7
    MFI = 8
    OTH = 9
    SBL = 10
    SME = 11
    VF = 12
    CC=13
    CL=14
    VL=15
    Consumer_Finance=16
    CV=17
    Gold_Loans=18



    AGRI_VAL = "AGRI"
    AHF_VAL = "AHF"
    BD_VAL = "BD"
    CF_VAL = "CF"
    CONS_VAL = "CONS"
    CORP_VAL = "CORP"
    INTER_COMPANY_VAL = "INTER COMPANY"
    MFI_VAL = "MFI"
    OTH_VAL = "OTH"
    SBL_VAL = "SBL"
    SME_VAL = "SME"
    VF_VAL = "VF"
    CC_VAL="CC"
    CL_VAL="CL"
    VL_VAL="VL"
    Consumer_Finance_VAL="Consumer Finance"
    CV_VAL="CV"
    Gold_Loans_VAL="Gold Loans"

    def getasset(self, number):
        vyslite = NWisefinList()
        if (number == Asset_class.AGRI):
            vyslite.id = number
            vyslite.name = Asset_class.AGRI_VAL
            return vyslite
        elif (number == Asset_class.AHF):
            vyslite.id = number
            vyslite.name = Asset_class.AHF_VAL
            return vyslite
        elif (number == Asset_class.BD):
            vyslite.id = number
            vyslite.name = Asset_class.BD_VAL
            return vyslite
        elif (number == Asset_class.CF):
            vyslite.id = number
            vyslite.name = Asset_class.CF_VAL
            return vyslite
        elif (number == Asset_class.CONS):
            vyslite.id = number
            vyslite.name = Asset_class.CONS_VAL
            return vyslite
        elif (number == Asset_class.CORP):
            vyslite.id = number
            vyslite.name = Asset_class.CORP_VAL
            return vyslite
        elif (number == Asset_class.INTER_COMPANY):
            vyslite.id = number
            vyslite.name = Asset_class.INTER_COMPANY_VAL
            return vyslite
        elif (number == Asset_class.MFI):
            vyslite.id = number
            vyslite.name = Asset_class.MFI_VAL
            return vyslite
        elif (number == Asset_class.OTH):
            vyslite.id = number
            vyslite.name = Asset_class.OTH_VAL
            return vyslite
        elif (number == Asset_class.SBL):
            vyslite.id = number
            vyslite.name = Asset_class.SBL_VAL
            return vyslite
        elif (number == Asset_class.SME):
            vyslite.id = number
            vyslite.name = Asset_class.SME_VAL
            return vyslite
        elif (number == Asset_class.VF):
            vyslite.id = number
            vyslite.name = Asset_class.VF_VAL
            return vyslite
        elif (number == Asset_class.CC):
            vyslite.id = number
            vyslite.name = Asset_class.CC_VAL
            return vyslite
        elif (number == Asset_class.CL):
            vyslite.id = number
            vyslite.name = Asset_class.CL_VAL
            return vyslite
        elif (number == Asset_class.VL):
            vyslite.id = number
            vyslite.name = Asset_class.VL_VAL
            return vyslite
        elif (number == Asset_class.Consumer_Finance):
                    vyslite.id = number
                    vyslite.name = Asset_class.Consumer_Finance_VAL
                    return vyslite
        elif (number == Asset_class.CV):
                    vyslite.id = number
                    vyslite.name = Asset_class.CV_VAL
                    return vyslite
        elif (number == Asset_class.Gold_Loans):
                    vyslite.id = number
                    vyslite.name = Asset_class.Gold_Loans_VAL
                    return vyslite


class Client_dtls:
    def getclient(self,number):
        vyslite = NWisefinList()
        if (number == Client_name.ASHIRWAD):
            vyslite.id = number
            vyslite.name = "ASHIRWAD"
            return vyslite
        elif (number == Client_name.AAA):
            vyslite.id = number
            vyslite.name = "AAA"
            return vyslite
        elif (number == Client_name.XYZ):
            vyslite.id = number
            vyslite.name = "XYZ"
            return vyslite
        elif (number == Client_name.ABC):
            vyslite.id = number
            vyslite.name = "ABC"
            return vyslite
        elif (number == Client_name.LMK):
            vyslite.id = number
            vyslite.name = "LMK"
            return vyslite
        elif (number == Client_name.LYK):
            vyslite.id = number
            vyslite.name = "LYK"
            return vyslite
        elif (number == Client_name.IMK):
            vyslite.id = number
            vyslite.name = "IMK"
            return vyslite

    def getproduct(self,number):
        vyslite = NWisefinList()
        if (number == Product_name.TL):
            vyslite.id = number
            vyslite.name = "TL"
            return vyslite
        elif (number == Product_name.WL):
            vyslite.id = number
            vyslite.name = "WL"
            return vyslite
        elif (number == Product_name.AB):
            vyslite.id = number
            vyslite.name = "AB"
            return vyslite
        elif (number == Product_name.CD):
            vyslite.id = number
            vyslite.name = "CD"
            return vyslite
        elif (number == Product_name.ML):
            vyslite.id = number
            vyslite.name = "ML"
            return vyslite
        elif (number == Product_name.NCD):
            vyslite.id = number
            vyslite.name = "NCD"
            return vyslite

    def getasset(self,number):
        vyslite = NWisefinList()
        if (number == Asset_class.MFI):
            vyslite.id = number
            vyslite.name = "MFI"
            return vyslite
        elif (number == Asset_class.CF):
            vyslite.id = number
            vyslite.name = "CF"
            return vyslite
        elif (number == Asset_class.AGRI):
            vyslite.id = number
            vyslite.name = "AGRI"
            return vyslite
        elif (number == Asset_class.SBL):
            vyslite.id = number
            vyslite.name = "SBL"
            return vyslite

class Client_type:
    VOLUME = 1
    TOTAL_DISBURSAL = 2
    DISBURSAL_FOR_MMM = 3
    VOLUME_VAL = "Volume"
    TOTAL_DISBURSAL_VAL = "TOTAL_DISBURSAL"
    DISBURSAL_FOR_MMM_VAL = "DISBURSAL_FOR_MMM"

class Client_flag:
    OWN = 1
    ENABLED = 2
    OWN_VAL = "OWN"
    ENABLED_VAL = "ENABLED"

    def get_client_type(self,number):
        vyslite = NWisefinList()
        if (number == Client_type.VOLUME):
            vyslite.id = number
            vyslite.name = Client_type.VOLUME_VAL
            return vyslite
        elif (number == Client_type.TOTAL_DISBURSAL):
            vyslite.id = number
            vyslite.name = Client_type.TOTAL_DISBURSAL_VAL
            return vyslite

    def get_client_flag(self,number):
        vyslite = NWisefinList()
        if (number == Client_flag.OWN):
            vyslite.id = number
            vyslite.name = Client_flag.OWN_VAL
            return vyslite
        elif (number == Client_flag.ENABLED):
            vyslite.id = number
            vyslite.name = Client_flag.ENABLED_VAL
            return vyslite

class Pprutility_keys:
    asset_id = "asset_id"

class Fees_type:
    Interest_income=1
    Syndication_fee=2
    Professional_fee=3
    Gurantee_fee=4
    Processing_fee=5
    Preclosure_fee=6
    Interest_income_var="Interest Income"
    Syndication_fee_var="Syndication Fee"
    Professional_fee_var="Professional Fee"
    Gurantee_fee_var="Gurantee Fee"
    Processing_fee_var="Processing Fee"
    Preclosure_fee_var="Preclosure Fee"
