from django.views.decorators.csrf import csrf_exempt
import json
from masterservice.models import MigrationVersion
from django.http import HttpResponse
from userservice.service.moduleservice import ModuleService
from userservice.data.request.modulerequest import ModuleResquest
from userservice.service.modulemappingservice import ModuleMappingService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def migration_version(request):
    user_id=request.user.id
    try :
        mig =  MigrationVersion.objects.get(module=1)
    except:
        module_service = ModuleService()
        module_data ={"data":[{"name":"memo","logo":1,"url":"memo/url"},
                              {"name":"vendor","logo":2,"url":"vendor/url"},
                              {"name":"inward","logo":3,"url":"inward/url"}]}

        for i in module_data.get('data'):
            module_obj = ModuleResquest(i)
            module_service.create_module(module_obj, user_id)

        modulemapping_service = ModuleMappingService()
        module_data = {"method":"add","module_id":[1,2,3]}
        resp_obj = modulemapping_service.addmodule(user_id, module_data)

        mig_update = MigrationVersion.objects.create(module=1)


    resp_obj =True
    response = HttpResponse(resp_obj, content_type="application/json")
    return response

