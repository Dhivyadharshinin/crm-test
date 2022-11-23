from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
import pandas as pd
import numpy as np
import datetime
from userservice.service.employeeservice import EmployeeService
from pprservice.data.response.success import Success, successMessage,Update,updateMessage
from pprservice.data.response.warning import Pprdata_warning

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_excelUpload(request):
    scope = request.scope
    check = request.GET['recheck']
    table_name = request.GET['table']
    sheet_name = str(request.GET['sheet_name'])
    date_time = datetime.datetime.now()
    ignore_keys = ['id', 'created_by', 'created_date', 'updated_by', 'updated_date']

    empid =  request.employee_id
    if check=='false':
        file_obj = pd.read_excel(request.FILES['file'],sheet_name).to_dict(orient='records')
        values = []
        columns = ""
        for j in file_obj[0]:
            if j in ignore_keys:
                continue
            else:
                columns += f"{j},"
        for i in file_obj:
            values.append(tuple(ignore_values(i,columns.split(','),empid,date_time)))
        original_values = ""
        for k in range(0,len(values)):
            if k == 0:
                original_values+=f"{values[k]}"
            else:
                original_values += f",{values[k]}"
        query = f"insert into {table_name} ({columns}created_by,created_date) values{original_values}".replace('nan','NULL')
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        suc_obj = Success()
        suc_obj.set_status(successMessage.SUCCESS)
        return HttpResponse(suc_obj.get(),content_type="application/json")
    elif check=='true':
        file_obj = pd.read_excel(request.FILES['file'],sheet_name).to_dict(orient='records')
        for i in file_obj:
            column_values = "set "
            for index,k in enumerate(i,start=0):
                if k in ignore_keys:
                    continue
                else:
                    column_values+=f"{k}='{i[k]}',"
            query = f"update {table_name} {column_values}updated_by={empid},updated_date='{date_time}' where id={i['id']}".replace('nan','NULL')
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.close()
        update_obj = Update()
        update_obj.set_status(updateMessage.UPDATE)
        return HttpResponse(update_obj.get(), content_type="application/json")
    else:
        invalid_obj = Success()
        invalid_obj.set_status(Pprdata_warning.INVALID_REQUEST)
        return HttpResponse(invalid_obj.get(), content_type="application/json")

def ignore_values(dict_,needed_keys,empid,data_time):
    arr = []
    for i in needed_keys:
        if i != "":
            arr.append(dict_[i])
    arr.append(empid)
    arr.append(f'{data_time}')
    return arr