from utilityservice.permissions.util.dbutil import ModuleList, RoleList


class QueryParams:

    employee_post= {'module':[ModuleList.master],'module_role':[RoleList.maker], 'submodule':[ModuleList.employee], 'submodule_role':[RoleList.maker]}
    employee_get = {'module':[ModuleList.master],'module_role':[RoleList.maker,RoleList.checker], 'submodule':[ModuleList.employee], 'submodule_role':[RoleList.checker,RoleList.maker]}

    department_get = {'module': [ModuleList.master], 'module_role': [RoleList.checker,RoleList.maker], 'submodule': [ModuleList.department],
                   'submodule_role': [RoleList.maker,RoleList.checker]}
    department_post = {'module': [ModuleList.master], 'module_role': [ RoleList.maker],
                    'submodule': [ModuleList.department], 'submodule_role': [RoleList.maker]}

    permission_get={'module': [ModuleList.master], 'module_role': [RoleList.checker,RoleList.maker], 'submodule': [ModuleList.permission],
                   'submodule_role': [RoleList.maker,RoleList.checker]}

    permission_post = {'module': [ModuleList.master], 'module_role': [RoleList.maker],
                       'submodule': [ModuleList.permission], 'submodule_role': [RoleList.maker]}

    module_get = {'module': [ModuleList.master], 'module_role': [RoleList.checker, RoleList.maker],
                      'submodule': [ModuleList.module],
                      'submodule_role': [RoleList.maker, RoleList.checker]}

    module_post = {'module': [ModuleList.master], 'module_role': [RoleList.maker],
                       'submodule': [ModuleList.module], 'submodule_role': [RoleList.maker]}

    role_get = {'module': [ModuleList.master], 'module_role': [RoleList.checker, RoleList.maker],
                      'submodule': [ModuleList.role],
                      'submodule_role': [RoleList.maker, RoleList.checker]}

    role_post = {'module': [ModuleList.master], 'module_role': [RoleList.maker],
                       'submodule': [ModuleList.role], 'submodule_role': [RoleList.maker]}


class UserUrlDict:
    DATA={'department':{'POST':QueryParams.department_post,'GET':QueryParams.department_get},
          'department/<int>':{'GET':QueryParams.department_get},
          'searchdepartment': {'GET': QueryParams.department_get},
          'deplist': {'POST': QueryParams.department_get},
          'department/<int>/employee':{'POST': QueryParams.department_post,'GET': QueryParams.department_get},

          'employee':{'POST':QueryParams.employee_post,'GET':QueryParams.employee_get},
          'employee/<int>':{'GET':QueryParams.employee_get},
          'searchemployee': {'GET': QueryParams.employee_get},
          'user/<int>': {'GET': QueryParams.employee_get},
          'emplist':{'POST':QueryParams.employee_get},
          'emplistbyeid':{'POST':QueryParams.employee_get},
          'userid':{'POST':QueryParams.employee_get},
          'user_emp_list':{'GET':QueryParams.employee_get},
          'filter': {'GET': QueryParams.employee_get},
          'employee/<int>/department':{'POST':QueryParams.employee_post,'GET': QueryParams.employee_get},

          'usermodule': {'POST': QueryParams.module_post, 'GET': QueryParams.module_get},
          'usermodule/<int>': {'GET': QueryParams.module_get},

          'role': {'POST': QueryParams.role_post, 'GET': QueryParams.role_get},
          'role/<int>': {'GET': QueryParams.role_get},

          'moduleorder': {'POST': QueryParams.permission_post},
          'modulemapping/<int>': {'POST': QueryParams.permission_post, 'GET': QueryParams.permission_get},
          'roleemployee': {'POST': QueryParams.permission_post, 'GET': QueryParams.permission_get},
          'roleemployee/<int>': {'GET': QueryParams.permission_get},
          'rolemodule': {'POST': QueryParams.permission_post, 'GET': QueryParams.permission_get},
          'rolemodule/<int>': {'GET': QueryParams.permission_get},
          'permission': {'POST': QueryParams.permission_post},
          'usermodule/<int>/submodule': {'GET': QueryParams.permission_get},
          'module/<int>/role/<int>/users': { 'GET': QueryParams.permission_get},
          # 'user/<int>/submodule': {'GET': QueryParams.permission_get},


          # 'employeehierarchy': {'POST': QueryParams.employee_post, 'GET': QueryParams.employee_get},
          # 'employeehierarchy/<int>': {'GET': QueryParams.employee_get},
          # 'employeebranch': {'POST': QueryParams.employee_post, 'GET': QueryParams.employee_get},
          # 'employeebranch/<int>': {'GET': QueryParams.employee_get},
          # 'costcentre': {'POST': QueryParams.employee_post, 'GET': QueryParams.employee_get},
          # 'costcentre/<int>': {'GET': QueryParams.employee_get},
          # 'businesssegment': {'POST': QueryParams.employee_post, 'GET': QueryParams.employee_get},
          # 'businesssegment/<int>': {'GET': QueryParams.employee_get},
          # 'ccbsmapping': {'POST': QueryParams.employee_post, 'GET': QueryParams.employee_get},
          # 'ccbsmapping/<int>': {'GET': QueryParams.employee_get}

                     }
