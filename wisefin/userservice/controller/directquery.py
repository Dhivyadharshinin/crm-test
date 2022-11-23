from django.db import connection
import pandas as pd
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
import re


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def query_get(request):
    query_obj = json.loads(request.body)
    schema = query_obj['schema']
    print(schema)
    arr = ['DROP', 'TRUNCATE', 'ALTER', 'MODIFY', 'RENAME', 'GRANT', 'PRIVILEGES',
           'REVOKE', 'CONVERT', 'REPLACE', 'ROLLBACK', 'UPDATE', 'DELETE', 'INSERT', 'CREATE']
    for i in arr:
        x = bool(re.search(i, query_obj['key'], re.IGNORECASE))
        if x:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

    resp_obj = query_get_return(query_obj['key'])
    data = json.dumps(resp_obj)
    response = HttpResponse(data, content_type="application/json")
    return response


def query_get_return(query_val):
    with connection.cursor() as cursor:
        cursor.execute(query_val)
        columns = [x[0] for x in cursor.description]
        rows = cursor.fetchall()
        rows = list(rows)
        df_data = pd.DataFrame(rows, columns=columns)
        resp = {"DATA": json.loads(df_data.to_json(orient='records'))}
        resp1 = resp['DATA']
    return resp1
