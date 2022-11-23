from utilityservice.permissions.util.dbutil import ModuleList, RoleList


class QueryParams:

    contact_post= {'module':[ModuleList.master],'module_role':[RoleList.maker], 'submodule':[ModuleList.contact], 'submodule_role':[RoleList.maker]}
    contact_get = {'module':[ModuleList.master],'module_role':[RoleList.maker,RoleList.checker], 'submodule':[ModuleList.contact], 'submodule_role':[RoleList.maker,RoleList.checker]}

    address_post = {'module': [ModuleList.master], 'module_role': [RoleList.maker], 'submodule': [ModuleList.address],
                   'submodule_role': [RoleList.maker]}
    address_get = {'module': [ModuleList.master], 'module_role': [RoleList.maker, RoleList.checker],
                    'submodule': [ModuleList.address], 'submodule_role': [RoleList.maker, RoleList.checker]}


class MasterUrlDict:
    DATA={'contacttype':{'POST':QueryParams.contact_post,'GET':QueryParams.contact_get},
          'contacttype/<int>':{'GET':QueryParams.contact_get},
          'designation':{'POST':QueryParams.contact_post,'GET':QueryParams.contact_get},
          'designation/<int>':{'GET':QueryParams.contact_get},

          'country':{'POST':QueryParams.address_post,'GET':QueryParams.address_get},
          'country/<int>':{'GET':QueryParams.address_get},
          'district':{'POST':QueryParams.address_post,'GET':QueryParams.address_get},
          'district/<int>': {'GET': QueryParams.address_get},
          'state':{'POST':QueryParams.address_post,'GET':QueryParams.address_get},
          'state/<int>':{'GET':QueryParams.address_get},
          'city':{'POST':QueryParams.address_post,'GET':QueryParams.address_get},
          'city/<int>':{'GET':QueryParams.address_get},
          'pincode':{'POST':QueryParams.address_post,'GET':QueryParams.address_get},
          'pincode/<int>':{'GET':QueryParams.address_get}
                     }
          # ['/tax', 'POST'], ['/tax', 'GET'], ['/tax/<int>', 'GET'],
          # ['/subtax', 'POST'], ['/subtax', 'GET'], ['/subtax/<int>', 'GET'],
          # ['/taxrate', 'POST'], ['/taxrate', 'GET'], ['/taxrate/<int>', 'GET'],
          # ['/paymode', 'POST'], ['/paymode', 'GET'], ['/paymode/<int>', 'GET'],
          # ['/bank', 'POST'], ['/bank', 'GET'], ['/bank/<int>', 'GET'],
          # ['/bankbranch', 'POST'], ['/bankbranch', 'GET'], ['/bankbranch/<int>', 'GET'],
          # ['/uom', 'POST'], ['/uom', 'GET'], ['/uom/<int>', 'GET'],
          # ['/Apcategory', 'POST'], ['/Apcategory', 'GET'], ['/Apcategory/<int>', 'GET'],
          # ['/Apsubcategory', 'POST'], ['/Apsubcategory', 'GET'], ['/Apsubcategory/<int>', 'GET'],
          # ['/customercategory', 'POST'], ['/customercategory', 'GET'], ['/customercategory/<int>', 'GET'],
          # ['/product', 'POST'], ['/product', 'GET'], ['/product/<int>', 'GET'],
          # ['/documentgroup', 'POST'], ['/documentgroup', 'GET'], ['/documentgroup/<int>', 'GET'],

          # ['/masteraudit', 'POST'], ['/masteraudit', 'GET'], ['/fetch_masteraudit/<int>', 'GET'],
          # ['/type', 'GET'], ['/org_type', 'GET'], ['/group', 'GET'],
          # ['/classification', 'GET'], ['/composite', 'GET'],

          # ['/search_doctype/<int>', 'POST'],['/search_courier/<int>', 'POST'],
          # ['/Documenttype', 'POST'], ['/Documenttype', 'GET'], ['/Documenttype/<int>', 'GET'],
          # ['/courier', 'POST'], ['/courier', 'GET'], ['/courier/<int>', 'GET'],
          # ['/channel', 'POST'], ['/channel', 'GET'], ['/channel/<int>', 'GET']


