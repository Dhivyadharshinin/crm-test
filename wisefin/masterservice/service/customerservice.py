import json

import django

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.cityresponse import CityResponse
from masterservice.data.response.customerresponse import CustomerResponse
from masterservice.models import Courier, Customer, City, Apcategory, APsubcategory, Commodity
from masterservice.data.response.courierresponse import CourierResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.addressservice import AddressService
from masterservice.service.contactservice import ContactService
from masterservice.util.masterutil import ModifyStatus, CustomerType, Code_Gen_Type, Code_Gen_Value, Expense_category
from utilityservice.data.response.nwisefinlist import NWisefinList

from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from datetime import datetime

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()


class CustomerService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_customer(self, customer_obj, add_id, cont_id, user_id,request=None):
        if not customer_obj.get_id() is None:
            try:
                Customer_var = Customer.objects.using(self._current_app_schema()).filter(id=customer_obj.get_id(),
                                                                                         entity_id=self._entity_id()).update(
                    customer_entitygid=self._entity_id(),
                    customer_name=customer_obj.get_customer_name(),
                    customer_billingname=customer_obj.get_customer_name(),
                    # customer_type = 1,
                    # customer_subtype = 1,
                    # custgroup_id = 1,
                    # category_id = 1,
                    # location_gid = 1,
                    customer_constitution=customer_obj.get_customer_constitution,
                    customer_salemode=customer_obj.get_customer_salemode(),
                    customer_size=customer_obj.get_customer_size(),
                    customer_landmark=customer_obj.get_customer_landmark(),
                    # insert_flag = customer_obj.get_insert_flag,
                    # update_flag = customer_obj.get_update_flag,
                    remarks=customer_obj.get_remarks,
                    address_id=add_id,
                    contact_id=cont_id,
                    updated_date=now,
                    updated_by=user_id)

                Customer_var = Customer.objects.using(self._current_app_schema()).get(id=customer_obj.get_id(),
                                                                                      entity_id=self._entity_id())

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Customer.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            # try:
            print('customer_obj ', customer_obj.get_customer_constitution())
            Customer_var = Customer.objects.using(self._current_app_schema()).create(
                customer_entitygid=self._entity_id(),
                customer_name=customer_obj.get_customer_name(),
                customer_billingname=customer_obj.get_customer_name(),
                customer_type=CustomerType.ADHOC,
                customer_subtype=CustomerType.ADHOC,
                custgroup_id=1,
                category_id=1,
                location_gid=1,
                customer_constitution=customer_obj.get_customer_constitution(),
                customer_salemode=customer_obj.get_customer_salemode(),
                customer_size=customer_obj.get_customer_size(),
                customer_landmark=customer_obj.get_customer_landmark(),
                # insert_flag=customer_obj.get_insert_flag,
                # update_flag=customer_obj.get_update_flag,
                remarks=customer_obj.get_remarks(),
                address_id=add_id,
                contact_id=cont_id,
                created_by=user_id, entity_id=self._entity_id())

            try:
                max_cat_code = Customer.objects.using(self._current_app_schema()).filter(code__icontains='CUST').order_by('-code')[0].code
                rnsl = int(max_cat_code[4:])
            except:
                rnsl = 0
            new_rnsl = rnsl + 1
            code = "CUST" + str(new_rnsl).zfill(4)# code = "CUST" + str(cust_code)
            Customer_var.customer_code = code
            Customer_var.save()
        # except IntegrityError as error:
        #     error_obj = Error()

        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        customer_data = CustomerResponse()


        customer_data.set_id(Customer_var.id)
        customer_data.set_customer_entitygid(Customer_var.customer_entitygid)
        customer_data.set_customer_code(Customer_var.customer_code)
        customer_data.set_customer_name(Customer_var.customer_name)
        customer_data.set_customer_billingname(Customer_var.customer_billingname)
        customer_data.set_customer_type(Customer_var.customer_type)
        customer_data.set_customer_subtype(Customer_var.customer_subtype)
        customer_data.set_custgroup_id(Customer_var.custgroup_id)
        customer_data.set_category_id(Customer_var.category_id)
        customer_data.set_location_gid(Customer_var.location_gid)
        customer_data.set_customer_constitution(Customer_var.customer_constitution)
        customer_data.set_customer_salemode(Customer_var.customer_salemode)
        customer_data.set_customer_size(Customer_var.customer_size)
        customer_data.set_customer_landmark(Customer_var.customer_landmark)
        customer_data.set_insert_flag(Customer_var.insert_flag)
        customer_data.set_update_flag(Customer_var.update_flag)
        customer_data.set_remarks(Customer_var.remarks)

        return customer_data

    def fetch_customer_list(self, vys_page, name, emp_id):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if name is not None:
            condition &= Q(customer_name__icontains=name)

        customer_list = Customer.objects.using(self._current_app_schema()).filter(condition)[
                        vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(customer_list)
        print('list_length', list_length)
        customer_list_data = NWisefinList()
        if list_length > 0:
            for customer_obj in customer_list:

                customer_data = CustomerResponse()
                customer_data.set_id(customer_obj.id)
                customer_data.set_code(customer_obj.customer_code)
                customer_data.set_name(customer_obj.customer_name)
                customer_list_data.append(customer_data)

            vpage = NWisefinPaginator(customer_list, vys_page.get_index(), 10)
            customer_list_data.set_pagination(vpage)
        return customer_list_data

    def fetch_customer(self, customer_id, emp_id):
        try:
            addrs_serv = AddressService(self._scope())  # changed
            customer_obj = Customer.objects.using(self._current_app_schema()).get(id=customer_id,
                                                                                  entity_id=self._entity_id())
            customer_data = CustomerResponse()
            customer_data.set_id(customer_obj.id)
            customer_data.set_code(customer_obj.customer_code)
            customer_data.set_name(customer_obj.customer_name)
            customer_data.set_address(addrs_serv.fetch_address(customer_obj.address_id,emp_id))
            return customer_data

        except Customer.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
            error_obj.set_description(ErrorDescription.INVALID_CUSTOMER_ID)
            return error_obj

    #TA

    def city_name(self, city_name):
        state = City.objects.using(self._current_app_schema()).filter(name__icontains=city_name,
                                                                      entity_id=self._entity_id()).last()
        state_id = False
        if state is not None:
            state_id = state.state_id
        return state_id
    def ta_city_id(self, city_id):
        cityname = City.objects.using(self._current_app_schema()).get(id=city_id)
        resp=CityResponse()
        resp.set_name(cityname.name)
        resp.set_code(cityname.code)
        return resp


    def ta_city_dropdown(self,request,city_name,vys_page):
        if city_name ==None:
            # city_name = City.objects.using(self._current_app_schema()).all()[vys_page.get_offset():vys_page.get_query_limit()]
            city_name = City.objects.using(self._current_app_schema()).values('name').distinct()[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            city_name = City.objects.using(self._current_app_schema()).filter(name__icontains=city_name).values('name').distinct()[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list= NWisefinList()
        for data in city_name:
            resp=CityResponse()
            resp.set_name(data['name'])
            # resp.set_code(data['code'])
            resp_list.append(resp)
        vpage = NWisefinPaginator(city_name, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)

        return resp_list

    def ecf_category_code(self, id):
        category_id = Apcategory.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        category_code = category_id.code
        return category_code

    def ecf_subcategory_code(self, id):
        subcategory_id = APsubcategory.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        subcategory_code = subcategory_id.code
        return subcategory_code

    def ap_cat_no_get(self, no):
        category = Apcategory.objects.using(self._current_app_schema()).filter(no=no, entity_id=self._entity_id())[0]
        return json.dumps({"id": category.id, "code": category.code})

    def ap_subcat_no_get(self, no, cat_id):
        subcategory = APsubcategory.objects.using(self._current_app_schema()).filter(no=no, category_id=cat_id,
                                                                                     entity_id=self._entity_id())[0]
        return subcategory.code

    def ta_reason_category(self,reason):

        category=Apcategory.objects.using(self._current_app_schema()).filter(name__icontains=reason)
        return category

    def ta_sub_category(self, category_no,expense):
        sub_category = APsubcategory.objects.using(self._current_app_schema()).filter(category_id=category_no,name__icontains=expense)
        if len(sub_category)==0:
            sub_category = APsubcategory.objects.using(self._current_app_schema()).filter(category_id=category_no,
                                                                                          name__icontains=Expense_category.others)
        return sub_category

    def ta_commodity(self,ta_commodity):
        ta_commodity = Commodity.objects.using(self._current_app_schema()).filter(name__icontains=ta_commodity).first()
        return ta_commodity.id
    def fetch_customer_fa(self, customer_id,request):
        try:
            scope=request.scope
            addrs_serv=AddressService(scope)
            customer_obj = Customer.objects.using(self._current_app_schema()).filter(id=customer_id)
            if len(customer_obj)>0:
                customer_obj = customer_obj[0]
                customer_data = CustomerResponse()
                customer_data.set_id(customer_obj.id)
                customer_data.set_code(customer_obj.customer_code)
                customer_data.set_name(customer_obj.customer_name)
                customer_data.set_address(addrs_serv.fetch_address(customer_obj.address_id,1))
                return customer_data
            else:
                customer_data = CustomerResponse()
                customer_data.set_customer_name(None)
                return customer_data

        except Customer.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
            error_obj.set_description(ErrorDescription.INVALID_CUSTOMER_ID)
            return error_obj


