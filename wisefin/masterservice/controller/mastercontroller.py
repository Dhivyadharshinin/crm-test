import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.util.fautil import dictdefault
from masterservice.data.request.cityrequest import CityRequest
from masterservice.data.request.countryrequest import CountryRequest
from masterservice.data.request.designationrequest import DesignationRequest
from masterservice.data.request.districtrequest import DistrictRequest
from masterservice.data.request.pincoderequest import PincodeResquest
from masterservice.data.request.staterequest import StateRequest
from masterservice.service.cityservice import CityService
from masterservice.service.contacttypeservice import ContactTypeService
from masterservice.service.counrtyservice import CountryService
from masterservice.service.designationservice import DesignationService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.stateservice import StateService
from nwisefin.settings import logger
from vendorservice.data.request.contacttyperequest import ContactTypeRequest
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.models.mastermodels import City, Pincode, State, Country, District
from utilityservice.data.response.nwisefinlist import NWisefinList

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
def get_pincode_searchlist(request):
    # search = request.GET.get('search',None)
    search = request.GET.get('query',None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    #city = request.GET.get('city',None)
    if search.isnumeric() or search=='' :
        scope = request.scope
        pincode_service = PincodeService(scope)
        user_id = request.employee_id
        resp_obj = pincode_service.fetch_pincode_search(search, vys_page)
        # city_service = CityService()
        # district_service = DistrictService()
        # city_id = resp_obj.city_id
        # city = city_service.fetch_city(city_id, user_id)
        # resp_obj.city_id = city
        # district_id = resp_obj.district_id
        # district = district_service.fetchdistrict(district_id)
        # resp_obj.district_id = district
        # state_service = StateService()
        # state_id = resp_obj.city_id.state_id
        # state = state_service.fetchstate(state_id)
        # resp_obj.city_id.state_id = state

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        scope = request.scope
        pincode_service = PincodeService(scope)
        user_id = request.employee_id
        resp_obj = pincode_service.fetch_pincode_city(search, vys_page)
        # city_service = CityService()
        # district_service = DistrictService()
        # city_id = resp_obj.city_id
        # city = city_service.fetch_city(city_id, user_id)
        # resp_obj.city_id = city
        # district_id = resp_obj.district_id
        # district = district_service.fetchdistrict(district_id)
        # resp_obj.district_id = district
        # state_service = StateService()
        # state_id = resp_obj.city_id.state_id
        # state = state_service.fetchstate(state_id)
        # resp_obj.city_id.state_id = state

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def contacttype(request):
    if request.method == 'POST':
        scope = request.scope
        contacttype_service = ContactTypeService(scope)
        user_id = request.employee_id
        contacttype_data = json.loads(request.body)
        contacttype_obj = ContactTypeRequest(contacttype_data)
        resp_obj = contacttype_service.create_contacttype(contacttype_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_contacttype_list(request)


def fetch_contacttype_list(request):
    scope = request.scope
    contacttype_service = ContactTypeService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = contacttype_service.fetch_contacttype_list(user_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_contacttype(request, contacttype_id):
    scope = request.scope
    contacttype_service = ContactTypeService(scope)
    user_id = request.employee_id
    resp_obj = contacttype_service.delete_contacttype(contacttype_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_contacttype(request, contacttype_id):
    if request.method == 'GET':
        scope = request.scope
        contacttype_service = ContactTypeService(scope)
        user_id = request.employee_id
        resp_obj = contacttype_service.fetch_contacttype(contacttype_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_contacttype(request, contacttype_id)


# designation - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def designation(request):
    if request.method == 'POST':
        scope = request.scope
        designation_service = DesignationService(scope)
        designation_data = json.loads(request.body)
        designation_obj = DesignationRequest(designation_data)
        user_id = request.employee_id
        resp_obj = designation_service.create_designation(designation_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_designation_list(request)


def fetch_designation_list(request):
    scope = request.scope
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    data= request.GET.get('data')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    designation_service = DesignationService(scope)
    resp_obj = designation_service.fetch_designation_list(user_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def designation_download(request):
    scope = request.scope
    designation_service = DesignationService(scope)
    user_id = request.user.id
    resp_obj = designation_service.fetch_designation_download(user_id)
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
    df = pd.DataFrame(data)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Designation Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Designation Master.xlsx"'
    logger.info("Test_Download Data:")
    return response


def delete_designation(request, designation_id):
    scope = request.scope
    designation_service = DesignationService(scope)
    user_id = request.employee_id
    resp_obj = designation_service.delete_designation(designation_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_designation(request, designation_id):
    if request.method == 'GET':
        scope = request.scope
        designation_service = DesignationService(scope)
        user_id = request.employee_id
        resp_obj = designation_service.fetch_designation(designation_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_designation(request, designation_id)


# country

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def country(request):
    if request.method == 'POST':
        scope = request.scope
        country_service = CountryService(scope)
        country_data = json.loads(request.body)
        country_obj = CountryRequest(country_data)
        user_id = request.employee_id
        resp_obj = country_service.create_country(country_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_country_list(request)


def fetch_country_list(request):
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    country_service = CountryService(scope)
    resp_obj = country_service.fetch_country_list(user_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_country(request, country_id):
    scope = request.scope
    country_service = CountryService(scope)
    user_id = request.employee_id
    resp_obj = country_service.delete_country(country_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_country(request, country_id):
    if request.method == 'GET':
        scope = request.scope
        country_service = CountryService(scope)
        user_id = request.employee_id
        resp_obj = country_service.fetch_country(country_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_country(request, country_id)

#district
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def district(request):
    if request.method == 'POST':
        scope = request.scope
        District_service =DistrictService(scope)
        district_obj = json.loads(request.body)
        Dis_obj = DistrictRequest(district_obj)
        user_id = request.employee_id
        resp_obj = District_service.create_district(Dis_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_district_list(request)

def fetch_district_list(request):
        scope = request.scope
        District_service = DistrictService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = District_service.fetch_district_list(vys_page)

        state_service = StateService(scope)
        x = resp_obj.data
        for i in x:
            state_id = i.state_id
            state = state_service.fetchstate(state_id)
            i.state_id= state

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def district_download(request):
    scope = request.scope
    District_service = DistrictService(scope)
    user_id = request.user.id
    resp_obj = District_service.fetch_district_dowload(request)
    state_service = StateService(scope)
    x = resp_obj.data
    for i in x:
        try:
            state_id = i.state_id
            state = state_service.fetchstate(state_id)
            i.State_Name= state.name
        except:
            i.State_Name = ""
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
    df_data = pd.DataFrame(data)
    df = df_data.drop(['state_id'], inplace=False, axis=1)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'District Master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="District Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_district(request,district_id):
    if request.method == 'GET':
        scope = request.scope
        District_service = DistrictService(scope)
        user_id = request.employee_id
        resp_obj = District_service.fetchdistrict(district_id)
        state_service = StateService(scope)
        state_id = resp_obj.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.state_id = state
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_district(request,district_id)


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_district_scroll(request,state_id):
    if request.method == 'GET':
        scope = request.scope
        District_service = DistrictService(scope)
        user_id = request.employee_id
        data = request.GET.get('data','')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = District_service.fetch_district_scroll_list(state_id,vys_page,data)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

def delete_district(request, district_id):
    scope = request.scope
    District_service = DistrictService(scope)
    user_id = request.employee_id
    resp_obj = District_service.delete_district( district_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# state
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def state(request):
    if request.method == 'POST':
        scope = request.scope
        state_service =StateService(scope)
        state_obj = json.loads(request.body)
        State_obj = StateRequest(state_obj)
        user_id = request.employee_id
        resp_obj = state_service.create_state(State_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_state_list(request)

def fetch_state_list(request):
        scope = request.scope
        state_service = StateService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = state_service.fetch_state_list(vys_page)


        country_service = CountryService(scope)
        x = resp_obj.data
        for i in x:
            country_id = i.country_id
            country = country_service.fetch_country(country_id,user_id)
            i.country_id = country
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def state_download(request):
    scope = request.scope
    state_service = StateService(scope)
    user_id = request.user.id
    pdt_resp = state_service.fetch_state_download(request)
    country_service = CountryService(scope)
    x = pdt_resp.data
    for i in x:
        country_id = i.country_id
        country = country_service.fetch_country(country_id, user_id)
        i.Country_name = country.name
    data = json.loads(json.dumps(pdt_resp.__dict__, default=dictdefault))['data']
    df_data = pd.DataFrame(data)
    df = df_data.drop(['country_id'], inplace=False, axis=1)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'State Master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="State Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_state_id(request,state_id):
    if request.method == 'GET':
        scope = request.scope
        state_service = StateService(scope)
        user_id = request.employee_id
        resp_obj = state_service.fetchstate(state_id)
        country_service = CountryService(scope)
        country_id = resp_obj.country_id
        country = country_service.fetch_country(country_id,user_id)
        resp_obj.country_id = country
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_state(request,state_id)

def delete_state(request, state_id):
    scope = request.scope
    state_service = StateService(scope)
    user_id = request.employee_id
    resp_obj = state_service.delete_state( state_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#City
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city(request):
    if request.method == 'POST':
        scope = request.scope
        city_service = CityService(scope)
        city_data = json.loads(request.body)
        city_obj = CityRequest(city_data)
        user_id = request.employee_id
        pincode_service=PincodeService(scope)
        city_resp_obj = city_service.create_city(city_obj, user_id,id='')
        if(city_resp_obj.code=='INVALID_DATA'):
            return HttpResponse(city_resp_obj.get(), content_type="application/json")
        print(city_resp_obj)
        city_resp_obj.no=city_data['no']
        city_resp_obj.district=city_data['district']
        res=pincode_service.create_pincode(city_resp_obj,user_id)
        response = HttpResponse(res.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_city_list(request)
def fetch_city_list(request):
    scope = request.scope
    user_id = request.employee_id
    city_service = CityService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = city_service.fetch_city_list(user_id,vys_page)

    state_service = StateService(scope)
    x = resp_obj.data
    for i in x:
        state_id = i.state_id
        state = state_service.fetchstate(state_id)
        i.state_id = state
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_download(request):
    scope = request.scope
    city_service = CityService(scope)
    user_id = request.user.id
    resp_obj = city_service.fetch_city_download(user_id)
    state_service = StateService(scope)
    x = resp_obj.data
    for i in x:
        try:
            state_id = i.state_id
            state = state_service.fetchstate(state_id)
            i.State_Name = state.name
        except:
            i.State_Name = ""
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
    df_data = pd.DataFrame(data)
    df = df_data.drop(['state_id'], inplace=False, axis=1)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'City Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="City Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

def delete_city(request, city_id):
    scope = request.scope
    city_service = CityService(scope)
    user_id = request.employee_id
    resp_obj =city_service .delete_city(city_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_city(request,city_id):
    if request.method == 'GET':
        scope = request.scope
        city_service = CityService(scope)
        user_id = request.employee_id
        resp_obj = city_service.fetch_city(city_id, user_id)
        state_service = StateService(scope)
        state_id = resp_obj.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.state_id = state
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_city(request, city_id)

#city scroll
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_city_scroll(request,state_id):
    if request.method == 'GET':
        scope = request.scope
        city_service = CityService(scope)
        user_id = request.employee_id
        data = request.GET.get('data')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = city_service.fetch_city_scroll(state_id, vys_page, data)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#city scroll
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_state_scroll(request,country_id):
    if request.method == 'GET':
        scope = request.scope
        state_service = StateService(scope)
        user_id = request.employee_id
        data = request.GET.get('data')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = state_service.state_scroll(country_id, vys_page, data)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#Pincode
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pincode(request):
    if request.method == 'POST':
        scope = request.scope
        pincode_service = PincodeService(scope)
        pincode_data = json.loads(request.body)
        pincode_obj = PincodeResquest(pincode_data)
        user_id = request.employee_id
        resp_obj = pincode_service.create_pincode(pincode_obj, user_id)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_pincode_list(request)
def fetch_pincode_list(request):
    user_id = request.employee_id
    scope = request.scope
    pincode_service = PincodeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = pincode_service.fetch_pincode_list(user_id,vys_page)

    city_service = CityService(scope)
    district_service = DistrictService(scope)
    x = resp_obj.data
    for i in x:
        city_id = i.city_id
        city = city_service.fetch_city(city_id, user_id)
        i.city_id = city
        district_id = i.district_id
        district = district_service.fetchdistrict(district_id)
        i.district_id = district

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pincode_download(request):
    scope = request.scope
    pincode_service = PincodeService(scope)
    user_id = request.user.id
    country = pincode_service.pincode_dataframe(user_id)
    df_data = pd.DataFrame(country)
    df = df_data.drop(['city_id','district_id','state_id','country_id'], inplace=False, axis=1)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Pincode Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Pincode Master.xlsx"'
    logger.info("Test_Download Data:")
    return response


def delete_pincode(request, pincode_id):
    scope = request.scope
    pincode_service = PincodeService(scope)
    user_id = request.employee_id
    resp_obj =pincode_service .delete_pincode(pincode_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_pincode(request, pincode_id):
    if request.method == 'GET':
        scope = request.scope
        pincode_service = PincodeService(scope)
        user_id = request.employee_id
        resp_obj = pincode_service.fetch_pincode(pincode_id, user_id)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        city_id = resp_obj.city_id
        city = city_service.fetch_city(city_id, user_id)
        resp_obj.city_id = city
        district_id = resp_obj.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.district_id = district

        state_service = StateService(scope)
        state_id = resp_obj.city_id.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.city_id.state_id = state

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_pincode(request, pincode_id)

# search api

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pincode_search(request):
    scope = request.scope
    pincode_service = PincodeService(scope)
    query=request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = pincode_service.fetch_pincode_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def state_search(request):
    scope = request.scope
    state_service = StateService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = state_service.fetch_state_search(query,vys_page)
    country_service = CountryService(scope)
    x = resp_obj.data
    for i in x:
        if i.country_id != None and i.country_id !='':
            country_id = i.country_id
            country = country_service.fetch_country(country_id, user_id)
            i.country_id = country
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_search(request):
    scope = request.scope
    city_service = CityService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    state_id = request.GET.get('state_id')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = city_service.fetch_city_search(query,vys_page,state_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_search_new(request):
    scope = request.scope
    city_service = CityService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    state_id = request.GET.get('state_id')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = city_service.fetch_city_search_new(query,vys_page,state_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_city_search(request):
    scope = request.scope
    city_service = CityService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    state_id = request.GET.get('state_id')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = city_service.fetch_new_city_search(query,vys_page,state_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def district_search(request):
    scope = request.scope
    district_service = DistrictService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    state_id = request.GET.get('state_id')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = district_service.fetch_district_search(query,vys_page,state_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def contacttype_search(request):
    scope = request.scope
    contacttype_service = ContactTypeService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = contacttype_service.fetch_contacttype_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def designation_search(request):
    scope = request.scope
    designation_service = DesignationService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = designation_service.fetch_designation_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def designation_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        designation_service = DesignationService(scope)
        designation_data = json.loads(request.body)
        action = request.GET.get('action')
        designation_obj = DesignationRequest(designation_data)
        user_id = request.employee_id
        resp_obj = designation_service.create_designation_mtom(designation_obj,action, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def district_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        District_service =DistrictService(scope)
        district_obj = json.loads(request.body)
        action = request.GET.get('action')
        Dis_obj = DistrictRequest(district_obj)
        user_id = request.employee_id
        resp_obj = District_service.create_district_mtom(Dis_obj,action, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        city_service = CityService(scope)
        city_data = json.loads(request.body)
        action = request.GET.get('action')
        city_obj = CityRequest(city_data)
        user_id = request.employee_id
        resp_obj = city_service.create_city_mtom(city_obj,action, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pincode_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        pincode_service = PincodeService(scope)
        pincode_data = json.loads(request.body)
        action = request.GET.get('action')
        print('action',action)
        pincode_obj = PincodeResquest(pincode_data)
        user_id = request.employee_id
        resp_obj = pincode_service.create_pincode_mtom(pincode_obj,action, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def state_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        state_service =StateService(scope)
        state_obj = json.loads(request.body)
        State_obj = StateRequest(state_obj)
        user_id = request.employee_id
        resp_obj = state_service.create_state_mtom(State_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

# microtomicro
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_city(request, city_id):
    city = City.objects.get(id=city_id)
    city_data = {"id": city.id,
                 "code":city.code,
                          "name": city.name
                          }
    city_dic = json.dumps(city_data, indent=4)
    return HttpResponse(city_dic, content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_pincode(request, pincode_id,city_id):
    pincode = Pincode.objects.get(id=pincode_id,city_id = city_id )
    pincode_data = {"id": pincode.id,
                          "no": pincode.no
                          }
    pincode_dic = json.dumps(pincode_data, indent=4)
    return HttpResponse(pincode_dic, content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_pincode_stateid(request):
    scope = request.scope
    data=json.loads(request.body)
    pinserv=PincodeService(scope)
    pincode_data=pinserv.fetch_pincode_state(request,data)
    pincode_dic = json.dumps(pincode_data, indent=4)
    return HttpResponse(pincode_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_state(request, state_id):
    state = State.objects.get(id=state_id)
    state_data = {"id": state.id,
                  "code":state.code,
                          "name": state.name
                          }
    state_dic = json.dumps(state_data, indent=4)
    return HttpResponse(state_dic, content_type='application/json')

#micro to micro New
#Get State
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_stateone(request,state_id):
    state = State.objects.get(id=state_id)
    state_data = {"id": state.id, "code": state.code, "name": state.name}
    state_dic = json.dumps(state_data, indent=4)
    return HttpResponse(state_dic, content_type='application/json')
#state getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_statelist(request):
    state_ids = json.loads(request.body)
    state_id2 = state_ids['state_id']
    obj = State.objects.filter(id__in=state_id2).values('id', 'name')
    state_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name']}
        state_list_data.append(data)
    return HttpResponse(state_list_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_district_state(request):
    if request.method == 'GET':
        scope=request.scope
        District_service = DistrictService(scope)
        user_id = request.employee_id
        status = request.GET.get('status')
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = District_service.fetch_distrcit_stateid(vys_page, status)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_district_city_state(request):
    if request.method == 'GET':
        scope=request.scope
        District_service = DistrictService(scope)
        status = request.GET.get('status')
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = District_service.fetch_city_state(vys_page,status)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
      
def fetch_state_dist_city(request):
    if request.method == 'GET':
        scope = request.scope
        District_service = DistrictService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = District_service.fetch_state_district_city(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

