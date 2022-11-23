import json
import traceback

from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import InvoiceHeader, ECFQueue, ECFHeader, InvoicePO, Invoicedetail, Debit, ccbsdtl, \
    Credit, ECFFiles
# from api.masterapi import MasterAPI
from ecfservice.service.ecfdocumentservice import ECFDocumentService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType,Type,PPX,Pay,ECFStatus
from ecfservice.service.ecfauditservice import ECFAuditService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType,Type,PPX,Pay,ECFStatus
from ecfservice.data.response.invoiceheaderresponse import Invoiceheaderresponse
from ecfservice.data.response.invoiceporesponse import Invoiceporesponse
from ecfservice.data.response.invoicedetailresponse import Invoicedetailresponse
from ecfservice.data.response.creditresponse import Creditresponse
from ecfservice.data.response.invoicedetailresponse import Debitresponse
from ecfservice.data.response.invoicedetailresponse import ccbsdtlresponse
from django.db.models import Q
from datetime import datetime, timedelta, date
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service import api_service
from utilityservice.service.api_service import ApiService
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now
from django.db import IntegrityError
from ecfservice.service.creditservice import CreditService
from masterservice.service.uomservice import UomService
# uom_serv = UomService()

class InvoiceheaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def invhdrcreate(self, request, invhdr_obj, emp_id):
        print("inv",invhdr_obj)
        print("ecfid",invhdr_obj.get_ecfheader_id())
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, emp_id)
        print('emp2', emp)
        emp_branch = emp['employee_branch']
        raisor_name = emp['name']
        emp1 = api_serv.get_empbranch_id(request, emp_branch)
        emp_add1 = emp1['gstin']
        emp_bran = emp1['name']
        ecf = ECFHeader.objects.using(self._current_app_schema()).get(id= invhdr_obj.get_ecfheader_id(),entity_id=self._entity_id())
        amt = ecf.ecfamount
        print("type",ecf.__dict__)
        type = ecf.ecftype
        print("type", type)
        if type == Type.NON_PO:
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                    emp_bran1 = emp_bran['employee_branch']
                    emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                    # emp = api_serv.get_empsingle_id(request, emp_id)
                    # print('emp2', emp1)
                    emp_add1 = emp1['gstin']
                    print(emp_add1)
                    emp_branch = emp1['name']
                    emp_code = emp1['code']
                    print('branch', emp_add1)
                    if invhdr_obj.get_supplier_id() != '':
                        supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                        supgst = supp['gstno']
                        print("supp", supgst)
                        if supgst != emp_add1:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                                                                                        invoiceno=invhdr_obj.get_invoiceno(),
                                                                                        dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                                                                                        invoicedate=invhdr_obj.get_invoicedate(),
                                                                                        suppliergst=supgst,
                                                                                        raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                                                                                        invoiceamount=invhdr_obj.get_invoiceamount(),
                                                                                        taxamount=invhdr_obj.get_taxamount(),
                                                                                        totalamount=invhdr_obj.get_totalamount(),
                                                                                        otheramount=invhdr_obj.get_otheramount(),
                                                                                        roundoffamt=invhdr_obj.get_roundoffamt(),
                                                                                        invoicegst=invhdr_obj.get_invoicegst(),
                                                                                        supplier_id=invhdr_obj.get_supplier_id(),
                                                                                        supplierstate_id=invhdr_obj.get_supplierstate_id(),
                                                                                        updated_by=emp_id,
                                                                                        updated_date=now())
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

                else:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                    emp_bran1 = emp_bran['employee_branch']
                    emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                    # emp = api_serv.get_empsingle_id(request, emp_id)
                    # print('emp2', emp1)
                    emp_add1 = emp1['gstin']
                    print(emp_add1)
                    emp_branch = emp1['name']
                    emp_code = emp1['code']
                    print('branch', emp_add1)
                    if invhdr_obj.get_supplier_id() != '':
                        supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                        supgst = supp['gstno']
                        print("supp", supgst)
                        if supgst != emp_add1:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                                                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                                                        invoiceno=invhdr_obj.get_invoiceno(),
                                                        dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                                                        invoicedate=invhdr_obj.get_invoicedate(),
                                                        suppliergst=supgst,
                                                        raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                                                        invoiceamount=invhdr_obj.get_invoiceamount(),
                                                        taxamount=invhdr_obj.get_taxamount(),
                                                        totalamount=invhdr_obj.get_totalamount(),
                                                        otheramount=invhdr_obj.get_otheramount(),
                                                        roundoffamt=invhdr_obj.get_roundoffamt(),
                                                        invoicegst=invhdr_obj.get_invoicegst(),
                                                        supplier_id=invhdr_obj.get_supplier_id(),
                                                        supplierstate_id=invhdr_obj.get_supplierstate_id(),
                                                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)




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
                inhdr_data.set_supplier(invhdr.supplier_id)
                inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                if invhdr_obj.get_supplier_id() != '':
                    inhdr_data.set_gsttype(gsttype)
                    # inhdr_data.set_supgstno(supgst)
                return inhdr_data
        elif type == Type.ERA:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_ecfheader_id(),entity_id=self._entity_id())
            type = ecf.ecftype
            print("type",type)
            amt = ecf.ecfamount
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                        invoiceno=invhdr_obj.get_invoiceno(),
                        # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                        invoicedate=invhdr_obj.get_invoicedate(),
                        # suppliergst=invhdr_obj.get_suppliergst(),
                        raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                        invoiceamount=invhdr_obj.get_invoiceamount(),
                        taxamount=invhdr_obj.get_taxamount(),
                        totalamount=invhdr_obj.get_totalamount(),
                        otheramount=invhdr_obj.get_otheramount(),
                        roundoffamt=invhdr_obj.get_roundoffamt(),
                        invoicegst="N",
                        # supplier_id=invhdr_obj.get_supplier_id(),
                        # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                        updated_by=emp_id,
                        updated_date=now())
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

                else:
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                        # invoiceno=invhdr_obj.get_invoiceno(),
                        # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                        invoicedate=invhdr_obj.get_invoicedate(),
                        # suppliergst=invhdr_obj.get_suppliergst(),
                        raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                        invoiceamount=invhdr_obj.get_invoiceamount(),
                        taxamount=invhdr_obj.get_taxamount(),
                        totalamount=invhdr_obj.get_totalamount(),
                        otheramount=invhdr_obj.get_otheramount(),
                        roundoffamt=invhdr_obj.get_roundoffamt(),
                        invoicegst="N",
                        # supplier_id=invhdr_obj.get_supplier_id(),
                        # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                        created_by=emp_id,
                        created_date = now(),entity_id=self._entity_id())

                    invoiceno = emp['code'] + str(datetime.now().strftime("%y%m%d")) + str(invhdr.id).zfill(4)
                    invhdr.invoiceno = invoiceno
                    invhdr.save()
                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(invhdr.id)
                inhdr_data.set_ecfheader(invhdr.ecfheader_id)
                inhdr_data.set_invoiceno(invhdr.invoiceno)
                # inhdr_data.set_dedupinvoiceno(invhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(invhdr.invoicedate)
                # inhdr_data.set_suppliergst(invhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(invhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(invhdr.invoiceamount)
                inhdr_data.set_taxamount(invhdr.taxamount)
                inhdr_data.set_totalamount(invhdr.totalamount)
                inhdr_data.set_otheramount(invhdr.otheramount)
                inhdr_data.set_roundoffamt(invhdr.roundoffamt)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                # inhdr_data.set_supplier(invhdr.supplier_id)
                # inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                # if invhdr_obj.get_supplier_id() != '':
                #     inhdr_data.set_gsttype(gsttype)
                    # inhdr_data.set_supgstno(supgst)
                return inhdr_data
        elif type == Type.ADVANCE:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_ecfheader_id(),entity_id=self._entity_id())
            type = ecf.ecftype
            print("type",type)
            amt = ecf.ecfamount
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    if invhdr_obj.get_supplier_id() != None:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            # supplier_id=invhdr_obj.get_supplier_id(),
                            # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)
                    else:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            # supplier_id=invhdr_obj.get_supplier_id(),
                            # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

                else:
                    print('supp',invhdr_obj.get_supplier_id())
                    if invhdr_obj.get_supplier_id() != "":
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            supplier_id=invhdr_obj.get_supplier_id(),
                            supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())

                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)
                    else:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=invhdr_obj.get_raisorbranchgst(),
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            # supplier_id=invhdr_obj.get_supplier_id(),
                            # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            created_by=emp_id,
                            created_date=now(),entity_id=self._entity_id())

                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(invhdr.id)
                inhdr_data.set_ecfheader(invhdr.ecfheader_id)
                # inhdr_data.set_invoiceno(invhdr.invoiceno)
                # inhdr_data.set_dedupinvoiceno(invhdr.dedupinvoiceno)
                # inhdr_data.set_invoicedate(invhdr.invoicedate)
                # inhdr_data.set_suppliergst(invhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(invhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(invhdr.invoiceamount)
                inhdr_data.set_taxamount(invhdr.taxamount)
                inhdr_data.set_totalamount(invhdr.totalamount)
                inhdr_data.set_otheramount(invhdr.otheramount)
                inhdr_data.set_roundoffamt(invhdr.roundoffamt)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                if invhdr.supplier_id != "":
                    inhdr_data.set_supplier(invhdr.supplier_id)
                    inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                else:
                    inhdr_data.set_supplier("")
                    inhdr_data.set_supplierstate("")
                # if invhdr_obj.get_supplier_id() != '':
                #     inhdr_data.set_gsttype(gsttype)
                    # inhdr_data.set_supgstno(supgst)
                return inhdr_data
    def invhdrppx(self,ecf_id,ecf_branchgst,ecf_amt, emp_id):
            try:
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                                                        ecfheader_id=ecf_id,
                                                        invoiceno="NOINVOICE",
                                                        dedupinvoiceno="NOINVOICE",
                                                        invoicedate=now(),
                                                        suppliergst="",
                                                        raisorbranchgst=ecf_branchgst,
                                                        invoiceamount=ecf_amt,
                                                        taxamount=0,
                                                        totalamount=ecf_amt,
                                                        otheramount=0,
                                                        roundoffamt=0,
                                                        invoicegst="N",
                                                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)
            except IntegrityError as error:
                traceback.print_exc(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Exception as ex:
                traceback.print_exc(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(ex))
                return error_obj

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
            return inhdr_data

    def fetchone_inv_list(self,request, vys_page, inv_id, emp_id):
        try:
            invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
            invpo_list = InvoicePO.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status = 1,entity_id=self._entity_id()).all()
            ecf = invhdr.ecfheader_id
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=ecf,entity_id=self._entity_id())
            type = ecfhdr.ecftype
            # if ecfhdr.supplier_id!= '':
            #     supp = ecfhdr.supplier_id
            if ((type == Type.NON_PO) or (type == Type.TCF)):
                invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status = 1,entity_id=self._entity_id()).all()
                deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status = 1,entity_id=self._entity_id()).all()
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status = 1,entity_id=self._entity_id()).all()
                bank_arr = []
                for i in credit_list:
                    bank_arr.append(i.creditbank_id)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                # bank_data = api_serv.get_bank_list(request, bank_arr)
                # emp = api_serv.get_empsingle_id(request, emp_id)
                # print('emp2', emp)
                # emp_add = emp['address_id']
                # empadd = api_serv.get_empaddress_id(request, emp_add)
                #
                # gst = empadd['state_id']
                # if invhdr.supplier_id != '':
                #     state = api_serv.get_statesingle_id(request, invhdr.supplierstate_id)
                #     supp = api_serv.get_supliersingle_id(request, invhdr.supplier_id)
                #     suppadd = supp['address_id']
                #     ven = api_serv.get_venaddress(request, suppadd)
                #     supgst = ven['state_id']
                #     if supgst != gst:
                #         gsttype = 'IGST'
                #     else:
                #         gsttype = 'SGST & CGST'
                bnnch = api_serv.get_empbranch_id(request, ecfhdr.branch)
                print("bnnch", bnnch)
                gstno = bnnch['gstin']
                print("gstno", gstno[:2])
                state = api_serv.get_statesingle_id(request, invhdr.supplierstate_id)
                supp = api_serv.get_supliersingle_id(request, invhdr.supplier_id)
                suppgst = supp['gstno']
                print("supp", suppgst[:2])
                print("supp", supp)
                if suppgst[:2] != gstno[:2]:
                    gsttype = 'IGST'
                else:
                    gsttype = 'SGST & CGST'

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
                inhdr_data.set_inv_crno(invhdr.inv_crno)
                inhdr_data.set_supplier(supp)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                inhdr_data.set_supplierstate(state)
                if invhdr.supplier_id != '':
                    inhdr_data.set_gsttype(gsttype)
                invhdr_list = []
                inv_list=[]
                crd_list=[]
                invdeb_list = []
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
                    uom_data = api_serv.get_uom(vys_page,invdtl.uom)
                    indtl_data.set_uom(uom_data.data[0])
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
                    indtl_data.set_roundoffamt(invdtl.roundoffamt)
                    indtl_data.set_otheramount(invdtl.otheramount)
                    inv_list.append(json.loads(indtl_data.get()))
                inhdr_data.set_invoicedtl(inv_list)
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
                    ccbs_list=[]
                    ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id())
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
                    # crd_data.set_creditbank_id(crd.creditbank_id,bank_data['data'])
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
                return inhdr_data
            elif type == Type.ERA:
                invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id,
                                                                                  status=1,entity_id=self._entity_id()).all()
                deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status=1,entity_id=self._entity_id()).all()
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status=1,entity_id=self._entity_id()).all()
                bank_arr = []
                for i in credit_list:
                    bank_arr.append(i.creditbank_id)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                bank_data = api_serv.get_bank_list(request, bank_arr)
                # emp = api_serv.get_empsingle_id(request, emp_id)
                # print('emp2', emp)
                # emp_add = emp['address_id']
                # empadd = api_serv.get_empaddress_id(request, emp_add)

                # gst = empadd['state_id']
                # if invhdr.supplier_id != '':
                #     state = api_serv.get_statesingle_id(request, invhdr.supplierstate_id)
                #     supp = api_serv.get_supliersingle_id(request, invhdr.supplier_id)
                #     suppadd = supp['address_id']
                #     ven = api_serv.get_venaddress(request, suppadd)
                #     supgst = ven['state_id']
                #     if supgst != gst:
                #         gsttype = 'IGST'
                #     else:
                #         gsttype = 'SGST & CGST'
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
                # inhdr_data.set_supplier(supp)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                # inhdr_data.set_supplierstate(state)
                # if invhdr.supplier_id != '':
                #     inhdr_data.set_gsttype(gsttype)
                invhdr_list = []
                inv_list = []
                crd_list = []
                invdeb_list = []
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
                    uom_data = api_serv.get_uom(vys_page, invdtl.uom)
                    indtl_data.set_uom(uom_data.data[0])
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
                    inv_list.append(json.loads(indtl_data.get()))
                inhdr_data.set_invoicedtl(inv_list)
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
                    crd_data.set_creditrefno(crd.creditrefno)
                    crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                    crd_data.set_taxexcempted(crd.taxexcempted)
                    crd_data.set_taxableamount(crd.taxableamount)
                    crd_data.set_ddtranbranch(crd.ddtranbranch)
                    crd_data.set_ddpaybranch(crd.ddpaybranch)
                    crd_list.append(json.loads(crd_data.get()))
                inhdr_data.set_credit(crd_list)
                return inhdr_data
            elif type == Type.ADVANCE:
                invdtl_list = Invoicedetail.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id,
                                                                                             status=1,
                                                                                             entity_id=self._entity_id()).all()
                deb_list = Debit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status=1,entity_id=self._entity_id()).all()
                credit_list = Credit.objects.using(self._current_app_schema()).filter(invoiceheader_id=inv_id, status=1,entity_id=self._entity_id()).all()
                bank_arr = []
                for i in credit_list:
                    bank_arr.append(i.creditbank_id)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                # bank_data = api_serv.get_bank_list(request, bank_arr)
                emp = api_serv.get_empsingle_id(request, emp_id)
                print('emp2', emp)
                emp_add = emp['address_id']
                empadd = api_serv.get_empaddress_id(request, emp_add)

                gst = empadd['state_id']
                if invhdr.supplier_id != None:
                    state = api_serv.get_statesingle_id(request, invhdr.supplierstate_id)
                    supp = api_serv.get_supliersingle_id(request, invhdr.supplier_id)
                    suppadd = supp['address_id']
                    ven = api_serv.get_venaddress(request, suppadd)
                    supgst = ven['state_id']
                    if supgst != gst:
                        gsttype = 'IGST'
                    else:
                        gsttype = 'SGST & CGST'
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
                if invhdr.supplier_id != None:
                    inhdr_data.set_supplier(supp)
                    inhdr_data.set_supplierstate(state)
                else:
                    inhdr_data.set_supplier("")
                    inhdr_data.set_supplierstate("")
                inhdr_data.set_invoicegst(invhdr.invoicegst)

                # if invhdr.supplier_id != '':
                #     inhdr_data.set_gsttype(gsttype)
                invhdr_list = []
                inv_list = []
                crd_list = []
                invdeb_list = []

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
                    uom_data = api_serv.get_uom(vys_page, invdtl.uom)
                    indtl_data.set_uom(uom_data.data[0])
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
                    inv_list.append(json.loads(indtl_data.get()))
                inhdr_data.set_invoicedtl(inv_list)
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
                    logger.info("debit data")
                    ccb_list = ccbsdtl.objects.using(self._current_app_schema()).filter(debit_id=dbt.id,entity_id=self._entity_id()).all()
                    logger.info("ccbsget :" + str(ccb_list))
                    for ccbs in ccb_list:
                        logger.info("ccbsdetail :" + str(ccbs))
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
                    crd_data.set_creditrefno(crd.creditrefno)
                    crd_data.set_suppliertaxtype(crd.suppliertaxtype)
                    crd_data.set_taxexcempted(crd.taxexcempted)
                    crd_data.set_taxableamount(crd.taxableamount)
                    crd_data.set_ddtranbranch(crd.ddtranbranch)
                    crd_data.set_ddpaybranch(crd.ddpaybranch)
                    crd_list.append(json.loads(crd_data.get()))
                inhdr_data.set_credit(crd_list)
                return inhdr_data

        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def Delete_invhdr(self,request, inv_id, emp_id):
        try:
            invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=inv_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=inv_id,entity_id=self._entity_id())
            self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=invhdr.id, ref_type=ECFRefType.INVOICEHEADER, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj
    def invhdrmodcreate(self,request,invhdr_obj,emp_id):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        emp = api_serv.get_empsingle_id(request, emp_id)
        print('emp2', emp)
        emp_branch = emp['employee_branch']
        raisor_name = emp['name']
        emp1 = api_serv.get_empbranch_id(request, emp_branch)
        emp_add1 = emp1['gstin']
        emp_bran = emp1['name']
        ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_ecfheader_id(),entity_id=self._entity_id())
        amt = ecf.ecfamount
        print("type", ecf.__dict__)
        type = ecf.ecftype
        print("type", type)
        if type == Type.NON_PO:
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                    emp_bran1 = emp_bran['employee_branch']
                    emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                    # emp = api_serv.get_empsingle_id(request, emp_id)
                    # print('emp2', emp1)
                    emp_add1 = emp1['gstin']
                    print(emp_add1)
                    emp_branch = emp1['name']
                    emp_code = emp1['code']
                    print('branch', emp_add1)
                    if invhdr_obj.get_supplier_id() != '':
                        supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                        supgst = supp['gstno']
                        print("supp", supgst)
                        if supgst != emp_add1:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                                                                                        invoiceno=invhdr_obj.get_invoiceno(),
                                                                                        dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                                                                                        invoicedate=invhdr_obj.get_invoicedate(),
                                                                                        suppliergst=supgst,
                                                                                        raisorbranchgst=emp1['gstin'],
                                                                                        invoiceamount=invhdr_obj.get_invoiceamount(),
                                                                                        taxamount=invhdr_obj.get_taxamount(),
                                                                                        totalamount=invhdr_obj.get_totalamount(),
                                                                                        otheramount=invhdr_obj.get_otheramount(),
                                                                                        roundoffamt=invhdr_obj.get_roundoffamt(),
                                                                                        invoicegst=invhdr_obj.get_invoicegst(),
                                                                                        supplier_id=invhdr_obj.get_supplier_id(),
                                                                                        supplierstate_id=invhdr_obj.get_supplierstate_id(),
                                                                                        updated_by=emp_id,
                                                                                        updated_date=now())
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

                else:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                    emp_bran1 = emp_bran['employee_branch']
                    emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                    # emp = api_serv.get_empsingle_id(request, emp_id)
                    # print('emp2', emp1)
                    emp_add1 = emp1['gstin']
                    print(emp_add1)
                    emp_branch = emp1['name']
                    emp_code = emp1['code']
                    print('branch', emp_add1)
                    if invhdr_obj.get_supplier_id() != '':
                        supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                        supgst = supp['gstno']
                        print("supp", supgst)
                        if supgst != emp_add1:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                                                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                                                        invoiceno=invhdr_obj.get_invoiceno(),
                                                        dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                                                        invoicedate=invhdr_obj.get_invoicedate(),
                                                        suppliergst=supgst,
                                                        raisorbranchgst=emp1['gstin'],
                                                        invoiceamount=invhdr_obj.get_invoiceamount(),
                                                        taxamount=invhdr_obj.get_taxamount(),
                                                        totalamount=invhdr_obj.get_totalamount(),
                                                        otheramount=invhdr_obj.get_otheramount(),
                                                        roundoffamt=invhdr_obj.get_roundoffamt(),
                                                        invoicegst=invhdr_obj.get_invoicegst(),
                                                        supplier_id=invhdr_obj.get_supplier_id(),
                                                        supplierstate_id=invhdr_obj.get_supplierstate_id(),
                                                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=invhdr.ecfheader_id,entity_id=self._entity_id()).update(
                                                                                ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                                                                                updated_by=emp_id,
                                                                                updated_date=now())
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="PENDING  FOR APPROVAL MODIFICATION",
                                                               is_sys=True,entity_id=self._entity_id()
                                                               )


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
                inhdr_data.set_supplier(invhdr.supplier_id)
                inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                if invhdr_obj.get_supplier_id() != '':
                    inhdr_data.set_gsttype(gsttype)
                    # inhdr_data.set_supgstno(supgst)
                return inhdr_data
        elif type == Type.ERA:
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                        invoiceno=invhdr_obj.get_invoiceno(),
                        # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                        invoicedate=invhdr_obj.get_invoicedate(),
                        # suppliergst=invhdr_obj.get_suppliergst(),
                        raisorbranchgst=emp_add1,
                        invoiceamount=invhdr_obj.get_invoiceamount(),
                        taxamount=invhdr_obj.get_taxamount(),
                        totalamount=invhdr_obj.get_totalamount(),
                        otheramount=invhdr_obj.get_otheramount(),
                        roundoffamt=invhdr_obj.get_roundoffamt(),
                        invoicegst=invhdr_obj.get_invoicegst(),
                        # supplier_id=invhdr_obj.get_supplier_id(),
                        # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                        updated_by=emp_id,
                        updated_date=now())
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)
                else:
                    invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                        ecfheader_id=invhdr_obj.get_ecfheader_id(),
                        invoiceno=invhdr_obj.get_invoiceno(),
                        # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                        invoicedate=invhdr_obj.get_invoicedate(),
                        # suppliergst=invhdr_obj.get_suppliergst(),
                        raisorbranchgst=emp_add1,
                        invoiceamount=invhdr_obj.get_invoiceamount(),
                        taxamount=invhdr_obj.get_taxamount(),
                        totalamount=invhdr_obj.get_totalamount(),
                        otheramount=invhdr_obj.get_otheramount(),
                        roundoffamt=invhdr_obj.get_roundoffamt(),
                        invoicegst=invhdr_obj.get_invoicegst(),
                        # supplier_id=invhdr_obj.get_supplier_id(),
                        # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).filter(id=invhdr.ecfheader_id,entity_id=self._entity_id()).update(
                    ecfstatus=ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION,
                    updated_by=emp_id,
                    updated_date=now())
                Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id,entity_id=self._entity_id())
                self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
                ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                               from_user_id=emp_id,
                                                               to_user_id=emp_id,
                                                               created_date=now(),
                                                               comments="PENDING  FOR APPROVAL MODIFICATION",
                                                               is_sys=True,entity_id=self._entity_id()
                                                               )

                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(invhdr.id)
                inhdr_data.set_ecfheader(invhdr.ecfheader_id)
                inhdr_data.set_invoiceno(invhdr.invoiceno)
                inhdr_data.set_dedupinvoiceno(invhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(invhdr.invoicedate)
                # inhdr_data.set_suppliergst(invhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(invhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(invhdr.invoiceamount)
                inhdr_data.set_taxamount(invhdr.taxamount)
                inhdr_data.set_totalamount(invhdr.totalamount)
                inhdr_data.set_otheramount(invhdr.otheramount)
                inhdr_data.set_roundoffamt(invhdr.roundoffamt)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                # inhdr_data.set_supplier(invhdr.supplier_id)
                # inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                # if invhdr_obj.get_supplier_id() != '':
                #     inhdr_data.set_gsttype(gsttype)
                    # inhdr_data.set_supgstno(supgst)
                return inhdr_data
        elif type == Type.ADVANCE:
            ecf = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_ecfheader_id(),entity_id=self._entity_id())
            type = ecf.ecftype
            print("type", type)
            amt = ecf.ecfamount
            if (amt != invhdr_obj.get_invtotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if not invhdr_obj.get_id() is None:
                    if invhdr_obj.get_supplier_id() != None:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=emp_add1,
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            supplier_id=invhdr_obj.get_supplier_id(),
                            supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)
                    else:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=emp_add1,
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            # supplier_id=invhdr_obj.get_supplier_id(),
                            # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

                else:
                    print('supp', invhdr_obj.get_supplier_id())
                    if invhdr_obj.get_supplier_id() != "":
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=emp_add1,
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            supplier_id=invhdr_obj.get_supplier_id(),
                            supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            created_by=emp_id,
                            created_date=now(),entity_id=self._entity_id())

                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)
                    else:
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                            ecfheader_id=invhdr_obj.get_ecfheader_id(),
                            invoiceno=invhdr_obj.get_invoiceno(),
                            # dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                            invoicedate=invhdr_obj.get_invoicedate(),
                            # suppliergst=invhdr_obj.get_suppliergst(),
                            raisorbranchgst=emp_add1,
                            invoiceamount=invhdr_obj.get_invoiceamount(),
                            taxamount=invhdr_obj.get_taxamount(),
                            totalamount=invhdr_obj.get_totalamount(),
                            otheramount=invhdr_obj.get_otheramount(),
                            roundoffamt=invhdr_obj.get_roundoffamt(),
                            invoicegst="N",
                            # supplier_id=invhdr_obj.get_supplier_id(),
                            # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                            created_by=emp_id,
                            created_date=now(),entity_id=self._entity_id())

                        self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_id(invhdr.id)
                inhdr_data.set_ecfheader(invhdr.ecfheader_id)
                inhdr_data.set_invoiceno(invhdr.invoiceno)
                # inhdr_data.set_dedupinvoiceno(invhdr.dedupinvoiceno)
                inhdr_data.set_invoicedate(invhdr.invoicedate)
                # inhdr_data.set_suppliergst(invhdr.suppliergst)
                inhdr_data.set_raisorbranchgst(invhdr.raisorbranchgst)
                inhdr_data.set_invoiceamount(invhdr.invoiceamount)
                inhdr_data.set_taxamount(invhdr.taxamount)
                inhdr_data.set_totalamount(invhdr.totalamount)
                inhdr_data.set_otheramount(invhdr.otheramount)
                inhdr_data.set_roundoffamt(invhdr.roundoffamt)
                inhdr_data.set_invoicegst(invhdr.invoicegst)
                if invhdr.supplier_id != "":
                    inhdr_data.set_supplier(invhdr.supplier_id)
                    inhdr_data.set_supplierstate(invhdr.supplierstate_id)
                else:
                    inhdr_data.set_supplier("")
                    inhdr_data.set_supplierstate("")
                # if invhdr_obj.get_supplier_id() != '':
                #     inhdr_data.set_gsttype(gsttype)
                # inhdr_data.set_supgstno(supgst)
                return inhdr_data
    def invhdrccreate(self, request,file_data, invhdr_obj, ecf_id, emp_id):
        ecf = ECFHeader.objects.using(self._current_app_schema()).get(id= ecf_id,entity_id=self._entity_id())
        amt = ecf.ecfamount
        if (amt != invhdr_obj.get_invtotalamt()):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj
        else:
            if not invhdr_obj.get_id() is None:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                emp_bran1 = emp_bran['employee_branch']
                emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                # emp = api_serv.get_empsingle_id(request, emp_id)
                # print('emp2', emp1)
                emp_add1 = emp1['gstin']
                print(emp_add1)
                emp_branch = emp1['name']
                emp_code = emp1['code']
                print('branch', emp_add1)
                # if invhdr_obj.get_supplier_id() != '':
                #     supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                #     supgst = supp['gstno']
                #     print("supp", supgst)
                #     if supgst != emp_add1:
                #         gsttype = 'IGST'
                #     else:
                #         gsttype = 'SGST & CGST'
                invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invhdr_obj.get_id(),entity_id=self._entity_id()).update(
                    ecfheader_id=ecf_id,
                    invoiceno=invhdr_obj.get_invoiceno(),
                    dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                    invoicedate=invhdr_obj.get_invoicedate(),
                    # suppliergst=supgst,
                    raisorbranchgst=emp1['gstin'],
                    invoiceamount=invhdr_obj.get_invoiceamount(),
                    taxamount=invhdr_obj.get_taxamount(),
                    totalamount=invhdr_obj.get_totalamount(),
                    otheramount=invhdr_obj.get_otheramount(),
                    roundoffamt=invhdr_obj.get_roundoffamt(),
                    invoicegst=invhdr_obj.get_invoicegst(),
                    # supplier_id=invhdr_obj.get_supplier_id(),
                    # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                    updated_by=emp_id,
                    updated_date=now())
                invhdr = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.INVOICEHEADER)

            else:
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_bran = api_serv.get_empsingle_id(request, emp['id'])
                emp_bran1 = emp_bran['employee_branch']
                emp1 = api_serv.get_empbranch_id(request, emp_bran1)
                # emp = api_serv.get_empsingle_id(request, emp_id)
                # print('emp2', emp1)
                emp_add1 = emp1['gstin']
                print(emp_add1)
                emp_branch = emp1['name']
                emp_code = emp1['code']
                print('branch', emp_add1)
                # if invhdr_obj.get_supplier_id() != '' or None:
                #     supp = api_serv.get_supliersingle_id(request, invhdr_obj.get_supplier_id())
                #     supgst = supp['gstno']
                #     print("supp", supgst)
                #     if supgst != emp_add1:
                #         gsttype = 'IGST'
                #     else:
                #         gsttype = 'SGST & CGST'
                # supgst=''
                invhdr = InvoiceHeader.objects.using(self._current_app_schema()).create(
                    ecfheader_id=ecf_id,
                    invoiceno=invhdr_obj.get_invoiceno(),
                    dedupinvoiceno=invhdr_obj.get_dedupinvoiceno(),
                    invoicedate=invhdr_obj.get_invoicedate(),
                    # suppliergst=supgst,
                    raisorbranchgst=emp1['gstin'],
                    invoiceamount=invhdr_obj.get_invoiceamount(),
                    taxamount=invhdr_obj.get_taxamount(),
                    totalamount=invhdr_obj.get_totalamount(),
                    otheramount=invhdr_obj.get_otheramount(),
                    roundoffamt=invhdr_obj.get_roundoffamt(),
                    invoicegst=invhdr_obj.get_invoicegst(),
                    # supplier_id=invhdr_obj.get_supplier_id(),
                    # supplierstate_id=invhdr_obj.get_supplierstate_id(),
                    created_by=emp_id,entity_id=self._entity_id())
                # file data insert here
                if file_data != None and len(file_data) > 0:
                    for file_json in file_data:
                        from apservice.service.apdocumentservice import APDocumentService
                        apdoc_serv = ECFDocumentService(self._scope())
                        file_json['id'] = file_json['file_id']
                        apdoc_serv.ecfdocumentcreate(request, file_json, invhdr.id, emp_id)

                self.audit_function(invhdr, invhdr.id, invhdr.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.INVOICEHEADER)

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
            # inhdr_data.set_supplier(invhdr.supplier_id)
            # inhdr_data.set_supplierstate(invhdr.supplierstate_id)
            # if invhdr_obj.get_supplier_id() != '':
            #     inhdr_data.set_gsttype(gsttype)
                # inhdr_data.set_supgstno(supgst)
            return inhdr_data
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
        audit_obj.set_reftype(ECFRefType.INVOICEHEADER)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.INVOICEHEADER)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def upload(self,document_json,header_id,emp_id):
        arrdoc = []
        for doc_json in document_json:
            dtpcdocument = ECFFiles.objects.using(self._current_app_schema()).create(
                ecffile_id=header_id,
                file_id=doc_json['id'],
                file_name=doc_json['file_name'],
                # gen_file_name=doc_json['gen_file_name'],
                created_by=emp_id,entity_id=self._entity_id()
            )
        arrdoc.append(dtpcdocument)
        print("save")

    # def uplode_ecf(self,invhdr,header_id,emp_id):
    #     arrdoc = []
    #     for doc_json in invhdr:
    #         dtpcdocument = ECFFiles.objects.using(self._current_app_schema()).create(
    #             ecffile_id=header_id,
    #             file_id=doc_json['id'],
    #             file_name=doc_json['file1'],
    #             # gen_file_name=doc_json['gen_file_name'],
    #             created_by=emp_id
    #         )
    #         arrdoc.append(dtpcdocument)
    #     print("save")
