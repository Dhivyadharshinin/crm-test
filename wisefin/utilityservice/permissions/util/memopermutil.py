from utilityservice.permissions.util.dbutil import ModuleList, RoleList


class QueryParams:

    set_get= {'module':[ModuleList.memo],'module_role':[RoleList.maker,RoleList.checker], 'submodule':[], 'submodule_role':[]}
    set_post = {'module':[ModuleList.memo],'module_role':[RoleList.maker], 'submodule':[], 'submodule_role':[]}

    category_get = {'module': [ModuleList.master], 'module_role': [RoleList.maker, RoleList.checker], 'submodule': [ModuleList.category],
               'submodule_role': [RoleList.maker, RoleList.checker]}
    category_post = {'module': [ModuleList.memo], 'module_role': [RoleList.maker], 'submodule': [ModuleList.category], 'submodule_role': [RoleList.maker]}

    subcategory_get = {'module': [ModuleList.master], 'module_role': [RoleList.maker, RoleList.checker], 'submodule': [ModuleList.subcategory],
               'submodule_role': [RoleList.maker, RoleList.checker]}
    subcategory_post = {'module': [ModuleList.memo], 'module_role': [RoleList.maker], 'submodule': [ModuleList.subcategory], 'submodule_role': [RoleList.maker]}





class MemoUrlDict:

    DATA = {'category': {'GET':QueryParams.category_get,'POST': QueryParams.category_post},
                 'category/<int>':{'GET':QueryParams.category_get},

                 'category/<int>/subcategory':{'GET':QueryParams.subcategory_get,'POST': QueryParams.subcategory_post},
                 'subcategory':{'GET':QueryParams.subcategory_get},
                 'category/<int>/subcategory/<int>':{'GET':QueryParams.subcategory_get},

                 'memo':{'GET':QueryParams.set_get,'POST': QueryParams.set_post},
                 'memo/<int>': {'GET': QueryParams.set_get},
                 'memo/<int>/close':{'GET':QueryParams.set_get},
                 'memo/<int>/comments':{'GET':QueryParams.set_get,'POST': QueryParams.set_post},
                 'memo/<int>/documents':{'GET':QueryParams.set_get},
                 'memo/<int>/audit':{'GET':QueryParams.set_get},
                 'memo/<int>/approver':{'GET':QueryParams.set_get},
                 'memo/<int>/pdf':{'GET':QueryParams.set_get},
                 'search':{'POST': QueryParams.set_post},
            }