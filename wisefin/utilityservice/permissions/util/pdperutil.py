from utilityservice.permissions.util.dbutil import ModuleList, RoleList


class QueryParams:

    set_post= {'module':[ModuleList.rems],'module_role':[RoleList.maker], 'submodule':[], 'submodule_role':[]}
    set_get = {'module': [ModuleList.rems], 'module_role': [RoleList.maker,RoleList.checker,RoleList.header,RoleList.Compliance], 'submodule': [], 'submodule_role': []}

    identification_post ={'module':[ModuleList.rems],'module_role':[RoleList.premise_identification_maker], 'submodule':[], 'submodule_role':[]}
    identification_get = {'module': [ModuleList.rems], 'module_role': [RoleList.premise_identification_maker,RoleList.premise_identification_approver,RoleList.proposed_premise_maker,RoleList.proposed_premise_approver],'submodule': [], 'submodule_role': []}

    Proposer_post ={'module':[ModuleList.rems],'module_role':[RoleList.proposed_premise_maker], 'submodule':[], 'submodule_role':[]}
    Proposer_get = {'module': [ModuleList.rems], 'module_role': [RoleList.proposed_premise_approver,RoleList.premise_identification_approver],'submodule': [], 'submodule_role': []}


class RemsUrlDict:

    DATA = {'premise': {'POST': QueryParams.set_post,'GET':QueryParams.set_get},
            'premiseidentification':{'POST':QueryParams.identification_post,'GET':QueryParams.identification_get},
            'premiseidentification /<int>':{'GET':QueryParams.identification_get,'DELETE':QueryParams.identification_post},
            'premiseidentification/<int>/premiseidentificationname':{'POST':QueryParams.Proposer_post,'GET':QueryParams.identification_get},
            'premiseidentification/<int>/premiseidentificationname/<int>': {'DELETE': QueryParams.Proposer_post, 'GET': QueryParams.identification_get},
            'premiseidentificationname/<int>/premiseidentificationdocument_info':{'GET':QueryParams.identification_get},



            }
