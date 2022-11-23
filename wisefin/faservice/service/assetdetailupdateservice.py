import base64
import json

import pandas as pd
import dateutil.tz
from dateutil import parser
from django.db import IntegrityError
from django.db.models import Q, Count
from django.http import HttpResponse
# from docutils.parsers.rst.directives import body

from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.data.response.assetupdateresponse import AssetUpdateResponse
from faservice.models.famodels import *
from faservice.service.clearingdetailsservice import ClearingDetailsService
from faservice.service.clearingheaderservice import ClearingHeaderService
from faservice.service.faauditservice import FaAuditService
from faservice.util.FaApiService import FaApiService, DictObj, ServiceCall, ApiCall
from faservice.util.fautil import FaModifyStatus, FaRefType, FaRequestStatusUtil, AssetDocs, data_group_by
from nwisefin import settings
from nwisefin.settings import logger
from userservice.models import EmployeeBranch
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
# from django.utils.timezone import now, utc
# from pandas.io.formats.style import Styler,jinja2
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

class AssetUpdateService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_asset_update(self, resp_obj, doc_id, emp_id):
        asset_loop = Asset_update.objects.all()
        id_loop=[]
        bool_exp=False
        id_old = []
        id_old = resp_obj.get_id()
        logger.info('PV-L- ' + str(len(asset_loop)))
        for i in asset_loop:
            if i.asset_details_id not in id_loop:
                id_loop.append(i.asset_details_id)
            if id_old in id_loop:
                bool_exp = True
        if bool_exp == False:
            asset_update = Asset_update.objects.create(
                # id=resp_obj.get_id(),
                                                   asset_details_id=resp_obj.get_id(),
                                                   asset_tag=resp_obj.get_asset_tag(),
                                                   make=resp_obj.get_make(),
                                                   serial_no=resp_obj.get_serial_no(),
                                                   cr_number=resp_obj.get_cr_number(),
                                                   kvb_asset_id=resp_obj.get_kvb_asset_id(),
                                                   condition=resp_obj.get_condition(),
                                                   status=resp_obj.get_status(),
                                                   remarks=resp_obj.get_remarks(),
                                                   update_record=1,
                                                   pv_done=resp_obj.get_pv_done(),
                                                   checker_date=resp_obj.get_checker_date(),
                                                   completed_date=resp_obj.get_completed_date(),
                                                   document_id=doc_id,
                                                   product_name=resp_obj.get_product_name(),
                                                   branch_code=resp_obj.get_branch_code(),
                                                   branch_name=resp_obj.get_branch_name(),
                                                   asset_value=resp_obj.get_asset_value(),
                                                   asset_cost=resp_obj.get_asset_cost(),
                                                   barcode=resp_obj.get_barcode(),
                                                   control_office_branch=resp_obj.get_control_office_branch())
            # asset_update = Asset_update.objects.create()
            logger.info('PV-L-Insert ' + str(asset_update))
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

        elif bool_exp == True:
            asset_update = Asset_update.objects.filter(asset_details_id=resp_obj.get_id()).update(
                # id=resp_obj.get_id(),
                asset_details_id=resp_obj.get_id(),
                asset_tag=resp_obj.get_asset_tag(),
                make=resp_obj.get_make(),
                serial_no=resp_obj.get_serial_no(),
                cr_number=resp_obj.get_cr_number(),
                kvb_asset_id=resp_obj.get_kvb_asset_id(),
                condition=resp_obj.get_condition(),
                status=resp_obj.get_status(),
                remarks=resp_obj.get_remarks(),
                update_record=1,
                pv_done=resp_obj.get_pv_done(),
                checker_date=resp_obj.get_checker_date(),
                completed_date=resp_obj.get_completed_date(),
                document_id=doc_id,
                product_name=resp_obj.get_product_name(),
                branch_code=resp_obj.get_branch_code(),
                branch_name=resp_obj.get_branch_name(),
                asset_value=resp_obj.get_asset_value(),
                asset_cost=resp_obj.get_asset_cost(),
                barcode=resp_obj.get_barcode(),
                control_office_branch=resp_obj.get_control_office_branch())
            logger.info('PV-L-Update ' + str(asset_update))
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj


        # print(asset_update)
        # assetupdatesrresponse = AssetUpdateResponse()
        # assetupdatesrresponse.set_id(asset_update.id)
        # assetupdatesrresponse.set_asset_details(asset_update.asset_details)
        # assetupdatesrresponse.set_assetdetails_id(asset_update.asset_details.assetdetails_id)
        # assetupdatesrresponse.set_asset_details_id(asset_update.asset_details_id)
        # assetupdatesrresponse.set_asset_tag(asset_update.asset_tag)
        # assetupdatesrresponse.set_make(asset_update.make)
        # assetupdatesrresponse.set_serial_no(asset_update.serial_no)
        # assetupdatesrresponse.set_cr_number(asset_update.cr_number)
        # assetupdatesrresponse.set_kvb_asset_id(asset_update.kvb_asset_id)
        # assetupdatesrresponse.set_condition(asset_update.condition)
        # assetupdatesrresponse.set_status(asset_update.status)
        # assetupdatesrresponse.set_remarks(asset_update.remarks)
        # assetupdatesrresponse.set_pv_done(asset_update.pv_done)
        # assetupdatesrresponse.set_barcode(asset_update.barcode)
        # assetupdatesrresponse.set_product_name(asset_update.product_name)
        # assetupdatesrresponse.set_branch_code(asset_update.branch_code)
        # assetupdatesrresponse.set_branch_name(asset_update.branch_name)
        # assetupdatesrresponse.set_control_office_branch(asset_update.control_office_branch)
        # assetupdatesrresponse.set_assetdetails_cost(asset_update.asset_cost)
        # assetupdatesrresponse.set_assetdetails_value(asset_update.asset_value)
        # print(assetupdatesrresponse)
        # logger.info('PV-L-Response ' + str('Success'))

        # return assetupdatesrresponse

    def create_asset_update1(self, resp_obj):
        asset_loop = Asset_update.objects.all()
        id_loop = []
        bool_exp = False
        id_old = []
        id_old = resp_obj.get_id()
        logger.info('PV-L- ' + str(len(asset_loop)))
        for i in asset_loop:
            if i.id not in id_loop:
                id_loop.append(i.id)
            if id_old in id_loop:
                bool_exp = True
        if bool_exp == False:
            asset_update = Asset_update.objects.filter(id=resp_obj.get_id()).update(
                asset_tag=resp_obj.get_asset_tag(),
                make=resp_obj.get_make(),
                serial_no=resp_obj.get_serial_no(),
                cr_number=resp_obj.get_cr_number(),
                kvb_asset_id=resp_obj.get_kvb_asset_id(),
                condition=resp_obj.get_condition(),
                status=resp_obj.get_status(),
                remarks=resp_obj.get_remarks(),
                update_record=1,
                pv_done=resp_obj.get_pv_done(),
                checker_date=resp_obj.get_checker_date(),
                completed_date=resp_obj.get_completed_date(),
                product_name=resp_obj.get_product_name(),
                branch_code=resp_obj.get_branch_code(),
                branch_name=resp_obj.get_branch_name(),
                asset_value=resp_obj.get_asset_value(),
                asset_cost=resp_obj.get_asset_cost(),
                barcode=resp_obj.get_barcode(),
                control_office_branch=resp_obj.get_control_office_branch())
            # asset_update = Asset_update.objects.get(id=resp_obj.get_id())
            logger.info('PV-L-Insert ' + str(asset_update))

        elif bool_exp == True:
            asset_update = Asset_update.objects.create(id=resp_obj.get_id(),
                                                       asset_details_id=resp_obj.get_id(),
                                                       asset_tag=resp_obj.get_asset_tag(),
                                                       make=resp_obj.get_make(),
                                                       serial_no=resp_obj.get_serial_no(),
                                                       cr_number=resp_obj.get_cr_number(),
                                                       kvb_asset_id=resp_obj.get_kvb_asset_id(),
                                                       condition=resp_obj.get_condition(),
                                                       status=resp_obj.get_status(),
                                                       remarks=resp_obj.get_remarks(),
                                                       update_record=1,
                                                       pv_done=resp_obj.get_pv_done(),
                                                       checker_date=resp_obj.get_checker_date(),
                                                       completed_date=resp_obj.get_completed_date(),
                                                       product_name=resp_obj.get_product_name(),
                                                       branch_code=resp_obj.get_branch_code(),
                                                       branch_name=resp_obj.get_branch_name(),
                                                       asset_value=resp_obj.get_asset_value(),
                                                       asset_cost=resp_obj.get_asset_cost(),
                                                       barcode=resp_obj.get_barcode(),
                                                       control_office_branch=resp_obj.get_control_office_branch())
        asset_update = Asset_update.objects.get(id=resp_obj.get_id())
        logger.info('PV-L-Update ' + str(asset_update))

        # print(asset_update)
        assetupdatesrresponse = AssetUpdateResponse()
        assetupdatesrresponse.set_id(asset_update.id)
        # assetupdatesrresponse.set_asset_details(asset_update.asset_details)
        # assetupdatesrresponse.set_assetdetails_id(asset_update.asset_details.assetdetails_id)
        assetupdatesrresponse.set_asset_details_id(asset_update.asset_details_id)
        assetupdatesrresponse.set_asset_tag(asset_update.asset_tag)
        assetupdatesrresponse.set_make(asset_update.make)
        assetupdatesrresponse.set_serial_no(asset_update.serial_no)
        assetupdatesrresponse.set_cr_number(asset_update.cr_number)
        assetupdatesrresponse.set_kvb_asset_id(asset_update.kvb_asset_id)
        assetupdatesrresponse.set_condition(asset_update.condition)
        assetupdatesrresponse.set_status(asset_update.status)
        assetupdatesrresponse.set_remarks(asset_update.remarks)
        assetupdatesrresponse.set_control_office_branch(asset_update.control_office_branch)
        assetupdatesrresponse.set_pv_done(asset_update.pv_done)
        assetupdatesrresponse.set_barcode(asset_update.barcode)
        assetupdatesrresponse.set_product_name(asset_update.product_name)
        assetupdatesrresponse.set_branch_code(asset_update.branch_code)
        assetupdatesrresponse.set_branch_name(asset_update.branch_name)
        assetupdatesrresponse.set_assetdetails_cost(asset_update.asset_cost)
        assetupdatesrresponse.set_assetdetails_value(asset_update.asset_value)
        # print(assetupdatesrresponse)
        logger.info('PV-L-Response ' + str(assetupdatesrresponse))
        return assetupdatesrresponse

    def approver_save(self, resp_obj):
        return_json = dict()
        if not resp_obj.get_branch_code() is None:
            asset_update = Asset_update.objects.filter(branch_code=resp_obj.get_branch_code())
            asset_branch_code = []
            for data in asset_update:
                if data not in asset_branch_code:
                    asset_branch_code.append(data)
            for i in asset_branch_code:
                asset_update = Asset_update.objects.filter(id=i.id).update(
                    update_record=1,
                    pv_done=resp_obj.get_pv_done(),
                    checker_date=resp_obj.get_checker_date(),
                    completed_date=resp_obj.get_completed_date())
            # asset_update = Asset_update.objects.get(branch_code=resp_obj.get_branch_code())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            logger.info('PV-L-Success ' + str(success_obj))
            return success_obj

    def get_all_assetupdate(self, vys_page, user_id, branch_id, request):
        scope=request.scope
        consumer_list_data = NWisefinList()
        api_obj = FaApiService(scope)
        asset_update = Asset_update.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        # print('asset_update ', asset_update)

        if len(asset_update) > 0:
            for asset in asset_update:
                assetupdatesrresponse = AssetUpdateResponse()
                assetupdatesrresponse.set_id(asset.id)
                assetupdatesrresponse.set_assetdetails_id(asset.asset_details.assetdetails_id)
                # assetupdatesrresponse.set_barcode(asset.asset_details.barcode)
                # assetupdatesrresponse.set_product_id(api_obj.fetch_product(asset.asset_details.product_id, user_id, request))
                # assetupdatesrresponse.set_branch_id(api_obj.fetch_branch(asset.asset_details.branch_id))
                assetupdatesrresponse.set_asset_tag(asset.asset_tag)
                assetupdatesrresponse.set_make(asset.make)
                assetupdatesrresponse.set_serial_no(asset.serial_no)
                assetupdatesrresponse.set_cr_number(asset.cr_number)
                assetupdatesrresponse.set_kvb_asset_id(asset.kvb_asset_id)
                assetupdatesrresponse.set_condition(asset.condition)
                assetupdatesrresponse.set_status(asset.status)
                assetupdatesrresponse.set_remarks(asset.remarks)
                assetupdatesrresponse.set_pv_done(asset.pv_done)
                assetupdatesrresponse.set_maker_date(asset.maker_date)
                assetupdatesrresponse.set_checker_date(asset.checker_date)
                assetupdatesrresponse.set_completed_date(asset.completed_date)
                assetupdatesrresponse.set_barcode(asset.barcode)
                assetupdatesrresponse.set_product_name(asset.product_name)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                assetupdatesrresponse.set_assetdetails_cost(asset.asset_cost)
                assetupdatesrresponse.set_assetdetails_value(asset.asset_value)
                consumer_list_data.append(assetupdatesrresponse)
                vpage = NWisefinPaginator(asset_update, vys_page.get_index(), 30)
                consumer_list_data.set_pagination(vpage)
            return consumer_list_data

    def get_asset_branch_update_records(self, brn_id, user_id, request, vys_page):
        condition = Q()
        scope = request.scope
        return_list = NWisefinList()
        apiserv = ApiCall(scope)
        branch_list = apiserv.get_emp_branch_ctrl(request)
        branchDO = []
        obj_new = []
        case = 0
        for i in branch_list['data']:
            branchDO.append(i['control_office_branch'])
        if brn_id in branchDO:
            case = 1  # if DO branch there
        elif brn_id not in branchDO and brn_id != None:
            case = 2  # branch_code not in do branch and its not null
        else:
            case = 3  # branch_code null
        if case == 1:
            if 'init' in request.GET:
                condition &= Q(control_office_branch=brn_id)
        elif case == 2:
            if 'branch' in request.GET:
                condition &= Q(branch_code__in=brn_id)
        elif case == 3:
            err = Error()
            err.set_code(ErrorMessage.INVALID_branch_ID)
            err.set_description(ErrorDescription.INVALID_branch_ID)
            resp = HttpResponse(err.get(), content_type='application/json')
            return resp

        if 'branch' in request.GET:
            condition &= Q(branch_code__in=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))

        if case == 2:
            data = Asset_update.objects.filter(branch_code=brn_id).values('branch_code')
            df = pd.DataFrame(data.values('id', 'branch_code', 'branch_name', 'maker_date',
                                          'checker_date', 'completed_date'))
            df_agg = {'id': 'first', 'branch_name': 'first', 'maker_date': 'first',
                      'checker_date': 'first', 'completed_date': 'first'}
            df = pd.DataFrame(df.groupby(by=['branch_code'], as_index=False).agg(df_agg))
            asset_details = df.to_dict('records')
            obj = self.get_branch_data_only(asset_details, vys_page)
            asset = json.loads(obj.get())
            asset['error'] = ErrorMessage.INVALID_branch_DO
            obj_new.append(asset)
            return obj_new
        else:
            brn_values = Asset_update.objects.filter(condition).values('branch_code')
            brn = []
            for i in brn_values:
                if i not in brn:
                    brn.append(i)
            # print('condition ', condition)
            if brn != None:
                data = Asset_update.objects.filter(condition)
                df = pd.DataFrame(data.values('id', 'branch_code', 'branch_name', 'maker_date',
                                              'checker_date', 'completed_date'))
                df_agg = {'id': 'first', 'branch_name': 'first', 'maker_date': 'first',
                          'checker_date': 'first', 'completed_date': 'first'}
                df = pd.DataFrame(df.groupby(by=['branch_code'], as_index=False).agg(df_agg))
                asset_details = df.to_dict('records')
                obj = self.get_branch_data_only(asset_details, vys_page)
                asset = json.loads(obj.get())
                obj_new.append(asset)
                return obj_new
            else:
                data = Asset_update.objects.filter(branch_code__in=brn)
                df = pd.DataFrame(data.values('id', 'branch_code', 'branch_name', 'maker_date',
                                              'checker_date', 'completed_date'))
                df_agg = {'id': 'first', 'branch_name': 'first', 'maker_date': 'first',
                          'checker_date': 'first', 'completed_date': 'first'}
                df = pd.DataFrame(df.groupby(by=['branch_code'], as_index=False).agg(df_agg))
                asset_details = df.to_dict('records')
                obj = self.get_branch_data_only(asset_details, vys_page)
                asset = json.loads(obj.get())
                obj_new.append(asset)
                return obj_new

    def get_branch_data_only(self, asset_details, vys_page):
        return_list = NWisefinList()
        # print("Count ", len(asset_details))
        if len(asset_details) > 0:
            for data in asset_details:
                asset = DictObj()
                asset = asset.get_obj(data)
                assetupdatesrresponse = AssetUpdateResponse()
                assetupdatesrresponse.set_id(asset.id)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                assetupdatesrresponse.set_maker_date(asset.maker_date)
                assetupdatesrresponse.set_checker_date(asset.checker_date)
                assetupdatesrresponse.set_completed_date(asset.completed_date)
                return_list.append(assetupdatesrresponse)
                # print("return_list ", return_list)
        vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
        return_list.set_pagination(vpage)
        return return_list

    def get_asset_update_records(self, brn_id, user_id, request, vys_page):
        condition = Q()
        return_list = NWisefinList()
        scope = request.scope
        apiserv = ApiCall(scope)
        branch_list = apiserv.get_emp_branch_ctrl(request)
        branchDO = []
        obj_new = []
        case=0
        for i in branch_list['data']:
            branchDO.append(i['control_office_branch'])
        if brn_id in branchDO:
            case = 1  #if DO branch there
        elif brn_id not in branchDO and brn_id != None:
            case = 2  #branch_code not in do branch and its not null
        else:
            case = 3  #branch_code null
        if case == 1:
            if 'init' in request.GET:
                condition &= Q(control_office_branch=brn_id)
        elif case == 2:
            if 'branch' in request.GET:
                condition &= Q(branch_code__in=brn_id)
        elif case == 3:
            err = Error()
            err.set_code(ErrorMessage.INVALID_branch_ID)
            err.set_description(ErrorDescription.INVALID_branch_ID)
            resp = HttpResponse(err.get(), content_type='application/json')
            return resp

        if 'branch' in request.GET:
            condition &= Q(branch_code__in=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))
        # print('condition ', condition)

        if case == 2:
            brn_data = []
            asset_details = Asset_update.objects.filter(branch_code=brn_id)[vys_page.get_offset():vys_page.get_query_limit()]
            obj = self.get_full_asset_update(asset_details, vys_page)
            asset = json.loads(obj.get())
            asset['error'] = ErrorMessage.INVALID_branch_DO
            obj_new.append(asset)
            return obj_new
        else:
            asset_details = Asset_update.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            obj = self.get_full_asset_update(asset_details, vys_page)
            asset = json.loads(obj.get())
            obj_new.append(asset)
            return obj_new


    def get_full_asset_update(self, asset_details, vys_page):
        return_list = NWisefinList()
        # print("Count ", len(asset_details))
        if len(asset_details) > 0:
            for asset in asset_details:
                    assetupdatesrresponse = AssetUpdateResponse()
                    assetupdatesrresponse.set_id(asset.id)
                    # assetupdatesrresponse.set_assetdetails_id(asset.assetdetails_id)
                    assetupdatesrresponse.set_barcode(asset.barcode)
                    assetupdatesrresponse.set_product_name(asset.product_name)
                    assetupdatesrresponse.set_branch_code(asset.branch_code)
                    assetupdatesrresponse.set_branch_name(asset.branch_name)
                    assetupdatesrresponse.set_asset_tag(asset.asset_tag)
                    assetupdatesrresponse.set_make(asset.make)
                    assetupdatesrresponse.set_serial_no(asset.serial_no)
                    assetupdatesrresponse.set_cr_number(asset.cr_number)
                    assetupdatesrresponse.set_kvb_asset_id(asset.kvb_asset_id)
                    assetupdatesrresponse.set_condition(asset.condition)
                    assetupdatesrresponse.set_status(asset.status)
                    assetupdatesrresponse.set_remarks(asset.remarks)
                    assetupdatesrresponse.set_pv_done(asset.pv_done)
                    assetupdatesrresponse.set_maker_date(asset.maker_date)
                    assetupdatesrresponse.set_checker_date(asset.checker_date)
                    assetupdatesrresponse.set_completed_date(asset.completed_date)
                    return_list.append(assetupdatesrresponse)
                    # print("return_list ", return_list)
            vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
            return_list.set_pagination(vpage)
            return return_list

    def get_asset_branch_update_records_Dup(self, request, vys_page):
        scope=request.scope
        return_list = NWisefinList()
        condition = Q()
        if 'branch' in request.GET:
            condition &= Q(branch_code=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))
        # print('condition ', condition)

        brn_values = Asset_update.objects.filter(condition).values('branch_code')
        brn = []
        for i in brn_values:
            if i not in brn:
                brn.append(i)
        # print('condition ', condition)
        if brn != None:
            data = Asset_update.objects.filter(condition)
            df = pd.DataFrame(data.values('id', 'branch_code', 'branch_name', 'maker_date',
                                          'checker_date', 'completed_date'))
            df_agg = {'id': 'first', 'branch_name': 'first', 'maker_date': 'first',
                      'checker_date': 'first', 'completed_date': 'first'}
            df = pd.DataFrame(df.groupby(by=['branch_code'], as_index=False).agg(df_agg))
            asset_details = df.to_dict('records')
        else:
            data = Asset_update.objects.filter(branch_code__in=brn)
            df = pd.DataFrame(data.values('id', 'branch_code', 'branch_name', 'maker_date',
                                          'checker_date', 'completed_date'))
            df_agg = {'id': 'first', 'branch_name': 'first', 'maker_date': 'first',
                      'checker_date': 'first', 'completed_date': 'first'}
            df = pd.DataFrame(df.groupby(by=['branch_code'], as_index=False).agg(df_agg))
            asset_details = df.to_dict('records')
        api_obj = FaApiService(scope)
        if len(asset_details) > 0:
            for data in asset_details:
                asset = DictObj()
                asset = asset.get_obj(data)
                assetupdatesrresponse = AssetUpdateResponse()
                assetupdatesrresponse.set_id(asset.id)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                assetupdatesrresponse.set_maker_date(asset.maker_date)
                assetupdatesrresponse.set_checker_date(asset.checker_date)
                assetupdatesrresponse.set_completed_date(asset.completed_date)
                return_list.append(assetupdatesrresponse)
                # print("return_list ", return_list)
        vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
        return_list.set_pagination(vpage)
        return return_list

    def get_asset_update_records_Dup(self, request, vys_page):
        scope=request.scope
        return_list = NWisefinList()
        condition = Q()
        if 'branch' in request.GET:
            condition &= Q(branch_code=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))

        # print('condition ', condition)
        asset_details = Asset_update.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        # print("Count ", len(asset_details))
        api_obj = FaApiService(scope)
        if len(asset_details) > 0:
            for asset in asset_details:
                assetupdatesrresponse = AssetUpdateResponse()
                assetupdatesrresponse.set_id(asset.id)
                # assetupdatesrresponse.set_assetdetails_id(asset.assetdetails_id)
                assetupdatesrresponse.set_barcode(asset.barcode)
                assetupdatesrresponse.set_product_name(asset.product_name)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                assetupdatesrresponse.set_asset_tag(asset.asset_tag)
                assetupdatesrresponse.set_make(asset.make)
                assetupdatesrresponse.set_serial_no(asset.serial_no)
                assetupdatesrresponse.set_cr_number(asset.cr_number)
                assetupdatesrresponse.set_kvb_asset_id(asset.kvb_asset_id)
                assetupdatesrresponse.set_condition(asset.condition)
                assetupdatesrresponse.set_status(asset.status)
                assetupdatesrresponse.set_remarks(asset.remarks)
                assetupdatesrresponse.set_pv_done(asset.pv_done)
                assetupdatesrresponse.set_maker_date(asset.maker_date)
                assetupdatesrresponse.set_checker_date(asset.checker_date)
                assetupdatesrresponse.set_completed_date(asset.completed_date)
                return_list.append(assetupdatesrresponse)
                # print("return_list ", return_list)
        vpage = NWisefinPaginator(asset_details, vys_page.get_index(), 10)
        return_list.set_pagination(vpage)
        return return_list

    def get_json_excel_branch_records(self, request, brn_id, user_id):
        json_resp = dict()
        condition = Q()
        if 'branch' in request.GET:
            condition &= Q(branch_code=brn_id)
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))

        # asset_update = Asset_update.objects.values('branch_code').annotate(new_value=Count('branch_code')).filter(condition).values('branch_name','branch_code','pv_done','maker_date','checker_date','completed_date')
        # asset_update = Asset_update.objects.filter(branch_code__in=filter)
        # print(asset_update.query)
        data = Asset_update.objects.filter(condition)
        value_id = []
        branch_code = []
        for i in data:
            if i.branch_code not in branch_code:
                value_id.append(i.id)
                branch_code.append(i.branch_code)

        asset_update = Asset_update.objects.filter(id__in=value_id)
        # branch_code = [i['branch_code'] for i in data]
        # asset_update = Asset_update.objects.values('branch_name','branch_code','pv_done','maker_date',
        #                                            'checker_date','completed_date').filter(branch_code__in=branch_code)
        # print(asset_update.query)
        branch_name_list = list(asset_update.values_list('branch_name', flat=True))
        branch_code_list = list(asset_update.values_list('branch_code', flat=True))
        pv_done_list = list(asset_update.values_list('pv_done', flat=True))
        maker_date_list = list(asset_update.values_list('maker_date', flat=True))
        checker_date_list = list(asset_update.values_list('checker_date', flat=True))
        completed_date_list = list(asset_update.values_list('completed_date', flat=True))

        json_resp['Branch_Code'] = branch_code_list
        json_resp['Branch_Name'] = branch_name_list
        json_resp['PV_Done'] = pv_done_list
        json_resp['Maker_Date'] = maker_date_list
        json_resp['Checker_Date'] = checker_date_list
        json_resp['Completed_Date'] = completed_date_list
        return json_resp


    def get_json_excel_branch_records1(self, request):
        json_resp = dict()
        condition = Q()
        if 'branch' in request.GET:
            condition &= Q(branch_code=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))

        # asset_update = Asset_update.objects.values('branch_code').annotate(id=Count('id')).filter(
        #     condition).values('branch_name', 'branch_code', 'pv_done', 'maker_date', 'checker_date', 'completed_date')
        # print(asset_update.query)

        data = Asset_update.objects.filter(condition)
        value_id = []
        branch_code = []
        for i in data:
            if i.branch_code not in branch_code:
                value_id.append(i.id)
                branch_code.append(i.branch_code)

        asset_update = Asset_update.objects.filter(id__in=value_id)

        branch_name_list = list(asset_update.values_list('branch_name', flat=True))
        branch_code_list = list(asset_update.values_list('branch_code', flat=True))
        pv_done_list = list(asset_update.values_list('pv_done', flat=True))
        maker_date_list = list(asset_update.values_list('maker_date', flat=True))
        checker_date_list = list(asset_update.values_list('checker_date', flat=True))
        completed_date_list = list(asset_update.values_list('completed_date', flat=True))

        json_resp['Branch_Code'] = branch_code_list
        json_resp['Branch_Name'] = branch_name_list
        json_resp['PV_Done'] = pv_done_list
        json_resp['Maker_Date'] = maker_date_list
        json_resp['Checker_Date'] = checker_date_list
        json_resp['Completed_Date'] = completed_date_list
        return json_resp

    # def get_json_excel_full_records(self, request, brn_id, user_id):
    #     json_resp = dict()
    #     condition = Q()
    #     if 'branch' in request.GET:
    #         condition &= Q(branch_code=brn_id)
    #     if 'ctrl_branch' in request.GET:
    #         condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))
    #     asset_update = Asset_update.objects.filter(condition)
    #     # product_id_list = list(asset_update.values_list('asset_details__assetdetails_productgid', flat=True))
    #     # branch_id_list = list(asset_update.values_list('asset_details__assetdetails_branchgid', flat=True))
    #     # details_id_list = list(asset_update.values_list('asset_details__assetdetails_gid', flat=True))
    #     # branch = api_obj.fetch_branch_listid ( branch_id_list )
    #     # product=api_obj.fetch_product_listid(product_id_list)
    #     # details = AssetDetails.objects.filter(assetdetails_id__in=details_id_list)
    #
    #     # assetdetails_id_list = list(asset_update.values_list('assetdetails_id', flat=True))
    #     assetdetails_barcode_list = list(asset_update.values_list('barcode', flat=True))
    #     assetdetails_cost_list = list(asset_update.values_list('asset_cost', flat=True))
    #     assetdetails_value_list = list(asset_update.values_list('asset_value', flat=True))
    #     product_name_list = list(asset_update.values_list('product_name', flat=True))
    #     branch_name_list = list(asset_update.values_list('branch_name', flat=True))
    #     branch_code_list = list(asset_update.values_list('branch_code', flat=True))
    #     asset_tag_list = list(asset_update.values_list('asset_tag', flat=True))
    #     make_list = list(asset_update.values_list('make', flat=True))
    #     serial_no_list = list(asset_update.values_list('serial_no', flat=True))
    #     cr_number_list = list(asset_update.values_list('cr_number', flat=True))
    #     kvb_asset_id_list = list(asset_update.values_list('kvb_asset_id', flat=True))
    #     condition_list = list(asset_update.values_list('condition', flat=True))
    #     status_list = list(asset_update.values_list('status', flat=True))
    #     remarks_list = list(asset_update.values_list('remarks', flat=True))
    #
    #     # json_resp['assetdetails_id'] = assetdetails_id_list
    #     json_resp['Barcode'] = assetdetails_barcode_list
    #     json_resp['Asset_Value'] = assetdetails_value_list
    #     json_resp['Asset_Cost'] = assetdetails_cost_list
    #     json_resp['Product_Name'] = product_name_list
    #     json_resp['Branch_Name'] = branch_name_list
    #     json_resp['Branch_Code'] = branch_code_list
    #     json_resp['Asset_Tag'] = asset_tag_list
    #     json_resp['Make'] = make_list
    #     json_resp['Serial_No'] = serial_no_list
    #     json_resp['cr_number'] = cr_number_list
    #     json_resp['kvb_asset_id'] = kvb_asset_id_list
    #     json_resp['Condition'] = condition_list
    #     json_resp['Status'] = status_list
    #     json_resp['Remarks'] = remarks_list
    #     return json_resp


    def get_json_excel_full_records(self, request, brn_id, user_id):
        scope=request.scope
        api_obj = FaApiService(scope)
        assetdetails_resp = AssetDetailsResponse()
        invoice = ClearingDetailsService(scope)
        json_resp = dict()
        condition = Q()
        newdata=[]
        app_asset=NWisefinList()
        if 'branch' in request.GET:
            condition &= Q(branch_code=brn_id)
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))
        asset_update = Asset_update.objects.filter(condition)
        df = pd.DataFrame(
            asset_update.values('id', 'barcode', 'asset_cost', 'asset_value', 'product_name', 'branch_code',
                                'branch_name', 'asset_tag', 'make', 'serial_no', 'cr_number', 'kvb_asset_id',
                                'condition', 'status', 'remarks', 'asset_details_id'))
        # print('df_query', df)
        df_agg = {'id': 'first', 'asset_cost': 'first', 'asset_value': 'first', 'product_name': 'first',
                  'branch_code': 'first','branch_name': 'first','asset_tag': 'first', 'make': 'first', 'serial_no': 'first',
                  'condition': 'first', 'status': 'first', 'kvb_asset_id': 'first', 'cr_number': 'first', 'remarks': 'first',
                  'asset_details_id': 'first'}
        df = pd.DataFrame(df.groupby(by=['barcode'], as_index=False).agg(df_agg))
        df = df.to_dict('records')
        branch_id_search = ServiceCall(scope)
        obj = branch_id_search.fetch_branch_code(brn_id)
        branch_id_get = obj['id']
        # print('first',df)
        asset_details = AssetDetails.objects.filter(branch_id=branch_id_get)
        df1 = pd.DataFrame(asset_details.values('id', 'assetdetails_value', 'assetdetails_cost', 'assetdetails_id',
                                               'barcode', 'product_id', 'branch_id', 'assetheader__barcode',
                                               'description',
                                               'faclringdetails_id')).rename(columns={'assetheader__barcode': 'header'})
        df_agg1 = {'id': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first',
                  'assetdetails_id': 'first',
                  'barcode': 'first', 'product_id': 'first', 'branch_id': 'first', 'faclringdetails_id': 'first',
                  'description': 'first'}
        # print('second', df1)
        df1 = pd.DataFrame(df1.groupby(by=['header'], as_index=False).agg(df_agg1))
        # print('df1_query',df1)
        df1 = df1.to_dict('records')
        for i in df1:
            i['product_name'] = api_obj.fetch_product(i['product_id'], user_id, request).name
            brn_data = api_obj.fetch_branch(i['branch_id'], request)
            i['branch_name'] = brn_data.name
            i['branch_code'] = brn_data.code
            i['cr_number'] = invoice.fetch_invoicedetailsforfaqery(i['faclringdetails_id']).ecfnum
        # print(df1)
        df = pd.DataFrame(df)
        df['asset_value'] = pd.to_numeric(df['asset_value'], errors='coerce')
        df['asset_cost'] = pd.to_numeric(df['asset_cost'], errors='coerce')
        df.fillna('')
        df1 = pd.DataFrame(df1)
        df1['assetdetails_value'] = pd.to_numeric(df1['assetdetails_value'], errors='coerce')
        df1['assetdetails_cost'] = pd.to_numeric(df1['assetdetails_cost'], errors='coerce')
        df1.fillna('')
        frame=[df,df1]
        result = pd.concat(frame, join='outer')
        init_data = pd.DataFrame(result)
        df_agg3 = {'id': 'first', 'asset_cost': 'first', 'asset_value': 'first', 'product_name': 'first',
                   'branch_code': 'first', 'branch_name': 'first', 'asset_tag': 'first', 'make': 'first',
                   'serial_no': 'first', 'condition': 'first', 'status': 'first', 'kvb_asset_id': 'first',
                   'cr_number': 'first', 'remarks': 'first', 'asset_details_id': 'first',
                   'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'assetdetails_id': 'first',
                   'product_id': 'first', 'branch_id': 'first', 'faclringdetails_id': 'first', 'description': 'first'}
        init_data = pd.DataFrame(init_data.groupby(by=['barcode'], as_index=False).agg(df_agg3))
        # init_data.drop_duplicates(subset=['barcode'], keep='first', inplace=False)
        init_data.fillna('', inplace=True)
        # print(init_data)
        init_data = init_data.reset_index(drop=True)
        # init_data = init_data.replace(init_data.nan, '', regex=True)
        final = init_data.to_dict('records')
        # print('df', final)
        final_out=[]
        if len(asset_update) > 0:
            for data in final:
                asset = DictObj()
                asset = asset.get_obj(data)
                Nan = float('nan')
                assetupdatesrresponse = AssetUpdateResponse()
                # assetupdatesrresponse.set_id(asset.id)
                # assetupdatesrresponse.set_assetdetails_id(asset.assetdetails_id)
                assetupdatesrresponse.set_barcode(asset.barcode)
                assetupdatesrresponse.set_product_name(asset.product_name)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                if asset.assetdetails_value != '':
                    assetupdatesrresponse.set_asset_value(asset.assetdetails_value)
                elif asset.asset_value != '':
                    assetupdatesrresponse.set_asset_value(asset.asset_value)
                if asset.assetdetails_cost != '':
                    assetupdatesrresponse.set_asset_cost(asset.assetdetails_cost)
                elif asset.asset_cost != '':
                    assetupdatesrresponse.set_asset_cost(asset.asset_cost)
                assetupdatesrresponse.set_asset_tag(asset.asset_tag)
                assetupdatesrresponse.set_make(asset.make)
                assetupdatesrresponse.set_serial_no(asset.serial_no)
                assetupdatesrresponse.set_cr_number(asset.cr_number)
                assetupdatesrresponse.set_kvb_asset_id(asset.kvb_asset_id)
                assetupdatesrresponse.set_condition(asset.condition)
                assetupdatesrresponse.set_status(asset.status)
                assetupdatesrresponse.set_remarks(asset.remarks)
                app_asset.append(assetupdatesrresponse)
                print(app_asset)
            for i in app_asset.data:
                json_resp = {}
                json_resp['Barcode'] = i.barcode
                json_resp['Asset_Value'] = i.asset_value
                json_resp['Asset_Cost'] = i.asset_cost
                json_resp['Product_Name'] = i.product_name
                json_resp['Branch_Name'] = i.branch_name
                json_resp['Branch_Code'] = i.branch_code
                json_resp['Asset_Details'] = str(i.asset_tag)
                json_resp['Make'] = str(i.make)
                json_resp['Serial_No'] = str(i.serial_no)
                json_resp['CR_number'] = i.cr_number
                json_resp['NAC_asset_id'] = str(i.kvb_asset_id)
                json_resp['Condition'] = str(i.condition)
                json_resp['Status'] = str(i.status)
                json_resp['Remarks'] = str(i.remarks)
                final_out.append(json_resp)
        return final_out

            # return app_asset
                # assetdetails_barcode_list =i.barcode
                # assetdetails_cost_list = i.asset_cost
                # assetdetails_value_list = i.asset_value
                # product_name_list = i.product_name
                # branch_name_list = i.branch_name
                # branch_code_list = i.branch_code
                # asset_tag_list = i.asset_tag
                # make_list = i.make
                # serial_no_list = i.serial_no
                # cr_number_list = i.cr_number
                # kvb_asset_id_list = i.kvb_asset_id
                # condition_list = i.condition
                # status_list = i.status
                # remarks_list = i.remarks


    def get_json_excel_full_records1(self, request, user_id):
        scope=request.scope
        api_obj = FaApiService(scope)
        assetdetails_resp = AssetDetailsResponse()
        invoice = ClearingDetailsService(scope)
        json_resp = dict()
        condition = Q()
        newdata = []
        app_asset = NWisefinList()
        if 'branch' in request.GET:
            condition &= Q(branch_code=request.GET.get('branch'))
        if 'ctrl_branch' in request.GET:
            condition &= Q(control_office_branch=request.GET.get('ctrl_branch'))
        asset_update = Asset_update.objects.filter(condition)
        df = pd.DataFrame(
            asset_update.values('id', 'barcode', 'asset_cost', 'asset_value', 'product_name', 'branch_code',
                                'branch_name', 'asset_tag', 'make', 'serial_no', 'cr_number', 'kvb_asset_id',
                                'condition', 'status', 'remarks', 'asset_details_id'))
        # print('df_query', df)
        df_agg = {'id': 'first', 'asset_cost': 'first', 'asset_value': 'first', 'product_name': 'first',
                  'branch_code': 'first', 'branch_name': 'first', 'asset_tag': 'first', 'make': 'first',
                  'serial_no': 'first',
                  'condition': 'first', 'status': 'first', 'kvb_asset_id': 'first', 'cr_number': 'first',
                  'remarks': 'first',
                  'asset_details_id': 'first'}
        df = pd.DataFrame(df.groupby(by=['barcode'], as_index=False).agg(df_agg))
        df = df.to_dict('records')
        branch_id_search = ServiceCall(scope)
        obj = branch_id_search.fetch_branch_code(request.GET.get('branch'))
        branch_id_get = obj['id']
        # print('first', df)
        asset_details = AssetDetails.objects.filter(branch_id=branch_id_get)
        df1 = pd.DataFrame(asset_details.values('id', 'assetdetails_value', 'assetdetails_cost', 'assetdetails_id',
                                                'barcode', 'product_id', 'branch_id', 'assetheader__barcode',
                                                'description',
                                                'faclringdetails_id')).rename(
            columns={'assetheader__barcode': 'header'})
        df_agg1 = {'id': 'first', 'assetdetails_value': 'first', 'assetdetails_cost': 'first',
                   'assetdetails_id': 'first',
                   'barcode': 'first', 'product_id': 'first', 'branch_id': 'first', 'faclringdetails_id': 'first',
                   'description': 'first'}
        # print('second', df1)
        df1 = pd.DataFrame(df1.groupby(by=['header'], as_index=False).agg(df_agg1))
        # print('df1_query', df1)
        df1 = df1.to_dict('records')
        for i in df1:
            i['product_name'] = api_obj.fetch_product(i['product_id'], user_id, request).name
            brn_data = api_obj.fetch_branch(i['branch_id'], request)
            i['branch_name'] = brn_data.name
            i['branch_code'] = brn_data.code
            i['cr_number'] = invoice.fetch_invoicedetailsforfaqery(i['faclringdetails_id']).ecfnum
        # print(df1)
        df = pd.DataFrame(df)
        df['asset_value'] = pd.to_numeric(df['asset_value'], errors='coerce')
        df['asset_cost'] = pd.to_numeric(df['asset_cost'], errors='coerce')
        df.fillna('')
        df1 = pd.DataFrame(df1)
        df1['assetdetails_value'] = pd.to_numeric(df1['assetdetails_value'], errors='coerce')
        df1['assetdetails_cost'] = pd.to_numeric(df1['assetdetails_cost'], errors='coerce')
        df1.fillna('')
        frame = [df, df1]
        result = pd.concat(frame, join='outer')
        init_data = pd.DataFrame(result)
        df_agg3 = {'id': 'first', 'asset_cost': 'first', 'asset_value': 'first', 'product_name': 'first',
                   'branch_code': 'first', 'branch_name': 'first', 'asset_tag': 'first', 'make': 'first',
                   'serial_no': 'first', 'condition': 'first', 'status': 'first', 'kvb_asset_id': 'first',
                   'cr_number': 'first', 'remarks': 'first', 'asset_details_id': 'first',
                   'assetdetails_value': 'first', 'assetdetails_cost': 'first', 'assetdetails_id': 'first',
                   'product_id': 'first', 'branch_id': 'first', 'faclringdetails_id': 'first', 'description': 'first'}
        init_data = pd.DataFrame(init_data.groupby(by=['barcode'], as_index=False).agg(df_agg3))
        # init_data.drop_duplicates(subset=['barcode'], keep='first', inplace=False)
        init_data.fillna('', inplace=True)
        # print(init_data)
        init_data = init_data.reset_index(drop=True)
        # init_data = init_data.replace(init_data.nan, '', regex=True)
        # init_data = init_data.apply(lambda x: x.astype(str).str.lower()).drop_duplicates(subset=['barcode'], keep='first')
        final = init_data.to_dict('records')
        # print('df', final)
        final_out = []
        if len(asset_update) > 0:
            for data in final:
                asset = DictObj()
                asset = asset.get_obj(data)
                Nan = float('nan')
                assetupdatesrresponse = AssetUpdateResponse()
                # assetupdatesrresponse.set_id(asset.id)
                # assetupdatesrresponse.set_assetdetails_id(asset.assetdetails_id)
                assetupdatesrresponse.set_barcode(asset.barcode)
                assetupdatesrresponse.set_product_name(asset.product_name)
                assetupdatesrresponse.set_branch_code(asset.branch_code)
                assetupdatesrresponse.set_branch_name(asset.branch_name)
                if asset.assetdetails_value != '':
                    assetupdatesrresponse.set_asset_value(asset.assetdetails_value)
                elif asset.asset_value != '':
                    assetupdatesrresponse.set_asset_value(asset.asset_value)
                if asset.assetdetails_cost != '':
                    assetupdatesrresponse.set_asset_cost(asset.assetdetails_cost)
                elif asset.asset_cost != '':
                    assetupdatesrresponse.set_asset_cost(asset.asset_cost)
                assetupdatesrresponse.set_asset_tag(asset.asset_tag)
                assetupdatesrresponse.set_make(asset.make)
                assetupdatesrresponse.set_serial_no(asset.serial_no)
                assetupdatesrresponse.set_cr_number(asset.cr_number)
                assetupdatesrresponse.set_kvb_asset_id(asset.kvb_asset_id)
                assetupdatesrresponse.set_condition(asset.condition)
                assetupdatesrresponse.set_status(asset.status)
                assetupdatesrresponse.set_remarks(asset.remarks)
                app_asset.append(assetupdatesrresponse)
                print(app_asset)
            for i in app_asset.data:
                json_resp = {}
                json_resp['Barcode'] = i.barcode
                json_resp['Asset_Value'] = i.asset_value
                json_resp['Asset_Cost'] = i.asset_cost
                json_resp['Product_Name'] = i.product_name
                json_resp['Branch_Name'] = i.branch_name
                json_resp['Branch_Code'] = i.branch_code
                json_resp['Asset_Details'] = str(i.asset_tag)
                json_resp['Make'] = str(i.make)
                json_resp['Serial_No'] = str(i.serial_no)
                json_resp['cr_number'] = i.cr_number
                json_resp['NAC_asset_id'] = str(i.kvb_asset_id)
                json_resp['Condition'] = str(i.condition)
                json_resp['Status'] = str(i.status)
                json_resp['Remarks'] = str(i.remarks)
                final_out.append(json_resp)
        return final_out

    def new_record(self, resp_obj, doc_id, emp_id):
        asset_update = Asset_update.objects.create(asset_details_id=resp_obj.get_id(),
                                                   barcode=resp_obj.get_barcode(),
                                                   product_name=resp_obj.get_product_name(),
                                                   branch_code=resp_obj.get_branch_code(),
                                                   branch_name=resp_obj.get_branch_name(),
                                                   asset_cost=resp_obj.get_asset_cost(),
                                                   asset_value=resp_obj.get_asset_value(),
                                                   asset_tag=resp_obj.get_asset_tag(),
                                                   make=resp_obj.get_make(),
                                                   serial_no=resp_obj.get_serial_no(),
                                                   cr_number=resp_obj.get_cr_number(),
                                                   kvb_asset_id=resp_obj.get_kvb_asset_id(),
                                                   condition=resp_obj.get_condition(),
                                                   status=resp_obj.get_status(),
                                                   remarks=resp_obj.get_remarks(),
                                                   update_record=0,
                                                   pv_done=resp_obj.get_pv_done(),
                                                   checker_date=resp_obj.get_checker_date(),
                                                   completed_date=resp_obj.get_completed_date(),
                                                   document_id=doc_id,
                                                   control_office_branch=resp_obj.get_control_office_branch())

        print(asset_update)
        assetupdatesrresponse = AssetUpdateResponse()
        assetupdatesrresponse.set_id(asset_update.id)
        # assetupdatesrresponse.set_assetdetails_id(asset_update.asset_details.assetdetails_id)
        assetupdatesrresponse.set_barcode(asset_update.barcode)
        assetupdatesrresponse.set_product_name(asset_update.product_name)
        assetupdatesrresponse.set_branch_code(asset_update.branch_code)
        assetupdatesrresponse.set_branch_name(asset_update.branch_name)
        assetupdatesrresponse.set_assetdetails_cost(asset_update.asset_cost)
        assetupdatesrresponse.set_assetdetails_value(asset_update.asset_value)
        assetupdatesrresponse.set_asset_details_id(asset_update.asset_details_id)
        assetupdatesrresponse.set_asset_tag(asset_update.asset_tag)
        assetupdatesrresponse.set_make(asset_update.make)
        assetupdatesrresponse.set_serial_no(asset_update.serial_no)
        assetupdatesrresponse.set_cr_number(asset_update.cr_number)
        assetupdatesrresponse.set_kvb_asset_id(asset_update.kvb_asset_id)
        assetupdatesrresponse.set_control_office_branch(asset_update.control_office_branch)
        assetupdatesrresponse.set_condition(asset_update.condition)
        assetupdatesrresponse.set_status(asset_update.status)
        assetupdatesrresponse.set_remarks(asset_update.remarks)
        assetupdatesrresponse.set_pv_done(asset_update.pv_done)
        print(assetupdatesrresponse)
        return assetupdatesrresponse


    def update_pv_new(self, resp_obj, doc_id, emp_id):
        asset_update = Asset_update.objects.filter(id=resp_obj.get_id()).update(
                                                   barcode=resp_obj.get_barcode(),
                                                   product_name=resp_obj.get_product_name(),
                                                   branch_code=resp_obj.get_branch_code(),
                                                   branch_name=resp_obj.get_branch_name(),
                                                   asset_cost=resp_obj.get_asset_cost(),
                                                   asset_value=resp_obj.get_asset_value(),
                                                   asset_tag=resp_obj.get_asset_tag(),
                                                   make=resp_obj.get_make(),
                                                   serial_no=resp_obj.get_serial_no(),
                                                   cr_number=resp_obj.get_cr_number(),
                                                   kvb_asset_id=resp_obj.get_kvb_asset_id(),
                                                   condition=resp_obj.get_condition(),
                                                   status=resp_obj.get_status(),
                                                   remarks=resp_obj.get_remarks(),
                                                   update_record=0,
                                                   pv_done=resp_obj.get_pv_done(),
                                                   checker_date=resp_obj.get_checker_date(),
                                                   completed_date=resp_obj.get_completed_date(),
                                                   document_id=doc_id,
                                                   control_office_branch=resp_obj.get_control_office_branch())

        logger.info('PV-L-Update_New ' + str(asset_update))
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    def update_pv_new1(self, resp_obj, doc_id, emp_id):
        asset_update = Asset_update.objects.filter(id=resp_obj.get_id()).update(
                                               asset_tag=resp_obj.get_asset_tag(),
                                               make=resp_obj.get_make(),
                                               serial_no=resp_obj.get_serial_no(),
                                               cr_number=resp_obj.get_cr_number(),
                                               kvb_asset_id=resp_obj.get_kvb_asset_id(),
                                               condition=resp_obj.get_condition(),
                                               status=resp_obj.get_status(),
                                               remarks=resp_obj.get_remarks(),
                                               update_record=0,
                                               pv_done=resp_obj.get_pv_done(),
                                               checker_date=resp_obj.get_checker_date(),
                                               completed_date=resp_obj.get_completed_date(),
                                               document_id=doc_id,
                                               product_name=resp_obj.get_product_name(),
                                               branch_code=resp_obj.get_branch_code(),
                                               branch_name=resp_obj.get_branch_name(),
                                               asset_value=resp_obj.get_asset_value(),
                                               asset_cost=resp_obj.get_asset_cost(),
                                               barcode=resp_obj.get_barcode(),
                                               control_office_branch=resp_obj.get_control_office_branch())

        logger.info('PV-L-Insert_New ' + str(asset_update))
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    # def duplicate_record(self, update_id):
    #     assetupdate = Asset_update.objects.get(asset_details_id=update_id)
    #     asset_update = Asset_update.objects.create(
    #         asset_details_id=assetupdate.asset_details_id,
    #         asset_tag=assetupdate.asset_tag,
    #         make=assetupdate.make,
    #         serial_no=assetupdate.serial_no,
    #         condition=assetupdate.condition,
    #         status=assetupdate.status,
    #         remarks=assetupdate.remarks,
    #         update_record=0,
    #         pv_done=assetupdate.pv_done,
    #         checker_date=assetupdate.checker_date,
    #         completed_date=assetupdate.completed_date)
    #     assetupdatesrresponse = AssetUpdateResponse()
    #     assetupdatesrresponse.set_id(asset_update.id)
    #     assetupdatesrresponse.set_assetdetails_id(asset_update.asset_details.assetdetails_id)
    #     assetupdatesrresponse.set_asset_tag(asset_update.asset_tag)
    #     assetupdatesrresponse.set_make(asset_update.make)
    #     assetupdatesrresponse.set_serial_no(asset_update.serial_no)
    #     assetupdatesrresponse.set_condition(asset_update.condition)
    #     assetupdatesrresponse.set_status(asset_update.status)
    #     assetupdatesrresponse.set_remarks(asset_update.remarks)
    #     assetupdatesrresponse.set_update_record(asset_update.update_record)
    #     print(assetupdatesrresponse)
    #     return assetupdatesrresponse
