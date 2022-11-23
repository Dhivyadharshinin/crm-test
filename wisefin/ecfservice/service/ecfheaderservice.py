import json
import smtplib
import ssl
import traceback
#test
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from environs import Env
from num2words import num2words
# from numpy import msg

from ecfservice.data.response.creditresponse import Creditresponse
from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.data.response.ecffilesresponse import ecffileResponse
from ecfservice.data.response.invoicedetailresponse import Invoicedetailresponse, Debitresponse, ccbsdtlresponse
from ecfservice.data.response.invoiceporesponse import Invoiceporesponse
from ecfservice.models.ecfmodels import ECFHeader, ECFQueue, InvoiceHeader, InvoicePO, Credit, Debit, ccbsdtl, \
    Invoicedetail, ECFFiles, ECFMailScheduler
from ecfservice.service.ecfauditservice import ECFAuditService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType, Type, PPX, Pay, ECFStatus, SupplierType, get_Pay, \
    get_Ppx, get_tds, TDS, ddl_status
from ecfservice.data.response.ecfheaderresponse import ECFHeaderresponse
from ecfservice.data.response.invoiceheaderresponse import Invoiceheaderresponse
from django.db.models import Q, Max
from django.template import loader
from datetime import datetime, timedelta, date
# from userservice.service.employeeservice import EmployeeService
from ecfservice.util.ecfutil_lite import get_authtoken_ecf
from nwisefin.settings import SERVER_IP, logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from django.utils.timezone import now
from ecfservice.controller.tokencontroller import send_mail,send_mailraiser
from django.db import IntegrityError
# from masterservice.controller.commoditycontroller import commodity_service
# from vendorservice.service.branchservice import branchservice
# from masterservice.service.stateservice import StateService
# from userservice.service.branchservice import EmployeeBranchService
# state_service =StateService()
# supplier_service = branchservice()
# employee_service = EmployeeService()
# empbranch_service=EmployeeBranchService()
from utilityservice.permissions.filter.commonpermission import ModulePermission
from utilityservice.permissions.util.dbutil import ModuleList, RoleList
from utilityservice.service import api_service
from utilityservice.service.utilityservice import NWisefinUtilityService

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

utilityservice=NWisefinUtilityService()
class EcfService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def ecfcreate(self,request,ecf_obj,emp_id):
        if ecf_obj.get_ecftype() == Type.NON_PO:
            branch = ecf_obj.get_branch()
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2',emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            emp1 = api_serv.get_empbranch_id(request, emp_branch)
            emp_add1 = emp1['gstin']
            emp_bran = emp1['name']
            emp2 = api_serv.get_empbranch_id(request, branch)
            emp_add2 = emp2['gstin']
            print(emp_add2)
            if (ecf_obj.get_commodity_id() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " CommodityField")
                return error_obj
            elif (ecf_obj.get_ecfdate() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " EcfDateField")
                return error_obj
            else:
                if not ecf_obj.get_id() is None:
                    print("1")
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                supplier_type=ecf_obj.get_supplier_type(),
                                                                                # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                                                commodity_id=ecf_obj.get_commodity_id(),
                                                                                ecftype=ecf_obj.get_ecftype(),
                                                                                ecfdate=ecf_obj.get_ecfdate(),
                                                                                ecfamount=ecf_obj.get_ecfamount(),
                                                                                ecfstatus=ECFStatus.DRAFT,
                                                                                ppx=ecf_obj.get_ppx(),
                                                                                notename=ecf_obj.get_notename(),
                                                                                remark=ecf_obj.get_remark(),
                                                                                payto="S",
                                                                                raisedby=emp_id,
                                                                                raiserbranch=emp_branch,
                                                                                raisername=raisor_name,
                                                                                branch=ecf_obj.get_branch(),
                                                                                rmcode = ecf_obj.get_rmcode(),
                                                                                client_code = ecf_obj.get_client_code(),
                                                                                ap_status = ecf_obj.get_ap_status(),
                                                                                updated_by=emp_id,
                                                                                updated_date=now())
                    print("2")
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                            to_user_id=emp_id,
                                            created_date=now(),
                                            comments="New",
                                            remarks=ecf_obj.get_remark(),
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )

                else:
                        print("3")
                        Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                                                            supplier_type=ecf_obj.get_supplier_type(),
                                                            # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                            commodity_id=ecf_obj.get_commodity_id(),
                                                            ecftype=ecf_obj.get_ecftype(),
                                                            ecfdate=ecf_obj.get_ecfdate(),
                                                            ecfamount=ecf_obj.get_ecfamount(),
                                                            ecfstatus=ECFStatus.DRAFT,
                                                            ppx=ecf_obj.get_ppx(),
                                                            notename=ecf_obj.get_notename(),
                                                            remark=ecf_obj.get_remark(),
                                                            payto="S",
                                                            raisedby=emp_id,
                                                            raiserbranch=emp_branch,
                                                            raisername=raisor_name,
                                                            branch = ecf_obj.get_branch(),
                                                            rmcode=ecf_obj.get_rmcode(),
                                                            client_code=ecf_obj.get_client_code(),
                                                            ap_status=ecf_obj.get_ap_status(),
                                                            created_by=emp_id,
                                                            entity_id=self._entity_id())

                        self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                        ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id, to_user_id=emp_id,
                                               created_date=now(),
                                               comments="New" ,
                                               remarks=ecf_obj.get_remark(),
                                               is_sys=True,
                                               entity_id=self._entity_id()
                                               )
                print("4")
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_supplier_type(Ecfhdr.supplier_type)
                # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
                ecf_data.set_commodity(Ecfhdr.commodity_id)
                ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
                ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_raiserbranchgst(emp_add2)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_branchgst(emp_add1)
                # if ecf_obj.get_supplier_id() != '':
                #     ecf_data.set_gsttype(gsttype)
                #     ecf_data.set_supgstno(supgst)
                ecf_data.set_branchname(emp_bran)
                ecf_data.set_branch(Ecfhdr.branch)
                ecf_data.set_rmcode(Ecfhdr.rmcode)
                ecf_data.set_client_code(Ecfhdr.client_code)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                return ecf_data
        elif ecf_obj.get_ecftype() == Type.ERA:
            branch = ecf_obj.get_branch()
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2', emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            emp1 = api_serv.get_empbranch_id(request, emp_branch)
            emp_add1 = emp1['gstin']
            emp_bran = emp1['name']
            emp2 = api_serv.get_empbranch_id(request, branch)
            emp_add2 = emp2['gstin']
            if not ecf_obj.get_id() is None:
                print("1")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                    supplier_type=ecf_obj.get_supplier_type(),
                    # supplierstate_id=ecf_obj.get_supplierstate_id(),
                    commodity_id=ecf_obj.get_commodity_id(),
                    ecftype=ecf_obj.get_ecftype(),
                    ecfdate=ecf_obj.get_ecfdate(),
                    ecfamount=ecf_obj.get_ecfamount(),
                    ecfstatus=ECFStatus.DRAFT,
                    ppx=ecf_obj.get_ppx(),
                    notename=ecf_obj.get_notename(),
                    remark=ecf_obj.get_remark(),
                    payto=ecf_obj.get_payto(),
                    raisedby=emp_id,
                    raiserbranch=emp_branch,
                    raisername=raisor_name,
                    branch=ecf_obj.get_branch(),
                    rmcode=ecf_obj.get_rmcode(),
                    client_code=ecf_obj.get_client_code(),
                    ap_status=ecf_obj.get_ap_status(),
                    updated_by=emp_id,
                    updated_date=now())
                print("2")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="New",
                                                               remarks=ecf_obj.get_remark(),
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )

            else:
                print("3")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                    supplier_type=ecf_obj.get_supplier_type(),
                    # supplierstate_id=ecf_obj.get_supplierstate_id(),
                    commodity_id=ecf_obj.get_commodity_id(),
                    ecftype=ecf_obj.get_ecftype(),
                    ecfdate=ecf_obj.get_ecfdate(),
                    ecfamount=ecf_obj.get_ecfamount(),
                    ecfstatus=ECFStatus.DRAFT,
                    ppx=ecf_obj.get_ppx(),
                    notename=ecf_obj.get_notename(),
                    remark=ecf_obj.get_remark(),
                    payto=ecf_obj.get_payto(),
                    raisedby=emp_id,
                    raiserbranch=emp_branch,
                    branch=ecf_obj.get_branch(),
                    raisername=raisor_name,
                    rmcode=ecf_obj.get_rmcode(),
                    client_code=ecf_obj.get_client_code(),
                    ap_status=ecf_obj.get_ap_status(),
                    created_by=emp_id,
                    entity_id=self._entity_id())

                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id, to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="New",
                                                               remarks=ecf_obj.get_remark(),
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )
            print("4")
            ecf_data = ECFHeaderresponse()
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_supplier_type(Ecfhdr.supplier_type)
            # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
            ecf_data.set_commodity(Ecfhdr.commodity_id)
            ecf_data.set_ecftype(Ecfhdr.ecftype)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
            ecf_data.set_ppx(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            ecf_data.set_payto(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            ecf_data.set_raiserbranchgst(emp_add2)
            # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_branchgst(emp_add1)
            # if ecf_obj.get_supplier_id() != '':
            #     ecf_data.set_gsttype(gsttype)
            #     ecf_data.set_supgstno(supgst)
            ecf_data.set_branchname(emp_bran)
            ecf_data.set_rmcode(Ecfhdr.rmcode)
            ecf_data.set_client_code(Ecfhdr.client_code)
            ecf_data.set_ap_status(Ecfhdr.ap_status)
            return ecf_data
        elif ecf_obj.get_ecftype() == Type.ADVANCE:
            branch = ecf_obj.get_branch()
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2', emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            emp1 = api_serv.get_empbranch_id(request, emp_branch)
            emp_add1 = emp1['gstin']
            emp_bran = emp1['name']
            emp2 = api_serv.get_empbranch_id(request, branch)
            emp_add2 = emp2['gstin']
            if not ecf_obj.get_id() is None:
                print("1")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                    supplier_type=ecf_obj.get_supplier_type(),
                    # supplierstate_id=ecf_obj.get_supplierstate_id(),
                    commodity_id=ecf_obj.get_commodity_id(),
                    ecftype=ecf_obj.get_ecftype(),
                    ecfdate=ecf_obj.get_ecfdate(),
                    ecfamount=ecf_obj.get_ecfamount(),
                    ecfstatus=ECFStatus.DRAFT,
                    ppx=ecf_obj.get_ppx(),
                    notename=ecf_obj.get_notename(),
                    remark=ecf_obj.get_remark(),
                    payto=ecf_obj.get_payto(),
                    raisedby=emp_id,
                    raiserbranch=emp_branch,
                    raisername=raisor_name,
                    branch=ecf_obj.get_branch(),
                    rmcode=ecf_obj.get_rmcode(),
                    client_code=ecf_obj.get_client_code(),
                    ap_status=ecf_obj.get_ap_status(),
                    updated_by=emp_id,
                    updated_date=now())
                print("2")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="New",
                                                               remarks=ecf_obj.get_remark(),
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )

            else:
                print("3")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                    supplier_type=ecf_obj.get_supplier_type(),
                    # supplierstate_id=ecf_obj.get_supplierstate_id(),
                    commodity_id=ecf_obj.get_commodity_id(),
                    ecftype=ecf_obj.get_ecftype(),
                    ecfdate=ecf_obj.get_ecfdate(),
                    ecfamount=ecf_obj.get_ecfamount(),
                    ecfstatus=ECFStatus.DRAFT,
                    ppx=ecf_obj.get_ppx(),
                    notename=ecf_obj.get_notename(),
                    remark=ecf_obj.get_remark(),
                    payto=ecf_obj.get_payto(),
                    raisedby=emp_id,
                    branch=ecf_obj.get_branch(),
                    raiserbranch=emp_branch,
                    raisername=raisor_name,
                    rmcode=ecf_obj.get_rmcode(),
                    client_code=ecf_obj.get_client_code(),
                    ap_status=ecf_obj.get_ap_status(),
                    created_by=emp_id,
                    entity_id=self._entity_id())

                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id, to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="New",
                                                               remarks=ecf_obj.get_remark(),
                                                               is_sys=True,
                                                               entity_id=self._entity_id()
                                                               )
            print("4")
            ecf_data = ECFHeaderresponse()
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_supplier_type(Ecfhdr.supplier_type)
            # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
            ecf_data.set_commodity(Ecfhdr.commodity_id)
            ecf_data.set_ecftype(Ecfhdr.ecftype)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
            ecf_data.set_ppx(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            ecf_data.set_payto(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            ecf_data.set_raiserbranchgst(emp_add2)
            # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_branchgst(emp_add1)
            # if ecf_obj.get_supplier_id() != '':
            #     ecf_data.set_gsttype(gsttype)
            #     ecf_data.set_supgstno(supgst)
            ecf_data.set_branchname(emp_bran)
            ecf_data.set_branch(Ecfhdr.branch)
            ecf_data.set_rmcode(Ecfhdr.rmcode)
            ecf_data.set_client_code(Ecfhdr.client_code)
            ecf_data.set_ap_status(Ecfhdr.ap_status)
            return ecf_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
    # from utilityservice.service.api_service import fetch_empbranch
    def fetch_ecf_list(self,request,vys_page,emp_id):
        emp_api=NWisefinUtilityService()
        condition = Q(status=1) & Q(created_by=emp_id)
        ecf_list =ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        # print("ecf",ecf_list.branch)
        ecf_listt =ECFHeader.objects.using(self._current_app_schema()).filter(condition)
        count = len(ecf_listt)
        print('lend',count)
        list_length = len(ecf_list)
        ecf_list_data = NWisefinList()
        com_arr = []
        # brn_arr = []
        # state_arr = []
        for i in ecf_list:
            com_arr.append(i.commodity_id)
            # brn_arr.append(i.branch)
            # api_serv = api_service.ApiService()
            # print("i.branch",i.branch)
            # if i.branch is not None:
            #     branch_co = api_serv.get_empbranch_id(request, i.branch)
            #     brnch_arr.append(branch_co)
            # supp_arr.append(i.branch)
            # state_arr.append(i.supplierstate_id)
        # bch_data = api_serv.get_empbranch_id(request, brnch_arr)
        # print("bch", bch_data)
        api_serv = api_service.ApiService(self._scope())
        commo_data = api_serv.get_commodity_list(request , com_arr)
        # branch_co = api_serv.get_empbranch_id(request, brn_arr)
        # bnch = branch_co['name']
        # print("name",bnch)
        # supplier_data = api_serv.get_supplier_list(self, request , supp_arr)
        # state_data = MasterAPI.get_state(self, request , supp_arr)
        # print('comm_data',commo_data.replace('"', "'"))
        # print('comm_data',commo_data["data"])
        # print("strrr", json.loads(commo_data))
        # s = json.loads(commo_data)
        # s1 = s['data']
        # print('comm_data', s1)
        if list_length <= 0:
            pass
        else:
            for Ecfhdr in ecf_list:
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity_id(Ecfhdr.commodity_id,commo_data['data'])
                # ecf_data.set_supplier_id(Ecfhdr.supplier_id,supplier_data['data'])
                # ecf_data.set_supplierstate_id(Ecfhdr.supplierstate_id,state_data['data'])
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                if Ecfhdr.ecftype == Type.TCF:
                    ecf_data.set_ecftype(Type.TCF_Type)
                # ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION:
                    ecf_data.set_ecfstatus(ECFStatus.Pending_For_Approval_Modification)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                ecf_data.set_ppx_id(Ecfhdr.ppx)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                emp_api = NWisefinUtilityService()
                branch=emp_api.get_employee_branch([Ecfhdr.branch])
                if len(branch)>0:
                    ecf_data.set_branch(branch)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto_id(Ecfhdr.payto)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_rmcode(api_serv.get_empsingle_id(request,Ecfhdr.rmcode))
                ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
                aph = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=Ecfhdr.id,entity_id=self._entity_id(), status=1)
                invheader_list = []
                for inhdr in aph:
                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                    inhdr_data.set_invoiceno(inhdr.invoiceno)
                    ecf_data.set_invoiceheader(inhdr_data)
                ecf_list_data.append(ecf_data)
            ecf_list_data.count=count
            vpage = NWisefinPaginator(ecf_list, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data

    def ECF_Submit(self,request, ecf_obj, emp_id):
        try:
            import datetime
            ecfstatus = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
            code = ''
            code1 = ''
            code2 = ''
            if ecf_obj.get_ecftype() == 1:
                code = "ECF"
            elif ecf_obj.get_ecftype() == 2:
                code = "NPO"
            elif ecf_obj.get_ecftype() == 3:
                code = "ERA"
            elif ecf_obj.get_ecftype() == 4:
                if ecfstatus.ppx == "S":
                    code = "ADV"
                elif ecfstatus.ppx == "E":
                    code = "ADE"
            elif ecf_obj.get_ecftype() == 5:
                code = "DTP"
            if ecf_obj.get_ecftype() == 4:
                code2 = code
            else:
                code2 = code
            date1 = ECFHeader.objects.using(self._current_app_schema()).all().count()
            if date1 == None or 0:
                import datetime
                today_date = datetime.datetime.now().date()
                rnsl = 0
                crno = code + str(today_date.year)[-2:] + str(today_date.month).zfill(2) + str(today_date.day).zfill(2) + str(rnsl).zfill(3)
            else:
                cr=''
                if code2 == '':
                    date = ECFHeader.objects.using(self._current_app_schema()).filter(ecftype=ecf_obj.get_ecftype()). \
                        order_by('-id')
                else:
                    date = ECFHeader.objects.using(self._current_app_schema()).filter(ecftype=ecf_obj.get_ecftype(),crno__icontains=code2).\
                    order_by ('-crno')
                case = 0
                if len(date) == 0:
                    rnsl = 1
                    prefix = code2
                    today_date = datetime.datetime.now().date()
                    print(today_date)
                    if code == '':
                        # prefix=code
                        pass
                    elif code != '':
                        prefix = code
                    crno = prefix + str(today_date.year)[-2:] + str(today_date.month).zfill(2) + str(
                        today_date.day).zfill(2) + str(
                        rnsl).zfill(4)
                    print(crno)
                else:
                    if date[0].crno==None:
                        case = 1
                    elif date[0].crno!=None:
                        case = 2
                    else:
                        case = 3
                    print(date.query)
                    obj = []
                    if case == 1:
                        for i in date:
                            year1 = i.crno[:2]
                            month1 = i.crno[2:4]
                            day1 = i.crno[4:]
                            last_code_date1 = datetime.datetime(int('20' + year1), int(month1), int(day1)).date()
                            if i.ecfdate == last_code_date1:
                                if i.crno!=None:
                                    obj.append(i.crno)
                        cr = max(obj)
                    elif case == 2:
                        cr = date[0].crno
                        last_code = cr
                        rnsl = int(last_code[-4:])
                        prefix = last_code[:3]
                        print(prefix)
                        last_code_date = last_code[-10:-4]
                        year = last_code_date[:2]
                        month = last_code_date[2:4]
                        day = last_code_date[4:]
                        last_code_date = datetime.datetime(int('20' + year), int(month), int(day)).date()
                        print(last_code_date)
                        today_date = datetime.datetime.now().date()
                        print(today_date)
                        if last_code_date != today_date:
                            rnsl = 1
                        else:
                            rnsl = rnsl + 1
                        if code == '':
                            # prefix=code
                            pass
                        elif code != '':
                            prefix = code
                        crno = prefix + str(today_date.year)[-2:] + str(today_date.month).zfill(2) + str(
                            today_date.day).zfill(2) + str(
                            rnsl).zfill(4)
                        print(crno)
                    elif case == 3:
                        date = ECFHeader.objects.using(self._current_app_schema()).filter(ecftype=ecf_obj.get_ecftype(),
                                                                                          crno__icontains=code2). \
                            order_by('-crno')
                    else:
                        traceback.print_exc()
            if ecf_obj.get_ecftype() == Type.ADVANCE:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp = api_serv.get_empsingle_id(request,ecf_obj.get_approvedby())
                appr_name = emp['name']
                ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                print("ecffff", ecf)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                user = api_serv.get_empsingle_id(request, ecf.raisedby)
                email_idd = user['email']
                print("raiser", email_idd)
                appname = user['name']
                createdate = ecf.created_date.date()
                creatby = ecf.created_by
                amt = ecf.ecfamount
                inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_obj.get_id(),
                                                                               entity_id=self._entity_id(),status=1).all()
                invheadertotal = float(0)
                sum = 0
                for inv_obj in inv_list:
                    count = sum + 1
                    sum+=1
                    invheadertotal = invheadertotal + inv_obj.totalamount
                    inv_crno = code + str(now().strftime("%y%m%d")) \
                               + str(ecf_obj.get_id()).zfill(4) + '_'+ str(int(count))
                    print()
                    inv_lis = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                        ecfheader_id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1).update(
                        inv_crno=inv_crno)
                if (amt != invheadertotal):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVOICE_AMOUNT_MISMATCH)
                    error_obj.set_description(ErrorDescription.INVOCIEHDR_AMOUNT_MISMATCH)
                    return error_obj
                for inv_obj in inv_list:
                    invtotal = inv_obj.totalamount
                    invid = inv_obj.id

                    deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,
                                                                           entity_id=self._entity_id(),status=1).all()
                    debittotal = float(0)
                    for deb_obj in deb_list:
                        debittotal = round(debittotal + deb_obj.amount,2)
                    print("debittotal",debittotal)
                    if (invtotal != debittotal):
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.DEBIT_AMOUNT_MISMATCH)
                        error_obj.set_description(ErrorDescription.DEBIT_AMOUNT_MISMATCH)
                        return error_obj
                    credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,entity_id=self._entity_id(), status=1).all()
                    credittotal = float(0)
                    for crd_obj in credit_list:
                        credittotal = credittotal + crd_obj.amount
                    if (invtotal != credittotal):
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.CREDIT_AMOUNT_MISMATCH)
                        error_obj.set_description(ErrorDescription.CREDIT_AMOUNT_MISMATCH)
                        return error_obj
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                    approvedby=ecf_obj.get_approvedby(),
                    approvername=appr_name,
                    approver_branch = ecf_obj.get_approver_branch(),
                    tds = ecf_obj.get_tds(),
                    crno=crno,
                    ecftype=ecf_obj.get_ecftype(),
                    ecfstatus=ECFStatus.PENDING_FOR_APPROVAL,
                    updated_by=emp_id,
                    updated_date=now())

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                        to_user_id=ecf_obj.get_approvedby(),
                                        created_date=now(),
                                        comments="PENDING FOR APPROVAL",
                                        remarks=ecf_obj.get_remark(),
                                        is_sys=True
                                        )

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                if SuccessStatus.SUCCESS == "success":
                    from utilityservice.service import api_service
                    env = Env()
                    env.read_env()
                    BASE_URL = env.str('WISEFIN_URL')
                    From_url = env.str('SMTP_USER_NAME')
                    PW_url = env.str('SMTP_KEY')
                    api_serv = api_service.ApiService(self._scope())
                    user = api_serv.get_empsingle_id(request, ecf.raisedby)
                    emp_name = user['name']
                    email_idd = user['email']
                    user1 = api_serv.get_empsingle_id(request, ecf_obj.get_approvedby())
                    approvername = user1['name']
                    email_idd1 = user1['email']
                    print("email_id", email_idd)
                    template = loader.get_template("nacraiser.html")
                    name = emp_name
                    subject = "Vendor payment request raised by Raiser"
                    m_id = emp_id
                    cc = [email_idd]
                    to = [email_idd1]

                    from1 = From_url
                    email = to
                    msg = MIMEMultipart('alternative')
                    Subject1 = subject
                    Cc1 = email_idd
                    referenceno = ecf.crno
                    raiseddate = createdate
                    amount = ecf.ecfamount
                    ecftype = ecf.ecftype
                    data = {"emp_name": name,
                            "id": m_id,
                            "server_ip":BASE_URL,
                            "subject": subject,
                            "cc": cc,
                            "to": to,
                            "raisername": appname,
                            "approvername": approvername,
                            "referenceno": referenceno,
                            "raiseddate": raiseddate,
                            "amount": amount,
                            "ecftype": ecftype
                            }
                    body_html = template.render(data)
                    part1 = MIMEText(body_html, "html")
                    # msd2 = ','.join(to)
                    # msg1 = ','.join(cc)
                    # toAddress =  msd2
                    msg.attach(part1)
                    msg['Subject'] = "Vendor payment request raised by Raiser"
                    TEXT = msg.as_string()
                    server = smtplib.SMTP("smtp-mail.outlook.com", 587)
                    server.starttls()
                    server.ehlo()
                    server.login(From_url, PW_url)
                    server.sendmail(from1, to, TEXT)
                    print("Successfully sent email")
                    server.quit()
                    logger.info("ECF mail data:" + str(msg))
                    return success_obj
            else:

                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp = api_serv.get_empsingle_id(request, ecf_obj.get_approvedby())
                appr_name = emp['name']
                ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                print("ecffff",ecf)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                user = api_serv.get_empsingle_id(request, ecf.raisedby)
                # user1 = api_serv.get_empsingle_id(request, ecf.approvedby)
                email_idd = user['email']
                print("raiser",email_idd)
                appname= user['name']
                # approvername = user1['name']
                # email_idd1 = user1['email']
                # print("approver", email_idd1)
                createdate = ecf.created_date.date()
                creatby = ecf.created_by
                amt = ecf.ecfamount
                inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_obj.get_id(),
                                                                               entity_id=self._entity_id(),status=1).all()
                invheadertotal = float(0)
                sum = 0
                for inv_obj in inv_list:
                    count = sum + 1
                    sum+=1
                    invheadertotal = invheadertotal + inv_obj.totalamount
                    print("invheader",invheadertotal)
                    inv_crno = code + str(now().strftime("%y%m%d")) \
                               + str(ecf_obj.get_id()).zfill(4) + '_'+ str(int(count))
                    print()
                    inv_lis = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                        ecfheader_id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1).update(
                        inv_crno=inv_crno)

                if (amt != invheadertotal):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVOICE_AMOUNT_MISMATCH)
                    error_obj.set_description(ErrorDescription.INVOCIEHDR_AMOUNT_MISMATCH)
                    return error_obj
                for inv_obj in inv_list:
                    invtotal = inv_obj.totalamount
                    invid = inv_obj.id
                    invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,
                                                                                      entity_id=self._entity_id(),status=1).all()
                    invdtltotal = float(0)
                    for invdtl_obj in invdtl_list:
                        invdtltotal = invdtltotal + invdtl_obj.totalamount + float(inv_obj.roundoffamt)
                    print("invdtltotal", invdtltotal)
                    if (invtotal != invdtltotal):
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVOICEDETAIL_AMOUNT_MISMATCH)
                        error_obj.set_description(ErrorDescription.INVOCIEDTL_AMOUNT_MISMATCH)
                        return error_obj
                    for invdtl_obj in invdtl_list:
                        invdtltotl = invdtl_obj.totalamount

                        invdtlid = invdtl_obj.id
                        deb_list = Debit.objects.using(self._current_app_schema()).filter(invoicedetail_id=invdtlid,
                                                                               entity_id=self._entity_id(),status=1).all()
                        debittotal = float(0)
                        if inv_obj.roundoffamt > 0:
                            for deb_obj in deb_list:
                                debittotal = round(debittotal + deb_obj.amount, 2)
                            rndoff = (debittotal + float(inv_obj.roundoffamt) + (inv_obj.otheramount))
                            print("debittotal", debittotal)
                            if (invdtltotal != rndoff):
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.DEBIT_AMOUNT_MISMATCH)
                                error_obj.set_description(ErrorDescription.DEBIT_AMOUNT_MISMATCH)
                                return error_obj
                        else:
                            for deb_obj in deb_list:
                                debittotal = round(debittotal + deb_obj.amount,2)
                            if (invdtltotl != debittotal):
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.DEBIT_AMOUNT_MISMATCH)
                                error_obj.set_description(ErrorDescription.DEBIT_AMOUNT_MISMATCH)
                                return error_obj
                        credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,
                                                                                              entity_id=self._entity_id(),
                                                                                              status=1).all()
                        credittotal = float(0)
                        if inv_obj.roundoffamt < 0:
                            for crd_obj in credit_list:
                                credittotal = credittotal + crd_obj.amount - round(float(inv_obj.roundoffamt),2)
                            rndoffamt = (credittotal + float(inv_obj.roundoffamt) + (inv_obj.otheramount))
                            if (invtotal != rndoffamt):
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.CREDIT_AMOUNT_MISMATCH)
                                error_obj.set_description(ErrorDescription.CREDIT_AMOUNT_MISMATCH)
                                return error_obj
                        else:
                            for crd_obj in credit_list:
                                credittotal = credittotal + crd_obj.amount
                            if (invtotal != credittotal):
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.CREDIT_AMOUNT_MISMATCH)
                                error_obj.set_description(ErrorDescription.CREDIT_AMOUNT_MISMATCH)
                                return error_obj
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                    approvedby=ecf_obj.get_approvedby(),
                    approvername=appr_name,
                    approver_branch=ecf_obj.get_approver_branch(),
                    tds=ecf_obj.get_tds(),
                    crno=crno,
                    ecftype=ecf_obj.get_ecftype(),
                    ecfstatus=ECFStatus.PENDING_FOR_APPROVAL,
                    updated_by=emp_id,
                    updated_date=now())

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                        to_user_id=ecf_obj.get_approvedby(),
                                        created_date=now(),
                                        comments="PENDING  FOR APPROVAL",
                                        remarks=ecf_obj.get_remark(),
                                        is_sys=True
                                        )
                ppx = api_serv.ppxdetails_ecfcrno_update(ecf_obj.get_id(), crno, emp_id)
                logger.info("PPX CRNO", ppx)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                if SuccessStatus.SUCCESS == "success":
                    from utilityservice.service import api_service
                    env = Env()
                    env.read_env()
                    BASE_URL = env.str('WISEFIN_URL')
                    From_url = env.str('SMTP_USER_NAME')
                    PW_url = env.str('SMTP_KEY')
                    api_serv = api_service.ApiService(self._scope())
                    user = api_serv.get_empsingle_id(request, emp_id)
                    emp_name = user['name']
                    email_id = user['email']
                    user1 = api_serv.get_empsingle_id(request, ecf_obj.get_approvedby())
                    approvername = user1['name']
                    email_idd1 = user1['email']
                    print("email_id", email_idd)
                    print("email_id", email_id)
                    template = loader.get_template("nacraiser.html")
                    name = emp_name
                    subject = "Vendor payment request raised by Raiser"
                    m_id = ecf_obj.get_id()
                    cc = [email_idd]
                    to = [email_idd1]

                    from1 = From_url
                    email = to
                    msg = MIMEMultipart('alternative')
                    Subject1 = subject
                    Cc1 = email_idd
                    referenceno = ecf.crno
                    raiseddate = createdate
                    amount = ecf.ecfamount
                    ecftype = ecf.ecftype
                    data = {"emp_name": name,
                            "id": m_id,
                            "server_ip": BASE_URL,
                            "subject": subject,
                            "cc": cc,
                            "to": to,
                            "raisername":appname,
                            "approvername":approvername,
                            "referenceno": referenceno,
                            "raiseddate": raiseddate,
                            "amount": amount,
                            "ecftype": ecftype
                            }
                    body_html = template.render(data)
                    part1 = MIMEText(body_html, "html")
                    # msd2=','.join(to)
                    # msg1 =','.join(cc)
                    # toAddress = msd2
                    msg.attach(part1)
                    msg['Subject'] = "Vendor payment request raised by Raiser"
                    TEXT = msg.as_string()
                    server = smtplib.SMTP("smtp-mail.outlook.com", 587)
                    server.starttls()
                    server.ehlo()
                    server.login(from1, PW_url)
                    server.sendmail(from1,to,TEXT)
                    print("Successfully sent email")
                    server.quit()
                    logger.info("ECF mail data:" + str(msg))
                return success_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(excep))
            return error_obj

    def fetch_ecf_search(self,request,ecf_obj,vys_page,emp_id):
        condition = Q(status=1) & Q(created_by=emp_id)
        if ecf_obj['crno'] != '':
            condition &= Q(crno__icontains=ecf_obj['crno'])
        if ecf_obj['ecftype'] != '':
            condition &= Q(ecftype=ecf_obj['ecftype'])
        # if 'fromdate' in ecf_obj:
        #     condition &= Q(ecfdate__range=(ecf_obj['fromdate'], ecf_obj['todate']))
        if ecf_obj['ecfstatus'] != '':
            condition &= Q(ecfstatus=ecf_obj['ecfstatus'])
        # if ecf_obj['supplier_id'] != '':
        #     condition &= Q(supplier_id=ecf_obj['supplier_id'])
        if ecf_obj['maxamt'] != '':
            condition &= Q(ecfamount__range=(ecf_obj['minamt'], ecf_obj['maxamt']))
        ecf_list =ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        print("list",ecf_list)
        list_length = len(ecf_list)
        ecf_list_data = NWisefinList()
        com_arr = []
        # supp_arr = []
        # state_arr = []
        for i in ecf_list:
            com_arr.append(i.commodity_id)
            # supp_arr.append(i.supplier_id)
            # state_arr.append(i.supplierstate_id)
        api_serv = api_service.ApiService(self._scope())
        commo_data = api_serv.get_commodity_list( request, com_arr)
        # supplier_data = api_serv.get_supplier_list(self, request, supp_arr)
        # state_data = MasterAPI.get_state(self, request, supp_arr)
        if list_length > 0:
            for Ecfhdr in ecf_list:
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity_id(Ecfhdr.commodity_id, commo_data['data'])
                # ecf_data.set_supplier_id(Ecfhdr.supplier_id, supplier_data['data'])
                # ecf_data.set_supplierstate_id(Ecfhdr.supplierstate_id, state_data['data'])
                emp_api = NWisefinUtilityService()
                branch = emp_api.get_employee_branch([Ecfhdr.branch])
                if len(branch) > 0:
                    ecf_data.set_branch(branch)
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                ecf_data.set_ppx_id(Ecfhdr.ppx)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto_id(Ecfhdr.payto)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_approvedby(Ecfhdr.approvedby)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_list_data.append(ecf_data)
            vpage = NWisefinPaginator(ecf_list, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data

    def fetchone_ecf_list(self,request,ecf_id,emp_id):
        try:
            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_id,entity_id=self._entity_id())
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_id,entity_id=self._entity_id()).all()
            ecf_data = ECFHeaderresponse()
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
            state = api_serv.get_statesingle_id(request, Ecfhdr.supplierstate_id)
            supp = api_serv.get_supliersingle_id(request, Ecfhdr.supplier_id)
            emp = api_serv.get_empsingle_id(request, emp_id)
            emp_branch = emp['employee_branch']
            empbranch = api_serv.get_empbranch_id(request, emp_branch)
            employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
            gstdtl = empbranch['gstin']
            gstno = gstdtl[:2]
            # branch_gst = gst.gstin
            # branchname = gst.name
            if Ecfhdr.supplier_id != '':
                supp = api_serv.get_supliersingle_id(request,Ecfhdr.supplier_id)
                supgst = supp['gstno']
                supgstno = supgst[:2]
                if supgstno != gstno:
                    gsttype = 'IGST'
                else:
                    gsttype = 'SGST & CGST'
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_commodity(commodity)
            # ecf_data.set_supplier(supp)
            # ecf_data.set_supplierstate(state)
            if Ecfhdr.ecftype == Type.PO:
                ecf_data.set_ecftype(Type.PO_Type)
            if Ecfhdr.ecftype == Type.NON_PO:
                ecf_data.set_ecftype(Type.NON_PO_Type)
            if Ecfhdr.ecftype == Type.ADVANCE:
                ecf_data.set_ecftype(Type.ADVANCE_Type)
            if Ecfhdr.ecftype == Type.ERA:
                ecf_data.set_ecftype(Type.ERA_Type)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecftype_id(Ecfhdr.ecftype)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
            if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                ecf_data.set_ecfstatus(ECFStatus.Delete)
            if Ecfhdr.ppx == PPX.EMPLOYEE:
                ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
            if Ecfhdr.ppx == PPX.SUPPLIER:
                ecf_data.set_ppx(PPX.SUPPLIER_PPX)
            ecf_data.set_ppx_id(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            if Ecfhdr.payto == Pay.EMPLOYEE:
                ecf_data.set_payto(Pay.EMPLOYEE_Pay)
            if Ecfhdr.payto == Pay.SUPPLIER:
                ecf_data.set_payto(Pay.SUPPLIER_Pay)
            if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                ecf_data.set_payto(Pay.BRANCH_Pay)
            emp_api = NWisefinUtilityService()
            branch = emp_api.get_employee_branch([Ecfhdr.branch])
            if len(branch) > 0:
                ecf_data.set_branch(branch)
            ecf_data.set_payto_id(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(employeebranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            ecf_data.set_approvedby(Ecfhdr.approvedby)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_ap_status(Ecfhdr.ap_status)
            if Ecfhdr.supplier_id != '':
                ecf_data.set_gsttype(gsttype)
                ecf_data.set_supgstno(supgst)
            ecfhdr_list = []
            for invhdr in inv_list:
                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(invhdr.id)
                inhdr_data.set_ecfheader(invhdr.ecfheader_id)
                inhdr_data.set_invoiceno(invhdr.invoiceno)
                inhdr_data.set_dedupinvoiceno(invhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(invhdr.invoicedate)
                inhdr_data.set_suppliergst(invhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(invhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(invhdr.invoiceamount)
                inhdr_data.set_taxamount(invhdr.taxamount)
                inhdr_data.set_totalamount(invhdr.totalamount)
                inhdr_data.set_otheramount(invhdr.otheramount)
                inhdr_data.set_roundoffamt(invhdr.roundoffamt)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                ecfhdr_list.append(json.loads(inhdr_data.get()))
            ecf_data.set_Invheader(ecfhdr_list)
            return ecf_data
        except:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(ErrorDescription.INVALID_INVOICE_ID)
            return error_obj

    def fetch_approvalecf_list(self,request,vys_page,emp_id):
        condition = Q(status=1) & Q(approvedby=emp_id) & Q(ecfstatus=ECFStatus.PENDING_FOR_APPROVAL)
        ecf_list =ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, emp_id)
        emp_name = emp['name']
        list_length = len(ecf_list)
        ecf_list_data = NWisefinList()
        com_arr = []
        brnch_arr = []
        # state_arr = []
        for i in ecf_list:
            com_arr.append(i.commodity_id)
            api_serv = api_service.ApiService(self._scope())
            print("i.branch", i.branch)
            # supp_arr.append(i.supplier_id)
            # state_arr.append(i.supplierstate_id)
        api_serv = api_service.ApiService(self._scope())
        commo_data = api_serv.get_commodity_list(request, com_arr)
        # branch_co = api_serv.get_empbranch_id(request, ecf_list.branch)
        # # disp_name = branch_co['code'] + '--' + branch_co['name']
        # print("branch", branch_co)
        # supplier_data = api_serv.get_supplier_list(self, request, supp_arr)
        # state_data = MasterAPI.get_state(self, request, supp_arr)
        if list_length > 0:
            for Ecfhdr in ecf_list:
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity_id(Ecfhdr.commodity_id, commo_data['data'])
                # ecf_data.set_supplier_id(Ecfhdr.supplier_id, supplier_data['data'])
                # ecf_data.set_supplierstate_id(Ecfhdr.supplierstate_id, state_data['data'])
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                # ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                ecf_data.set_ppx_id(Ecfhdr.ppx)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto_id(Ecfhdr.payto)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto(Ecfhdr.payto)
                emp_api = NWisefinUtilityService()
                branch = emp_api.get_employee_branch([Ecfhdr.branch])
                if len(branch) > 0:
                    ecf_data.set_branch(branch)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_approvedby(Ecfhdr.approvedby)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_list_data.append(ecf_data)
            vpage = NWisefinPaginator(ecf_list, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data

    def fetch_approvalecf_search(self,request,ecf_obj,vys_page,emp_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, emp_id)
        emp_name = emp['name']
        condition = Q(status=1) & Q(approvedby=emp_id) & Q(ecfstatus=ECFStatus.PENDING_FOR_APPROVAL)
        if ecf_obj['crno'] != '':
            condition &= Q(crno__icontains=ecf_obj['crno'])
        if ecf_obj['ecftype'] != '':
            condition &= Q(ecftype=ecf_obj['ecftype'])
        # if 'fromdate' in ecf_obj:
        #     condition &= Q(ecfdate__range=(ecf_obj['fromdate'], ecf_obj['todate']))
        # if ecf_obj['ecfstatus'] != '':
        #     condition &= Q(ecfstatus=ecf_obj['ecfstatus'])
        # if ecf_obj['supplier'] != '':
        #     condition &= Q(supplier_id=ecf_obj['supplier'])
        if ecf_obj['maxamt'] != '':
            condition &= Q(ecfamount__range=(ecf_obj['minamt'], ecf_obj['maxamt']))
        ecf_list =ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        print("list",ecf_list)
        list_length = len(ecf_list)
        ecf_list_data = NWisefinList()
        com_arr = []
        # supp_arr = []
        # state_arr = []
        for i in ecf_list:
            com_arr.append(i.commodity_id)
        #     supp_arr.append(i.supplier_id)
        #     state_arr.append(i.supplierstate_id)
        commo_data = api_serv.get_commodity_list(request, com_arr)
        # supplier_data = api_serv.get_supplier_list(self, request, supp_arr)
        # state_data = MasterAPI.get_state(self, request, supp_arr)
        if list_length > 0:
            for Ecfhdr in ecf_list:
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity_id(Ecfhdr.commodity_id, commo_data['data'])
                # ecf_data.set_supplier_id(Ecfhdr.supplier_id, supplier_data['data'])
                # ecf_data.set_supplierstate_id(Ecfhdr.supplierstate_id, state_data['data'])
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                ecf_data.set_ppx_id(Ecfhdr.ppx)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto_id(Ecfhdr.payto)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                emp_api = NWisefinUtilityService()
                branch = emp_api.get_employee_branch([Ecfhdr.branch])
                if len(branch) > 0:
                    ecf_data.set_branch(branch)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_approvedby(Ecfhdr.approvedby)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_approvername(emp_name)
                ecf_list_data.append(ecf_data)
            vpage = NWisefinPaginator(ecf_list, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data

    def status_ECFUpdateApproved(self, request,ecf_obj, emp_id):
        try:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
            from utilityservice.service import api_service
            env = Env()
            env.read_env()
            BASE_URL = env.str('WISEFIN_URL')
            From_url = env.str('SMTP_USER_NAME')
            PW_url = env.str('SMTP_KEY')
            api_serv = api_service.ApiService(self._scope())
            user = api_serv.get_empsingle_id(request, ecf.raisedby)
            appname = user['name']
            email_idd = user['email']
            createdate = ecf.created_date.date()
            print("raiser", email_idd)
            print("ecf",ecf.crno)
            print("id",ecf.id)
            creatby = ecf.created_by
            if creatby != emp_id:
                # Ecfhdr.ecfstatus == ECFStatus.APPROVED
                # ecfstat = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                if ecf.ecfstatus != ECFStatus.APPROVED:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1).update(ecfstatus=ECFStatus.APPROVED,
                                                                              remark=ecf_obj.get_remark(),
                                                                              updated_by=emp_id,
                                                                              updated_date=now())

                    ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                    self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                            to_user_id=emp_id,
                                            created_date=now(),
                                            comments="APPROVED",
                                            remarks=ecf_obj.get_remark(),
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    if SuccessStatus.SUCCESS == "success":
                        from utilityservice.service import api_service
                        api_serv = api_service.ApiService(self._scope())
                        user = api_serv.get_empsingle_id(request, ecf.raisedby)
                        emp_name = user['name']
                        email_idd = user['email']
                        print("email_id", email_idd)
                        template = loader.get_template("nacapprover.html")
                        name = emp_name
                        subject = "Approved by RM"
                        m_id = ecf_obj.get_id()
                        to = [email_idd]
                        from1 = From_url
                        email = to
                        msg = MIMEMultipart('alternative')
                        Subject1 = subject
                        Cc1 = email_idd
                        referenceno = ecf.crno
                        raiseddate = createdate
                        amount = ecf.ecfamount
                        ecftype = ecf.ecftype
                        data = {"emp_name": name,
                                "id": m_id,
                                "server_ip": BASE_URL,
                                "subject": subject,
                                "to": to,
                                "raisername": appname,
                                "referenceno": referenceno,
                                "raiseddate": raiseddate,
                                "amount": amount,
                                "ecftype": ecftype
                                }
                        body_html = template.render(data)
                        part1 = MIMEText(body_html, "html")
                        # msd2 = ','.join(to)
                        # msg1 = ','.join(cc)
                        # toAddress =  msd2
                        msg.attach(part1)
                        msg['Subject'] = "Approved by RM"
                        TEXT = msg.as_string()
                        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
                        server.starttls()
                        server.ehlo()
                        server.login(From_url, PW_url)
                        server.sendmail(from1, to, TEXT)
                        print("Successfully sent email")
                        server.quit()
                        logger.info("ECF mail data:" + str(msg))
                        return success_obj
                else:
                    traceback.print_exc()
                    error_obj = NWisefinError()
                    error_obj.set_code("Invalid Data")
                    error_obj.set_description("Invoice is already approved")
                    return error_obj
            else:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APPROVER_ID)
                error_obj.set_description(ErrorDescription.No_Rights_To_Approve)
                return error_obj

        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(excep))
            return error_obj


    def status_UpdateRejected(self, request,ecf_obj, emp_id):
        try:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
            from utilityservice.service import api_service
            env = Env()
            env.read_env()
            BASE_URL = env.str('WISEFIN_URL')
            From_url = env.str('SMTP_USER_NAME')
            PW_url = env.str('SMTP_KEY')
            api_serv = api_service.ApiService(self._scope())
            user = api_serv.get_empsingle_id(request, ecf.raisedby)
            appname = user['name']
            email_idd = user['email']
            createdate = ecf.created_date.date()
            print("ecf", ecf.crno)
            print("id", ecf.id)
            creatby = ecf.created_by
            if creatby != emp_id:
                if ecf.ecfstatus != ECFStatus.APPROVED:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1).update(
                                                                        ecfstatus=ECFStatus.REJECT,
                                                                        remark=ecf_obj.get_remark(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
                    ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                    self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                            to_user_id=emp_id,
                                            created_date=now(),
                                            comments=ECFStatus.REJECT,
                                            remarks=ecf_obj.get_remark(),
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    if SuccessStatus.SUCCESS == "success":
                        from utilityservice.service import api_service
                        api_serv = api_service.ApiService(self._scope())
                        user = api_serv.get_empsingle_id(request, ecf.raisedby)
                        emp_name = user['name']
                        email_idd = user['email']
                        print("email_id", email_idd)
                        template = loader.get_template("nacrejecter.html")
                        name = emp_name
                        subject = "Rejection by RM"
                        m_id = ecf_obj.get_id()
                        to = [email_idd]
                        from1 = From_url
                        email = to
                        msg = MIMEMultipart('alternative')
                        Subject1 = subject
                        Cc1 = email_idd
                        referenceno = ecf.crno
                        raiseddate = createdate
                        amount = ecf.ecfamount
                        ecftype = ecf.ecftype
                        data = {"emp_name": name,
                                "id": m_id,
                                "server_ip": BASE_URL,
                                "subject": subject,
                                "to": to,
                                "raisername": appname,
                                "referenceno": referenceno,
                                "raiseddate": raiseddate,
                                "amount": amount,
                                "ecftype": ecftype
                                }
                        body_html = template.render(data)
                        part1 = MIMEText(body_html, "html")
                        # msd2 = ','.join(to)
                        # msg1 = ','.join(cc)
                        # toAddress = msd2
                        msg.attach(part1)
                        msg['Subject'] = "Rejection by RM"
                        TEXT = msg.as_string()
                        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
                        server.starttls()
                        server.ehlo()
                        server.login(From_url,PW_url)
                        server.sendmail(from1, to, TEXT)
                        print("Successfully sent email")
                        server.quit()
                        logger.info("ECF mail data:" + str(msg))
                        return success_obj
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code("Invalid data")
                    error_obj.set_description("Invoice is already approved or rejected")
                    return error_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REJECT_ID)
                error_obj.set_description(ErrorDescription.No_Rights_To_Reject)
                return error_obj

        except Exception as excep:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(excep))
            return error_obj

    def status_ECFNextApprover(self, request ,ecf_obj, emp_id):
        try:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            print('app', ecf_obj['approvedby'])
            emp = api_serv.get_empsingle_id(request, ecf_obj['approvedby'])
            appr_name = emp['name']
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj['id'],entity_id=self._entity_id())
            creatby = ecf.created_by
            if creatby != emp_id:
                if ecf.ecfstatus != ECFStatus.APPROVED:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj['id'],entity_id=self._entity_id()).update(approvedby=ecf_obj['approvedby'],
                                                                                  approvername=appr_name,
                                                                                ecfstatus=ECFStatus.PENDING_FOR_APPROVAL,
                                                                                remark=ecf_obj['remarks'],
                                                                                updated_by=emp_id,
                                                                                updated_date=now())

                    ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj['id'])
                    self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                            to_user_id=ecf_obj['approvedby'],
                                            created_date=now(),
                                            comments=ECFStatus.PENDING_FOR_APPROVAL,
                                            remarks=ecf_obj['remarks'],
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    return success_obj
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code("Invalid data")
                    error_obj.set_description("Invoice is already approved or rejected")
                    return error_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APPROVER_ID)
                error_obj.set_description(ErrorDescription.No_Rights_To_Approve)
                return error_obj
        except Exception as excep:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(excep))
            return error_obj

    def fetchone_inv_list(self,request, inv_id, emp_id):
        try:
            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=inv_id ,entity_id=self._entity_id(), status = 1).all()
            type = Ecfhdr.ecftype

            # if ecfhdr.supplier_id!= '':
            #     supp = ecfhdr.supplier_id
            if ((type == (Type.NON_PO)) or (type ==(Type.TCF))):
                ecf_data = ECFHeaderresponse()
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
                # ven_service = VendorAPI()
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_branch = emp['employee_branch']
                try:
                    bnch_name = Ecfhdr.approvedby
                    emp = api_serv.get_empsingle_id(request, bnch_name)
                except:
                    bnch_name=None
                print("bnch_name", bnch_name)
                emp_branch = emp['employee_branch']

                emp_name = emp['name']
                print("emp_name", emp_name)
                empbranch = api_serv.get_empbranch_id(request, emp_branch)
                appbranch_name = empbranch['name']
                try:
                    emp_branch1 = Ecfhdr.approver_branch
                    empbranch1 = api_serv.get_empbranch_id(request, emp_branch1)
                except:
                    empbranch1 = None
                # appbrnh_name = empbranch1['name']
                print("empbranch", empbranch['name'])
                employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
                branch_co = api_serv.get_empbranch_id(request, Ecfhdr.branch)
                # disp_name = branch_co['code'] + '--' + branch_co['name']
                print("branch",branch_co)
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity(commodity)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                if Ecfhdr.ecftype == Type.TCF:
                    ecf_data.set_ecftype(Type.TCF_Type)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx_id(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto_id(Ecfhdr.payto)
                ecf_data.set_payto_id(get_Pay(Ecfhdr.payto))
                ecf_data.set_ppx_id(get_Ppx(Ecfhdr.ppx))
                # emp_api = NWisefinUtilityService()
                # branch = api_serv.get_branch_data([Ecfhdr.branch],request)
                # if len(branch) > 0:
                ecf_data.set_branch(branch_co)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(employeebranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                if Ecfhdr.tds == TDS.NA:
                    ecf_data.set_tds(TDS.NA_TDS)
                elif Ecfhdr.tds == TDS.YES:
                    ecf_data.set_tds(TDS.YES_TDS)
                elif Ecfhdr.tds == TDS.NOT_KNOWN:
                    ecf_data.set_tds(TDS.NOT_KNOWN_TDS)
                ecf_data.set_data({"approvedby": bnch_name, "approvername": emp, "approverbranch": empbranch,"tds":(get_tds(Ecfhdr.tds)),"approver_branch":empbranch1})
                ecf_data.set_approvedby(bnch_name)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_approverbranch(appbranch_name)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_branch(branch_co)
                ecf_data.set_rmcode(api_serv.get_empsingle_id(request, Ecfhdr.rmcode))
                ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
                ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
                if Ecfhdr.supplier_type == SupplierType.SINGLE:
                    ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
                if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                    ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
                ecfhdr_list = []
                # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

                # ecf = invhdr.ecfheader_id
                # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

                invhdr_list = []
                if len(inv_list)!=0:
                    for inhdr in inv_list:
                        invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                        invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                        deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                        credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                        file_list = ECFFiles.objects.using(self._current_app_schema()).filter(ecffile_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                        bank_arr = []
                        for i in credit_list:
                            bank_arr.append(i.creditbank_id)
                        bnnch = api_serv.get_empbranch_id(request, Ecfhdr.branch)
                        print("bnnch",bnnch)
                        gstno = bnnch['gstin']
                        print("gstno",gstno[:2])
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                        suppgst = supp['gstno']
                        print("supp",suppgst[:2])
                        print("supp",supp)
                        if suppgst[:2] != gstno[:2]:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'

                        inhdr_data = Invoiceheaderresponse()
                        inhdr_data.set_id(inhdr.id)
                        inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                        inhdr_data.set_invoiceno(inhdr.invoiceno)
                        inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                        inhdr_data.set_invoicedate(inhdr.invoicedate)
                        inhdr_data.set_suppliergst(inhdr.suppliergst)
                        inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                        inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                        inhdr_data.set_taxamount(inhdr.taxamount)
                        inhdr_data.set_totalamount(inhdr.totalamount)
                        inhdr_data.set_otheramount(inhdr.otheramount)
                        inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                        inhdr_data.set_supplier(supp)
                        inhdr_data.set_inv_crno(inhdr.inv_crno)
                        inhdr_data.set_invoicegst(inhdr.invoicegst)
                        inhdr_data.set_supplierstate(state)
                        if inhdr.supplier_id != '':
                            inhdr_data.set_gsttype(gsttype)
                        for invpo in invpo_list:
                            inpo_data = Invoiceporesponse()
                            inpo_data.set_id(invpo.id)
                            inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                            inpo_data.set_ponumber(invpo.ponumber)
                            inpo_data.set_grnnumber(invpo.grnnumber)
                            inpo_data.set_grndate(invpo.grndate)
                            inpo_data.set_poquantity(invpo.poquantity)
                            inpo_data.set_receivedqty(invpo.receivedqty)
                            inpo_data.set_balanceqty(invpo.balanceqty)
                            inpo_data.set_receiveddate(invpo.receiveddate)
                            inpo_data.set_product_code(invpo.product_code)
                            inpo_data.set_invoicedqty(invpo.invoicedqty)
                            inpo_data.set_invoiceqty(invpo.invoiceqty)
                            invhdr_list.append(json.loads(inpo_data.get()))
                            inhdr_data.set_invoicepo(invhdr_list)

                        inv_list = []
                        for invdtl in invdtl_list:
                            hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                            indtl_data = Invoicedetailresponse()
                            indtl_data.set_id(invdtl.id)
                            indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                            indtl_data.set_invoice_po(invdtl.invoice_po)
                            indtl_data.set_productcode(invdtl.productcode)
                            indtl_data.set_productname(invdtl.productname)
                            indtl_data.set_description(invdtl.description)
                            indtl_data.set_hsn(hsn)
                            indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                            indtl_data.set_uom(invdtl.uom)
                            indtl_data.set_unitprice(invdtl.unitprice)
                            indtl_data.set_quantity(invdtl.quantity)
                            indtl_data.set_amount(invdtl.amount)
                            indtl_data.set_discount(invdtl.discount)
                            indtl_data.set_sgst(invdtl.sgst)
                            indtl_data.set_cgst(invdtl.cgst)
                            indtl_data.set_igst(invdtl.igst)
                            indtl_data.set_taxamount(invdtl.taxamount)
                            indtl_data.set_totalamount(invdtl.totalamount)
                            indtl_data.set_invoiceno(invdtl.invoiceno)
                            indtl_data.set_invoicedate(invdtl.invoicedate)
                            indtl_data.set_supplier_name(invdtl.supplier_name)
                            indtl_data.set_suppliergst(invdtl.suppliergst)
                            indtl_data.set_pincode(invdtl.pincode)
                            indtl_data.set_otheramount(invdtl.otheramount)
                            indtl_data.set_roundoffamt(invdtl.roundoffamt)
                            inv_list.append(json.loads(indtl_data.get()))
                            inhdr_data.set_invoicedtl(inv_list)

                            invdeb_list = []
                            for dbt in deb_list:
                                cat = api_serv.get_cat_code(request,dbt.category_code)
                                sub = api_serv.get_subcat_code(request,dbt.subcategory_code)
                                dbt_data = Debitresponse()
                                dbt_data.set_id(dbt.id)
                                dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                                dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                                dbt_data.set_category_code(cat)
                                dbt_data.set_subcategory_code(sub)
                                dbt_data.set_debitglno(dbt.debitglno)
                                dbt_data.set_amount(dbt.amount)
                                dbt_data.set_bsproduct(api_serv.get_bscode(dbt.bsproduct))
                                dbt_data.set_deductionamount(dbt.deductionamount)
                                ccbs_list=[]
                                ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                                for ccbs in ccb_list:
                                    cc = api_serv.get_cc_code(request,ccbs.cc_code)
                                    bs = api_serv.get_bs_code(request,ccbs.bs_code)
                                    ccbs_data = ccbsdtlresponse()
                                    ccbs_data.set_id(ccbs.id)
                                    ccbs_data.set_debit(ccbs.debit_id)
                                    ccbs_data.set_cc_code(cc)
                                    ccbs_data.set_bs_code(bs)
                                    ccbs_data.set_code(ccbs.code)
                                    ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                                    ccbs_data.set_glno(ccbs.glno)
                                    ccbs_data.set_amount(ccbs.amount)
                                    ccbs_data.set_remarks(ccbs.remarks)
                                    ccbs_list.append(json.loads(ccbs_data.get()))
                                    dbt_data.set_ccbs(ccbs_data)
                                    invdeb_list.append(json.loads(dbt_data.get()))
                                    inhdr_data.set_debit(invdeb_list)

                        crd_list = []
                        for crd in credit_list:
                            cat = api_serv.get_cat_code(request, crd.category_code)
                            sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                            crd_data = Creditresponse()
                            crd_data.set_id(crd.id)
                            crd_data.set_invoiceheader(crd.invoiceheader_id)
                            pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                            crd_data.set_paymode(pay)
                            print("crd.paymode_id",crd.paymode_id)
                            # creditdtl = api_serv.get_creditpayment(i.creditbank_id,emp_id)
                            # print("crdtl",creditdtl)
                            # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                            # crd_data.set_paydetails(bankdtl)
                            crd_data.set_category_code(cat)
                            crd_data.set_subcategory_code(sub)
                            bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                            crd_data.set_credit_bank(bank_data)
                            # crd_data.set_creditbank_id(crd.creditbank_id,bank_data['data'])
                            crd_data.set_suppliertax(crd.suppliertax_id)
                            crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                            crd_data.set_amount(crd.amount)
                            crd_data.set_creditglno(crd.creditglno)
                            if crd.paymode_id==4:
                                from utilityservice.service.ap_api_service import APApiService
                                appservice = APApiService(self._scope())
                                app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, crd.creditrefno,
                                                                                                           Ecfhdr.raisedby)
                                print("empappservice",app_service)
                                crd_data.set_creditrefno(app_service)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                            else:
                                crd_data.set_creditrefno(crd.creditrefno)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                        filelist = []
                        print("!")
                        print("!!",file_list)
                        for fl in file_list:
                            list_lent = len(file_list)
                            if list_lent > 0:
                                dtpc_res = ecffileResponse()
                                dtpc_res.set_id(fl.id)
                                dtpc_res.set_file_id(fl.file_id)
                                dtpc_res.set_file_name(fl.file_name)
                            filelist.append(dtpc_res)
                            inhdr_data.set_file_data(filelist)
                        ecfhdr_list.append(json.loads(inhdr_data.get()))
                ecf_data.set_Invheader(ecfhdr_list)
                return ecf_data
            elif type == Type.ERA:
                ecf_data = ECFHeaderresponse()
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
                # ven_service = VendorAPI()
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_branch = emp['employee_branch']
                try:
                    emp_branch1 = Ecfhdr.approver_branch
                    empbranch1 = api_serv.get_empbranch_id(request, emp_branch1)
                except:
                    empbranch1 = None
                try:
                    bnch_name = Ecfhdr.approvedby
                    emp = api_serv.get_empsingle_id(request, bnch_name)
                except:
                    bnch_name = None
                print("bnch_name", bnch_name)
                emp_branch = emp['employee_branch']
                emp_name = emp['name']
                print("emp_name", emp_name)
                empbranch = api_serv.get_empbranch_id(request, emp_branch)
                appbranch_name = empbranch['name']
                print("empbranch", empbranch['name'])
                employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
                branch_co = api_serv.get_empbranch_id(request, Ecfhdr.branch)
                # disp_name = branch_co['code'] + '--' + branch_co['name']
                print("branch", branch_co)
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity(commodity)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx_id(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto_id(Ecfhdr.payto)
                ecf_data.set_payto_id(get_Pay(Ecfhdr.payto))
                ecf_data.set_ppx_id(get_Ppx(Ecfhdr.ppx))
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(employeebranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_data({"approvedby": bnch_name, "approvername": emp, "approverbranch": empbranch,"tds":(get_tds(Ecfhdr.tds)),"approver_branch":empbranch1})
                ecf_data.set_approvedby(bnch_name)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_approverbranch(appbranch_name)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_branch(branch_co)
                ecf_data.set_rmcode(api_serv.get_empsingle_id(request, Ecfhdr.rmcode))
                ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
                ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
                if Ecfhdr.supplier_type == SupplierType.SINGLE:
                    ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
                if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                    ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
                ecfhdr_list = []
                # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

                # ecf = invhdr.ecfheader_id
                # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)
                invhdr_list = []
                if len(inv_list) != 0:
                    for inhdr in inv_list:
                        invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                                          entity_id=self._entity_id(),status=1).all()
                        invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                                     entity_id=self._entity_id(),status=1).all()
                        deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                               entity_id=self._entity_id(),status=1).all()
                        credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                                   entity_id=self._entity_id(),status=1).all()
                        file_list = ECFFiles.objects.using(self._current_app_schema()).filter(ecffile_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                        bank_arr = []
                        for i in credit_list:
                            bank_arr.append(i.creditbank_id)
                        # state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        # supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                        bank_data = api_serv.get_bank_list(request, bank_arr)
                        # from utilityservice.service import api_service
                        # api_serv = api_service.ApiService()
                        # emp = api_serv.get_empsingle_id(request, emp_id)
                        # print('emp2', emp)
                        # emp_add = emp['address_id']
                        # empadd = api_serv.get_empaddress_id(request, emp_add)
                        #
                        # gst = empadd['state_id']
                        # if inhdr.supplier_id != '':
                        #     supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                        #     suppadd = supp['address_id']
                        #     ven = api_serv.get_venaddress(request, suppadd)
                        #     supgst = ven['state_id']
                        #     if supgst != gst:
                        #         gsttype = 'IGST'
                        #     else:
                        #         gsttype = 'SGST & CGST'

                        inhdr_data = Invoiceheaderresponse()
                        inhdr_data.set_id(inhdr.id)
                        inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                        inhdr_data.set_inv_crno(inhdr.inv_crno)
                        inhdr_data.set_invoiceno(inhdr.invoiceno)
                        inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                        inhdr_data.set_invoicedate(inhdr.invoicedate)
                        inhdr_data.set_suppliergst(inhdr.suppliergst)
                        inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                        inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                        inhdr_data.set_taxamount(inhdr.taxamount)
                        inhdr_data.set_totalamount(inhdr.totalamount)
                        inhdr_data.set_otheramount(inhdr.otheramount)
                        inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                        # inhdr_data.set_supplier(supp)
                        inhdr_data.set_invoicegst(inhdr.invoicegst)
                        # inhdr_data.set_supplierstate(state)
                        # if inhdr.supplier_id != '':
                        #     inhdr_data.set_gsttype(gsttype)

                        for invpo in invpo_list:
                            inpo_data = Invoiceporesponse()
                            inpo_data.set_id(invpo.id)
                            inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                            inpo_data.set_ponumber(invpo.ponumber)
                            inpo_data.set_grnnumber(invpo.grnnumber)
                            inpo_data.set_grndate(invpo.grndate)
                            inpo_data.set_poquantity(invpo.poquantity)
                            inpo_data.set_receivedqty(invpo.receivedqty)
                            inpo_data.set_balanceqty(invpo.balanceqty)
                            inpo_data.set_receiveddate(invpo.receiveddate)
                            inpo_data.set_product_code(invpo.product_code)
                            inpo_data.set_invoicedqty(invpo.invoicedqty)
                            inpo_data.set_invoiceqty(invpo.invoiceqty)
                            invhdr_list.append(json.loads(inpo_data.get()))
                            inhdr_data.set_invoicepo(invhdr_list)

                        inv_list = []
                        for invdtl in invdtl_list:
                            hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                            indtl_data = Invoicedetailresponse()
                            indtl_data.set_id(invdtl.id)
                            indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                            indtl_data.set_invoice_po(invdtl.invoice_po)
                            indtl_data.set_productcode(invdtl.productcode)
                            indtl_data.set_productname(invdtl.productname)
                            indtl_data.set_description(invdtl.description)
                            indtl_data.set_hsn(hsn)
                            indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                            indtl_data.set_uom(invdtl.uom)
                            indtl_data.set_unitprice(invdtl.unitprice)
                            indtl_data.set_quantity(invdtl.quantity)
                            indtl_data.set_amount(invdtl.amount)
                            indtl_data.set_discount(invdtl.discount)
                            indtl_data.set_sgst(invdtl.sgst)
                            indtl_data.set_cgst(invdtl.cgst)
                            indtl_data.set_igst(invdtl.igst)
                            indtl_data.set_taxamount(invdtl.taxamount)
                            indtl_data.set_totalamount(invdtl.totalamount)
                            indtl_data.set_invoiceno(invdtl.invoiceno)
                            indtl_data.set_invoicedate(invdtl.invoicedate)
                            indtl_data.set_supplier_name(invdtl.supplier_name)
                            indtl_data.set_suppliergst(invdtl.suppliergst)
                            indtl_data.set_pincode(invdtl.pincode)
                            indtl_data.set_otheramount(invdtl.otheramount)
                            indtl_data.set_roundoffamt(invdtl.roundoffamt)
                            inv_list.append(json.loads(indtl_data.get()))
                            inhdr_data.set_invoicedtl(inv_list)

                            invdeb_list = []
                            for dbt in deb_list:
                                cat = api_serv.get_cat_code(request, dbt.category_code)
                                sub = api_serv.get_subcat_code(request, dbt.subcategory_code)
                                dbt_data = Debitresponse()
                                dbt_data.set_id(dbt.id)
                                dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                                dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                                dbt_data.set_category_code(cat)
                                dbt_data.set_subcategory_code(sub)
                                dbt_data.set_debitglno(dbt.debitglno)
                                dbt_data.set_amount(dbt.amount)
                                dbt_data.set_deductionamount(dbt.deductionamount)
                                dbt_data.set_bsproduct(api_serv.get_bscode(dbt.bsproduct))
                                ccbs_list = []
                                ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                                for ccbs in ccb_list:
                                    cc = api_serv.get_cc_code(request, ccbs.cc_code)
                                    bs = api_serv.get_bs_code(request, ccbs.bs_code)
                                    ccbs_data = ccbsdtlresponse()
                                    ccbs_data.set_id(ccbs.id)
                                    ccbs_data.set_debit(ccbs.debit_id)
                                    ccbs_data.set_cc_code(cc)
                                    ccbs_data.set_bs_code(bs)
                                    ccbs_data.set_code(ccbs.code)
                                    ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                                    ccbs_data.set_glno(ccbs.glno)
                                    ccbs_data.set_amount(ccbs.amount)
                                    ccbs_data.set_remarks(ccbs.remarks)
                                    ccbs_list.append(json.loads(ccbs_data.get()))
                                    dbt_data.set_ccbs(ccbs_data)
                                    invdeb_list.append(json.loads(dbt_data.get()))
                                    inhdr_data.set_debit(invdeb_list)

                        crd_list = []
                        for crd in credit_list:
                            cat = api_serv.get_cat_code(request, crd.category_code)
                            sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                            crd_data = Creditresponse()
                            crd_data.set_id(crd.id)
                            crd_data.set_invoiceheader(crd.invoiceheader_id)
                            pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                            crd_data.set_paymode(pay)
                            # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                            # crd_data.set_paydetails(bankdtl)
                            crd_data.set_category_code(cat)
                            crd_data.set_subcategory_code(sub)
                            crd_data.set_creditbank_id(crd.creditbank_id, bank_data['data'])
                            crd_data.set_suppliertax(crd.suppliertax_id)
                            crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                            crd_data.set_amount(crd.amount)
                            crd_data.set_creditglno(crd.creditglno)
                            if crd.paymode_id==4:
                                from utilityservice.service.ap_api_service import APApiService
                                appservice = APApiService(self._scope())
                                app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, crd.creditrefno,
                                                                                                           Ecfhdr.raisedby)
                                print("empappservice",app_service)
                                crd_data.set_creditrefno(app_service)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                            else:
                                crd_data.set_creditrefno(crd.creditrefno)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                        filelist = []
                        for fl in file_list:
                            list_lent = len(file_list)
                            if list_lent > 0:
                                dtpc_res = ecffileResponse()
                                dtpc_res.set_id(fl.id)
                                dtpc_res.set_file_id(fl.file_id)
                                dtpc_res.set_file_name(fl.file_name)
                            filelist.append(dtpc_res)
                            inhdr_data.set_file_data(filelist)
                        ecfhdr_list.append(json.loads(inhdr_data.get()))
                ecf_data.set_Invheader(ecfhdr_list)
                return ecf_data
            elif type == Type.ADVANCE:
                ecf_data = ECFHeaderresponse()
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
                # ven_service = VendorAPI()
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_branch = emp['employee_branch']
                try:
                    emp_branch1 = Ecfhdr.approver_branch
                    empbranch1 = api_serv.get_empbranch_id(request, emp_branch1)
                except:
                    empbranch1 = None
                try:
                    bnch_name = Ecfhdr.approvedby
                    emp = api_serv.get_empsingle_id(request, bnch_name)
                except:
                    bnch_name = None
                print("bnch_name", bnch_name)
                emp_branch = emp['employee_branch']
                emp_name = emp['name']
                print("emp_name", emp_name)
                empbranch = api_serv.get_empbranch_id(request, emp_branch)
                appbranch_name = empbranch['name']
                print("empbranch", empbranch['name'])
                employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
                branch_co = api_serv.get_empbranch_id(request, Ecfhdr.branch)
                # disp_name = branch_co['code'] + '--' + branch_co['name']
                print("branch", branch_co)
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity(commodity)
                # ecf_data.set_ecftype(get_Type(Type.PO_Type))
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                # ecf_data.set_ecftype_id(get_Type(Ecfhdr.ecftype))
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx_id(Ecfhdr.ppx)
                ecf_data.set_ppx_id(get_Ppx(Ecfhdr.ppx))
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto_id(Ecfhdr.payto)
                ecf_data.set_payto_id(get_Pay(Ecfhdr.payto))
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(employeebranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_data({"approvedby": bnch_name, "approvername": emp, "approverbranch": empbranch,"tds":(get_tds(Ecfhdr.tds)),"approver_branch":empbranch1})
                ecf_data.set_approvedby(bnch_name)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_approverbranch(appbranch_name)
                ecf_data.set_branch(branch_co)
                ecf_data.set_rmcode(api_serv.get_empsingle_id(request, Ecfhdr.rmcode))
                ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
                ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
                if Ecfhdr.supplier_type == SupplierType.SINGLE:
                    ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
                if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                    ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
                ecfhdr_list = []
                # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

                # ecf = invhdr.ecfheader_id
                # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)
                invhdr_list = []
                if len(inv_list) != 0:
                    for inhdr in inv_list:

                        deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                               entity_id=self._entity_id(),status=1).all()
                        credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                                   entity_id=self._entity_id(),status=1).all()
                        file_list = ECFFiles.objects.using(self._current_app_schema()).filter(ecffile_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                        bank_arr = []
                        for i in credit_list:
                            bank_arr.append(i.creditbank_id)


                        # bank_data = api_serv.get_bank_list(request, bank_arr)
                        from utilityservice.service import api_service
                        api_serv = api_service.ApiService(self._scope())
                        emp = api_serv.get_empsingle_id(request, emp_id)
                        print('emp2', emp)
                        emp_add = emp['address_id']
                        empadd = api_serv.get_empaddress_id(request, emp_add)

                        gst = empadd['state_id']
                        if inhdr.supplier_id != None:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                            suppadd = supp['address_id']
                            ven = api_serv.get_venaddress(request, suppadd)
                            supgst = ven['state_id']
                            if supgst != gst:
                                gsttype = 'IGST'
                            else:
                                gsttype = 'SGST & CGST'

                        inhdr_data = Invoiceheaderresponse()
                        inhdr_data.set_id(inhdr.id)
                        inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                        inhdr_data.set_inv_crno(inhdr.inv_crno)
                        inhdr_data.set_invoiceno(inhdr.invoiceno)
                        inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                        inhdr_data.set_invoicedate(inhdr.invoicedate)
                        inhdr_data.set_suppliergst(inhdr.suppliergst)
                        inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                        inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                        inhdr_data.set_taxamount(inhdr.taxamount)
                        inhdr_data.set_totalamount(inhdr.totalamount)
                        inhdr_data.set_otheramount(inhdr.otheramount)
                        inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                        if inhdr.supplier_id != None:
                            inhdr_data.set_supplier(supp)
                            inhdr_data.set_supplierstate(state)
                        else:
                            inhdr_data.set_supplier("")
                            inhdr_data.set_supplierstate("")
                        inhdr_data.set_invoicegst(inhdr.invoicegst)

                        # if inhdr.supplier_id != '':
                        #     inhdr_data.set_gsttype(gsttype)





                        invdeb_list = []
                        for dbt in deb_list:
                            cat = api_serv.get_cat_code(request, dbt.category_code)
                            sub = api_serv.get_subcat_code(request, dbt.subcategory_code)
                            dbt_data = Debitresponse()
                            dbt_data.set_id(dbt.id)
                            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                            dbt_data.set_category_code(cat)
                            dbt_data.set_subcategory_code(sub)
                            dbt_data.set_debitglno(dbt.debitglno)
                            dbt_data.set_amount(dbt.amount)
                            dbt_data.set_bsproduct(api_serv.get_bscode(dbt.bsproduct))
                            dbt_data.set_deductionamount(dbt.deductionamount)
                            ccbs_list = []
                            ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                            for ccbs in ccb_list:
                                cc = api_serv.get_cc_code(request, ccbs.cc_code)
                                bs = api_serv.get_bs_code(request, ccbs.bs_code)
                                ccbs_data = ccbsdtlresponse()
                                ccbs_data.set_id(ccbs.id)
                                ccbs_data.set_debit(ccbs.debit_id)
                                ccbs_data.set_cc_code(cc)
                                ccbs_data.set_bs_code(bs)
                                ccbs_data.set_code(ccbs.code)
                                ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                                ccbs_data.set_glno(ccbs.glno)
                                ccbs_data.set_amount(ccbs.amount)
                                ccbs_data.set_remarks(ccbs.remarks)
                                ccbs_list.append(json.loads(ccbs_data.get()))
                                dbt_data.set_ccbs(ccbs_data)
                                invdeb_list.append(json.loads(dbt_data.get()))
                                inhdr_data.set_debit(invdeb_list)

                        crd_list = []
                        for crd in credit_list:
                            cat = api_serv.get_cat_code(request, crd.category_code)
                            sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                            crd_data = Creditresponse()
                            crd_data.set_id(crd.id)
                            crd_data.set_invoiceheader(crd.invoiceheader_id)
                            pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                            crd_data.set_paymode(pay)
                            # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                            # crd_data.set_paydetails(bankdtl)
                            crd_data.set_category_code(cat)
                            crd_data.set_subcategory_code(sub)
                            bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                            crd_data.set_credit_bank(bank_data)
                            # crd_data.set_creditbank_id(crd.creditbank_id, bank_data['data'])
                            crd_data.set_suppliertax(crd.suppliertax_id)
                            crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                            crd_data.set_amount(crd.amount)
                            crd_data.set_creditglno(crd.creditglno)
                            if crd.paymode_id==4:
                                from utilityservice.service.ap_api_service import APApiService
                                appservice = APApiService(self._scope())
                                app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, crd.creditrefno,
                                                                                                           Ecfhdr.raisedby)
                                print("empappservice",app_service)
                                crd_data.set_creditrefno(app_service)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                            else:
                                crd_data.set_creditrefno(crd.creditrefno)
                                crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                                crd_data.set_taxexcempted(crd.taxexcempted)
                                crd_data.set_taxableamount(crd.taxableamount)
                                crd_data.set_ddtranbranch(crd.ddtranbranch)
                                crd_data.set_ddpaybranch(crd.ddpaybranch)
                                crd_list.append(json.loads(crd_data.get()))
                                inhdr_data.set_credit(crd_list)
                        filelist = []
                        for fl in file_list:
                            list_lent = len(file_list)
                            if list_lent > 0:
                                dtpc_res = ecffileResponse()
                                dtpc_res.set_id(fl.id)
                                dtpc_res.set_file_id(fl.file_id)
                                dtpc_res.set_file_name(fl.file_name)
                            filelist.append(dtpc_res)
                            inhdr_data.set_file_data(filelist)
                        ecfhdr_list.append(json.loads(inhdr_data.get()))
                ecf_data.set_Invheader(ecfhdr_list)
                return ecf_data
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(excep))
            return error_obj

    def Delete_ecfhdr(self,request, ecf_id, emp_id):
        try:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_id)
            if ecf.ecfstatus != ECFStatus.APPROVED:
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_id,entity_id=self._entity_id()).update(ecfstatus=ECFStatus.DELETE,
                                                                          status=0,
                                                                          updated_by=emp_id,
                                                                          updated_date=now())
                ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_id)
                self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                        to_user_id=emp_id,
                                        created_date=now(),
                                        comments="DELETE",
                                        is_sys=True,
                                        entity_id=self._entity_id()
                                        )
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description("Data is already approved")
                return error_obj
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(excep))
            return error_obj

    def ecfmodcreate(self,request,ecf_obj,emp_id):
        if ecf_obj.get_ecftype() == Type.NON_PO:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2',emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            if (ecf_obj.get_commodity_id() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " CommodityField")
                return error_obj
            elif (ecf_obj.get_ecfdate() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " EcfDateField")
                return error_obj
            else:
                if not ecf_obj.get_id() is None:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                supplier_type=ecf_obj.get_supplier_type(),
                                                                                # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                                                commodity_id=ecf_obj.get_commodity_id(),
                                                                                ecftype=ecf_obj.get_ecftype(),
                                                                                ecfdate=ecf_obj.get_ecfdate(),
                                                                                ecfamount=ecf_obj.get_ecfamount(),
                                                                                ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                                                                                ppx=ecf_obj.get_ppx(),
                                                                                notename=ecf_obj.get_notename(),
                                                                                remark=ecf_obj.get_remark(),
                                                                                payto=ecf_obj.get_payto(),
                                                                                raisedby=emp_id,
                                                                                raiserbranch=emp_branch,
                                                                                raisername=raisor_name,
                                                                                branch=ecf_obj.get_branch(),
                                                                                rmcode=ecf_obj.get_rmcode(),
                                                                                client_code=ecf_obj.get_client_code(),
                                                                                ap_status=ecf_obj.get_ap_status(),
                                                                                updated_by=emp_id,
                                                                                updated_date=now())

                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                            to_user_id=emp_id,
                                            created_date=now(),
                                            comments="New in Modification",
                                            remarks=ecf_obj.get_remark(),
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )

                else:
                        Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                                                            supplier_type=ecf_obj.get_supplier_type(),
                                                            # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                            commodity_id=ecf_obj.get_commodity_id(),
                                                            ecftype=ecf_obj.get_ecftype(),
                                                            ecfdate=ecf_obj.get_ecfdate(),
                                                            ecfamount=ecf_obj.get_ecfamount(),
                                                            ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                                                            ppx=ecf_obj.get_ppx(),
                                                            notename=ecf_obj.get_notename(),
                                                            remark=ecf_obj.get_remark(),
                                                            payto=ecf_obj.get_payto(),
                                                            raisedby=emp_id,
                                                            raiserbranch=emp_branch,
                                                            raisername=raisor_name,
                                                            branch=ecf_obj.get_branch(),
                                                            rmcode=ecf_obj.get_rmcode(),
                                                            client_code=ecf_obj.get_client_code(),
                                                            ap_status=ecf_obj.get_ap_status(),
                                                            created_by=emp_id,
                                                            entity_id=self._entity_id())

                        self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                        ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id, to_user_id=emp_id,
                                               created_date=now(),
                                               comments="New in Modification" ,
                                               remarks=ecf_obj.get_remark(),
                                               is_sys=True,
                                               entity_id=self._entity_id()
                                               )

                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_supplier_type(Ecfhdr.supplier_type)
                # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
                ecf_data.set_commodity(Ecfhdr.commodity_id)
                ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
                ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_branchgst(1)
                ecf_data.set_branchname('adyar')
                return ecf_data
        elif ecf_obj.get_ecftype() == Type.ERA:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2', emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            emp1 = api_serv.get_empbranch_id(request, emp_branch)
            emp_add1 = emp1['gstin']
            emp_bran = emp1['name']
            if (ecf_obj.get_commodity_id() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " CommodityField")
                return error_obj
            elif (ecf_obj.get_ecfdate() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " EcfDateField")
                return error_obj
            else:
                if not ecf_obj.get_id() is None:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                        supplier_type=ecf_obj.get_supplier_type(),
                        # supplierstate_id=ecf_obj.get_supplierstate_id(),
                        commodity_id=ecf_obj.get_commodity_id(),
                        ecftype=ecf_obj.get_ecftype(),
                        ecfdate=ecf_obj.get_ecfdate(),
                        ecfamount=ecf_obj.get_ecfamount(),
                        ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                        ppx=ecf_obj.get_ppx(),
                        notename=ecf_obj.get_notename(),
                        remark=ecf_obj.get_remark(),
                        payto=ecf_obj.get_payto(),
                        raisedby=emp_id,
                        raiserbranch=emp_branch,
                        raisername=raisor_name,
                        branch=ecf_obj.get_branch(),
                        rmcode=ecf_obj.get_rmcode(),
                        client_code=ecf_obj.get_client_code(),
                        ap_status=ecf_obj.get_ap_status(),
                        updated_by=emp_id,
                        updated_date=now())

                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                                   from_user_id=emp_id,
                                                                   to_user_id=emp_id,
                                                                   created_date=now(),
                                                                   comments="New in Modification",
                                                                   remarks=ecf_obj.get_remark(),
                                                                   is_sys=True,
                                                                   entity_id=self._entity_id()
                                                                   )

                else:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                        supplier_type=ecf_obj.get_supplier_type(),
                        # supplierstate_id=ecf_obj.get_supplierstate_id(),
                        commodity_id=ecf_obj.get_commodity_id(),
                        ecftype=ecf_obj.get_ecftype(),
                        ecfdate=ecf_obj.get_ecfdate(),
                        ecfamount=ecf_obj.get_ecfamount(),
                        ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                        ppx=ecf_obj.get_ppx(),
                        notename=ecf_obj.get_notename(),
                        remark=ecf_obj.get_remark(),
                        payto=ecf_obj.get_payto(),
                        raisedby=emp_id,
                        raiserbranch=emp_branch,
                        raisername=raisor_name,
                        branch=ecf_obj.get_branch(),
                        rmcode=ecf_obj.get_rmcode(),
                        client_code=ecf_obj.get_client_code(),
                        ap_status=ecf_obj.get_ap_status(),
                        created_by=emp_id,
                        entity_id=self._entity_id())

                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                                   from_user_id=emp_id, to_user_id=emp_id,
                                                                   created_date=now(),
                                                                   comments="New in Modification",
                                                                   remarks=ecf_obj.get_remark(),
                                                                   is_sys=True,
                                                                   entity_id=self._entity_id()
                                                                   )

                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_supplier_type(Ecfhdr.supplier_type)
                # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
                ecf_data.set_commodity(Ecfhdr.commodity_id)
                ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
                ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_branchgst(emp_add1)
                # if ecf_obj.get_supplier_id() != '':
                #     ecf_data.set_gsttype(gsttype)
                #     ecf_data.set_supgstno(supgst)
                ecf_data.set_branchname(emp_bran)
                return ecf_data
        elif ecf_obj.get_ecftype() == Type.ADVANCE:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            print('emp2', emp)
            emp_branch = emp['employee_branch']
            raisor_name = emp['name']
            emp1 = api_serv.get_empbranch_id(request, emp_branch)
            emp_add1 = emp1['gstin']
            emp_bran = emp1['name']
            if (ecf_obj.get_commodity_id() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " CommodityField")
                return error_obj
            elif (ecf_obj.get_ecfdate() == ''):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.NULL_DATA)
                error_obj.set_description(ErrorDescription.NULL_DATA + " EcfDateField")
                return error_obj
            else:
                if not ecf_obj.get_id() is None:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                        supplier_type=ecf_obj.get_supplier_type(),
                        # supplierstate_id=ecf_obj.get_supplierstate_id(),
                        commodity_id=ecf_obj.get_commodity_id(),
                        ecftype=ecf_obj.get_ecftype(),
                        ecfdate=ecf_obj.get_ecfdate(),
                        ecfamount=ecf_obj.get_ecfamount(),
                        ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                        ppx=ecf_obj.get_ppx(),
                        notename=ecf_obj.get_notename(),
                        remark=ecf_obj.get_remark(),
                        payto=ecf_obj.get_payto(),
                        raisedby=emp_id,
                        raiserbranch=emp_branch,
                        raisername=raisor_name,
                        branch=ecf_obj.get_branch(),
                        rmcode=ecf_obj.get_rmcode(),
                        client_code=ecf_obj.get_client_code(),
                        ap_status=ecf_obj.get_ap_status(),
                        updated_by=emp_id,
                        updated_date=now())

                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                                   from_user_id=emp_id,
                                                                   to_user_id=emp_id,
                                                                   created_date=now(),
                                                                   comments="New in Modification",
                                                                   remarks=ecf_obj.get_remark(),
                                                                   is_sys=True,
                                                                   entity_id=self._entity_id()
                                                                   )

                else:
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                        supplier_type=ecf_obj.get_supplier_type(),
                        # supplierstate_id=ecf_obj.get_supplierstate_id(),
                        commodity_id=ecf_obj.get_commodity_id(),
                        ecftype=ecf_obj.get_ecftype(),
                        ecfdate=ecf_obj.get_ecfdate(),
                        ecfamount=ecf_obj.get_ecfamount(),
                        ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                        ppx=ecf_obj.get_ppx(),
                        notename=ecf_obj.get_notename(),
                        remark=ecf_obj.get_remark(),
                        payto=ecf_obj.get_payto(),
                        raisedby=emp_id,
                        raiserbranch=emp_branch,
                        raisername=raisor_name,
                        branch=ecf_obj.get_branch(),
                        rmcode=ecf_obj.get_rmcode(),
                        client_code=ecf_obj.get_client_code(),
                        ap_status=ecf_obj.get_ap_status(),
                        created_by=emp_id,
                        entity_id=self._entity_id())

                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                                   from_user_id=emp_id, to_user_id=emp_id,
                                                                   created_date=now(),
                                                                   comments="New in Modification",
                                                                   remarks=ecf_obj.get_remark(),
                                                                   is_sys=True,
                                                                   entity_id=self._entity_id()
                                                                   )

                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_supplier_type(Ecfhdr.supplier_type)
                # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
                ecf_data.set_commodity(Ecfhdr.commodity_id)
                ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
                ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                ecf_data.set_ap_status(Ecfhdr.ap_status)
                ecf_data.set_branchgst(emp_add1)
                # if ecf_obj.get_supplier_id() != '':
                #     ecf_data.set_gsttype(gsttype)
                #     ecf_data.set_supgstno(supgst)
                ecf_data.set_branchname(emp_bran)
                return ecf_data
    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == ECFModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = ECFAuditService(self._scope())
        audit_obj = ECFAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(ECFRefType.ECFHEADER)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.ECFHEADER)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def fetchone_invoice_pdf_list(self,request, inv_id, emp_id):

        Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
        inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=inv_id, entity_id=self._entity_id(),status=1).all()
        ecf_data = ECFHeaderresponse()

        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
        empcode = api_serv.get_empsingle_id(request, Ecfhdr.raisedby)
        raisercode = empcode['code']
        # ven_service = VendorAPI()
        emp = api_serv.get_empsingle_id(request, emp_id)
        emp_branch = emp['employee_branch']
        empbranch = api_serv.get_empbranch_id(request, emp_branch)
        employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
        ecf_data.set_id(Ecfhdr.id)
        ecf_data.set_crno(Ecfhdr.crno)
        ecf_data.set_commodity(commodity)

        # queuedetails for PDF
        ecf_data.queue_details = self.ecf_queuedetails(request, Ecfhdr.id)
        ecf_data.totalamount_in_words = num2words(float(Ecfhdr.ecfamount))
        #emp_designation_dept for PDF
        # token = get_authtoken_ecf()
        # url = SERVER_IP + '/usrserv/get_emp_designation_dept/' + str(Ecfhdr.raisedby)
        # logger.info("get_emp_designation_dept  url: " + str(url))
        # print("emp_designation_dept  url: " + str(url))
        # headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        # resp = requests.get(url, headers=headers, verify=False)
        # print('resp ', resp)
        # empdtls_resp = json.loads(resp.content)
        # ecf_data.raiser_emp_details = (empdtls_resp)
        #raiseremp_code  for PDF
        # ecf_data.raiseremp_code = (emp['code'])


        if Ecfhdr.ecftype == Type.PO:
            ecf_data.set_ecftype(Type.PO_Type)
        if Ecfhdr.ecftype == Type.NON_PO:
            ecf_data.set_ecftype(Type.NON_PO_Type)
        if Ecfhdr.ecftype == Type.ADVANCE:
            ecf_data.set_ecftype(Type.ADVANCE_Type)
        if Ecfhdr.ecftype == Type.ERA:
            ecf_data.set_ecftype(Type.ERA_Type)
        if Ecfhdr.ecftype == Type.TCF:
            ecf_data.set_ecftype(Type.TCF_Type)
        ecf_data.set_ecfdate(Ecfhdr.ecfdate)
        ecf_data.set_ecftype_id(Ecfhdr.ecftype)
        ecf_data.set_ecfamount(Ecfhdr.ecfamount)
        ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
        if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
            ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
            ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
            ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.REJECT:
            ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.DELETE:
            ecf_data.set_ecfstatus(ECFStatus.Delete)
        if Ecfhdr.ppx == PPX.EMPLOYEE:
            ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
        if Ecfhdr.ppx == PPX.SUPPLIER:
            ecf_data.set_ppx(PPX.SUPPLIER_PPX)
        ecf_data.set_ppx_id(Ecfhdr.ppx)
        ecf_data.set_notename(Ecfhdr.notename)
        ecf_data.set_remark(Ecfhdr.remark)
        if Ecfhdr.payto == Pay.EMPLOYEE:
            ecf_data.set_payto(Pay.EMPLOYEE_Pay)
        if Ecfhdr.payto == Pay.SUPPLIER:
            ecf_data.set_payto(Pay.SUPPLIER_Pay)
        if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
            ecf_data.set_payto(Pay.BRANCH_Pay)
        ecf_data.set_payto_id(Ecfhdr.payto)
        ecf_data.set_raisedby(Ecfhdr.raisedby)
        ecf_data.set_raiserbranch(employeebranch)
        ecf_data.set_raisername(Ecfhdr.raisername)
        ecf_data.set_ap_status(Ecfhdr.ap_status)
        ecf_data.set_raisercode(raisercode)
        emp_api = NWisefinUtilityService()
        branch = emp_api.get_employee_branch([Ecfhdr.branch])
        if len(branch) > 0:
            ecf_data.set_branch(branch)
        ecf_data.set_approvedby(Ecfhdr.approvedby)
        ecf_data.set_approvername(Ecfhdr.approvername)
        ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
        if Ecfhdr.supplier_type == SupplierType.SINGLE:
            ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
        if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
            ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
        ecfhdr_list = []
        # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

        # ecf = invhdr.ecfheader_id
        # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

        invhdr_list = []
        if len(inv_list) != 0:
            for inhdr in inv_list:
                invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                                  entity_id=self._entity_id(),status=1).all()
                invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                             entity_id=self._entity_id(),status=1).all()
                deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                           entity_id=self._entity_id(),status=1).all()
                bank_arr = []
                for i in credit_list:
                    bank_arr.append(i.creditbank_id)

                # bank_data = api_serv.get_bank_list(request, bank_arr)
                if  Ecfhdr.ecftype  not in [Type.TCF ,Type.ERA]:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp_bran = api_serv.get_empsingle_id(request, emp_id)
                    emp_bran1 = emp_bran['employee_branch']
                    emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    print('emp2', emp1)
                    emp_add1 = emp1['gstin']
                    emp_branch = emp1['name']
                    print('branch', emp_add1)
                    if inhdr.supplier_id != '':
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                        print("supp", supp)
                        supgst = supp['gstno']
                        if supgst[:2] != emp_add1[:2]:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(inhdr.id)
                inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                inhdr_data.set_invoiceno(inhdr.invoiceno)
                inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(inhdr.invoicedate)
                inhdr_data.set_suppliergst(inhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                inhdr_data.set_taxamount(inhdr.taxamount)
                inhdr_data.set_totalamount(inhdr.totalamount)
                inhdr_data.set_otheramount(inhdr.otheramount)
                inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                inhdr_data.set_inv_crno(inhdr.inv_crno)
                inhdr_data.set_invoicegst(inhdr.invoicegst)

                if inhdr.supplier_id != None:
                    inhdr_data.set_supplier(supp)
                    # inhdr_data.set_supplierstate(state)
                    inhdr_data.set_gsttype(gsttype)
                else:
                    inhdr_data.set_supplier("")
                    inhdr_data.set_supplierstate("")
                    inhdr_data.set_gsttype("")

                for invpo in invpo_list:
                    inpo_data = Invoiceporesponse()
                    inpo_data.set_id(invpo.id)
                    inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                    inpo_data.set_ponumber(invpo.ponumber)
                    inpo_data.set_grnnumber(invpo.grnnumber)
                    inpo_data.set_grndate(invpo.grndate)
                    inpo_data.set_poquantity(invpo.poquantity)
                    inpo_data.set_receivedqty(invpo.receivedqty)
                    inpo_data.set_balanceqty(invpo.balanceqty)
                    inpo_data.set_receiveddate(invpo.receiveddate)
                    inpo_data.set_product_code(invpo.product_code)
                    inpo_data.set_invoicedqty(invpo.invoicedqty)
                    inpo_data.set_invoiceqty(invpo.invoiceqty)
                    invhdr_list.append(json.loads(inpo_data.get()))
                    inhdr_data.set_invoicepo(invhdr_list)

                inv_list = []
                for invdtl in invdtl_list:
                    hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(hsn)
                    indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                    indtl_data.set_uom(invdtl.uom)
                    indtl_data.set_unitprice(invdtl.unitprice)
                    indtl_data.set_quantity(invdtl.quantity)
                    indtl_data.set_amount(invdtl.amount)
                    indtl_data.set_discount(invdtl.discount)
                    indtl_data.set_sgst(invdtl.sgst)
                    indtl_data.set_cgst(invdtl.cgst)
                    indtl_data.set_igst(invdtl.igst)
                    indtl_data.set_taxamount(invdtl.taxamount)
                    indtl_data.set_totalamount(invdtl.totalamount)
                    indtl_data.set_otheramount(invdtl.otheramount)
                    indtl_data.set_roundoffamt(invdtl.roundoffamt)
                    inv_list.append(json.loads(indtl_data.get()))
                    inhdr_data.set_invoicedtl(inv_list)

                    invdeb_list = []
                    for dbt in deb_list:
                        cat = api_serv.get_cat_code(request, dbt.category_code)
                        sub = api_serv.get_subcat_code(request, dbt.subcategory_code)
                        dbt_data = Debitresponse()
                        dbt_data.set_id(dbt.id)
                        dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                        dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                        dbt_data.set_category_code(cat)
                        dbt_data.set_subcategory_code(sub)
                        dbt_data.set_debitglno(dbt.debitglno)
                        dbt_data.set_amount(dbt.amount)
                        dbt_data.set_deductionamount(dbt.deductionamount)
                        ccbs_list = []
                        ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                        for ccbs in ccb_list:
                            cc = api_serv.get_cc_code(request, ccbs.cc_code)
                            bs = api_serv.get_bs_code(request, ccbs.bs_code)
                            ccbs_data = ccbsdtlresponse()
                            ccbs_data.set_id(ccbs.id)
                            ccbs_data.set_debit(ccbs.debit_id)
                            ccbs_data.set_cc_code(cc)
                            ccbs_data.set_bs_code(bs)
                            ccbs_data.set_code(ccbs.code)
                            ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                            ccbs_data.set_glno(ccbs.glno)
                            ccbs_data.set_amount(ccbs.amount)
                            ccbs_data.set_remarks(ccbs.remarks)
                            ccbs_list.append(json.loads(ccbs_data.get()))
                            dbt_data.set_ccbs(ccbs_data)
                            invdeb_list.append(json.loads(dbt_data.get()))
                            inhdr_data.set_debit(invdeb_list)

                crd_list = []
                for crd in credit_list:
                    cat = api_serv.get_cat_code(request, crd.category_code)
                    sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                    crd_data = Creditresponse()
                    crd_data.set_id(crd.id)
                    crd_data.set_invoiceheader(crd.invoiceheader_id)
                    pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                    crd_data.set_paymode(pay)
                    # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                    # crd_data.set_paydetails(bankdtl)
                    crd_data.set_category_code(cat)
                    crd_data.set_subcategory_code(sub)
                    bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                    crd_data.set_credit_bank(bank_data)
                    # crd_data.set_creditbank_id(crd.creditbank_id, bank_data['data'])
                    crd_data.set_suppliertax(crd.suppliertax_id)
                    crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                    crd_data.set_amount(crd.amount)
                    crd_data.set_creditglno(crd.creditglno)
                    if crd.paymode_id == 4:
                        from utilityservice.service.ap_api_service import APApiService
                        appservice = APApiService(self._scope())
                        app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, crd.creditrefno,
                                                                                            Ecfhdr.raisedby)
                        print("empappservice", app_service)
                        crd_data.set_creditrefno(app_service)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                        inhdr_data.set_credit(crd_list)
                    else:
                        crd_data.set_creditrefno(crd.creditrefno)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                        inhdr_data.set_credit(crd_list)
                ecfhdr_list.append(json.loads(inhdr_data.get()))
        ecf_data.set_Invheader(ecfhdr_list)
        return ecf_data



    def ecf_queuedetails(self,request,ecfhdr_id):
        from utilityservice.service import api_service

        ecf_que=ECFQueue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,entity_id=self._entity_id())
        array_list=list()
        stop_count=len(ecf_que)
        if len(ecf_que) > 0:
            for ecfque in ecf_que:
                if  stop_count > 2:
                    stop_count=stop_count-1
                    continue
                api_serv = api_service.ApiService(self._scope())
                ecfque_json=dict()
                ecfque_json['from_user'] = api_serv.get_empsingle_id(request,ecfque.from_user_id)
                ecfque_json['to_user'] = api_serv.get_empsingle_id(request,ecfque.to_user_id)

                if ecfque.comments == "PENDING  FOR APPROVAL" :
                    ecfque_json['status'] = "SUBMITTED"
                else:
                    ecfque_json['status'] = ecfque.comments
                ecfque_json['remarks'] = ecfque.remarks
                ecfque_json['created_date'] = str(ecfque.created_date.date())
                array_list.append(ecfque_json)
        return array_list

    def ecfccreate(self,request,ecf_obj,emp_id):
        from utilityservice.service import api_service
        raiser = ecf_obj.get_raisedby()
        appname = ecf_obj.get_approvedby()
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, raiser)
        print('emp2',emp)
        emp_branch = emp['employee_branch']
        raisor_name = emp['name']
        print("raisor_name",raisor_name)
        emp2 = api_serv.get_empsingle_id(request, appname)
        appr_name = emp2['name']
        print("appr_name",appr_name)
        emp1 = api_serv.get_empbranch_id(request, emp_branch)
        emp_add1 = emp1['gstin']
        emp_bran = emp1['name']
        if (ecf_obj.get_commodity_id() == ''):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.NULL_DATA)
            error_obj.set_description(ErrorDescription.NULL_DATA + " CommodityField")
            return error_obj
        elif (ecf_obj.get_ecfdate() == ''):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.NULL_DATA)
            error_obj.set_description(ErrorDescription.NULL_DATA + " EcfDateField")
            return error_obj
        else:
            if not ecf_obj.get_id() is None:
                print("1")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                                                                            supplier_type=ecf_obj.get_supplier_type(),
                                                                            # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                                            commodity_id=ecf_obj.get_commodity_id(),
                                                                            ecftype=ecf_obj.get_ecftype(),
                                                                            ecfdate=ecf_obj.get_ecfdate(),
                                                                            ecfamount=ecf_obj.get_ecfamount(),
                                                                            ecfstatus=ECFStatus.APPROVED,
                                                                            ppx=ecf_obj.get_ppx(),
                                                                            notename=ecf_obj.get_notename(),
                                                                            remark=ecf_obj.get_remark(),
                                                                            payto=ecf_obj.get_payto(),
                                                                            raisedby=ecf_obj.get_raisedby(),
                                                                            approvedby=ecf_obj.get_approvedby(),
                                                                            raiserbranch=emp_branch,
                                                                            raisername=raisor_name,
                                                                            approvername=appr_name,
                                                                            branch=ecf_obj.get_branch(),
                                                                            rmcode = ecf_obj.get_rmcode(),
                                                                            client_code = ecf_obj.get_client_code(),
                    ap_status=ecf_obj.get_ap_status(),
                                                                            updated_by=emp_id,
                                                                            updated_date=now())
                print("2")
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
                                        to_user_id=emp_id,
                                        created_date=now(),
                                        comments="APPROVED",
                                        remarks=ecf_obj.get_remark(),
                                        is_sys=True,
                                        entity_id=self._entity_id()
                                        )

            else:
                    print("3")
                    Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).create(
                                                        supplier_type=ecf_obj.get_supplier_type(),
                                                        # supplierstate_id=ecf_obj.get_supplierstate_id(),
                                                        commodity_id=ecf_obj.get_commodity_id(),
                                                        ecftype=ecf_obj.get_ecftype(),
                                                        ecfdate=ecf_obj.get_ecfdate(),
                                                        ecfamount=ecf_obj.get_ecfamount(),
                                                        ecfstatus=ECFStatus.APPROVED,
                                                        ppx=ecf_obj.get_ppx(),
                                                        notename=ecf_obj.get_notename(),
                                                        remark=ecf_obj.get_remark(),
                                                        payto=ecf_obj.get_payto(),
                                                        raisedby=ecf_obj.get_raisedby(),
                                                        approvedby=ecf_obj.get_approvedby(),
                                                        approvername=appr_name,
                                                        raiserbranch=emp_branch,
                                                        raisername=raisor_name,
                                                        branch=ecf_obj.get_branch(),
                                                        rmcode=ecf_obj.get_rmcode(),
                                                        client_code=ecf_obj.get_client_code(),
                        ap_status=ecf_obj.get_ap_status(),
                                                        created_by=emp_id,
                                                        entity_id=self._entity_id())

                    self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.ECFHEADER)
                    ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id, to_user_id=emp_id,
                                           created_date=now(),
                                           comments="APPROVED" ,
                                           remarks=ecf_obj.get_remark(),
                                           is_sys=True,
                                           entity_id=self._entity_id()
                                           )
            print("4")
            ecf_data = ECFHeaderresponse()
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_supplier_type(Ecfhdr.supplier_type)
            # ecf_data.set_supplierstate(Ecfhdr.supplierstate_id)
            ecf_data.set_commodity(Ecfhdr.commodity_id)
            ecf_data.set_ecftype(Ecfhdr.ecftype)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus(Ecfhdr.ecfstatus)
            ecf_data.set_ppx(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            ecf_data.set_payto(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_ap_status(Ecfhdr.ap_status)
            ecf_data.set_branchgst(emp_add1)
            # if ecf_obj.get_supplier_id() != '':
            #     ecf_data.set_gsttype(gsttype)
            #     ecf_data.set_supgstno(supgst)
            ecf_data.set_branchname(emp_bran)
            return ecf_data

    def ECFF_Submit(self, request, ecf_obj, ecf_id, emp_id):
        try:
            if ecf_obj.get_ecftype() == 1:
                code = "ECF"
            elif ecf_obj.get_ecftype() == 2:
                code = "NPO"
            elif ecf_obj.get_ecftype() == 3:
                code = "PPX"
            elif ecf_obj.get_ecftype() == 4:
                code = "ERA"
            elif ecf_obj.get_ecftype() == 5:
                code = "DTP"
            elif ecf_obj.get_ecftype() == 6:
                code = "RNT"
            elif ecf_obj.get_ecftype() == 7:
                code = "SGB"
            elif ecf_obj.get_ecftype() == 8:
                code = "TCF"
            crno = code + str(datetime.now().strftime("%Y%m%d")) + str(ecf_id).zfill(4)
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            emp = api_serv.get_empsingle_id(request, emp_id)
            appr_name = emp['name']
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_id,entity_id=self._entity_id())
            amt = ecf.ecfamount
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_id,entity_id=self._entity_id(), status=1).all()
            invheadertotal = float(0)
            sum = 0
            for inv_obj in inv_list:
                count = sum + 1
                sum += 1
                invheadertotal = invheadertotal + inv_obj.totalamount
                inv_crno = code + str(datetime.now().strftime("%y%m%d")) \
                           + str(ecf_id).zfill(4) + '_' + str(int(count))
                print()
                inv_lis = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                    ecfheader_id=ecf_obj.get_id(), entity_id=self._entity_id()).update(
                    inv_crno=inv_crno,
                    status=1)
            if (amt != invheadertotal):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVOICE_AMOUNT_MISMATCH)
                error_obj.set_description(ErrorDescription.INVOCIEHDR_AMOUNT_MISMATCH)
                return error_obj
            for inv_obj in inv_list:
                invtotal = inv_obj.totalamount
                invid = inv_obj.id
                invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,
                                                                                  entity_id=self._entity_id(),status=1).all()
                invdtltotal = float(0)
                for invdtl_obj in invdtl_list:
                    invdtltotal = invdtltotal + invdtl_obj.totalamount
                if (invtotal != invdtltotal):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVOICEDETAIL_AMOUNT_MISMATCH)
                    error_obj.set_description(ErrorDescription.INVOCIEDTL_AMOUNT_MISMATCH)
                    return error_obj
                for invdtl_obj in invdtl_list:
                    invdtltotal = invdtl_obj.totalamount
                    invdtlid = invdtl_obj.id
                    deb_list = Debit.objects.using(self._current_app_schema()).filter(invoicedetail_id=invdtlid,entity_id=self._entity_id(), status=1).all()
                    debittotal = float(0)
                    for deb_obj in deb_list:
                        debittotal = round(debittotal + deb_obj.amount,2)
                    if (invdtltotal != debittotal):
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.DEBIT_AMOUNT_MISMATCH)
                        error_obj.set_description(ErrorDescription.DEBIT_AMOUNT_MISMATCH)
                        return error_obj
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=invid,entity_id=self._entity_id(), status=1).all()
                credittotal = float(0)
                for crd_obj in credit_list:
                    credittotal = credittotal + crd_obj.amount
                if (invtotal != credittotal):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.CREDIT_AMOUNT_MISMATCH)
                    error_obj.set_description(ErrorDescription.CREDIT_AMOUNT_MISMATCH)
                    return error_obj
            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=ecf_id,entity_id=self._entity_id()).update(
                # approvedby=ecf_obj.get_approvedby(),
                # approvername=appr_name,
                crno=crno,
                ecftype=ecf_obj.get_ecftype(),
                ecfstatus=ECFStatus.APPROVED,
                updated_by=emp_id,
                updated_date=now())

            # Ecfhdr = ECFHeader.objects.get(id=ecf_obj.get_id())
            # self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
            #                     ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
            # ECFQueue.objects.create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER, from_user_id=emp_id,
            #                         to_user_id=ecf_obj.get_approvedby(),
            #                         created_date=now(),
            #                         comments="PENDING  FOR APPROVAL",
            #                         remarks=ecf_obj.get_remark(),
            #                         is_sys=True
            #                         )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.crno=crno
            success_obj.ecf_id=ecf_id
            # success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
            return success_obj
        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def fetch_ecf(self,request, inv_id, emp_id):
        try:
            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=inv_id ,entity_id=self._entity_id(), status = 1).all()
            ecf_data = ECFHeaderresponse()

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
            # ven_service = VendorAPI()
            emp = api_serv.get_empsingle_id(request, emp_id)
            emp_branch = emp['employee_branch']
            empbranch = api_serv.get_empbranch_id(request, emp_branch)
            employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
            branch_co = api_serv.get_empbranch_id(request, Ecfhdr.branch)
            # disp_name = branch_co['code'] + '--' + branch_co['name']
            print("branch", branch_co)
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_commodity(commodity)
            if Ecfhdr.ecftype == Type.PO:
                ecf_data.set_ecftype(Type.PO_Type)
            if Ecfhdr.ecftype == Type.NON_PO:
                ecf_data.set_ecftype(Type.NON_PO_Type)
            if Ecfhdr.ecftype == Type.ADVANCE:
                ecf_data.set_ecftype(Type.ADVANCE_Type)
            if Ecfhdr.ecftype == Type.ERA:
                ecf_data.set_ecftype(Type.ERA_Type)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecftype_id(Ecfhdr.ecftype)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
            if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                ecf_data.set_ecfstatus(ECFStatus.Delete)
            if Ecfhdr.ppx == PPX.EMPLOYEE:
                ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
            if Ecfhdr.ppx == PPX.SUPPLIER:
                ecf_data.set_ppx(PPX.SUPPLIER_PPX)
            ecf_data.set_ppx_id(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            if Ecfhdr.payto == Pay.EMPLOYEE:
                ecf_data.set_payto(Pay.EMPLOYEE_Pay)
            if Ecfhdr.payto == Pay.SUPPLIER:
                ecf_data.set_payto(Pay.SUPPLIER_Pay)
            if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                ecf_data.set_payto(Pay.BRANCH_Pay)
            ecf_data.set_payto_id(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(employeebranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            ecf_data.set_approvedby(Ecfhdr.approvedby)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_ap_status(Ecfhdr.ap_status)
            ecf_data.set_branch(branch_co)
            ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
            if Ecfhdr.supplier_type == SupplierType.SINGLE:
                ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
            if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
            ecfhdr_list = []
            # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            # ecf = invhdr.ecfheader_id
            # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            invhdr_list = []
            if len(inv_list)!=0:
                for inhdr in inv_list:
                    invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    bank_arr = []
                    for i in credit_list:
                        bank_arr.append(i.creditbank_id)
                    # state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                    # supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    bank_data = api_serv.get_bank_list(request, bank_arr)
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    print('emp2', emp)
                    emp_add = emp['address_id']
                    empadd = api_serv.get_empaddress_id(request, emp_add)

                    gst = empadd['state_id']
                    # if inhdr.supplier_id != '':
                    #     supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    #     suppadd = supp['address_id']
                    #     ven = api_serv.get_venaddress(request, suppadd)
                    #     supgst = ven['state_id']
                    #     if supgst != gst:
                    #         gsttype = 'IGST'
                    #     else:
                    #         gsttype = 'SGST & CGST'

                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                    inhdr_data.set_invoiceno(inhdr.invoiceno)
                    inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                    inhdr_data.set_invoicedate(inhdr.invoicedate)
                    inhdr_data.set_suppliergst(inhdr.suppliergst)
                    inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                    inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                    inhdr_data.set_taxamount(inhdr.taxamount)
                    inhdr_data.set_totalamount(inhdr.totalamount)
                    inhdr_data.set_otheramount(inhdr.otheramount)
                    inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                    # inhdr_data.set_supplier(supp)
                    inhdr_data.set_invoicegst(inhdr.invoicegst)
                    # inhdr_data.set_supplierstate(state)
                    # if inhdr.supplier_id != '':
                    #     inhdr_data.set_gsttype(gsttype)

                    for invpo in invpo_list:
                        inpo_data = Invoiceporesponse()
                        inpo_data.set_id(invpo.id)
                        inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                        inpo_data.set_ponumber(invpo.ponumber)
                        inpo_data.set_grnnumber(invpo.grnnumber)
                        inpo_data.set_grndate(invpo.grndate)
                        inpo_data.set_poquantity(invpo.poquantity)
                        inpo_data.set_receivedqty(invpo.receivedqty)
                        inpo_data.set_balanceqty(invpo.balanceqty)
                        inpo_data.set_receiveddate(invpo.receiveddate)
                        inpo_data.set_product_code(invpo.product_code)
                        inpo_data.set_invoicedqty(invpo.invoicedqty)
                        inpo_data.set_invoiceqty(invpo.invoiceqty)
                        invhdr_list.append(json.loads(inpo_data.get()))
                        inhdr_data.set_invoicepo(invhdr_list)

                    inv_list = []
                    for invdtl in invdtl_list:
                        hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                        indtl_data = Invoicedetailresponse()
                        indtl_data.set_id(invdtl.id)
                        indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                        indtl_data.set_invoice_po(invdtl.invoice_po)
                        indtl_data.set_productcode(invdtl.productcode)
                        indtl_data.set_productname(invdtl.productname)
                        indtl_data.set_description(invdtl.description)
                        indtl_data.set_hsn(hsn)
                        indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                        indtl_data.set_uom(invdtl.uom)
                        indtl_data.set_unitprice(invdtl.unitprice)
                        indtl_data.set_quantity(invdtl.quantity)
                        indtl_data.set_amount(invdtl.amount)
                        indtl_data.set_discount(invdtl.discount)
                        indtl_data.set_sgst(invdtl.sgst)
                        indtl_data.set_cgst(invdtl.cgst)
                        indtl_data.set_igst(invdtl.igst)
                        indtl_data.set_taxamount(invdtl.taxamount)
                        indtl_data.set_totalamount(invdtl.totalamount)
                        indtl_data.set_otheramount(invdtl.otheramount)
                        indtl_data.set_roundoffamt(invdtl.roundoffamt)
                        inv_list.append(json.loads(indtl_data.get()))
                        inhdr_data.set_invoicedtl(inv_list)

                        invdeb_list = []
                        for dbt in deb_list:
                            cat = api_serv.get_cat_code(request,dbt.category_code)
                            sub = api_serv.get_subcat_code(request,dbt.subcategory_code)
                            dbt_data = Debitresponse()
                            dbt_data.set_id(dbt.id)
                            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                            dbt_data.set_category_code(cat)
                            dbt_data.set_subcategory_code(sub)
                            dbt_data.set_debitglno(dbt.debitglno)
                            dbt_data.set_amount(dbt.amount)
                            dbt_data.set_deductionamount(dbt.deductionamount)
                            ccbs_list=[]
                            ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                            for ccbs in ccb_list:
                                cc = api_serv.get_cc_code(request,ccbs.cc_code)
                                bs = api_serv.get_bs_code(request,ccbs.bs_code)
                                ccbs_data = ccbsdtlresponse()
                                ccbs_data.set_id(ccbs.id)
                                ccbs_data.set_debit(ccbs.debit_id)
                                ccbs_data.set_cc_code(cc)
                                ccbs_data.set_bs_code(bs)
                                ccbs_data.set_code(ccbs.code)
                                ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                                ccbs_data.set_glno(ccbs.glno)
                                ccbs_data.set_amount(ccbs.amount)
                                ccbs_data.set_remarks(ccbs.remarks)
                                ccbs_list.append(json.loads(ccbs_data.get()))
                                dbt_data.set_ccbs(ccbs_data)
                                invdeb_list.append(json.loads(dbt_data.get()))
                                inhdr_data.set_debit(invdeb_list)

                    crd_list = []
                    for crd in credit_list:
                        cat = api_serv.get_cat_code(request, crd.category_code)
                        sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                        crd_data = Creditresponse()
                        crd_data.set_id(crd.id)
                        crd_data.set_invoiceheader(crd.invoiceheader_id)
                        pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                        crd_data.set_paymode(pay)
                        # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                        # crd_data.set_paydetails(bankdtl)
                        crd_data.set_category_code(cat)
                        crd_data.set_subcategory_code(sub)
                        crd_data.set_creditbank_id(crd.creditbank_id,bank_data['data'])
                        crd_data.set_suppliertax(crd.suppliertax_id)
                        crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                        crd_data.set_amount(crd.amount)
                        crd_data.set_creditglno(crd.creditglno)
                        crd_data.set_creditrefno(crd.creditrefno)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                    inhdr_data.set_credit(crd_list)
                    ecfhdr_list.append(json.loads(inhdr_data.get()))
            ecf_data.set_Invheader(ecfhdr_list)
            return ecf_data
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(excep))
            return error_obj
    def fetch_ecfno(self,request, inv_no, emp_id):
        try:
            condition = Q(ecfstatus=3) & Q(crno=inv_no)
            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(condition)
            ecf_id  = Ecfhdr.id
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_id ,entity_id=self._entity_id(), status = 1).all()
            ecf_data = ECFHeaderresponse()
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
            # ven_service = VendorAPI()
            emp = api_serv.get_empsingle_id(request, emp_id)
            emp_branch = emp['employee_branch']
            try:
                bnch_name = Ecfhdr.approvedby
                emp = api_serv.get_empsingle_id(request, bnch_name)
            except:
                bnch_name = None
            print("bnch_name", bnch_name)
            emp_branch = emp['employee_branch']

            emp_name = emp['name']
            print("emp_name", emp_name)
            empbranch = api_serv.get_empbranch_id(request, emp_branch)
            appbranch_name = empbranch['name']
            try:
                emp_branch1 = Ecfhdr.approver_branch
                empbranch1 = api_serv.get_empbranch_id(request, emp_branch1)
            except:
                empbranch1 = None
            # appbrnh_name = empbranch1['name']
            print("empbranch", empbranch['name'])
            employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
            branch_co = api_serv.get_empbranch_id(request, Ecfhdr.branch)
            # disp_name = branch_co['code'] + '--' + branch_co['name']
            print("branch", branch_co)
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_commodity(commodity)
            if Ecfhdr.ecftype == Type.PO:
                ecf_data.set_ecftype(Type.PO_Type)
            if Ecfhdr.ecftype == Type.NON_PO:
                ecf_data.set_ecftype(Type.NON_PO_Type)
            if Ecfhdr.ecftype == Type.ADVANCE:
                ecf_data.set_ecftype(Type.ADVANCE_Type)
            if Ecfhdr.ecftype == Type.ERA:
                ecf_data.set_ecftype(Type.ERA_Type)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecftype_id(Ecfhdr.ecftype)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
            if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                ecf_data.set_ecfstatus(ECFStatus.Delete)
            if Ecfhdr.ppx == PPX.EMPLOYEE:
                ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
            if Ecfhdr.ppx == PPX.SUPPLIER:
                ecf_data.set_ppx(PPX.SUPPLIER_PPX)
            # ecf_data.set_ppx_id(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            if Ecfhdr.payto == Pay.EMPLOYEE:
                ecf_data.set_payto(Pay.EMPLOYEE_Pay)
            if Ecfhdr.payto == Pay.SUPPLIER:
                ecf_data.set_payto(Pay.SUPPLIER_Pay)
            if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                ecf_data.set_payto(Pay.BRANCH_Pay)
            # ecf_data.set_payto_id(Ecfhdr.payto)
            ecf_data.set_payto_id(get_Pay(Ecfhdr.payto))
            ecf_data.set_ppx_id(get_Ppx(Ecfhdr.ppx))
            # emp_api = NWisefinUtilityService()
            # branch = api_serv.get_branch_data([Ecfhdr.branch],request)
            # if len(branch) > 0:
            ecf_data.set_branch(branch_co)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(employeebranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            if Ecfhdr.tds == TDS.NA:
                ecf_data.set_tds(TDS.NA_TDS)
            elif Ecfhdr.tds == TDS.YES:
                ecf_data.set_tds(TDS.YES_TDS)
            elif Ecfhdr.tds == TDS.NOT_KNOWN:
                ecf_data.set_tds(TDS.NOT_KNOWN_TDS)
            ecf_data.set_data({"approvedby": bnch_name, "approvername": emp, "approverbranch": empbranch,
                               "tds": (get_tds(Ecfhdr.tds)), "approver_branch": empbranch1})
            ecf_data.set_approvedby(bnch_name)
            ecf_data.set_approvername(emp_name)
            ecf_data.set_approverbranch(appbranch_name)
            ecf_data.set_branch(branch_co)
            ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
            if Ecfhdr.supplier_type == SupplierType.SINGLE:
                ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
            if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
            ecf_data.set_rmcode(api_serv.get_empsingle_id(request, Ecfhdr.rmcode))
            ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
            ecfhdr_list = []
            # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            # ecf = invhdr.ecfheader_id
            # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            invhdr_list = []
            if len(inv_list)!=0:
                for inhdr in inv_list:
                    invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    file_list = ECFFiles.objects.using(self._current_app_schema()).filter(ecffile_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                    bank_arr = []
                    for i in credit_list:
                        bank_arr.append(i.creditbank_id)
                    try:
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    except:
                        state = None
                        supp = None
                    bank_data = api_serv.get_bank_list(request, bank_arr)
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    print('emp2', emp)
                    emp_add = emp['address_id']
                    empadd = api_serv.get_empaddress_id(request, emp_add)

                    gst = empadd['state_id']
                    if inhdr.supplier_id != '':
                        try:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            suppadd = supp['address_id']
                            ven = api_serv.get_venaddress(request, suppadd)
                            supgst = ven['state_id']
                        except:
                            supp = None
                            supgst = None
                        if supgst != gst:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'

                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                    inhdr_data.set_inv_crno(inhdr.inv_crno)
                    inhdr_data.set_invoiceno(inhdr.invoiceno)
                    inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                    inhdr_data.set_invoicedate(inhdr.invoicedate)
                    inhdr_data.set_suppliergst(inhdr.suppliergst)
                    inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                    inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                    inhdr_data.set_taxamount(inhdr.taxamount)
                    inhdr_data.set_totalamount(inhdr.totalamount)
                    inhdr_data.set_otheramount(inhdr.otheramount)
                    inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                    inhdr_data.set_supplier(supp)
                    inhdr_data.set_invoicegst(inhdr.invoicegst)
                    inhdr_data.set_supplierstate(state)
                    if inhdr.supplier_id != '':
                        inhdr_data.set_gsttype(gsttype)

                    for invpo in invpo_list:
                        inpo_data = Invoiceporesponse()
                        inpo_data.set_id(invpo.id)
                        inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                        inpo_data.set_ponumber(invpo.ponumber)
                        inpo_data.set_grnnumber(invpo.grnnumber)
                        inpo_data.set_grndate(invpo.grndate)
                        inpo_data.set_poquantity(invpo.poquantity)
                        inpo_data.set_receivedqty(invpo.receivedqty)
                        inpo_data.set_balanceqty(invpo.balanceqty)
                        inpo_data.set_receiveddate(invpo.receiveddate)
                        inpo_data.set_product_code(invpo.product_code)
                        inpo_data.set_invoicedqty(invpo.invoicedqty)
                        inpo_data.set_invoiceqty(invpo.invoiceqty)
                        invhdr_list.append(json.loads(inpo_data.get()))
                        inhdr_data.set_invoicepo(invhdr_list)

                    inv_list = []
                    for invdtl in invdtl_list:
                        hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                        indtl_data = Invoicedetailresponse()
                        indtl_data.set_id(invdtl.id)
                        indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                        indtl_data.set_invoice_po(invdtl.invoice_po)
                        indtl_data.set_productcode(invdtl.productcode)
                        indtl_data.set_productname(invdtl.productname)
                        indtl_data.set_description(invdtl.description)
                        indtl_data.set_hsn(hsn)
                        indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                        indtl_data.set_uom(invdtl.uom)
                        indtl_data.set_unitprice(invdtl.unitprice)
                        indtl_data.set_quantity(invdtl.quantity)
                        indtl_data.set_amount(invdtl.amount)
                        indtl_data.set_discount(invdtl.discount)
                        indtl_data.set_sgst(invdtl.sgst)
                        indtl_data.set_cgst(invdtl.cgst)
                        indtl_data.set_igst(invdtl.igst)
                        indtl_data.set_taxamount(invdtl.taxamount)
                        indtl_data.set_totalamount(invdtl.totalamount)
                        indtl_data.set_otheramount(invdtl.otheramount)
                        indtl_data.set_roundoffamt(invdtl.roundoffamt)
                        inv_list.append(json.loads(indtl_data.get()))
                        inhdr_data.set_invoicedtl(inv_list)

                    invdeb_list = []
                    for dbt in deb_list:
                        cat = api_serv.get_cat_code(request,dbt.category_code)
                        sub = api_serv.get_subcat_code(request,dbt.subcategory_code)
                        dbt_data = Debitresponse()
                        dbt_data.set_id(dbt.id)
                        dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                        dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                        dbt_data.set_category_code(cat)
                        dbt_data.set_subcategory_code(sub)
                        dbt_data.set_debitglno(dbt.debitglno)
                        dbt_data.set_amount(dbt.amount)
                        dbt_data.set_deductionamount(dbt.deductionamount)
                        dbt_data.set_bsproduct(api_serv.get_bscode(dbt.bsproduct))
                        ccbs_list=[]
                        ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                        for ccbs in ccb_list:
                            cc = api_serv.get_cc_code(request,ccbs.cc_code)
                            bs = api_serv.get_bs_code(request,ccbs.bs_code)
                            ccbs_data = ccbsdtlresponse()
                            ccbs_data.set_id(ccbs.id)
                            ccbs_data.set_debit(ccbs.debit_id)
                            ccbs_data.set_cc_code(cc)
                            ccbs_data.set_bs_code(bs)
                            ccbs_data.set_code(ccbs.code)
                            ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                            ccbs_data.set_glno(ccbs.glno)
                            ccbs_data.set_amount(ccbs.amount)
                            ccbs_data.set_remarks(ccbs.remarks)
                            ccbs_list.append(json.loads(ccbs_data.get()))
                            dbt_data.set_ccbs(ccbs_data)
                            invdeb_list.append(json.loads(dbt_data.get()))
                            inhdr_data.set_debit(invdeb_list)

                    crd_list = []
                    for crd in credit_list:
                        cat = api_serv.get_cat_code(request, crd.category_code)
                        sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                        crd_data = Creditresponse()
                        crd_data.set_id(crd.id)
                        crd_data.set_invoiceheader(crd.invoiceheader_id)
                        pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                        crd_data.set_paymode(pay)
                        # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                        # crd_data.set_paydetails(bankdtl)
                        crd_data.set_category_code(cat)
                        crd_data.set_subcategory_code(sub)
                        bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                        # crd_data.set_credit_bank(bank_data)
                        # crd_data.set_creditbank_id(crd.creditbank_id,bank_data['data'])
                        crd_data.creditbank_id = ({"id":crd.creditbank_id})
                        crd_data.set_suppliertax(crd.suppliertax_id)
                        crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                        crd_data.set_amount(crd.amount)
                        crd_data.set_creditglno(crd.creditglno)
                        crd_data.set_creditrefno(crd.creditrefno)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                        inhdr_data.set_credit(crd_list)
                    filelist = []
                    for fl in file_list:
                        list_lent = len(file_list)
                        if list_lent > 0:
                            dtpc_res = ecffileResponse()
                            dtpc_res.set_id(fl.id)
                            dtpc_res.set_file_id(fl.file_id)
                            dtpc_res.set_file_name(fl.file_name)
                        filelist.append(dtpc_res)
                        inhdr_data.set_file_data(filelist)
                    ecfhdr_list.append(json.loads(inhdr_data.get()))
            ecf_data.set_Invheader(ecfhdr_list)
            return ecf_data
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(excep))
            return error_obj


    def fetchone_invoiceadv_pdf_list(self,request, inv_id, emp_id):

        Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
        inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=inv_id,entity_id=self._entity_id(), status=1).all()
        ecf_data = ECFHeaderresponse()

        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
        # ven_service = VendorAPI()
        emp = api_serv.get_empsingle_id(request, emp_id)
        emp_branch = emp['employee_branch']
        empbranch = api_serv.get_empbranch_id(request, emp_branch)
        employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
        ecf_data.set_id(Ecfhdr.id)
        ecf_data.set_crno(Ecfhdr.crno)
        ecf_data.set_commodity(commodity)

        # queuedetails for PDF
        ecf_data.queue_details = self.ecf_queuedetails(request, Ecfhdr.id)
        ecf_data.totalamount_in_words = num2words(float(Ecfhdr.ecfamount))
        #emp_designation_dept for PDF
        # token = get_authtoken_ecf()
        # url = SERVER_IP + '/usrserv/get_emp_designation_dept/' + str(Ecfhdr.raisedby)
        # logger.info("get_emp_designation_dept  url: " + str(url))
        # print("emp_designation_dept  url: " + str(url))
        # headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        # resp = requests.get(url, headers=headers, verify=False)
        # print('resp ', resp)

        # empdtls_resp = json.loads(resp.content)
        # ecf_data.raiser_emp_details = (empdtls_resp)
        #raiseremp_code  for PDF
        ecf_data.raiseremp_code = (emp['code'])


        if Ecfhdr.ecftype == Type.PO:
            ecf_data.set_ecftype(Type.PO_Type)
        if Ecfhdr.ecftype == Type.NON_PO:
            ecf_data.set_ecftype(Type.NON_PO_Type)
        if Ecfhdr.ecftype == Type.ADVANCE:
            ecf_data.set_ecftype(Type.ADVANCE_Type)
        if Ecfhdr.ecftype == Type.ERA:
            ecf_data.set_ecftype(Type.ERA_Type)
        ecf_data.set_ecfdate(Ecfhdr.ecfdate)
        ecf_data.set_ecftype_id(Ecfhdr.ecftype)
        ecf_data.set_ecfamount(Ecfhdr.ecfamount)
        ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
        if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
            ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
            ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
            ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.REJECT:
            ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
        if Ecfhdr.ecfstatus == ECFStatus.DELETE:
            ecf_data.set_ecfstatus(ECFStatus.Delete)
        if Ecfhdr.ppx == PPX.EMPLOYEE:
            ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
        if Ecfhdr.ppx == PPX.SUPPLIER:
            ecf_data.set_ppx(PPX.SUPPLIER_PPX)
        ecf_data.set_ppx_id(Ecfhdr.ppx)
        ecf_data.set_notename(Ecfhdr.notename)
        ecf_data.set_remark(Ecfhdr.remark)
        if Ecfhdr.payto == Pay.EMPLOYEE:
            ecf_data.set_payto(Pay.EMPLOYEE_Pay)
        if Ecfhdr.payto == Pay.SUPPLIER:
            ecf_data.set_payto(Pay.SUPPLIER_Pay)
        if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
            ecf_data.set_payto(Pay.BRANCH_Pay)
        ecf_data.set_payto_id(Ecfhdr.payto)
        ecf_data.set_raisedby(Ecfhdr.raisedby)
        ecf_data.set_raiserbranch(employeebranch)
        ecf_data.set_raisername(Ecfhdr.raisername)
        ecf_data.set_approvedby(Ecfhdr.approvedby)
        ecf_data.set_approvername(Ecfhdr.approvername)
        ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
        if Ecfhdr.supplier_type == SupplierType.SINGLE:
            ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
        if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
            ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
        ecfhdr_list = []
        # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

        # ecf = invhdr.ecfheader_id
        # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

        invhdr_list = []
        if len(inv_list) != 0:
            for inhdr in inv_list:

                deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,
                                                                           entity_id=self._entity_id(),status=1).all()
                bank_arr = []
                for i in credit_list:
                    bank_arr.append(i.creditbank_id)

                bank_data = api_serv.get_bank_list(request, bank_arr)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp = api_serv.get_empsingle_id(request, emp_id)
                print('emp2', emp)
                emp_add = emp['address_id']
                empadd = api_serv.get_empaddress_id(request, emp_add)

                gst = empadd['state_id']
                if inhdr.supplier_id != None:
                    state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                    supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    suppadd = supp['address_id']
                    ven = api_serv.get_venaddress(request, suppadd)
                    supgst = ven['state_id']
                    if supgst != gst:
                        gsttype = 'IGST'
                    else:
                        gsttype = 'SGST & CGST'

                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(inhdr.id)
                inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                inhdr_data.set_invoiceno(inhdr.invoiceno)
                inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(inhdr.invoicedate)
                inhdr_data.set_suppliergst(inhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                inhdr_data.set_taxamount(inhdr.taxamount)
                inhdr_data.set_totalamount(inhdr.totalamount)
                inhdr_data.set_otheramount(inhdr.otheramount)
                inhdr_data.set_roundoffamt(inhdr.roundoffamt)

                inhdr_data.set_invoicegst(inhdr.invoicegst)

                if inhdr.supplier_id != None:
                    inhdr_data.set_supplier(supp)
                    inhdr_data.set_supplierstate(state)
                    inhdr_data.set_gsttype(gsttype)
                else:
                    inhdr_data.set_supplier("")
                    inhdr_data.set_supplierstate("")
                    inhdr_data.set_gsttype("")




                invdeb_list = []
                for dbt in deb_list:
                    cat = api_serv.get_cat_code(request, dbt.category_code)
                    sub = api_serv.get_subcat_code(request, dbt.subcategory_code)
                    dbt_data = Debitresponse()
                    dbt_data.set_id(dbt.id)
                    dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                    dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                    dbt_data.set_category_code(cat)
                    dbt_data.set_subcategory_code(sub)
                    dbt_data.set_debitglno(dbt.debitglno)
                    dbt_data.set_amount(dbt.amount)
                    dbt_data.set_deductionamount(dbt.deductionamount)
                    ccbs_list = []
                    ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                    for ccbs in ccb_list:
                        cc = api_serv.get_cc_code(request, ccbs.cc_code)
                        bs = api_serv.get_bs_code(request, ccbs.bs_code)
                        ccbs_data = ccbsdtlresponse()
                        ccbs_data.set_id(ccbs.id)
                        ccbs_data.set_debit(ccbs.debit_id)
                        ccbs_data.set_cc_code(cc)
                        ccbs_data.set_bs_code(bs)
                        ccbs_data.set_code(ccbs.code)
                        ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                        ccbs_data.set_glno(ccbs.glno)
                        ccbs_data.set_amount(ccbs.amount)
                        ccbs_data.set_remarks(ccbs.remarks)
                        ccbs_list.append(json.loads(ccbs_data.get()))
                        dbt_data.set_ccbs(ccbs_data)
                        invdeb_list.append(json.loads(dbt_data.get()))
                        inhdr_data.set_debit(invdeb_list)

                crd_list = []
                for crd in credit_list:
                    cat = api_serv.get_cat_code(request, crd.category_code)
                    sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                    crd_data = Creditresponse()
                    crd_data.set_id(crd.id)
                    crd_data.set_invoiceheader(crd.invoiceheader_id)
                    pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                    crd_data.set_paymode(pay)
                    # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                    # crd_data.set_paydetails(bankdtl)
                    crd_data.set_category_code(cat)
                    crd_data.set_subcategory_code(sub)
                    crd_data.set_creditbank_id(crd.creditbank_id, bank_data['data'])
                    crd_data.set_suppliertax(crd.suppliertax_id)
                    crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                    crd_data.set_amount(crd.amount)
                    crd_data.set_creditglno(crd.creditglno)
                    bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                    crd_data.set_credit_bank(bank_data)
                    if crd.paymode_id == 4:
                        from utilityservice.service.ap_api_service import APApiService
                        appservice = APApiService(self._scope())
                        app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request, crd.creditrefno,
                                                                                            Ecfhdr.raisedby)
                        print("empappservice", app_service)
                        crd_data.set_creditrefno(app_service)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                        inhdr_data.set_credit(crd_list)
                    else:
                        crd_data.set_creditrefno(crd.creditrefno)
                        crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                        crd_data.set_taxexcempted(crd.taxexcempted)
                        crd_data.set_taxableamount(crd.taxableamount)
                        crd_data.set_ddtranbranch(crd.ddtranbranch)
                        crd_data.set_ddpaybranch(crd.ddpaybranch)
                        crd_list.append(json.loads(crd_data.get()))
                        inhdr_data.set_credit(crd_list)

                    #credit bank details for PDF
                    # token = get_authtoken_ecf()
                    # token_name = request.headers['Authorization']
                    # url = SERVER_IP + '/mstserv/bankbranch_search?bank_id=' + str(crd.creditbank_id)
                    # logger.info("get_emp_designation_dept  url: " + str(url))
                    # print("bankbranch  url: " + str(url))
                    # headers = {"content-type": "application/json", "Authorization": "" + token_name + ""}
                    # bankbranch_resp = requests.get(url, headers=headers, verify=False)
                    # print(bankbranch_resp.status_code, crd.creditbank_id)
                    # bankbranch_json = json.loads(bankbranch_resp.content)
                    # print('bankbranch_json', bankbranch_json)
                    # # bank details for PDF
                    # if 'name' in pay and pay['name'] == "NEFT":
                    #     crd_data.set_creditbank_id(crd.creditbank_id, bank_data['data'])
                    #     crd_data.bankbranch = (bankbranch_json['data'])[0]
                    # else:
                    #     crd_data.creditbank_id = None
                    #     crd_data.bankbranch = None
                    # #account_no for PDF
                    # if crd.creditglno == 0:
                    #     crd_data.account_no = (crd.creditrefno)
                    # else:
                    #     crd_data.account_no = (crd.creditglno)
                ecfhdr_list.append(json.loads(inhdr_data.get()))
        ecf_data.set_Invheader(ecfhdr_list)
        return ecf_data


    def Delete_ecffiles(self,request, file_id, emp_id):
        try:
            Ecfhdr = ECFFiles.objects.using(self._current_app_schema()).filter(file_id=file_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            ecf = ECFFiles.objects.using(self._current_app_schema()).get(file_id=file_id)
            self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.ECFFILES)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=ECFRefType.ECFFILES, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,
                                    entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def fetch_ecfnoo(self,request, inv_no, emp_id):
        try:

            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(crno=inv_no,entity_id=self._entity_id())
            ecf_id  = Ecfhdr.id
            inv_list = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=ecf_id ,entity_id=self._entity_id(), status = 1).all()
            ecf_data = ECFHeaderresponse()

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            commodity = api_serv.get_commosingle_id(request, Ecfhdr.commodity_id)
            # ven_service = VendorAPI()
            emp = api_serv.get_empsingle_id(request, emp_id)
            emp_branch = emp['employee_branch']
            empbranch = api_serv.get_empbranch_id(request, emp_branch)
            employeebranch = api_serv.get_empbranch_id(request, Ecfhdr.raiserbranch)
            ecf_data.set_id(Ecfhdr.id)
            ecf_data.set_crno(Ecfhdr.crno)
            ecf_data.set_commodity(commodity)
            if Ecfhdr.ecftype == Type.PO:
                ecf_data.set_ecftype(Type.PO_Type)
            if Ecfhdr.ecftype == Type.NON_PO:
                ecf_data.set_ecftype(Type.NON_PO_Type)
            if Ecfhdr.ecftype == Type.ADVANCE:
                ecf_data.set_ecftype(Type.ADVANCE_Type)
            if Ecfhdr.ecftype == Type.ERA:
                ecf_data.set_ecftype(Type.ERA_Type)
            ecf_data.set_ecfdate(Ecfhdr.ecfdate)
            ecf_data.set_ecftype_id(Ecfhdr.ecftype)
            ecf_data.set_ecfamount(Ecfhdr.ecfamount)
            ecf_data.set_ecfstatus_id(Ecfhdr.ecfstatus)
            if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
            if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                ecf_data.set_ecfstatus(ECFStatus.Delete)
            if Ecfhdr.ppx == PPX.EMPLOYEE:
                ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
            if Ecfhdr.ppx == PPX.SUPPLIER:
                ecf_data.set_ppx(PPX.SUPPLIER_PPX)
            ecf_data.set_ppx_id(Ecfhdr.ppx)
            ecf_data.set_notename(Ecfhdr.notename)
            ecf_data.set_remark(Ecfhdr.remark)
            if Ecfhdr.payto == Pay.EMPLOYEE:
                ecf_data.set_payto(Pay.EMPLOYEE_Pay)
            if Ecfhdr.payto == Pay.SUPPLIER:
                ecf_data.set_payto(Pay.SUPPLIER_Pay)
            if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                ecf_data.set_payto(Pay.BRANCH_Pay)
            ecf_data.set_payto_id(Ecfhdr.payto)
            ecf_data.set_raisedby(Ecfhdr.raisedby)
            ecf_data.set_raiserbranch(employeebranch)
            ecf_data.set_raisername(Ecfhdr.raisername)
            ecf_data.set_approvedby(Ecfhdr.approvedby)
            ecf_data.set_approvername(Ecfhdr.approvername)
            ecf_data.set_supplier_type_id(Ecfhdr.supplier_type)
            if Ecfhdr.supplier_type == SupplierType.SINGLE:
                ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
            if Ecfhdr.supplier_type == SupplierType.MULTIPLE:
                ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
            ecf_data.set_rmcode(api_serv.get_empsingle_id(request, Ecfhdr.rmcode))
            ecf_data.set_client_code(api_serv.get_clicode(Ecfhdr.client_code))
            ecfhdr_list = []
            # invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            # ecf = invhdr.ecfheader_id
            # ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv_id)

            invhdr_list = []
            if len(inv_list)!=0:
                for inhdr in inv_list:
                    invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inhdr.id,entity_id=self._entity_id(), status = 1).all()
                    file_list = ECFFiles.objects.using(self._current_app_schema()).filter(ecffile_id=inhdr.id,entity_id=self._entity_id(), status=1).all()
                    bank_arr = []
                    for i in credit_list:
                        bank_arr.append(i.creditbank_id)
                    try:
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    except:
                        state = None
                        supp = None
                    bank_data = api_serv.get_bank_list(request, bank_arr)
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    print('emp2', emp)
                    emp_add = emp['address_id']
                    empadd = api_serv.get_empaddress_id(request, emp_add)

                    gst = empadd['state_id']
                    if inhdr.supplier_id != '':
                        try:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            suppadd = supp['address_id']
                            ven = api_serv.get_venaddress(request, suppadd)
                            supgst = ven['state_id']
                        except:
                            supp = None
                            supgst = None
                        if supgst != gst:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'

                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                    inhdr_data.set_invoiceno(inhdr.invoiceno)
                    inhdr_data.set_dedupinvoiceno(inhdr.dedupinvoiceno)
                    inhdr_data.set_invoicedate(inhdr.invoicedate)
                    inhdr_data.set_suppliergst(inhdr.suppliergst)
                    inhdr_data.set_raisorbranchgst(inhdr.raisorbranchgst)
                    inhdr_data.set_invoiceamount(inhdr.invoiceamount)
                    inhdr_data.set_taxamount(inhdr.taxamount)
                    inhdr_data.set_totalamount(inhdr.totalamount)
                    inhdr_data.set_otheramount(inhdr.otheramount)
                    inhdr_data.set_roundoffamt(inhdr.roundoffamt)
                    inhdr_data.set_supplier(supp)
                    inhdr_data.set_invoicegst(inhdr.invoicegst)
                    inhdr_data.set_supplierstate(state)
                    if inhdr.supplier_id != '':
                        inhdr_data.set_gsttype(gsttype)

                    for invpo in invpo_list:
                        inpo_data = Invoiceporesponse()
                        inpo_data.set_id(invpo.id)
                        inpo_data.set_invoiceheader(invpo.invoiceheader_id)
                        inpo_data.set_ponumber(invpo.ponumber)
                        inpo_data.set_grnnumber(invpo.grnnumber)
                        inpo_data.set_grndate(invpo.grndate)
                        inpo_data.set_poquantity(invpo.poquantity)
                        inpo_data.set_receivedqty(invpo.receivedqty)
                        inpo_data.set_balanceqty(invpo.balanceqty)
                        inpo_data.set_receiveddate(invpo.receiveddate)
                        inpo_data.set_product_code(invpo.product_code)
                        inpo_data.set_invoicedqty(invpo.invoicedqty)
                        inpo_data.set_invoiceqty(invpo.invoiceqty)
                        invhdr_list.append(json.loads(inpo_data.get()))
                        inhdr_data.set_invoicepo(invhdr_list)

                    inv_list = []
                    for invdtl in invdtl_list:
                        hsn = api_serv.get_hsn_code(request, invdtl.hsn)
                        indtl_data = Invoicedetailresponse()
                        indtl_data.set_id(invdtl.id)
                        indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                        indtl_data.set_invoice_po(invdtl.invoice_po)
                        indtl_data.set_productcode(invdtl.productcode)
                        indtl_data.set_productname(invdtl.productname)
                        indtl_data.set_description(invdtl.description)
                        indtl_data.set_hsn(hsn)
                        indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                        indtl_data.set_uom(invdtl.uom)
                        indtl_data.set_unitprice(invdtl.unitprice)
                        indtl_data.set_quantity(invdtl.quantity)
                        indtl_data.set_amount(invdtl.amount)
                        indtl_data.set_discount(invdtl.discount)
                        indtl_data.set_sgst(invdtl.sgst)
                        indtl_data.set_cgst(invdtl.cgst)
                        indtl_data.set_igst(invdtl.igst)
                        indtl_data.set_taxamount(invdtl.taxamount)
                        indtl_data.set_totalamount(invdtl.totalamount)
                        indtl_data.set_otheramount(invdtl.otheramount)
                        indtl_data.set_roundoffamt(invdtl.roundoffamt)
                        inv_list.append(json.loads(indtl_data.get()))
                        inhdr_data.set_invoicedtl(inv_list)

                        invdeb_list = []
                        for dbt in deb_list:
                            cat = api_serv.get_cat_code(request,dbt.category_code)
                            sub = api_serv.get_subcat_code(request,dbt.subcategory_code)
                            dbt_data = Debitresponse()
                            dbt_data.set_id(dbt.id)
                            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                            dbt_data.set_category_code(cat)
                            dbt_data.set_subcategory_code(sub)
                            dbt_data.set_debitglno(dbt.debitglno)
                            dbt_data.set_amount(dbt.amount)
                            dbt_data.set_deductionamount(dbt.deductionamount)
                            dbt_data.set_bsproduct(api_serv.get_bscode(dbt.bsproduct))
                            ccbs_list=[]
                            ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                            for ccbs in ccb_list:
                                cc = api_serv.get_cc_code(request,ccbs.cc_code)
                                bs = api_serv.get_bs_code(request,ccbs.bs_code)
                                ccbs_data = ccbsdtlresponse()
                                ccbs_data.set_id(ccbs.id)
                                ccbs_data.set_debit(ccbs.debit_id)
                                ccbs_data.set_cc_code(cc)
                                ccbs_data.set_bs_code(bs)
                                ccbs_data.set_code(ccbs.code)
                                ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
                                ccbs_data.set_glno(ccbs.glno)
                                ccbs_data.set_amount(ccbs.amount)
                                ccbs_data.set_remarks(ccbs.remarks)
                                ccbs_list.append(json.loads(ccbs_data.get()))
                                dbt_data.set_ccbs(ccbs_data)
                                invdeb_list.append(json.loads(dbt_data.get()))
                                inhdr_data.set_debit(invdeb_list)

                    crd_list = []
                    for crd in credit_list:
                        cat = api_serv.get_cat_code(request, crd.category_code)
                        sub = api_serv.get_subcat_code(request, crd.subcategory_code)
                        crd_data = Creditresponse()
                        crd_data.set_id(crd.id)
                        crd_data.set_invoiceheader(crd.invoiceheader_id)
                        pay = api_serv.get_paymodesingle_id(request, crd.paymode_id)
                        crd_data.set_paymode(pay)
                        # bankdtl = (credit_service.fetch_payment_listget(request, vys_page,supp,,emp_id))
                        # crd_data.set_paydetails(bankdtl)
                        crd_data.set_category_code(cat)
                        crd_data.set_subcategory_code(sub)
                        bank_data = api_serv.get_creditpayment([crd.creditbank_id], emp_id)
                        crd_data.set_credit_bank(bank_data)
                        crd_data.set_suppliertax(crd.suppliertax_id)
                        crd_data.set_suppliertaxrate(crd.suppliertaxrate)
                        crd_data.set_amount(crd.amount)
                        crd_data.set_creditglno(crd.creditglno)
                        if crd.paymode_id == 4:
                            from utilityservice.service.ap_api_service import APApiService
                            appservice = APApiService(self._scope())
                            app_service = appservice.fetch_apraiser_emp_accntdtls_using_accntno(request,
                                                                                                crd.creditrefno,
                                                                                                Ecfhdr.raisedby)
                            print("empappservice", app_service)
                            crd_data.set_creditrefno(app_service)
                            crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                            crd_data.set_taxexcempted(crd.taxexcempted)
                            crd_data.set_taxableamount(crd.taxableamount)
                            crd_data.set_ddtranbranch(crd.ddtranbranch)
                            crd_data.set_ddpaybranch(crd.ddpaybranch)
                            crd_list.append(json.loads(crd_data.get()))
                            inhdr_data.set_credit(crd_list)
                        else:
                            crd_data.set_creditrefno(crd.creditrefno)
                            crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                            crd_data.set_taxexcempted(crd.taxexcempted)
                            crd_data.set_taxableamount(crd.taxableamount)
                            crd_data.set_ddtranbranch(crd.ddtranbranch)
                            crd_data.set_ddpaybranch(crd.ddpaybranch)
                            crd_list.append(json.loads(crd_data.get()))
                            inhdr_data.set_credit(crd_list)
                    filelist = []
                    for fl in file_list:
                        list_lent = len(file_list)
                        if list_lent > 0:
                            dtpc_res = ecffileResponse()
                            dtpc_res.set_id(fl.id)
                            dtpc_res.set_file_id(fl.file_id)
                            dtpc_res.set_file_name(fl.file_name)
                        filelist.append(dtpc_res)
                        inhdr_data.set_file_data(filelist)
                    ecfhdr_list.append(json.loads(inhdr_data.get()))
            ecf_data.set_Invheader(ecfhdr_list)
            return ecf_data
        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def ds(self, request,arr_obj,branch_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        # emp_bran = api_serv.get_empsingle_id(request, branch_id)
        # emp_bran1 = emp_bran['employee_branch']
        emp1 = api_serv.get_empbranch_id(request, branch_id)
        # emp = api_serv.get_empsingle_id(request, branch_id)
        print('emp2', emp1)
        emp_add1 = emp1['gstin']
        emp_branch = emp1['name']
        print('branch', emp_add1)
        if arr_obj != '':
            supp = api_serv.get_supliersingle_id(request, arr_obj)
            print("supp", supp)
            supgst = supp['gstno']
            if supgst[:2] != emp_add1[:2]:
                gsttype = 'IGST'
            else:
                gsttype = 'SGST & CGST'
            invh_data = Invoiceheaderresponse()
            invh_data.set_Branchgst(emp_add1)
            if arr_obj != '':
                invh_data.set_Gsttype(gsttype)
                invh_data.set_Supgstno(supgst)
            invh_data.set_Branchname(emp_branch)
            return invh_data


    def fetch_ecf_list_common_smmary(self, request, vys_page, emp_id, status):
        module_permission = ModulePermission(self._scope())
        emp_api = NWisefinUtilityService()
        role_arr = module_permission.employee_modulerole(emp_id, ModuleList.ECF)
        print('role_arr', role_arr)
        maker = RoleList.maker
        checker = RoleList.checker
        # if maker in role_arr or checker in role_arr:
        #     condition = Q(created_by =emp_id)
        #     print('top_cdn',condition)
        # else:
        #     error_obj = Error()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description('You dont have permission')
        #     return error_obj
        status = int(status)
        if status == ddl_status.ECF_CREATED_BY_ME:
            condition = Q(created_by=emp_id)

        statuss = int(status)
        # if statuss == ddl_status.ECF_CREATED_BY_ME:
        #     condition = Q(ecfstatus=ddl_status.ECF_CREATED_BY_ME,created_by=emp_id)
        if statuss == ddl_status.PENDING_FOR_APPROVAL:
            condition = Q(ecfstatus=ddl_status.PENDING_FOR_APPROVAL, created_by=emp_id)
        if statuss == ddl_status.ECF_REJECTED_BY_ME:
            condition = Q(ecfstatus=ddl_status.ECF_REJECTED_BY_ME)
        if statuss == ddl_status.ECF_APPROVED_BY_ME:
            condition = Q(ecfstatus=ddl_status.ECF_APPROVED_BY_ME)
        if statuss == ddl_status.ECF_RE_AUDIT_BY_ME:
            condition = Q(ecfstatus=ddl_status.ECF_RE_AUDIT_BY_ME, created_by=emp_id)
        if statuss == ddl_status.DELETE:
            condition = Q(ecfstatus=ddl_status.DELETE, created_by=emp_id)
        ecf_list = ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                   vys_page.get_offset():vys_page.get_query_limit()]
        # print("ecf",ecf_list.branch)
        ecf_listt = ECFHeader.objects.using(self._current_app_schema()).filter(condition)
        count = len(ecf_listt)
        print('lend', count)
        list_length = len(ecf_list)
        ecf_list_data = NWisefinList()
        com_arr = []
        # state_arr = []
        for i in ecf_list:
            com_arr.append(i.commodity_id)
            # api_serv = api_service.ApiService()
            # print("i.branch",i.branch)
            # if i.branch is not None:
            #     branch_co = api_serv.get_empbranch_id(request, i.branch)
            #     brnch_arr.append(branch_co)
            # supp_arr.append(i.branch)
            # state_arr.append(i.supplierstate_id)
        # bch_data = api_serv.get_empbranch_id(request, brnch_arr)
        # print("bch", bch_data)
        api_serv = api_service.ApiService(self._scope())
        commo_data = api_serv.get_commodity_list(request, com_arr)
        # bnch = branch_co['name']
        # print("name",bnch)
        # supplier_data = api_serv.get_supplier_list(self, request , supp_arr)
        # state_data = MasterAPI.get_state(self, request , supp_arr)
        # print('comm_data',commo_data.replace('"', "'"))
        # print('comm_data',commo_data["data"])
        # print("strrr", json.loads(commo_data))
        # s = json.loads(commo_data)
        # s1 = s['data']
        # print('comm_data', s1)
        if list_length <= 0:
            pass
        else:
            for Ecfhdr in ecf_list:
                ecf_data = ECFHeaderresponse()
                ecf_data.set_id(Ecfhdr.id)
                ecf_data.set_crno(Ecfhdr.crno)
                ecf_data.set_commodity_id(Ecfhdr.commodity_id, commo_data['data'])
                # ecf_data.set_supplier_id(Ecfhdr.supplier_id,supplier_data['data'])
                # ecf_data.set_supplierstate_id(Ecfhdr.supplierstate_id,state_data['data'])
                ecf_data.set_ecftype_id(Ecfhdr.ecftype)
                if Ecfhdr.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if Ecfhdr.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if Ecfhdr.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if Ecfhdr.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                # ecf_data.set_ecftype(Ecfhdr.ecftype)
                ecf_data.set_ecfdate(Ecfhdr.ecfdate)
                ecf_data.set_ecfamount(Ecfhdr.ecfamount)
                if Ecfhdr.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if Ecfhdr.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                ecf_data.set_ppx_id(Ecfhdr.ppx)
                if Ecfhdr.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if Ecfhdr.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx(Ecfhdr.ppx)
                ecf_data.set_notename(Ecfhdr.notename)
                branch = emp_api.get_employee_branch([Ecfhdr.branch])
                if len(branch) > 0:
                    ecf_data.set_branch(branch)
                ecf_data.set_remark(Ecfhdr.remark)
                ecf_data.set_payto_id(Ecfhdr.payto)
                if Ecfhdr.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if Ecfhdr.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if Ecfhdr.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto(Ecfhdr.payto)
                ecf_data.set_raisedby(Ecfhdr.raisedby)
                ecf_data.set_raiserbranch(Ecfhdr.raiserbranch)
                ecf_data.set_raisername(Ecfhdr.raisername)
                # ecf_data.set_approvedby(Ecfhdr.approvedby_id)
                ecf_data.set_approvername(Ecfhdr.approvername)
                aph = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=Ecfhdr.id, status=1)
                invheader_list = []
                for inhdr in aph:
                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(inhdr.ecfheader_id)
                    inhdr_data.set_invoiceno(inhdr.invoiceno)
                    ecf_data.set_invoiceheader(inhdr_data)
                ecf_list_data.append(ecf_data)
            ecf_list_data.count = count
            vpage = NWisefinPaginator(ecf_list, vys_page.get_index(), 10)
            ecf_list_data.set_pagination(vpage)
        return ecf_list_data


    def apstat(self,aps,emp_id):
        try:
            ap = ECFHeader.objects.using(self._current_app_schema()).get(crno=aps.get_crno())
            ap.ap_status = aps.get_ap_status()
            ap.status = 1
            ap.updated_by = emp_id
            ap.updated_date = now()
            ap.save()
            success_obj = ECFHeaderresponse()
            success_obj.set_status("SUCCESS")
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code("INVALID_CRNO")
            error_obj.set_description("AP Status is not properly updated")
            return error_obj


    def ecfmail_data(self, ecf_id,emp_id):
        try:
            ecfmail = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf_id)
            ta = ECFMailScheduler.objects.using(self._current_app_schema()).create(ecf_id=ecfmail.id,
                                                                              raiser_id=ecfmail.raisedby,
                                                                              ecf_status=ecfmail.ecfstatus,
                                                                              ecf_type=ecfmail.ecftype,
                                                                              mail_type=ecfmail.ecfstatus,
                                                                              created_by=emp_id,
                                                                              created_date=now())

            ecfmail1 = self.ecfmail1_data(ecf_id,emp_id)
            print(ecfmail1)
            print(ta)
            return ta
        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code("INVALID_CRNO")
            error_obj.set_description(str(ex))
            return error_obj

    def ecfmail1_data(self, ecf_id,emp_id):
        try:
            condition=Q(is_send=0)
            ecfmail = ECFMailScheduler.objects.using(self._current_app_schema()).filter(condition)
            return ecfmail
        except:
            pass

