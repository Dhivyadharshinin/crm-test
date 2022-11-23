import json
import traceback
from datetime import datetime, date, timedelta

import pandas as pd
from dateutil import parser
from django.db import IntegrityError, Error, transaction
from django.db.models import Q,QuerySet
from faservice.data.response.assetidresponse import AssetidResponse
from faservice.data.response.assetsaleresponse import AssetSaleResponse
from faservice.data.response.assetvaluechangeresponse import AssetValueResponse
from faservice.models.famodels import AssetId, AssetValue, AssetDetails, AssetHeader, AssetTFR, Depreciation, \
    AssetsaleHeader, AssetsaleDetails, InvoiceHeader, InvoiceDetails, AssetEntry, AssetCat
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import ApiCall, ServiceCall, FaApiService, DictObj
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetRequestfor, AssetRequestStatus, \
    AssetStatus, AssetSource, assetvaluedtl_status, asset_requestfor_status, asset_requeststatus, assetrequst_status, \
    AssetEntryType, AssetDetailsRequestStatus, AssetDetailsProcess
from nwisefin.settings import BASE_DIR
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.data.response.faauditresponse import FaAuditResponse
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import RoleList,ModuleList
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetSale(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def get_assetsale_list(self, vys_page,filter_json,emp_id,request=None):
        scope=request.scope
        try:
            assetid_list = NWisefinList()
            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr,' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker
            if maker in role_arr :
                condition = Q(assetdetails_status=AssetStatus.ACTIVE,requestfor=AssetRequestfor.DEFAULT)
            else:
                return assetid_list
            if 'assetdetails_value' in filter_json:
                condition&= Q(assetheader__valuetot=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition&= Q(branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition&= Q(assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition&= Q(barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition&= Q(capdate=filter_json['capdate'])

            from django.db.models import Max
            summary_data=AssetDetails.objects.values('barcode').filter(condition).exclude(assetheader_id=0,requeststatus=AssetRequestStatus.SUBMITTED).annotate(last_id=Max('id',)).order_by('barcode')[vys_page.get_offset():vys_page.get_query_limit()]
            summary_data=summary_data.values_list('last_id',flat=True)
            id_list=[i for i in summary_data]
            condition&=Q(id__in=id_list)
            summary_data = AssetDetails.objects.filter(condition).values()
            fields = list(summary_data[0].keys())
            agg = dict.fromkeys(fields, 'first')
            df = pd.DataFrame(summary_data)#.groupby(by=['barcode']).agg(agg)
            summary_data = df.to_dict('records')
            # summary_data = summary_data[vys_page.get_offset():vys_page.get_query_limit()]
            fa_obj = FaApiService(scope)
            resp_list = NWisefinList()
            dictobj = DictObj()
            if len(summary_data) > 0 :
                for assetfr in summary_data:
                    assetfr=dictobj.get_obj(assetfr)
                    assetvalue_resp = AssetSaleResponse()
                    #Asset_Details
                    assetvalue_resp.set_capdate(assetfr.capdate)
                    assetvalue_resp.set_assetdetails_id(assetfr.id)
                    assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                    assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.assetdetails_status))
                    assetvalue_resp.set_status(assetrequst_status(assetfr.status))
                    asst_header_data=AssetHeader.objects.filter(id=assetfr.assetheader_id)
                    if len(asst_header_data)>0:
                        assetvalue_resp.set_assetvalue(asst_header_data[0].valuetot)
                    else:
                        continue
                    assetvalue_resp.set_barcode(assetfr.barcode)
                    assetvalue_resp.set_end_date(assetfr.enddate)
                    #depreciation #last_dep_rundate
                    try:
                        assetdepre_data = Depreciation.objects.filter(assetdetails_id=assetfr.id)[0]
                        assetvalue_resp.set_last_dep_rundate(str(assetdepre_data.depreciation_todate))
                    except:
                        assetvalue_resp.set_last_dep_rundate("")

                    #CB Value
                    #assethdr_data = AssetHeader.objects.filter(barcode=assetfr.barcode)[0]
                    assethdr_data = asst_header_data[0]
                    print(assetfr.id,' assethdr_data ')
                    assetvalue_resp.set_cb_value(assethdr_data.revisedcbtot)


                    #product
                    fa_service_call=FaApiService(scope)
                    product_data=fa_service_call.fetch_product(assetfr.product_id,emp_id,request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    #HSN Details
                    assetvalue_resp.set_hsn_details(product_data.hsn_id)
                    print('product_data  ',product_data)
                    #print('product_data ',product_data.name)
                    #asset Location
                    location_serv = AssetLocationService(scope)
                    print(assetfr.id)
                    location = location_serv.fetch_assetlocation(assetfr.assetlocation_id)
                    print(assetfr.assetlocation_id,'assetdetails.assetlocation_id')
                    assetvalue_resp.set_location(location.name)
                    assetvalue_resp.set_location_id(assetfr.assetlocation_id)
                    #employee_branch
                    # employee_branch = assetval.assetdetails.branch # employee_branch FK details get
                    employee_branch = fa_obj.fetch_branch(assetfr.branch_id)
                    assetvalue_resp.set_branch_id(employee_branch.id)
                    assetvalue_resp.set_branch_name(employee_branch.name)
                    #assetcat
                    assetcat=AssetCat.objects.get(id=assetfr.assetcat_id).__dict__
                    assetcat.pop('_state') # assetcat FK details get
                    assetcat=dictobj.get_obj(assetcat)
                    assetvalue_resp.set_assetcat_id(assetcat)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                assetid_list.data=assetid_list.data
                vpage = NWisefinPaginator(assetid_list.data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    #@transaction.atomic(using='fa_service')
    def make_assetsale(self,  sale_json, emp_id,request):
        try:
            scope=request.scope
            with transaction.atomic(using=self._current_app_schema()):
                totalamount=0
                assetsale_date = sale_json['assetsale_date']
                reason=None
                if 'reason' in sale_json:
                    reason=sale_json['reason']
                for sale_data in sale_json['assetdetails']:
                    totalamount=float(totalamount)+float(sale_data['sale_rate'])
                    branch_id=sale_data['branch_id']
                assetdtl_data = AssetDetails.objects.filter(assetdetails_id=sale_json['assetdetails'][0]['assetdetails_id'])[0]
                sal_val_tax = self.get_sale_val_gst(assetsale_date, assetdtl_data, sale_json['assetdetails'][0])
                #invoice header insert here
                invoiceheader_data=self.invoice_header_sale_enter(totalamount,branch_id,sale_json,emp_id,sal_val_tax)
                #Asset Sale header insert here
                assetsalehdr_data = AssetsaleHeader.objects.create(customergid=sale_json['customer_id'],
                            salebranchgid=branch_id,
                     saledate=assetsale_date, saletotalamount=totalamount,
                     invoiceheadergid=invoiceheader_data.id,
                     status=AssetRequestStatus.PENDING,
                     assetsaleheader_remarks=reason,
                     issalenote= sale_json['is_salenote'],
                     created_by=emp_id)
                #Asset Sale details insert here and asset details update
                for sale in sale_json['assetdetails']:
                    assetdtl_update = AssetDetails.objects.filter(assetdetails_id=sale['assetdetails_id']).update(
                        requestfor=AssetRequestfor.SALE,
                        requeststatus=AssetRequestStatus.PENDING,
                        updated_by=emp_id,
                        updated_date = now())

                    assetdtl_data = AssetDetails.objects.filter(assetdetails_id=sale['assetdetails_id'])[0]


                    conditions=Q(assetdetails_id=sale['assetdetails_id'])
                    print(conditions)
                    assetdtlsdata = AssetDetails.objects.filter(conditions)[0]
                    if 'igst_rate' in sale:
                        sale['sgst_rate']=0
                        sale['cgst_rate']=0
                    ##Asset Sale value as per GST
                    assetsaledtl_data = AssetsaleDetails.objects.create( assetdetails_id=assetdtlsdata.id,
                                                saledetailsdate=assetsale_date,reason=reason,
                                                customer=sale_json['customer_id'],assetsaledetails_value=sale['sale_rate'],
                                                sgst=sale['sgst_rate'],cgst=sale['cgst_rate'],igst=sale['igst_rate'],
                                                invoiceheadergid=1, hsncode=sale['hsn_code'],
                                                status=AssetRequestStatus.PENDING,
                                                created_by=emp_id,  assetsaleheader_id=assetsalehdr_data.id)
                    product_service = FaApiService(scope)
                    product_respobj = product_service.fetch_product(assetdtl_data.product_id, emp_id)
                    print('product_respobj ',product_respobj.id)
                    print('assetdtl_data.product_id ',assetdtl_data.product_id)
                    print('product_respobj.uom ',product_respobj.uom_id.id)

                    invoice_dtl=InvoiceDetails.objects.create(invoiceheader_id=invoiceheader_data.id,
                                                        #campaign_id = models.IntegerField(default=0)
                                                        product_id = assetdtl_data.product_id,
                                                        product_code =product_respobj.code,
                                                        uom_id=product_respobj.uom_id.id,
                                                        unitprice = sale['sale_rate'],
                                                        qty=1,
                                                        hsncode=sale['hsn_code'],
                                                        invoiceheader_channel ="FA",
                                                        invoiceheader_remarks =reason,
                                                        # dealerprice = sale['sale_rate,'],
                                                        # nrpprice = sale['sale_rate'],
                                                        sgst = sale['sgst_rate'],
                                                        cgst = sale['cgst_rate'],
                                                        igst = sale['igst_rate'],
                                                        #discount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
                                                        taxamount = sal_val_tax[-1],
                                                        total = invoiceheader_data.total,
                                                        created_by=emp_id)



                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        except Exception  as excep:
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj
        return success_obj
    def get_sale_val_gst(self,assetsale_date,assetdtlsdata,sale):
        end_date = assetsale_date
        cap_date = assetdtlsdata.capdate
        no_of_days = (parser.parse(end_date).date() - cap_date + timedelta(days=1)).days
        no_of_months = round(no_of_days / 30)
        asset_cost = assetdtlsdata.assetdetails_value
        asst_cat = assetdtlsdata.assetcat_id
        asset_cat_data = AssetCat.objects.get(id=asst_cat)
        lifetime = asset_cat_data.lifetime
        sale_val_gst = asset_cost - (asset_cost * no_of_months / lifetime)
        if False:#sale_val_gst > sale['sale_rate']:
            cgst_amount = float((sale_val_gst * 9) / 100)
            sgst_amount = float((sale_val_gst * 9) /100)
            igst_amount=float((sale_val_gst * 18) /100)
        else:
            cgst_amount = float((sale['sale_rate'] * 9) / 100)
            sgst_amount = float((sale['sale_rate'] * 9) / 100)
            igst_amount = float((sale['sale_rate'] * 18) / 100)
        return cgst_amount,sgst_amount,igst_amount
    def invoice_header_sale_enter(self,totalamount,branch_id,sale_json,emp_id,tax_values_list):
        reason = None
        if 'reason' in sale_json:
            reason = sale_json['reason']

        tax_amount = tax_values_list[-1]
        tax_totalamt=float(totalamount)+float(tax_amount)

        inv_hdr=InvoiceHeader.objects.create(
                    customer_id = sale_json['customer_id'],
                    invoiceheader_gstno = "VSOLVGST463657",#****here we need to replace our company GST NO******
                    invoiceheader_date = sale_json['assetsale_date'],
                    employee_id = emp_id,
                    invoiceheader_channel = "FA",
                    invoiceheader_remarks = reason,
                    amount = totalamount,
                    taxamount = tax_amount,
                    total = tax_totalamt,
                    outstanding = tax_totalamt,
                    branch_id=branch_id,
                    created_by=emp_id)

        return inv_hdr


    def fetch_assetsale_list(self, vys_page, filter_json, emp_id,request=None): #for asset sale mr summary
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr, ' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if maker in role_arr:
                condition = Q(assetdetails__status__in=[AssetStatus.ACTIVE,AssetStatus.IN_ACTIVE],
                              status__in=[AssetRequestStatus.PENDING,AssetRequestStatus.APPROVED,
                                          AssetRequestStatus.REJECTED],
                              assetdetails__requestfor__in=[AssetRequestfor.SALE,AssetRequestfor.NEW,AssetRequestfor.DEFAULT])
            else:
                return assetid_list

            if 'assetdetails_value' in filter_json:
                condition &= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition &= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition &= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition &= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition &= Q(assetdetails__capdate=filter_json['capdate'])

            assetsale_dtls_data = AssetsaleDetails.objects.filter(condition).order_by('-id')[
                                    vys_page.get_offset():vys_page.get_query_limit()]

            # print('condition',condition)

            if len(assetsale_dtls_data) > 0:
                for assetfr in assetsale_dtls_data:
                    assetvalue_resp = AssetSaleResponse()
                    assetsaledtls_data=assetfr
                    assetfr=assetfr.assetdetails

                    # Asset_Details
                    assetvalue_resp.set_capdate(assetfr.capdate)
                    assetvalue_resp.set_assetdetails_id(assetfr.id)
                    assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                    asst_status=AssetStatus()
                    #assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.assetdetails_status))
                    assetvalue_resp.set_status(asst_status.get_val(assetfr.assetdetails_status))
                    assetvalue_resp.set_assetvalue(assetfr.assetheader.valuetot)
                    assetvalue_resp.set_assetsaleheader_id(assetsaledtls_data.assetsaleheader.id)
                    assetvalue_resp.set_barcode(assetfr.barcode)
                    assetvalue_resp.set_end_date(assetfr.enddate)
                    # depreciation #last_dep_rundate
                    try:
                        assetdepre_data = Depreciation.objects.filter(assetdetails_id=assetfr.id)[0]
                        assetvalue_resp.set_depreciation_value(str(assetdepre_data.depreciation_value))
                    except:
                        assetvalue_resp.set_depreciation_value(None)

                    # assetsale_amount
                    #assetsaledtls_data = AssetsaleDetails.objects.filter(assetdetails_id=assetfr.id)[0]
                    assetvalue_resp.set_assetsale_amount(assetsaledtls_data.assetsaleheader.saletotalamount)
                    assetvalue_resp.set_reason(assetsaledtls_data.reason)
                    assetvalue_resp.set_assetsale_status(assetrequst_status(assetsaledtls_data.status))
                    assetvalue_resp.set_assetsale_date(assetsaledtls_data.saledetailsdate)

                    # customer
                    customer_serv = FaApiService(scope)
                    customer_data = customer_serv.fetch_customer(assetsaledtls_data.assetsaleheader.customergid,request)

                    assetvalue_resp.set_customer_name(customer_data.name)


                    # product
                    fa_service_call = FaApiService(scope)
                    product_data = fa_service_call.fetch_product(assetfr.product_id, emp_id, request=None)
                    assetvalue_resp.set_product_name(product_data.name)
                    # HSN Details
                    assetvalue_resp.set_hsn_details(product_data.hsn_id)
                    print('product_data  ', product_data)
                    # print('product_data ',product_data.name)
                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetfr.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assetfr.branch_id))
                    # assetcat
                    assetcat = assetfr.assetcat  # assetcat FK details get
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)
                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetsale_dtls_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list


    def get_assetsalechecker(self, vys_page, filter_json, emp_id,request=None): #for asset sale checker summary
        scope=request.scope
        try:
            assetid_list = NWisefinList()

            module_permission = ModulePermission(scope)
            role_arr = module_permission.employee_modulerole(emp_id, ModuleList.FA)
            print(role_arr, ' role_arr')
            maker = RoleList.maker
            checker = RoleList.checker

            if checker in role_arr:
                condition = Q(assetdetails__status=AssetStatus.ACTIVE,
                              status=AssetRequestStatus.PENDING,
                              assetdetails__requestfor=AssetRequestfor.SALE)
            else:
                return assetid_list

            if 'assetdetails_value' in filter_json:
                condition &= Q(assetdetails__assetdetails_value=filter_json['assetdetails_value'])
            if 'branch_id' in filter_json:
                condition &= Q(assetdetails__branch_id=filter_json['branch_id'])
            if 'assetcat_id' in filter_json:
                condition &= Q(assetdetails__assetcat_id=filter_json['assetcat_id'])
            if 'barcode' in filter_json:
                condition &= Q(assetdetails__barcode__icontains=filter_json['barcode'])
            if 'capdate' in filter_json:
                condition &= Q(assetdetails__capdate=filter_json['capdate'])

            assetsale_dtls_data = AssetsaleDetails.objects.filter(condition).order_by('-id')


            # print('condition  ',condition)

            assetsaleheader_list=list()
            if len(assetsale_dtls_data) > 0:
                for assesale in assetsale_dtls_data:
                    if assesale.assetsaleheader_id  in assetsaleheader_list:
                        continue
                    if assesale.assetsaleheader_id not in assetsaleheader_list:
                        assetsaleheader_list.append(assesale.assetsaleheader_id)


                    assetfr=assesale.assetdetails
                    assetvalue_resp = AssetSaleResponse()

                    # Asset_Details
                    assetvalue_resp.set_capdate(assetfr.capdate)
                    assetvalue_resp.set_assetdetails_id(assetfr.id)
                    assetvalue_resp.set_assetdtls_id(assetfr.assetdetails_id)
                    #assetvalue_resp.set_assetdetails_status(assetvaluedtl_status(assetfr.assetdetails_status))
                    assetvalue_resp.set_status(assetvaluedtl_status(assetfr.status))
                    assetvalue_resp.set_assetvalue(assetfr.assetheader.valuetot)
                    assetvalue_resp.set_assetsaleheader_id(assesale.assetsaleheader.id)
                    assetvalue_resp.set_barcode(assetfr.barcode)
                    assetvalue_resp.set_end_date(assetfr.enddate)
                    # depreciation #last_dep_rundate
                    try:
                        assetdepre_data = Depreciation.objects.filter(assetdetails_id=assetfr.id)[0]
                        assetvalue_resp.set_depreciation_value(str(assetdepre_data.depreciation_value))
                    except:
                        assetvalue_resp.set_depreciation_value(None)


                    # assetsale_amount
                    assetsaledtls_data = assesale
                    assetvalue_resp.sale_value = str(assetsaledtls_data.assetsaleheader.saletotalamount)

                    assetvalue_resp.set_reason(assetsaledtls_data.reason)
                    assetvalue_resp.set_assetsale_status(assetrequst_status(assetsaledtls_data.status))
                    assetvalue_resp.set_assetsale_date(assetsaledtls_data.saledetailsdate)

                    # customer
                    customer_serv = FaApiService(scope)
                    customer_data = customer_serv.fetch_customer(assetsaledtls_data.assetsaleheader.customergid, request)
                    assetvalue_resp.set_customer_name(customer_data.name)

                    if int(assetsaledtls_data.created_by) == int(emp_id):
                        approval_flage=False
                    else:
                        approval_flage=True
                    assetvalue_resp.set_approval_flage(approval_flage)

                    # product
                    fa_service_call = FaApiService(scope)
                    product_data = fa_service_call.fetch_product(assetfr.product_id, emp_id, request=None)
                    assetvalue_resp.set_product_name(product_data.name)

                    # asset Location
                    location_serv = AssetLocationService(scope)
                    assetvalue_resp.set_location(location_serv.fetch_assetlocation(assetfr.assetlocation_id))
                    # employee_branch
                    emp_branch = FaApiService(scope)
                    assetvalue_resp.branch = (emp_branch.fetch_branch(assetfr.branch_id))
                    # assetcat
                    assetcat = assetfr.assetcat  # assetcat FK details get
                    assetvalue_resp.set_assetcat_id(assetcat.id)
                    assetvalue_resp.set_assetcat_subcatname(assetcat.subcatname)



                    asset_dtls_data = AssetsaleDetails.objects.filter(assetsaleheader_id=assesale.assetsaleheader_id)
                    assetvalue_resp.total_count = (len(asset_dtls_data))

                    saledata_list = list()
                    for dtls_data in asset_dtls_data:
                        print(dtls_data.assetdetails_id,'dtls_data.assetdetails_id')
                        # product
                        fa_service_call = FaApiService(scope)
                        product_data = fa_service_call.fetch_product(dtls_data.assetdetails.product_id, emp_id, request=None)

                        asset_cat = dtls_data.assetdetails.assetcat  # assetcat FK details get
                        emp_branch = FaApiService(scope)
                        empl_branch = emp_branch.fetch_branch(dtls_data.assetdetails.branch_id)

                        # customer
                        customers_serv = FaApiService(scope)
                        assetsalehdr_data=dtls_data.assetsaleheader
                        customers_data = customers_serv.fetch_customer(assetsalehdr_data.customergid, request)


                        saledata_dict={"assetdetails_id":dtls_data.assetdetails.assetdetails_id,"product_name":product_data.name,"category_name":asset_cat.subcatname,
                                       "sale_value":str(dtls_data.assetsaledetails_value),"customer_name":customers_data.name,
                                       "branch_name":empl_branch.name,"reason":dtls_data.reason,
                                       "status":assetrequst_status(dtls_data.status),"assetsaleheader_id":assesale.assetsaleheader.id}

                        saledata_list.append(saledata_dict)
                    assetvalue_resp.sale_details = (saledata_list)

                    assetid_list.append(assetvalue_resp)
                vpage = NWisefinPaginator(assetsale_dtls_data, vys_page.get_index(), 10)
                assetid_list.set_pagination(vpage)

        except Exception  as excep:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return assetid_list

    #@transaction.atomic(using='fa_service')
    def assetsaleapprove(self,  sale_json, emp_id,request):
        scope=request.scope
        try:
            reason=None
            if 'reason' in sale_json:
                reason=sale_json['reason']
            for sale in sale_json['assetdetails']:
                if int(sale['status']) == 1 :
                    conditions = Q(assetdetails_id=sale['assetdetails_id'])
                    asset_dtls_data = AssetDetails.objects.filter(conditions).update(
                        assetdetails_status=AssetStatus.IN_ACTIVE,
                        requeststatus=AssetRequestStatus.APPROVED,
                        #requestfor=AssetRequestfor.NEW,
                                 updated_by = emp_id,
                                 updated_date = now())
                    assetdata=AssetDetails.objects.filter(barcode=sale['assetdetails_id'][:-6]).update(
                        assetdetails_status=AssetStatus.IN_ACTIVE
                    )
                    assetdtls_update = AssetDetails.objects.filter(conditions)[0]
                    assetdtls_update=AssetDetails.objects.filter(barcode=assetdtls_update.barcode).order_by('-assetdetails_id')[0]
                    id_split=assetdtls_update.assetdetails_id.split('/')
                    salep_id=id_split[0]+'/'+id_split[1]+'/'+str(int(id_split[2])+1).zfill(2)

                    asset_hdr_data = AssetHeader.objects.filter(id=assetdtls_update.assetheader_id).update(
                        issale=1,
                        updated_by=emp_id,
                        updated_date=now())
                    cap_date=assetdtls_update.capdate
                    asset_sale=AssetsaleDetails.objects.filter(assetdetails_id=assetdtls_update.id)[0]
                    end_date =asset_sale.saledetailsdate
                    datediff = end_date - cap_date
                    dep_rate=(365 / (datediff.days)) * 100
                    asset_hdr= AssetHeader.objects.filter(id=assetdtls_update.assetheader_id)[0]
                    self.create_assetentry(emp_id, sale['assetdetails_id'], request)
                    new_asset=AssetDetails.objects.create(assetdetails_id=salep_id,
                                                qty=1,  # assetdetails_obj.get_qty(),
                                                barcode=salep_id[:-6],
                                                date=now(),
                                                assetgroup_id=assetdtls_update.assetgroup_id,
                                                assetheader=assetdtls_update.assetheader,
                                                product_id=assetdtls_update.product_id,
                                                cat=assetdtls_update.cat,  # apcat
                                                subcat=assetdtls_update.subcat,  # apsubcat
                                                assetcat_id=assetdtls_update.assetcat_id,
                                                assetdetails_value=asset_hdr.valuetot,
                                                assetdetails_cost=asset_hdr.valuetot,
                                                description=assetdtls_update.description,
                                                capdate=assetdtls_update.capdate,
                                                source=AssetSource.FASALEN,
                                                assetdetails_status=AssetStatus.IN_ACTIVE,
                                                requestfor=AssetRequestfor.DEFAULT,
                                                requeststatus=AssetRequestStatus.APPROVED,
                                                assettfr_id=AssetDetailsProcess.DEFAULT,
                                                assetsale_id=AssetDetailsProcess.DEFAULT,
                                                not5k=AssetDetailsProcess.DEFAULT,
                                                assetowner=AssetDetailsProcess.DEFAULT,
                                                lease_startdate=assetdtls_update.lease_startdate,
                                                lease_enddate=assetdtls_update.lease_enddate,
                                                impairasset_id=AssetDetailsProcess.DEFAULT,
                                                impairasset=AssetDetailsProcess.DEFAULT,
                                                writeoff_id=AssetDetailsProcess.DEFAULT,
                                                assetcatchange_id=AssetDetailsProcess.DEFAULT,
                                                assetvalue_id=AssetDetailsProcess.DEFAULT,
                                                assetcapdate_id=AssetDetailsProcess.DEFAULT,
                                                assetsplit_id=AssetDetailsProcess.DEFAULT,
                                                assetmerge_id=AssetDetailsProcess.DEFAULT,
                                                assetcatchangedate=assetdtls_update.assetcatchangedate,
                                                # Need to change default date
                                                reducedvalue=AssetDetailsProcess.DEFAULT,
                                                branch_id=assetdtls_update.branch_id,
                                                assetlocation_id=assetdtls_update.assetlocation_id,
                                                assetdetails_bs=assetdtls_update.assetdetails_bs,
                                                assetdetails_cc=assetdtls_update.assetdetails_cc,
                                                deponhold=assetdtls_update.deponhold,
                                                deprate=assetdtls_update.deprate,
                                                enddate=assetdtls_update.enddate,
                                                parent_id=AssetDetailsProcess.DEFAULT,
                                                assetserialno=AssetDetailsProcess.DEFAULT,  # From prpo
                                                invoice_id=AssetDetailsProcess.DEFAULT,  # need to from faclearing
                                                faclringdetails_id=assetdtls_update.faclringdetails_id,
                                                # faclearing invoide id
                                                inwheader_id=AssetDetailsProcess.DEFAULT,
                                                inwdetail_id=AssetDetailsProcess.DEFAULT,
                                                inwarddate=assetdtls_update.inwarddate,  # default date
                                                mepno=assetdtls_update.mepno,
                                                ponum=assetdtls_update.ponum,
                                                crnum=assetdtls_update.crnum,
                                                debit_id=AssetDetailsProcess.DEFAULT,
                                                imagepath=assetdtls_update.imagepath,
                                                vendorname=assetdtls_update.vendorname,
                                                created_by=emp_id,
                                                status=AssetStatus.ACTIVE)
                    from faservice.service.depreciationservice import DepreciationService
                    depsingel_obj = {"from_date": str(cap_date), "to_date": str(end_date),
                                     "deptyp": 1, "assetdetails_id": new_asset.id, "assetdetails_source": str(AssetSource.FASALEN)}
                    dep_obj=DepreciationService(scope)
                    depsingel = dep_obj.create_singledepreciation(depsingel_obj, emp_id)

                elif  int(sale['status']) == 3 :
                    conditions = Q(assetdetails_id=sale['assetdetails_id'])
                    asset_dtls_data = AssetDetails.objects.filter(conditions).update(
                        assetdetails_status=AssetStatus.ACTIVE,
                        requestfor=AssetRequestfor.DEFAULT,
                        requeststatus=AssetRequestStatus.REJECTED,
                                 updated_by = emp_id,
                                 updated_date = now())

                asset_saledtls_update = AssetsaleDetails.objects.filter(assetdetails__assetdetails_id=sale['assetdetails_id'])
                asset_saledtls_update.update(
                                status=sale['status'],
                                reason=reason,
                                 updated_by = emp_id,
                                 updated_date = now())
                asset_salehdr_update = AssetsaleHeader.objects.filter(id=asset_saledtls_update[0].assetsaleheader_id).update(
                    status=sale['status'],
                    updated_by=emp_id,
                    updated_date=now())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        except Exception  as excep:
            traceback.print_exc()
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        return success_obj

    def create_assetentry(self,emp_id,assetdetails_id,request):
        scope=request.scope
        asstdet = AssetDetails.objects.filter(assetdetails_id=assetdetails_id)[0]
        asstsale_dtls = AssetsaleDetails.objects.filter(assetdetails_id=asstdet.id)[0]
        invoiceheadergid=asstsale_dtls.invoiceheadergid
        invhdr_data = InvoiceHeader.objects.filter(id=invoiceheadergid)[0]
        print('asstdet_id ',asstdet.id)
        saledetailsdate = asstsale_dtls.saledetailsdate
        try:
            depreciation_data = Depreciation.objects.filter(assetdetails_id=asstdet.id)[0]
            last_dep_rundate = depreciation_data.depreciation_todate
        except:
            last_dep_rundate = datetime.strptime(str(now().today().date()), '%Y-%m-%d') - timedelta(days=15)
            last_dep_rundate=last_dep_rundate.date()

        print('saledetailsdate ',last_dep_rundate,saledetailsdate)
        #print('saledetailsdate ',last_dep_rundate,saledetailsdate).fkkfk
        saletotalamount=asstsale_dtls.assetsaleheader.saletotalamount

        taxamount=float(invhdr_data.taxamount)
        assetentry_amount=float(invhdr_data.total)
        cloasingbalance_amount=float(asstdet.assetheader.revisedcbtot)
        asset_cost=float(asstdet.assetheader.costtot)
        deprate=float(asstdet.deprate)
        #saledetailsdate=asstsale_dtls.saledetailsdate

        #date_different=(saledetailsdate.date()-last_dep_rundate)
        print('last_dep_rundate',saledetailsdate,last_dep_rundate)
        print('saledetailsdate',last_dep_rundate)
        print('saledetailsdate',(saledetailsdate-last_dep_rundate).days)

        SLM_amount=float(asset_cost*deprate*(((saledetailsdate-last_dep_rundate).days)+1)/100/365)




        fa_obj=FaApiService(scope)
        apsubcat_data=fa_obj.fetchsubcategory(asstdet.subcat,request)
        apcat_data=fa_obj.fetchcategory(asstdet.cat,request)
        product_data = fa_obj.fetch_product(asstdet.product_id,emp_id,request)
        #branch details
        branch_data = fa_obj.fetch_branch(asstdet.branch_id,request)
        addres_rep = fa_obj.fetch_employee_address(branch_data.address_id)

        emp_branch_state=addres_rep['state_id']
        print('emp_branch_state ',emp_branch_state)

        logger.info("assetentry")
        Module = "FA"
        Screen = "Sale"

        Entry_Remarks = branch_data.code+asstdet.barcode+product_data.name
        logger.info("creditsuccess")
        #customer
        customer_serv = FaApiService(scope)
        customer_data = customer_serv.fetch_customer(asstsale_dtls.assetsaleheader.customergid, request)
        customer_sate=customer_data.address.city_id.state_id

        if int(emp_branch_state) != int(customer_sate) :
            igst_amount =taxamount
            print('igst_amount ',igst_amount)


            #loss amount
            if (float(cloasingbalance_amount)+float(igst_amount)) < (float(assetentry_amount)+float(SLM_amount)):
                print('igst loss amount ')
                assetentry_type_tuple = (AssetEntryType.DEBIT, AssetEntryType.CREDIT, AssetEntryType.DEBIT,
                                         AssetEntryType.CREDIT, AssetEntryType.CREDIT)
                loss_amt=(assetentry_amount+SLM_amount)-(cloasingbalance_amount+igst_amount)
                entry_amt_tuple = (assetentry_amount, cloasingbalance_amount, SLM_amount, igst_amount,loss_amt)
            #profit
            else:
                print('igst profit amount ')
                assetentry_type_tuple = (AssetEntryType.DEBIT, AssetEntryType.CREDIT, AssetEntryType.DEBIT,
                                         AssetEntryType.CREDIT, AssetEntryType.DEBIT)
                profit_amt = (cloasingbalance_amount + float(igst_amount))-(assetentry_amount + float(SLM_amount))
                entry_amt_tuple = (assetentry_amount, cloasingbalance_amount, SLM_amount, igst_amount, profit_amt)

        else:
            cgst_amount = taxamount/2
            sgst_amount = taxamount/2

            print(' cgst_amount sgst_amount ', sgst_amount)

            # loss amount
            if (cloasingbalance_amount + cgst_amount+sgst_amount) < (assetentry_amount + float(SLM_amount)):
                print(' cgst, sgst  loss amount')
                assetentry_type_tuple = (AssetEntryType.DEBIT, AssetEntryType.CREDIT, AssetEntryType.DEBIT,
                                         AssetEntryType.CREDIT,AssetEntryType.CREDIT, AssetEntryType.CREDIT)
                loss_amt = (assetentry_amount + float(SLM_amount)) - (cloasingbalance_amount + cgst_amount+sgst_amount)
                entry_amt_tuple = (assetentry_amount, cloasingbalance_amount, SLM_amount, cgst_amount,sgst_amount, loss_amt)
            # profit
            else:
                print(' cgst, sgst  profit amount')
                assetentry_type_tuple = (AssetEntryType.DEBIT, AssetEntryType.CREDIT, AssetEntryType.DEBIT,
                                         AssetEntryType.CREDIT, AssetEntryType.CREDIT, AssetEntryType.DEBIT)
                profit_amt = (cloasingbalance_amount + cgst_amount + sgst_amount)-(assetentry_amount + float(SLM_amount))
                entry_amt_tuple =(assetentry_amount,cloasingbalance_amount,SLM_amount,cgst_amount,sgst_amount,profit_amt)


        for type,entry_amt in zip(assetentry_type_tuple,entry_amt_tuple):
            assetentry_obj = AssetEntry.objects.create(branch_id=asstdet.branch_id,
                                            fiscalyear = now().year,
                                            period = now().month,
                                            module = Module,
                                            screen = Screen,
                                            transactiondate = now().date(),
                                            transactiontime = now().time(),
                                            valuedate = now().date(),
                                            valuetime = now().time(),
                                            cbsdate = now(),
                                            # localcurrency = arr_obj.get_localcurrency(),
                                            # localexchangerate = arr_obj.get_localexchangerate(),
                                            # currency = arr_obj.get_currency(),
                                            # exchangerate = arr_obj.get_exchangerate(),
                                            # isprevyrentry = arr_obj.get_isprevyrentry(),
                                            # reversalentry = arr_obj.get_reversalentry(),
                                            refno =asstdet.barcode,
                                            # crno = ,
                                            refid = asstdet.id,
                                            # reftableid = arr_obj.get_reftableid(),
                                            type = type,
                                            gl = apsubcat_data.glno,
                                            apcatno = apcat_data.no,
                                            apsubcatno =apsubcat_data.no,
                                            # wisefinmap = arr_obj.get_wisefinmap(),
                                            glremarks = Entry_Remarks,
                                            amount = entry_amt,
                                            fcamount = 0,
                                            # ackrefno = arr_obj.get_ackrefno(),
                                            created_by=emp_id,
                                            created_date=now())




    def pdf_data_return (self,assetsaleheader_id,emp_id,request=None):
        scope=request.scope
        saledtl_data=AssetsaleDetails.objects.filter(assetsaleheader_id=assetsaleheader_id)
        salehdr_data=saledtl_data[0].assetsaleheader
        asst_beanch_id=saledtl_data[0].assetdetails.branch_id
        fa_obj = FaApiService(scope)
        branch_data = fa_obj.fetch_branch(asst_beanch_id, request)
        addres_rep = fa_obj.fetch_employee_address(branch_data.address_id)
        emp_branch_state = addres_rep['state_id']
        # customer
        customers_serv = FaApiService(scope)
        customers_data = customers_serv.fetch_customer(salehdr_data.customergid, request)

        state=customers_data.address.state_id.id
        state_data=fa_obj.get_state_from_id(state,request)
        state_par={
            "state_id":state
        }
        pincode=fa_obj.fetch_pincode_state_id(state_par)
        customer_sate=state_data
        inv_data=InvoiceHeader.objects.filter(id=salehdr_data.invoiceheadergid)[0]
        saletotaltax_amt_only = float((salehdr_data.saletotalamount*saledtl_data[0].igst)/100)
        taxtotal_amount = round(float(salehdr_data.saletotalamount) + saletotaltax_amt_only)
        assetvalue_resp={"is_salenote":salehdr_data.issalenote,
            "customer_name" : customers_data.name,
                         "addr_line1":customers_data.address.line1,
                         "addr_line2":customers_data.address.line2,
                         "addr_line3":customers_data.address.line3,
                         "city_name":'',
                         "district_name":'',
                         "state_name":customer_sate.name,
                         "pincode_no":pincode['no'],"assetsale_date":str(salehdr_data.saledate),
                         "total_amount":salehdr_data.saletotalamount,"taxtotal_amount":taxtotal_amount,
                         "vsolv_GSTNO":inv_data.invoiceheader_gstno,"invoice_no":inv_data.invoiceheader_no}
                        # "img" : image_path }

        GST_Details=list()
        for i in saledtl_data:
            inv_data = InvoiceHeader.objects.filter(id=i.invoiceheadergid)[0]
            sgst_amt= round(float((i.assetsaledetails_value)*(i.sgst)/100),2)
            cgst_amt= round(float((i.assetsaledetails_value)*(i.cgst)/100),2)
            igst_amt= round(float((i.assetsaledetails_value)*(i.igst)/100),2)
            singletaxtotal_amount= round(float((i.assetsaledetails_value)*(i.igst)/100)+(float(i.assetsaledetails_value)),2)
            singletotal_amount= round(float(i.assetsaledetails_value),2)
            if int(emp_branch_state) != int(customer_sate.id):
                saledtl_dict={"singlesale_value":str(i.assetsaledetails_value),
                          "sgst_amt": '0', "cgst_amt": '0', "igst_amt": str(igst_amt),
                "sgst":"0","cgst":"0","igst":str(i.igst),"hsn_code":i.hsncode,
                          "singletaxtotal_amount":singletaxtotal_amount,"singletotal_amount":singletotal_amount}
            else:
                saledtl_dict = {"singlesale_value": str(i.assetsaledetails_value),
                                "sgst_amt": str(sgst_amt), "cgst_amt": str(cgst_amt), "igst_amt": "0",
                                "sgst": str(i.sgst), "cgst": str(i.cgst), "igst": "0", "hsn_code": i.hsncode,
                                "singletaxtotal_amount": singletaxtotal_amount,
                                "singletotal_amount": singletotal_amount}
            GST_Details.append(saledtl_dict)
        assetvalue_resp['gst_details']=(GST_Details)


        return assetvalue_resp

    def barcodelist_return(self,sale_approve_data):
        barcode_list=list()
        for assetdetls_json in sale_approve_data['assetdetails']:
            conditions = Q(assetdetails_id=assetdetls_json['assetdetails_id'])
            asset_dtls_data = AssetDetails.objects.filter(conditions)[0]
            barcode_list.append(asset_dtls_data.barcode)
        return barcode_list


    def sale_approver_validation(self,assetsale_json,approver_emp_id):
        for sale in assetsale_json['assetdetails']:
            asset_saledtls = AssetsaleDetails.objects.filter(assetdetails__assetdetails_id=sale['assetdetails_id'])[0]
            created_by=int(asset_saledtls.created_by)
            print('created_by  ',int(approver_emp_id) , created_by)
            if int(approver_emp_id) == created_by:
                return True
        return False

