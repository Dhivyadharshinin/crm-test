from utilityservice.permissions.util.dbutil import ModuleList, RoleList



class QueryParams:

    set_get = {'module':[ModuleList.ppr_module],'module_role':[RoleList.maker,RoleList.checker],'submodule':[ModuleList.bgt_builder], 'submodule_role':[RoleList.maker,RoleList.checker]}
    set_post = {'module':[ModuleList.ppr_module],'module_role':[RoleList.maker,RoleList.checker],'submodule':[ModuleList.bgt_builder], 'submodule_role':[RoleList.maker,RoleList.checker]}
    set_post_approver = {'module':[ModuleList.ppr_module],'module_role':[RoleList.checker],'submodule':[ModuleList.bgt_builder], 'submodule_role':[RoleList.checker]}

class PPRUrlDict:
    DATA = {'budget_expensegrp_list':{'POST':QueryParams.set_post},
            'budget_expense_list':{'POST':QueryParams.set_post},
            'budget_subcat_list':{'POST':QueryParams.set_post},
            'budget_suppliergrp_list':{'POST':QueryParams.set_post},
            'budget_builder_set':{'POST':QueryParams.set_post},
            'budget_approver_set':{'POST':QueryParams.set_post_approver}}