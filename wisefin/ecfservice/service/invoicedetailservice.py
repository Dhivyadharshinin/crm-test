import json
import traceback

from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import Invoicedetail, InvoicePO, InvoiceHeader, ECFQueue, ECFHeader, Debit, ccbsdtl
# from userservice.models.usermodels import Employee
# from masterservice.models.mastermodels import Hsn
from ecfservice.service.ecfauditservice import ECFAuditService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType
from ecfservice.data.response.invoicedetailresponse import Invoicedetailresponse, Debitresponse, ccbsdtlresponse
from django.db.models import Q
from datetime import datetime, timedelta, date
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType,Type,PPX,Pay,ECFStatus
from masterservice.models import Hsn
from django.utils.timezone import now
from django.db import IntegrityError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service import api_service
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class InvoicedetailService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def invdtlcreate(self,invdtl_obj,emp_id):
        inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id())
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr",ecfhdr)
        type = ecfhdr.ecftype
        amt = inv.totalamount
        if type == Type.NON_PO:
            if (amt != invdtl_obj.get_dtltotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if invdtl_obj.get_invoice_po() != "":
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                                                                                            mepno = invdtl_obj.get_mepno(),
                                                                                            invoice_po=invdtl_obj.get_invoice_po(),
                                                                                            productcode=invdtl_obj.get_productcode(),
                                                                                            productname=invdtl_obj.get_productname(),
                                                                                            description=invdtl_obj.get_description(),
                                                                                            hsn=invdtl_obj.get_hsn(),
                                                                                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                                                                                            uom=invdtl_obj.get_uom(),
                                                                                            unitprice=invdtl_obj.get_unitprice(),
                                                                                            quantity=invdtl_obj.get_quantity(),
                                                                                            amount=invdtl_obj.get_amount(),
                                                                                            discount=invdtl_obj.get_discount(),
                                                                                            sgst=invdtl_obj.get_sgst(),
                                                                                            cgst=invdtl_obj.get_cgst(),
                                                                                            igst=invdtl_obj.get_igst(),
                                                                                            taxamount=invdtl_obj.get_taxamount(),
                                                                                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                                                                                            # invoiceno = invdtl_obj.get_invoiceno(),
                                                                                            # invoicedate = invdtl_obj.get_invoicedate(),
                                                                                            # supplier_name = invdtl_obj.get_supplier_name(),
                                                                                            # suppliergst = invdtl_obj.get_suppliergst(),
                                                                                            # pincode =invdtl_obj.get_pincode(),
                                                                                            updated_by=emp_id,
                                                                                            updated_date=now())

                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                                                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                                                            mepno=invdtl_obj.get_mepno(),
                                                            invoice_po=invdtl_obj.get_invoice_po(),
                                                            productcode=invdtl_obj.get_productcode(),
                                                            productname=invdtl_obj.get_productname(),
                                                            description=invdtl_obj.get_description(),
                                                            hsn=invdtl_obj.get_hsn(),
                                                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                                                            uom=invdtl_obj.get_uom(),
                                                            unitprice=invdtl_obj.get_unitprice(),
                                                            quantity=invdtl_obj.get_quantity(),
                                                            amount=invdtl_obj.get_amount(),
                                                            discount=invdtl_obj.get_discount(),
                                                            sgst=invdtl_obj.get_sgst(),
                                                            cgst=invdtl_obj.get_cgst(),
                                                            igst=invdtl_obj.get_igst(),
                                                            taxamount=invdtl_obj.get_taxamount(),
                                                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                                                            # invoiceno=invdtl_obj.get_invoiceno(),
                                                            # invoicedate=invdtl_obj.get_invoicedate(),
                                                            # supplier_name=invdtl_obj.get_supplier_name(),
                                                            # suppliergst=invdtl_obj.get_suppliergst(),
                                                            # pincode=invdtl_obj.get_pincode(),
                                                            created_by=emp_id,
                                                            created_date = now(),entity_id=self._entity_id())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                else:
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())

                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)


                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_mepno(invdtl.mepno)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(invdtl.hsn)
                    indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                    indtl_data.set_uom(invdtl.uom)
                    indtl_data.set_unitprice(invdtl.unitprice)
                    indtl_data.set_quantity(invdtl.quantity)
                    indtl_data.set_amount(invdtl.amount)
                    indtl_data.set_discount(invdtl.discount)
                    indtl_data.set_sgst(invdtl.sgst)
                    indtl_data.set_cgst(invdtl.cgst)
                    indtl_data.set_igst(invdtl.igst)
                    indtl_data.set_otheramount(invdtl.otheramount)
                    indtl_data.set_roundoffamt(invdtl.roundoffamt)
                    indtl_data.set_taxamount(invdtl.taxamount)
                    indtl_data.set_totalamount(invdtl.totalamount)
                    return indtl_data
        elif type == Type.ERA:
            if (amt != invdtl_obj.get_dtltotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if invdtl_obj.get_invoice_po() != "":
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            invoice_po=invdtl_obj.get_invoice_po(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            updated_by=emp_id,
                            updated_date=now())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            invoice_po=invdtl_obj.get_invoice_po(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())
                else:
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            updated_by=emp_id,
                            updated_date=now())
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            created_by=emp_id,entity_id=self._entity_id())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)

                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_mepno(invdtl.mepno)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(invdtl.hsn)
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
                    return indtl_data
        elif type == Type.ADVANCE:
            # if (amt != invdtl_obj.get_dtltotalamt()):
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            # else:
                if invdtl_obj.get_invoice_po() != "":
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                                                                                            mepno = "",
                                                                                            invoice_po="",
                                                                                            productcode="dummy",
                                                                                            productname="dummy",
                                                                                            description="Hardcode",
                                                                                            hsn="00000000-0",
                                                                                            hsn_percentage=0,
                                                                                            uom="Number",
                                                                                            unitprice=invdtl_obj.get_unitprice(),
                                                                                            quantity=1,
                                                                                            amount=invdtl_obj.get_amount(),
                                                                                            discount=0,
                                                                                            sgst=0,
                                                                                            cgst=0,
                                                                                            igst=0,
                                                                                            taxamount=0,
                                                                                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                                                                                            # invoiceno = invdtl_obj.get_invoiceno(),
                                                                                            # invoicedate = invdtl_obj.get_invoicedate(),
                                                                                            # supplier_name = invdtl_obj.get_supplier_name(),
                                                                                            # suppliergst = invdtl_obj.get_suppliergst(),
                                                                                            # pincode =invdtl_obj.get_pincode(),
                                                                                            updated_by=emp_id,
                                                                                            updated_date=now())

                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno="",
                            invoice_po=invdtl_obj.get_invoice_po(),
                            productcode="dummy",
                            productname="dummy",
                            description="Hardcode",
                            hsn="00000000-0",
                            hsn_percentage=0,
                            uom="Number",
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=1,
                            amount=invdtl_obj.get_amount(),
                            discount=0,
                            sgst=0,
                            cgst=0,
                            igst=0,
                            taxamount=0,
                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=0,
                            roundoffamt=0,
                                                            # invoiceno=invdtl_obj.get_invoiceno(),
                                                            # invoicedate=invdtl_obj.get_invoicedate(),
                                                            # supplier_name=invdtl_obj.get_supplier_name(),
                                                            # suppliergst=invdtl_obj.get_suppliergst(),
                                                            # pincode=invdtl_obj.get_pincode(),
                                                            created_by=emp_id,
                                                            created_date = now(),entity_id=self._entity_id())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                else:
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            updated_by=emp_id,
                            updated_date=now())
                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())

                        invhdr = InvoiceHeader.objects.using(self._current_app_schema()).filter(
                            id=invdtl_obj.get_invoiceheader_id(), entity_id=self._entity_id()).update(
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt()
                        )

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)


                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_mepno(invdtl.mepno)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(invdtl.hsn)
                    indtl_data.set_hsn_percentage(invdtl.hsn_percentage)
                    indtl_data.set_uom(invdtl.uom)
                    indtl_data.set_unitprice(invdtl.unitprice)
                    indtl_data.set_quantity(invdtl.quantity)
                    indtl_data.set_amount(invdtl.amount)
                    indtl_data.set_discount(invdtl.discount)
                    indtl_data.set_sgst(invdtl.sgst)
                    indtl_data.set_cgst(invdtl.cgst)
                    indtl_data.set_igst(invdtl.igst)
                    indtl_data.set_otheramount(invdtl.otheramount)
                    indtl_data.set_roundoffamt(invdtl.roundoffamt)
                    indtl_data.set_taxamount(invdtl.taxamount)
                    indtl_data.set_totalamount(invdtl.totalamount)
                    return indtl_data

    def invdtlppx(self,inv_id,ecf_amt, emp_id):
            try:
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                                                        invoiceheader_id=inv_id,
                                                        invoice_po="",
                                                        productcode="NOCODE",
                                                        productname="NONE",
                                                        description="NONE",
                                                        hsn="NOHSN",
                                                        hsn_percentage=0,
                                                        uom="",
                                                        unitprice=ecf_amt,
                                                        quantity=1,
                                                        amount=ecf_amt,
                                                        discount=0,
                                                        sgst=0,
                                                        cgst=0,
                                                        igst=0,
                                                        taxamount=0,
                                                        totalamount=ecf_amt,
                                                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)
            except IntegrityError as error:
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

            indtl_data = Invoicedetailresponse()
            indtl_data.set_id(invdtl.id)
            indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
            indtl_data.set_invoice_po(invdtl.invoice_po)
            indtl_data.set_productcode(invdtl.productcode)
            indtl_data.set_productname(invdtl.productname)
            indtl_data.set_description(invdtl.description)
            indtl_data.set_hsn(invdtl.hsn)
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
            return indtl_data
    def taxcalculation(self,tax_obj,code):
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        hsncode = api_serv.get_hsn(code)
        sgstrate = float(hsncode['sgstrate'])
        cgstrate = float(hsncode['cgstrate'])
        igstrate = float(hsncode['igstrate'])

        if (tax_obj['discount'] == 0):
            print('unitprice ',tax_obj['unitprice'],tax_obj['qty'] , sgstrate)

            sgst = ((float(tax_obj['unitprice'])*float(tax_obj['qty'])) * float(sgstrate)) / 100
            s_gst = round(sgst, 2)
            cgst = ((float(tax_obj['unitprice'])*float(tax_obj['qty'])) * float(cgstrate)) / 100
            c_gst = round(cgst, 2)
            igst = ((float(tax_obj['unitprice'])*float(tax_obj['qty'])) * float(igstrate)) / 100
            i_gst = round(igst, 2)
            cs_gst = s_gst + c_gst
            c_s_gst = round(cs_gst, 2)
        else:
            sgst = (((float(tax_obj['unitprice']) * float(tax_obj['qty']))-float(tax_obj['discount'])) * float(sgstrate)) / 100
            s_gst = round(sgst, 2)
            cgst = (((float(tax_obj['unitprice']) * float(tax_obj['qty']))-float(tax_obj['discount'])) * float(cgstrate)) / 100
            c_gst = round(cgst, 2)
            igst = (((float(tax_obj['unitprice']) * float(tax_obj['qty']))-float(tax_obj['discount'])) * float(igstrate)) / 100
            i_gst = round(igst, 2)
            cs_gst = s_gst + c_gst
            c_s_gst = round(cs_gst, 2)
        if (tax_obj['type'] == 'IGST'):
            indtl_data = Invoicedetailresponse()
            indtl_data.set_igst(i_gst)
            indtl_data.set_sgst(0)
            indtl_data.set_cgst(0)

        else :
            indtl_data = Invoicedetailresponse()
            indtl_data.set_igst(0)
            indtl_data.set_sgst(s_gst)
            indtl_data.set_cgst(c_gst)
        return indtl_data

    def fetch_single_invdtl(self,request,invdtl_id,emp_id):
        try:
            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_id,entity_id=self._entity_id())
            condition = Q(invoicedetail_id=invdtl_id) & Q(status=1)
            deb_list = Debit.objects.using(self._current_app_schema()).filter(condition).all()
            indtl=[]
            debit_list=[]
            print('invdtl',invdtl)
            print('dbt',len(deb_list))
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
            if len(deb_list) != 0:
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
                    if len(ccb_list) != 0:
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
                    # else:
                    #     ccbs_data = ccbsdtlresponse()
                    #     ccbs_data.set_id("")
                    #     ccbs_data.set_debit("")
                    #     ccbs_data.set_cc_code("")
                    #     ccbs_data.set_bs_code("")
                    #     ccbs_data.set_code("")
                    #     ccbs_data.set_ccbspercentage("")
                    #     ccbs_data.set_glno("")
                    #     ccbs_data.set_amount("")
                    #     ccbs_data.set_remarks("")
                    #     ccbs_list.append(json.loads(ccbs_data.get()))
                    #     dbt_data.set_ccbs(ccbs_data)
                    debit_list.append(json.loads(dbt_data.get()))
            indtl_data.set_debit(debit_list)
            # else:
            #     dbt_data = Debitresponse()
            #     dbt_data.set_id("")
            #     dbt_data.set_invoiceheader("")
            #     dbt_data.set_invoicedetail("")
            #     dbt_data.set_category_code("")
            #     dbt_data.set_subcategory_code("")
            #     dbt_data.set_debitglno("")
            #     dbt_data.set_amount("")
            #     dbt_data.set_deductionamount("")
            #     ccbs_list = []
            #     ccbs_data = ccbsdtlresponse()
            #     ccbs_data.set_id("")
            #     ccbs_data.set_debit("")
            #     ccbs_data.set_cc_code("")
            #     ccbs_data.set_bs_code("")
            #     ccbs_data.set_code("")
            #     ccbs_data.set_ccbspercentage("")
            #     ccbs_data.set_glno("")
            #     ccbs_data.set_amount("")
            #     ccbs_data.set_remarks("")
            #     ccbs_list.append(json.loads(ccbs_data.get()))
            #     dbt_data.set_ccbs(ccbs_data)
            #     debit_list.append(json.loads(dbt_data.get()))
            #     indtl_data.set_debit(debit_list)
            return indtl_data
        except Exception as ex:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INVOICE_ID)
            error_obj.set_description(str(ex))
            return error_obj

    def Delete_invdtl(self,request, invdtl_id, emp_id):
        try:
            Invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())

            deb = Debit.objects.using(self._current_app_schema()).filter(invoicedetail_id=invdtl_id,entity_id=self._entity_id()).update(
                status=0,
                updated_by=emp_id,
                updated_date=now())
            invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_id,entity_id=self._entity_id())
            for i in range(deb):
                deb = Debit.objects.using(self._current_app_schema()).filter(invoicedetail_id=i,entity_id=self._entity_id())
            self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=invdtl.id, ref_type=ECFRefType.INVOICEDETAIL, from_user_id=emp_id,
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

    def invdtlmodcreate(self,invdtl_obj,emp_id):
        inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id())
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr", ecfhdr)
        type = ecfhdr.ecftype
        amt = inv.totalamount
        if type == Type.NON_PO:
            if (amt != invdtl_obj.get_dtltotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if invdtl_obj.get_invoice_po() != "":
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                                                                                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                                                                                            mepno = invdtl_obj.get_mepno(),
                                                                                            invoice_po=invdtl_obj.get_invoice_po(),
                                                                                            productcode=invdtl_obj.get_productcode(),
                                                                                            productname=invdtl_obj.get_productname(),
                                                                                            description=invdtl_obj.get_description(),
                                                                                            hsn=invdtl_obj.get_hsn(),
                                                                                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                                                                                            uom=invdtl_obj.get_uom(),
                                                                                            unitprice=invdtl_obj.get_unitprice(),
                                                                                            quantity=invdtl_obj.get_quantity(),
                                                                                            amount=invdtl_obj.get_amount(),
                                                                                            discount=invdtl_obj.get_discount(),
                                                                                            sgst=invdtl_obj.get_sgst(),
                                                                                            cgst=invdtl_obj.get_cgst(),
                                                                                            igst=invdtl_obj.get_igst(),
                                                                                            taxamount=invdtl_obj.get_taxamount(),
                                                                                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                                                                                            updated_by=emp_id,
                                                                                            updated_date=now())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                                                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                                                            mepno=invdtl_obj.get_mepno(),
                                                            invoice_po=invdtl_obj.get_invoice_po(),
                                                            productcode=invdtl_obj.get_productcode(),
                                                            productname=invdtl_obj.get_productname(),
                                                            description=invdtl_obj.get_description(),
                                                            hsn=invdtl_obj.get_hsn(),
                                                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                                                            uom=invdtl_obj.get_uom(),
                                                            unitprice=invdtl_obj.get_unitprice(),
                                                            quantity=invdtl_obj.get_quantity(),
                                                            amount=invdtl_obj.get_amount(),
                                                            discount=invdtl_obj.get_discount(),
                                                            sgst=invdtl_obj.get_sgst(),
                                                            cgst=invdtl_obj.get_cgst(),
                                                            igst=invdtl_obj.get_igst(),
                                                            taxamount=invdtl_obj.get_taxamount(),
                                                            totalamount=invdtl_obj.get_totalamount(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                                                            created_by=emp_id,
                                                            created_date = now(),entity_id=self._entity_id())
                else:
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            updated_by=emp_id,
                            updated_date=now())
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id(),entity_id=self._entity_id())
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            # invoiceno=invdtl_obj.get_invoiceno(),
                            # invoicedate=invdtl_obj.get_invoicedate(),
                            # supplier_name=invdtl_obj.get_supplier_name(),
                            # suppliergst=invdtl_obj.get_suppliergst(),
                            # pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)

                    invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id())
                    invhdr = invhdr1[0]

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

                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_mepno(invdtl.mepno)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(invdtl.hsn)
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
                    return indtl_data
        elif type == Type.ERA:
            if (amt != invdtl_obj.get_dtltotalamt()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                return error_obj
            else:
                if invdtl_obj.get_invoice_po() != "":
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            invoice_po=invdtl_obj.get_invoice_po(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            updated_by=emp_id,
                            updated_date=now())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            invoice_po=invdtl_obj.get_invoice_po(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())
                else:
                    if not invdtl_obj.get_id() is None:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            updated_by=emp_id,
                            updated_date=now())
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id())
                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                    else:
                        invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                            invoiceheader_id=invdtl_obj.get_invoiceheader_id(),
                            mepno=invdtl_obj.get_mepno(),
                            productcode=invdtl_obj.get_productcode(),
                            productname=invdtl_obj.get_productname(),
                            description=invdtl_obj.get_description(),
                            hsn=invdtl_obj.get_hsn(),
                            hsn_percentage=invdtl_obj.get_hsn_percentage(),
                            uom=invdtl_obj.get_uom(),
                            unitprice=invdtl_obj.get_unitprice(),
                            quantity=invdtl_obj.get_quantity(),
                            amount=invdtl_obj.get_amount(),
                            discount=invdtl_obj.get_discount(),
                            sgst=invdtl_obj.get_sgst(),
                            cgst=invdtl_obj.get_cgst(),
                            igst=invdtl_obj.get_igst(),
                            taxamount=invdtl_obj.get_taxamount(),
                            totalamount=invdtl_obj.get_totalamount(),
                            invoiceno=invdtl_obj.get_invoiceno(),
                            invoicedate=invdtl_obj.get_invoicedate(),
                            supplier_name=invdtl_obj.get_supplier_name(),
                            suppliergst=invdtl_obj.get_suppliergst(),
                            pincode=invdtl_obj.get_pincode(),
                            otheramount=invdtl_obj.get_otheramount(),
                            roundoffamt=invdtl_obj.get_roundoffamt(),
                            created_by=emp_id,
                            created_date = now(),entity_id=self._entity_id())

                        self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                            ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)

                    invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_invoiceheader_id(),entity_id=self._entity_id())
                    invhdr = invhdr1[0]

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

                    indtl_data = Invoicedetailresponse()
                    indtl_data.set_id(invdtl.id)
                    indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                    indtl_data.set_invoice_po(invdtl.invoice_po)
                    indtl_data.set_mepno(invdtl.mepno)
                    indtl_data.set_productcode(invdtl.productcode)
                    indtl_data.set_productname(invdtl.productname)
                    indtl_data.set_description(invdtl.description)
                    indtl_data.set_hsn(invdtl.hsn)
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
                    return indtl_data
    def invdtlccreate(self, invdtl_obj, hdr_id, emp_id):
        inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=hdr_id,entity_id=self._entity_id())
        amt = inv.totalamount
        if (amt != invdtl_obj.get_dtltotalamt()):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj
        else:
            if invdtl_obj.get_invoice_po() != "":
                if not invdtl_obj.get_id() is None:
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=hdr_id,
                        mepno=invdtl_obj.get_mepno(),
                        invoice_po=invdtl_obj.get_invoice_po(),
                        productcode=invdtl_obj.get_productcode(),
                        productname=invdtl_obj.get_productname(),
                        description=invdtl_obj.get_description(),
                        hsn=invdtl_obj.get_hsn(),
                        hsn_percentage=invdtl_obj.get_hsn_percentage(),
                        uom=invdtl_obj.get_uom(),
                        unitprice=invdtl_obj.get_unitprice(),
                        quantity=invdtl_obj.get_quantity(),
                        amount=invdtl_obj.get_amount(),
                        discount=invdtl_obj.get_discount(),
                        sgst=invdtl_obj.get_sgst(),
                        cgst=invdtl_obj.get_cgst(),
                        igst=invdtl_obj.get_igst(),
                        taxamount=invdtl_obj.get_taxamount(),
                        totalamount=invdtl_obj.get_totalamount(),
                        otheramount=invdtl_obj.get_otheramount(),
                        roundoffamt=invdtl_obj.get_roundoffamt(),
                        updated_by=emp_id,
                        updated_date=now())

                    self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                else:
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                        invoiceheader_id=hdr_id,
                        mepno=invdtl_obj.get_mepno(),
                        invoice_po=invdtl_obj.get_invoice_po(),
                        productcode=invdtl_obj.get_productcode(),
                        productname=invdtl_obj.get_productname(),
                        description=invdtl_obj.get_description(),
                        hsn=invdtl_obj.get_hsn(),
                        hsn_percentage=invdtl_obj.get_hsn_percentage(),
                        uom=invdtl_obj.get_uom(),
                        unitprice=invdtl_obj.get_unitprice(),
                        quantity=invdtl_obj.get_quantity(),
                        amount=invdtl_obj.get_amount(),
                        discount=invdtl_obj.get_discount(),
                        sgst=invdtl_obj.get_sgst(),
                        cgst=invdtl_obj.get_cgst(),
                        igst=invdtl_obj.get_igst(),
                        taxamount=invdtl_obj.get_taxamount(),
                        totalamount=invdtl_obj.get_totalamount(),
                        otheramount=invdtl_obj.get_otheramount(),
                        roundoffamt=invdtl_obj.get_roundoffamt(),
                        created_by=emp_id,entity_id=self._entity_id())
            else:
                if not invdtl_obj.get_id() is None:
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).filter(id=invdtl_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=hdr_id,
                        mepno=invdtl_obj.get_mepno(),
                        productcode=invdtl_obj.get_productcode(),
                        productname=invdtl_obj.get_productname(),
                        description=invdtl_obj.get_description(),
                        hsn=invdtl_obj.get_hsn(),
                        hsn_percentage=invdtl_obj.get_hsn_percentage(),
                        uom=invdtl_obj.get_uom(),
                        unitprice=invdtl_obj.get_unitprice(),
                        quantity=invdtl_obj.get_quantity(),
                        amount=invdtl_obj.get_amount(),
                        discount=invdtl_obj.get_discount(),
                        sgst=invdtl_obj.get_sgst(),
                        cgst=invdtl_obj.get_cgst(),
                        igst=invdtl_obj.get_igst(),
                        taxamount=invdtl_obj.get_taxamount(),
                        totalamount=invdtl_obj.get_totalamount(),
                        otheramount=invdtl_obj.get_otheramount(),
                        roundoffamt=invdtl_obj.get_roundoffamt(),
                        updated_by=emp_id,
                        updated_date=now())
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).get(id=invdtl_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.INVOICEDETAIL)

                else:
                    invdtl = Invoicedetail.objects.using(self._current_app_schema()).create(
                        invoiceheader_id=hdr_id,
                        mepno=invdtl_obj.get_mepno(),
                        productcode=invdtl_obj.get_productcode(),
                        productname=invdtl_obj.get_productname(),
                        description=invdtl_obj.get_description(),
                        hsn=invdtl_obj.get_hsn(),
                        hsn_percentage=invdtl_obj.get_hsn_percentage(),
                        uom=invdtl_obj.get_uom(),
                        unitprice=invdtl_obj.get_unitprice(),
                        quantity=invdtl_obj.get_quantity(),
                        amount=invdtl_obj.get_amount(),
                        discount=invdtl_obj.get_discount(),
                        sgst=invdtl_obj.get_sgst(),
                        cgst=invdtl_obj.get_cgst(),
                        igst=invdtl_obj.get_igst(),
                        taxamount=invdtl_obj.get_taxamount(),
                        totalamount=invdtl_obj.get_totalamount(),
                        otheramount=invdtl_obj.get_otheramount(),
                        roundoffamt=invdtl_obj.get_roundoffamt(),
                        created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(invdtl, invdtl.id, invdtl.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.INVOICEDETAIL)

                indtl_data = Invoicedetailresponse()
                indtl_data.set_id(invdtl.id)
                indtl_data.set_invoiceheader(invdtl.invoiceheader_id)
                indtl_data.set_invoice_po(invdtl.invoice_po)
                indtl_data.set_mepno(invdtl.mepno)
                indtl_data.set_productcode(invdtl.productcode)
                indtl_data.set_productname(invdtl.productname)
                indtl_data.set_description(invdtl.description)
                indtl_data.set_hsn(invdtl.hsn)
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
                return indtl_data
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
        audit_obj.set_reftype(ECFRefType.INVOICEDETAIL)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.INVOICEDETAIL)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)