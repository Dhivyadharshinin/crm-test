import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.catelogrequest import CatelogRequest
from vendorservice.models import Catelog
from vendorservice.service.catelogservice import CatelogService
from vendorservice.service.vendorservice import VendorService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.service.activitydetailsservice import ActivityDetailsService
from masterservice.service.uomservice import UomService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.productservice import ProductService
from vendorservice.service.activityservice import ActivityService
from vendorservice.util.vendormandatory import VendorMandatory
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catelogdataforrcn(request):
    if request.method == 'GET':
        scope = request.scope
        catelog_service = CatelogService(scope)
        product_id = request.GET.get('product_id', None)
        query = request.GET.get('query', None)
        dts = request.GET.get('DTS', 0)
        page = request.GET.get('page', '1')
        page = int(page)
        catelog_id = request.GET.get('catelog_id', None)
        catname_supplier = request.GET.get('catname_supplier', None)
        if catelog_id:
            resp_obj = catelog_service.fetch_catelog(catelog_id)
            return HttpResponse(resp_obj.get(), content_type="application/json")

        data = catelog_service.get_cat_forrcn(product_id, query,catname_supplier,dts,page)
        logger.info(str(data))
    return HttpResponse(data.get(), content_type="application/json")


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def suppliercatelog(request, activitydetail_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        catelog_service = CatelogService(scope)
        catlog_obj = json.loads(request.body)
        catelog_obj = CatelogRequest(catlog_obj)
        vendor_mand = VendorMandatory()
        validate = vendor_mand.catalog(catelog_obj)
        if validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")

        vendor_service = VendorService(scope)
        vendor_id = catelog_service.get_vendorid_catalog(activitydetail_id)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            resp_obj = catelog_service.catelog_modification(activitydetail_id, catelog_obj, employee_id, vendor_id)
        else:
            resp_obj = catelog_service.create_catelog(activitydetail_id, catelog_obj, employee_id, vendor_id)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_catelog_list(request, activitydetail_id)


def fetch_catelog_list(request, activitydetail_id):
    employee_id = request.employee_id
    scope = request.scope
    catelog_service = CatelogService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = catelog_service.fetch_catelog_list(request, vys_page, employee_id, activitydetail_id)
    activitydetail_service = ActivityDetailsService(scope)
    activity_service = ActivityService(scope)
    category_service = CategoryService(scope)
    subcategory_service = SubcategoryService(scope)
    product_service = ProductService(scope)
    uom_service = UomService(scope)
    x = resp_obj.data
    for i in x:
        activitydetail_id = i.activitydetail_id
        activity = activitydetail_service.fetch_activitydtl(activitydetail_id)
        i.activitydetail_id = activity

        category_id = i.category
        category = category_service.fetchcategory(category_id)
        i.category = category
        subcategory_id = i.subcategory
        subcategory = subcategory_service.fetchsubcategory(subcategory_id)
        i.subcategory = subcategory
        product_id = i.productname
        product = product_service.fetch_product(product_id, employee_id)
        i.productname = product

        uom_id = i.uom
        if uom_id is not None:
            uom = uom_service.fetch_uom(uom_id, employee_id)
            i.uom = uom

        vendor_status = activity_service.get_vendorstatus_catalog(activitydetail_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
    #     modification
    #     i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_catelog(request, activitydetail_id, catelog_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        catelog_service = CatelogService(scope)
        resp_obj = catelog_service.fetch_catelog(catelog_id)
        activitydetail_service = ActivityDetailsService(scope)
        activitydetail_id = resp_obj.activitydetail_id
        activitydetail = activitydetail_service.fetch_activitydtl(activitydetail_id)
        resp_obj.activitydetail_id = activitydetail
        uom_service = UomService(scope)
        uom_id = resp_obj.uom
        if uom_id is not None:
            uom = uom_service.fetch_uom(uom_id, employee_id)
            resp_obj.uom = uom
        category_service = CategoryService(scope)
        category_id = resp_obj.category
        category = category_service.fetchcategory(category_id)
        resp_obj.category = category

        subcategory_service = SubcategoryService(scope)
        subcategory_id = resp_obj.subcategory
        subcategory = subcategory_service.fetchsubcategory(subcategory_id)
        resp_obj.subcategory = subcategory

        product_service = ProductService(scope)
        product_id = resp_obj.productname
        product = product_service.fetch_product(product_id, employee_id)
        resp_obj.productname = product

        activity_service = ActivityService(scope)
        vendor_status = activity_service.get_vendorstatus_catalog(activitydetail_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True
        # modification
        # resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_catelog(request, activitydetail_id, catelog_id)


def delete_catelog(request, activitydetail_id, catelog_id):
    employee_id = request.employee_id
    scope = request.scope
    catelog_service = CatelogService(scope)
    vendor_service = VendorService(scope)
    vendor_id = catelog_service.get_vendorid_catalog(activitydetail_id)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status:
        resp_obj = catelog_service.modification_delete_catelog(catelog_id, vendor_id, employee_id, activitydetail_id)
    else:
        resp_obj = catelog_service.delete_catelog(activitydetail_id, catelog_id, employee_id, vendor_id,
                                                  activitydetail_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplier_catalog(request):
    if request.method == 'GET':
        scope = request.scope
        catalog_service = CatelogService(scope)
        supplier_id = request.GET.get('supplier_id', None)
        product_id = request.GET.get('product_id', None)
        dts = request.GET.get('dts', 0)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.user.id
        resp_obj = catalog_service.fetch_supplier_catalog(supplier_id,product_id,dts,vys_page,employee_id,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_catalog(request):
    if request.method == 'GET':
        scope = request.scope
        catalog_service = CatelogService(scope)
        product_id = request.GET.get('product_id', None)
        dts = request.GET.get('dts', 0)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = catalog_service.fetch_product_catalog(product_id, dts, vys_page, employee_id, query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catalog_unitprice(request):
    if request.method == 'GET':
        scope = request.scope
        catalog_service = CatelogService(scope)
        catalog_name = request.GET.get('catalog', None)
        supplier_id = request.GET.get('supplier', 0)
        product_id = request.GET.get('product_id', 0)
        query = request.GET.get('query', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_id = request.employee_id
        resp_obj = catalog_service.fetch_catalog_unitprice(catalog_name, supplier_id, product_id, vys_page, employee_id, query)

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

# prpo-micro to micro
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_catelogdata(request, catelog_id):
    scope = request.scope
    catelog_serv = CatelogService(scope)
    resp_data = catelog_serv.fetch_catelogdata(catelog_id)
    # catelog = Catelog.objects.get(id=catelog_id)
    # catelog_data = {"id": catelog.id, "name": catelog.name}
    catelog_dic = json.dumps(resp_data, indent=4)
    return HttpResponse(catelog_dic, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catelog_productdts(request, dts):
    product_data = json.loads(request.body)
    scope = request.scope
    catelog_service = CatelogService(scope)
    resp_data = catelog_service.catelog_productdts(product_data, dts)
    # productId_arr = product_data['product_id']
    # catalog_obj1 = Catelog.objects.filter(productname__in=productId_arr, direct_to=dts)
    # list_id = []
    # list_ary = []
    # if len(catalog_obj1) > 0:
    #     for c in catalog_obj1:
    #         if c.productname not in list_ary:
    #             list_id.append(c.id)
    #             list_ary.append(c.productname)
    # product_data = {"id": list_ary}
    # print(list_id)
    # print("p", list_ary)
    product_dic = json.dumps(resp_data, indent=4)
    return HttpResponse(product_dic, content_type='application/json')


#prpo-related api
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_get(request):
    catalog_data = json.loads(request.body)
    catalogId_arr = catalog_data['catalog_id']
    scope = request.scope
    catalog_serv = CatelogService(scope)
    list_data = catalog_serv.product_get(catalogId_arr)
    # catalog = Catelog.objects.filter(id__in = catalogId_arr).values('id', 'code', 'name', 'productname')
    # product_list_data = NWisefinList()
    # for i in catalog:
    #     data = {"id": i['id'], "code": i['code'], "name": i['name']}
    #     product_list_data.append(data)
    return HttpResponse(list_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_unitprice(request):
    scope = request.scope
    catalog_service = CatelogService(scope)
    employee_id = request.employee_id
    supplier_id = request.GET.get('supplier_id')
    product_id = request.GET.get('product_id')
    resp_obj = catalog_service.fetch_unitprice(supplier_id, product_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
