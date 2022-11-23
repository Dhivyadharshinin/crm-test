from vendorservice.models import Vendor, VendorContact, VendorRelAddress, VendorAddress, VendorProfile, \
    VendorRelContact, SupplierBranch, SupplierActivity, Catelog, ActivityDetail
from vendorservice.util.vendorutil import VendorDefaults, Code_Gen_Type
from vendorservice.service.vendorservice import VendorService
from vendorservice.data.response.supplierresponse import BranchResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
from utilityservice.data.response.nwisefinlist import NWisefinList
from vendorservice.data.request.vendorrequest import VowVendorRequest, VowActivityRequest
from utilityservice.service.vendorapiservice import VendorAPIService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator


class VOWService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def insert_approved_vendor(self, resp_json):
            resp_data = VowVendorRequest(resp_json)
        # try:
            ven_serv = VendorService(self._scope())
            default = VendorDefaults()
            vendor = Vendor.objects.using(self._current_app_schema()).create(name=resp_data.get_main_name(),
                                                                             panno=resp_data.get_pan_no(),
                                                                             gstno=resp_data.get_gst_no(),
                                                                             rm_id=resp_data.get_rm_id(),
                                                                             entity_id=self._entity_id(),
                                                                             emaildays=default.EMAIL_DAYS,
                                                                             comregno=default.COM_REG_NO,
                                                                             website=default.WEBSITE,
                                                                             activecontract=default.ACTIVE_CONTACT,
                                                                             nocontract_reason=default.NO_CONTACT_REASON,
                                                                             aproxspend=default.APPROX_SPEND,
                                                                             actualspend=default.ACTUAL_SPEND,
                                                                             remarks=default.REMARKS,
                                                                             description=default.DESCRIPTION,
                                                                             portal_flag=default.PORTAL_FLAG,
                                                                             composite=default.get_composite(
                                                                                 resp_data.get_gst_no()),
                                                                             group=default.GROUP,
                                                                             custcategory_id=default.CUSTOMER_CATEGORY,
                                                                             classification=default.CLASSIFIACTION,
                                                                             type=default.TYPE,
                                                                             orgtype=default.ORGTYPE,
                                                                             created_by=resp_data.get_created_by())
            vendor_code = ven_serv.codegenerator(Code_Gen_Type.vendor, resp_data.get_created_by())
            code = "PA" + str(vendor_code)
            vendor.code = code
            vendor.save()
            vendor_address = VendorAddress.objects.using(self._current_app_schema()
                                                         ).create(line1=resp_data.get_line_1(),
                                                                  line2=resp_data.get_line_2(),
                                                                  line3=resp_data.get_line_3(),
                                                                  pincode_id=resp_data.get_pincode_id(),
                                                                  city_id=resp_data.get_city_id(),
                                                                  district_id=resp_data.get_district_id(),
                                                                  state_id=resp_data.get_state_id(),
                                                                  entity_id=self._entity_id(),
                                                                  portal_flag=default.PORTAL_FLAG,
                                                                  vendor_id=vendor.id,
                                                                  created_by=resp_data.get_created_by())

            vendor_contact = VendorContact.objects.using(self._current_app_schema()
                                                         ).create(name=resp_data.get_cont_name(),
                                                                  designation=resp_data.get_designation(),
                                                                  mobile=resp_data.get_mobile_1(),
                                                                  mobile2=resp_data.get_mobile_2(),
                                                                  email=resp_data.get_email(),
                                                                  entity_id=self._entity_id(),
                                                                  landline=default.LAND_LINE,
                                                                  landline2=default.LAND_LINE_2,
                                                                  portal_flag=default.PORTAL_FLAG,
                                                                  vendor_id=vendor.id,
                                                                  created_by=resp_data.get_created_by())
            vendor_profile = VendorProfile.objects.using(self._current_app_schema()
                                                         ).create(branch=default.BRANCH,
                                                                  entity_id=self._entity_id(),
                                                                  portal_flag=default.PORTAL_FLAG,
                                                                  vendor_id=vendor.id,
                                                                  created_by=resp_data.get_created_by())

            supplier_address = VendorRelAddress.objects.using(self._current_app_schema()
                                                              ).create(line1=resp_data.get_line_1(),
                                                                       line2=resp_data.get_line_2(),
                                                                       line3=resp_data.get_line_3(),
                                                                       pincode_id=resp_data.get_pincode_id(),
                                                                       city_id=resp_data.get_city_id(),
                                                                       district_id=resp_data.get_district_id(),
                                                                       state_id=resp_data.get_state_id(),
                                                                       entity_id=self._entity_id(),
                                                                       portal_flag=default.PORTAL_FLAG,
                                                                       created_by=resp_data.get_created_by())
            supplier_contact = VendorRelContact.objects.using(self._current_app_schema()
                                                              ).create(name=resp_data.get_cont_name(),
                                                                       designation=resp_data.get_designation(),
                                                                       mobile=resp_data.get_mobile_1(),
                                                                       mobile2=resp_data.get_mobile_2(),
                                                                       email=resp_data.get_email(),
                                                                       entity_id=self._entity_id(),
                                                                       landline=default.LAND_LINE,
                                                                       landline2=default.LAND_LINE_2,
                                                                       portal_flag=default.PORTAL_FLAG,
                                                                       created_by=resp_data.get_created_by())

            supplier_branch = SupplierBranch.objects.using(self._current_app_schema()
                                                           ).create(name=resp_data.get_main_name(),
                                                                    panno=resp_data.get_pan_no(),
                                                                    gstno=resp_data.get_gst_no(),
                                                                    entity_id=self._entity_id(),
                                                                    remarks=default.REMARKS,
                                                                    creditterms=default.CREDIT_TERMS,
                                                                    portal_flag=default.PORTAL_FLAG,
                                                                    vendor_id=vendor.id,
                                                                    address_id=supplier_address.id,
                                                                    contact_id=supplier_contact.id,
                                                                    created_by=resp_data.get_created_by())

            supplier = ven_serv.codegenerator(Code_Gen_Type.supplier, resp_data.get_created_by())
            code = "SU" + str(supplier)
            supplier_branch.code = code
            supplier_branch.save()
            activity_contact = VendorRelContact.objects.using(self._current_app_schema()
                                                              ).create(
                mobile=default.MOBILE_1,
                mobile2=default.MOBILE_2,
                email=default.EMAIL,
                entity_id=self._entity_id(),
                landline=default.LAND_LINE,
                landline2=default.LAND_LINE_2,
                portal_flag=default.PORTAL_FLAG,
                created_by=resp_data.get_created_by())
            activity = SupplierActivity.objects.using(self._current_app_schema()
                                                      ).create(type=resp_data.get_activity_type(),
                                                               name=resp_data.get_activity_name(),
                                                               rm=resp_data.get_rm_name(),
                                                               description=default.DESCRIPTION,
                                                               fidelity=default.FIDELITY,
                                                               bidding=default.BIDDING,
                                                               activity_status=default.ACTIVE_STATUS,
                                                               portal_flag=default.PORTAL_FLAG,
                                                               contact_id=activity_contact.id,
                                                               branch_id=supplier_branch.id,
                                                               created_by=resp_data.get_created_by(),
                                                               entity_id=self._entity_id(),
                                                               is_validate=True)

            activity_detail = ActivityDetail.objects.using(self._current_app_schema()
                                                           ).create(activity_id=activity.id,
                                                                    detailname=resp_data.get_activity_name(),
                                                                    raisor=resp_data.get_created_by(),
                                                                    approver=resp_data.get_rm_id(),
                                                                    remarks=default.REMARKS,
                                                                    portal_flag=default.PORTAL_FLAG,
                                                                    entity_id=self._entity_id(),
                                                                    created_by=resp_data.get_created_by(),
                                                                    is_validate=True)

            code = 'AD' + str(activity_detail.id)
            activity_detail.code = code
            activity_detail.save()

            detail_name = '(' + code + ')' + ' ' + str(activity_detail.detailname)
            catelog = Catelog.objects.using(self._current_app_schema()
                                            ).create(activitydetail_id=activity_detail.id,
                                                     detailname=detail_name,
                                                     productname=resp_data.get_product_name(),
                                                     category=resp_data.get_catelog_category(),
                                                     subcategory=resp_data.get_catelog_subcategory(),
                                                     name=default.NAME,
                                                     specification=default.SPECIFICATION,
                                                     size=default.SIZE,
                                                     remarks=default.REMARKS,
                                                     capacity=default.CAPACITY,
                                                     direct_to=default.DIRECT_TO,
                                                     portal_flag=default.PORTAL_FLAG,
                                                     entity_id=self._entity_id(),
                                                     created_by=resp_data.get_created_by())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            success_obj.vendor_code= vendor.code
            success_obj.vendor_id= vendor.id
            return success_obj
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj

    def get_pan_exist(self, pan_no):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(panno=pan_no, entity_id=self._entity_id())
        if len(vendor) == 0:
            pan_exist = False
        else:
            pan_exist = True
        data = NWisefinLiteList()
        data.pan_exist = pan_exist
        return data

    def insert_activity(self, resp_json, branch_code):
        branch = SupplierBranch.objects.using(self._current_app_schema()).filter(code=branch_code,
                                                                                 entity_id=self._entity_id(),
                                                                                 modify_status=-1)
        if len(branch) != 0:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(id=branch[0].vendor_id,
                                                                             entity_id=self._entity_id())
            rm_id = vendor[0].rm_id
            emp_serv = VendorAPIService(self._scope())
            rm_name = emp_serv.get_emp_name_id(rm_id)
            created_by = vendor[0].created_by
            supplier_branch = branch[0]
            resp_data = VowActivityRequest(resp_json)
            try:
                default = VendorDefaults()
                activity_contact = VendorRelContact.objects.using(self._current_app_schema()
                                                                  ).create(
                    mobile=default.MOBILE_1,
                    mobile2=default.MOBILE_2,
                    email=default.EMAIL,
                    entity_id=self._entity_id(),
                    landline=default.LAND_LINE,
                    landline2=default.LAND_LINE_2,
                    portal_flag=default.PORTAL_FLAG,
                    created_by=created_by)
                activity = SupplierActivity.objects.using(self._current_app_schema()
                                                          ).create(type=resp_data.get_activity_type(),
                                                                   name=resp_data.get_activity_name(),
                                                                   rm=rm_name,
                                                                   description=default.DESCRIPTION,
                                                                   fidelity=default.FIDELITY,
                                                                   bidding=default.BIDDING,
                                                                   activity_status=default.ACTIVE_STATUS,
                                                                   portal_flag=default.PORTAL_FLAG,
                                                                   contact_id=activity_contact.id,
                                                                   branch_id=supplier_branch.id,
                                                                   created_by=created_by,
                                                                   entity_id=self._entity_id(),
                                                                   is_validate=True)

                activity_detail = ActivityDetail.objects.using(self._current_app_schema()
                                                               ).create(activity_id=activity.id,
                                                                        detailname=resp_data.get_activity_name(),
                                                                        raisor=created_by,
                                                                        approver=rm_id,
                                                                        remarks=default.REMARKS,
                                                                        portal_flag=default.PORTAL_FLAG,
                                                                        entity_id=self._entity_id(),
                                                                        created_by=created_by,
                                                                        is_validate=True)

                code = 'AD' + str(activity_detail.id)
                activity_detail.code = code
                activity_detail.save()

                detail_name = '(' + code + ')' + ' ' + str(activity_detail.detailname)
                catelog = Catelog.objects.using(self._current_app_schema()
                                                ).create(activitydetail_id=activity_detail.id,
                                                         detailname=detail_name,
                                                         productname=resp_data.get_product_name(),
                                                         category=resp_data.get_catelog_category(),
                                                         subcategory=resp_data.get_catelog_subcategory(),
                                                         name=default.NAME,
                                                         specification=default.SPECIFICATION,
                                                         size=default.SIZE,
                                                         remarks=default.REMARKS,
                                                         capacity=default.CAPACITY,
                                                         direct_to=default.DIRECT_TO,
                                                         portal_flag=default.PORTAL_FLAG,
                                                         entity_id=self._entity_id(),
                                                         created_by=created_by)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


class VendorVOWService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def get_supplier_summary(self, code, ven_type, vys_page):
        if ven_type == 1:
            vendor = Vendor.objects.using(self._current_app_schema()).filter(code=code, entity_id=self._entity_id(),
                                                                             modify_status=-1)
            supplier_list = SupplierBranch.objects.using(self._current_app_schema()
                                                         ).filter(vendor_id=vendor[0].id, modify_status=-1,
                                                                  entity_id=self._entity_id())[
                            vys_page.get_offset():vys_page.get_query_limit()]
            list_data = NWisefinList()
            for supplier in supplier_list:
                resp = BranchResponse()
                resp.set_id(supplier.id)
                resp.set_code(supplier.code)
                resp.set_name(supplier.name)
                resp.pan_no = supplier.panno
                resp.gst_no = supplier.gstno
                resp.phone_no = ''
                list_data.append(resp)
            vpage = NWisefinPaginator(supplier_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
            return list_data


        else:
            supplier_list = SupplierBranch.objects.using(self._current_app_schema()).filter(code=code,
                                                                                            entity_id=self._entity_id(),
                                                                                            modify_status=-1)[
                            vys_page.get_offset():vys_page.get_query_limit()]
            list_data = NWisefinList()
            for supplier in supplier_list:
                resp = BranchResponse()
                resp.set_id(supplier.id)
                resp.set_code(supplier.code)
                resp.set_name(supplier.name)
                resp.pan_no = supplier.panno
                resp.gst_no = supplier.gstno
                resp.phone_no = ''
                list_data.append(resp)
            vpage = NWisefinPaginator(supplier_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
            return list_data

    def branch_details(self, ven_code, vys_page):
        vendor = Vendor.objects.using(self._current_app_schema()).filter(code=ven_code, entity_id=self._entity_id(),
                                                                         modify_status=-1)
        list_data = NWisefinList()
        if len(vendor) != 0:
            branch_list = SupplierBranch.objects.using(self._current_app_schema()).filter(vendor_id=vendor[0].id,
                                                                                          entity_id=self._entity_id(),
                                                                                          modify_status=-1)
            for branch in branch_list:
                resp = BranchResponse()
                resp.set_id(branch.id)
                resp.set_code(branch.code)
                resp.set_name(branch.name)
                resp.pan_no = branch.panno
                resp.gst_no = branch.gstno
                list_data.append(resp)
            vpage = NWisefinPaginator(branch_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
        return list_data
