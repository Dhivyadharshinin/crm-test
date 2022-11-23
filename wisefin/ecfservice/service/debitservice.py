import traceback

from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import Debit,ccbsdtl,Invoicedetail,InvoicePO,InvoiceHeader,ECFQueue,ECFHeader
from ecfservice.service.ecfauditservice import ECFAuditService
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType,Type
from ecfservice.data.response.invoicedetailresponse import Debitresponse,ccbsdtlresponse
from django.db.models import Q
from datetime import datetime, timedelta, date
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from django.utils.timezone import now
from django.db import IntegrityError

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DebitService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def debitcreate(self,dbt_obj,emp_id):
        inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr", ecfhdr)
        type = ecfhdr.ecftype
        if type == Type.NON_PO:
            invhdr = Invoicedetail.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoicedetail(),entity_id=self._entity_id())
            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr.invoiceheader_id,entity_id=self._entity_id())
            print("inv", inv)

            amt = invhdr.totalamount
            amttotal = inv.totalamount
            if (amt != dbt_obj.get_debittotal()):
                dbt_data = Debitresponse()
                dbt_data.set_id("")
                return dbt_data
            else:
                if not dbt_obj.get_id() is None:
                    dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                           invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                           category_code=dbt_obj.get_category_code(),
                                                                           subcategory_code=dbt_obj.get_subcategory_code(),
                                                                           debitglno=dbt_obj.get_debitglno(),
                                                                           amount=dbt_obj.get_amount(),
                                                                           deductionamount=dbt_obj.get_deductionamount(),
                                                                           bsproduct=dbt_obj.get_bsproduct(),
                                                                           updated_by=emp_id,
                                                                           updated_date=now())
                    dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
                else:
                    dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                invoicedetail_id = dbt_obj.get_invoicedetail(),
                                               category_code=dbt_obj.get_category_code(),
                                               subcategory_code=dbt_obj.get_subcategory_code(),
                                                debitglno = dbt_obj.get_debitglno(),
                                                amount = dbt_obj.get_amount(),
                                                deductionamount = dbt_obj.get_deductionamount(),
                                                                                 bsproduct=dbt_obj.get_bsproduct(),
                                                created_by=emp_id,entity_id=self._entity_id())

                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                                    ECFModifyStatus.CREATE, ECFRefType.DEBIT)


                dbt_data = Debitresponse()
                dbt_data.set_id(dbt.id)
                dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                dbt_data.set_category_code(dbt.category_code)
                dbt_data.set_subcategory_code(dbt.subcategory_code)
                dbt_data.set_debitglno(dbt.debitglno)
                dbt_data.set_amount(dbt.amount)
                dbt_data.set_bsproduct(dbt.bsproduct)
                dbt_data.set_deductionamount(dbt.deductionamount)
                return dbt_data
        elif type == Type.ERA:
            invhdr = Invoicedetail.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoicedetail(),entity_id=self._entity_id())
            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr.invoiceheader_id,entity_id=self._entity_id())
            print("inv", inv)
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
            print("ecfhdr", ecfhdr)
            type = ecfhdr.ecftype
            amt = invhdr.totalamount
            amttotal = inv.totalamount
            if (amt != dbt_obj.get_debittotal()):
                dbt_data = Debitresponse()
                dbt_data.set_id("")
                return dbt_data
            else:
                if not dbt_obj.get_id() is None:
                    dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=dbt_obj.get_invoiceheader(),
                        invoicedetail_id=dbt_obj.get_invoicedetail(),
                        category_code=dbt_obj.get_category_code(),
                        subcategory_code=dbt_obj.get_subcategory_code(),
                        debitglno=dbt_obj.get_debitglno(),
                        amount=dbt_obj.get_amount(),
                        deductionamount=dbt_obj.get_deductionamount(),
                        bsproduct=dbt_obj.get_bsproduct(),
                        updated_by=emp_id,
                        updated_date=now())
                    dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
                else:
                    dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                      invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                      category_code=dbt_obj.get_category_code(),
                                                                      subcategory_code=dbt_obj.get_subcategory_code(),
                                                                      debitglno=dbt_obj.get_debitglno(),
                                                                      amount=dbt_obj.get_amount(),
                                                                      deductionamount=dbt_obj.get_deductionamount(),
                                                                                 bsproduct=dbt_obj.get_bsproduct(),
                                                                      created_by=emp_id,
                                                                      created_date = now(),entity_id=self._entity_id())

                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.DEBIT)

                dbt_data = Debitresponse()
                dbt_data.set_id(dbt.id)
                dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                dbt_data.set_category_code(dbt.category_code)
                dbt_data.set_subcategory_code(dbt.subcategory_code)
                dbt_data.set_debitglno(dbt.debitglno)
                dbt_data.set_amount(dbt.amount)
                dbt_data.set_bsproduct(dbt.bsproduct)
                dbt_data.set_deductionamount(dbt.deductionamount)
                return dbt_data
        elif type == Type.ADVANCE:

            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
            print("inv", inv)
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
            print("ecfhdr", dbt_obj.get_debittotal())
            type = ecfhdr.ecftype

            amttotal = inv.totalamount
            if (amttotal != dbt_obj.get_debittotal()):
                dbt_data = Debitresponse()
                dbt_data.set_id("")
                return dbt_data
            else:
                if not dbt_obj.get_id() is None:
                    dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(
                        invoiceheader_id=dbt_obj.get_invoiceheader(),
                        invoicedetail_id=dbt_obj.get_invoicedetail(),
                        category_code=dbt_obj.get_category_code(),
                        subcategory_code=dbt_obj.get_subcategory_code(),
                        debitglno=dbt_obj.get_debitglno(),
                        amount=dbt_obj.get_amount(),
                        deductionamount=dbt_obj.get_deductionamount(),
                        bsproduct=dbt_obj.get_bsproduct(),
                        updated_by=emp_id,
                        updated_date=now())
                    dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                        ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
                else:
                    dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                      invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                      category_code=dbt_obj.get_category_code(),
                                                                      subcategory_code=dbt_obj.get_subcategory_code(),
                                                                      debitglno=dbt_obj.get_debitglno(),
                                                                      amount=dbt_obj.get_amount(),
                                                                      deductionamount=dbt_obj.get_deductionamount(),
                                                                                 bsproduct=dbt_obj.get_bsproduct(),
                                                                      created_by=emp_id,
                                                                      created_date = now(),entity_id=self._entity_id())

                    self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                        ECFModifyStatus.CREATE, ECFRefType.DEBIT)

                dbt_data = Debitresponse()
                dbt_data.set_id(dbt.id)
                dbt_data.set_invoiceheader(dbt.invoiceheader_id)
                dbt_data.set_invoicedetail(dbt.invoicedetail_id)
                dbt_data.set_category_code(dbt.category_code)
                dbt_data.set_subcategory_code(dbt.subcategory_code)
                dbt_data.set_debitglno(dbt.debitglno)
                dbt_data.set_amount(dbt.amount)
                dbt_data.set_bsproduct(dbt.bsproduct)
                dbt_data.set_deductionamount(dbt.deductionamount)
                return dbt_data
    def ccbscreate(self,ccbs_obj,debit_id,emp_id):

        if not ccbs_obj.get_id() is None:
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).filter(id=ccbs_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        debit_id=debit_id,
                                                                        cc_code=ccbs_obj.get_cc_code(),
                                                                        bs_code=ccbs_obj.get_bs_code(),
                                                                        code=ccbs_obj.get_code(),
                                                                        ccbspercentage=ccbs_obj.get_ccbspercentage(),
                                                                        glno=ccbs_obj.get_glno(),
                                                                        amount=ccbs_obj.get_amount(),
                                                                        remarks=ccbs_obj.get_remarks(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).get(id=ccbs_obj.get_id(),entity_id=self._entity_id())

        else:
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).create(
                                            debit_id=debit_id,
                                            cc_code = ccbs_obj.get_cc_code(),
                                            bs_code = ccbs_obj.get_bs_code(),
                                            code = ccbs_obj.get_code(),
                                            ccbspercentage = ccbs_obj.get_ccbspercentage(),
                                            glno = ccbs_obj.get_glno(),
                                            amount = ccbs_obj.get_amount(),
                                            remarks = ccbs_obj.get_remarks(),
                                            created_by=emp_id,entity_id=self._entity_id())

        ccbs_data = ccbsdtlresponse()
        ccbs_data.set_id(ccbs.id)
        ccbs_data.set_debit(ccbs.debit_id)
        ccbs_data.set_cc_code(ccbs.cc_code)
        ccbs_data.set_bs_code(ccbs.bs_code)
        ccbs_data.set_code(ccbs.code)
        ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
        ccbs_data.set_glno(ccbs.glno)
        ccbs_data.set_amount(ccbs.amount)
        ccbs_data.set_remarks(ccbs.remarks)
        return ccbs_data
    def Delete_debit(self,request, dbt_id, emp_id):
        try:
            dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_id,entity_id=self._entity_id())
            self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=dbt.id, ref_type=ECFRefType.DEBIT, from_user_id=emp_id,
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

    def debitmodcreate(self,dbt_obj,emp_id):

        inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
        print("inv", inv)
        ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
        print("ecfhdr", ecfhdr)
        type = ecfhdr.ecftype

        if type == Type.NON_PO:
            invhdr = Invoicedetail.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoicedetail(),entity_id=self._entity_id())
            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr.invoiceheader_id,entity_id=self._entity_id())
            print("inv", inv)
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
            print("ecfhdr", ecfhdr)
            type = ecfhdr.ecftype
            amt = invhdr.totalamount
            if not dbt_obj.get_id() is None:
                dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                       invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                       category_code=dbt_obj.get_category_code(),
                                                                       subcategory_code=dbt_obj.get_subcategory_code(),
                                                                       debitglno=dbt_obj.get_debitglno(),
                                                                       amount=dbt_obj.get_amount(),
                                                                       deductionamount=dbt_obj.get_deductionamount(),
                                                                                                                                     bsproduct=dbt_obj.get_bsproduct(),
                                                                       updated_by=emp_id,
                                                                       updated_date=now())
                dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            else:
                dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                            invoicedetail_id = dbt_obj.get_invoicedetail(),
                                           category_code=dbt_obj.get_category_code(),
                                           subcategory_code=dbt_obj.get_subcategory_code(),
                                            debitglno = dbt_obj.get_debitglno(),
                                            amount = dbt_obj.get_amount(),
                                            deductionamount = dbt_obj.get_deductionamount(),
                                                                             bsproduct=dbt_obj.get_bsproduct(),
                                            created_by=emp_id,entity_id=self._entity_id())

                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                                ECFModifyStatus.CREATE, ECFRefType.DEBIT)

            invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
            invhdr = invhdr1[0]

            Ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=invhdr.ecfheader_id)
            self.audit_function(Ecfhdr, Ecfhdr.id, Ecfhdr.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.ECFHEADER)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=Ecfhdr.id, ref_type=ECFRefType.ECFHEADER,
                                                           from_user_id=emp_id,
                                                           to_user_id=emp_id,
                                                           created_date=now(),
                                                           comments="PENDING  FOR APPROVAL MODIFICATION",
                                                           is_sys=True,entity_id=self._entity_id()
                                                           )


            dbt_data = Debitresponse()
            dbt_data.set_id(dbt.id)
            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
            dbt_data.set_category_code(dbt.category_code)
            dbt_data.set_subcategory_code(dbt.subcategory_code)
            dbt_data.set_debitglno(dbt.debitglno)
            dbt_data.set_amount(dbt.amount)
            dbt_data.set_bsproduct(dbt.bsproduct)
            dbt_data.set_deductionamount(dbt.deductionamount)
            return dbt_data
        elif type == Type.ERA:
            invhdr = Invoicedetail.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoicedetail(),entity_id=self._entity_id())
            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=invhdr.invoiceheader_id,entity_id=self._entity_id())
            print("inv", inv)
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
            print("ecfhdr", ecfhdr)
            type = ecfhdr.ecftype
            amt = invhdr.totalamount
            if not dbt_obj.get_id() is None:
                dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(
                    invoiceheader_id=dbt_obj.get_invoiceheader(),
                    invoicedetail_id=dbt_obj.get_invoicedetail(),
                    category_code=dbt_obj.get_category_code(),
                    subcategory_code=dbt_obj.get_subcategory_code(),
                    debitglno=dbt_obj.get_debitglno(),
                    amount=dbt_obj.get_amount(),
                    deductionamount=dbt_obj.get_deductionamount(),
                    bsproduct=dbt_obj.get_bsproduct(),
                    updated_by=emp_id,
                    updated_date=now())
                dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            else:
                dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                  invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                  category_code=dbt_obj.get_category_code(),
                                                                  subcategory_code=dbt_obj.get_subcategory_code(),
                                                                  debitglno=dbt_obj.get_debitglno(),
                                                                  amount=dbt_obj.get_amount(),
                                                                  deductionamount=dbt_obj.get_deductionamount(),
                                                                             bsproduct=dbt_obj.get_bsproduct(),
                                                                  created_by=emp_id,entity_id=self._entity_id())

                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.DEBIT)

            invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
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

            dbt_data = Debitresponse()
            dbt_data.set_id(dbt.id)
            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
            dbt_data.set_category_code(dbt.category_code)
            dbt_data.set_subcategory_code(dbt.subcategory_code)
            dbt_data.set_debitglno(dbt.debitglno)
            dbt_data.set_amount(dbt.amount)
            dbt_data.set_bsproduct(dbt.bsproduct)
            dbt_data.set_deductionamount(dbt.deductionamount)
            return dbt_data
        elif type == Type.ADVANCE:

            inv = InvoiceHeader.objects.using(self._current_app_schema()).get(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
            print("inv", inv)
            ecfhdr = ECFHeader.objects.using(self._current_app_schema()).get(id=inv.ecfheader_id,entity_id=self._entity_id())
            print("ecfhdr", ecfhdr)
            type = ecfhdr.ecftype
            amttotal = inv.totalamount
            if not dbt_obj.get_id() is None:
                dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(
                    invoiceheader_id=dbt_obj.get_invoiceheader(),
                    invoicedetail_id=dbt_obj.get_invoicedetail(),
                    category_code=dbt_obj.get_category_code(),
                    subcategory_code=dbt_obj.get_subcategory_code(),
                    debitglno=dbt_obj.get_debitglno(),
                    amount=dbt_obj.get_amount(),
                    deductionamount=dbt_obj.get_deductionamount(),
                    bsproduct=dbt_obj.get_bsproduct(),
                    updated_by=emp_id,
                    updated_date=now())
                dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            else:
                dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                  invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                  category_code=dbt_obj.get_category_code(),
                                                                  subcategory_code=dbt_obj.get_subcategory_code(),
                                                                  debitglno=dbt_obj.get_debitglno(),
                                                                  amount=dbt_obj.get_amount(),
                                                                  deductionamount=dbt_obj.get_deductionamount(),
                                                                             bsproduct=dbt_obj.get_bsproduct(),
                                                                  created_by=emp_id,entity_id=self._entity_id())

                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.CREATE, ECFRefType.DEBIT)

            invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_invoiceheader(),entity_id=self._entity_id())
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

            dbt_data = Debitresponse()
            dbt_data.set_id(dbt.id)
            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
            dbt_data.set_category_code(dbt.category_code)
            dbt_data.set_subcategory_code(dbt.subcategory_code)
            dbt_data.set_debitglno(dbt.debitglno)
            dbt_data.set_amount(dbt.amount)
            dbt_data.set_bsproduct(dbt.bsproduct)
            dbt_data.set_deductionamount(dbt.deductionamount)
            return dbt_data

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
        audit_obj.set_reftype(ECFRefType.DEBIT)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.DEBIT)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def Delete_debit(self,request, dbt_id, emp_id):
        try:
            dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_id,entity_id=self._entity_id())
            self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            ECFQueue.objects.using(self._current_app_schema()).create(ref_id=dbt.id, ref_type=ECFRefType.DEBIT, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    def debitccreate(self,dbt_obj,dbt_id,emp_id):
        invhdr = Invoicedetail.objects.using(self._current_app_schema()).get(id=dbt_id,entity_id=self._entity_id())
        invhdr_id = invhdr.invoiceheader_id
        amt = invhdr.totalamount
        if (amt != dbt_obj.get_debittotal()):
            dbt_data = Debitresponse()
            dbt_data.set_id("")
            return dbt_data
        else:
            if not dbt_obj.get_id() is None:
                dbt = Debit.objects.using(self._current_app_schema()).filter(id=dbt_obj.get_id(),entity_id=self._entity_id()).update(invoiceheader_id=dbt_obj.get_invoiceheader(),
                                                                       invoicedetail_id=dbt_obj.get_invoicedetail(),
                                                                       category_code=dbt_obj.get_category_code(),
                                                                       subcategory_code=dbt_obj.get_subcategory_code(),
                                                                       debitglno=dbt_obj.get_debitglno(),
                                                                       amount=dbt_obj.get_amount(),
                                                                       deductionamount=dbt_obj.get_deductionamount(),
                                                                       updated_by=emp_id,
                                                                       updated_date=now())
                dbt = Debit.objects.using(self._current_app_schema()).get(id=dbt_obj.get_id(),entity_id=self._entity_id())
                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                    ECFModifyStatus.UPDATE, ECFRefType.DEBIT)
            else:
                dbt = Debit.objects.using(self._current_app_schema()).create(invoiceheader_id=invhdr_id,
                                            invoicedetail_id = dbt_id,
                                           category_code=dbt_obj.get_category_code(),
                                           subcategory_code=dbt_obj.get_subcategory_code(),
                                            debitglno = dbt_obj.get_debitglno(),
                                            amount = dbt_obj.get_amount(),
                                            deductionamount = dbt_obj.get_deductionamount(),
                                            created_by=emp_id,entity_id=self._entity_id())

                self.audit_function(dbt, dbt.id, dbt.id, emp_id,
                                                ECFModifyStatus.CREATE, ECFRefType.DEBIT)


            dbt_data = Debitresponse()
            dbt_data.set_id(dbt.id)
            dbt_data.set_invoiceheader(dbt.invoiceheader_id)
            dbt_data.set_invoicedetail(dbt.invoicedetail_id)
            dbt_data.set_category_code(dbt.category_code)
            dbt_data.set_subcategory_code(dbt.subcategory_code)
            dbt_data.set_debitglno(dbt.debitglno)
            dbt_data.set_amount(dbt.amount)
            dbt_data.set_deductionamount(dbt.deductionamount)
            return dbt_data


    def ccbsccreate(self,ccbs_obj,debit_id,emp_id):

        if not ccbs_obj.get_id() is None:
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).filter(id=ccbs_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        debit_id=debit_id,
                                                                        cc_code=ccbs_obj.get_cc_code(),
                                                                        bs_code=ccbs_obj.get_bs_code(),
                                                                        code=ccbs_obj.get_code(),
                                                                        ccbspercentage=ccbs_obj.get_ccbspercentage(),
                                                                        glno=ccbs_obj.get_glno(),
                                                                        amount=ccbs_obj.get_amount(),
                                                                        remarks=ccbs_obj.get_remarks(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).get(id=ccbs_obj.get_id(),entity_id=self._entity_id())

        else:
            ccbs = ccbsdtl.objects.using(self._current_app_schema()).create(
                                            debit_id=debit_id,
                                            cc_code = ccbs_obj.get_cc_code(),
                                            bs_code = ccbs_obj.get_bs_code(),
                                            code = ccbs_obj.get_code(),
                                            ccbspercentage = ccbs_obj.get_ccbspercentage(),
                                            glno = ccbs_obj.get_glno(),
                                            amount = ccbs_obj.get_amount(),
                                            remarks = ccbs_obj.get_remarks(),
                                            created_by=emp_id,entity_id=self._entity_id())

        ccbs_data = ccbsdtlresponse()
        ccbs_data.set_id(ccbs.id)
        ccbs_data.set_debit(ccbs.debit_id)
        ccbs_data.set_cc_code(ccbs.cc_code)
        ccbs_data.set_bs_code(ccbs.bs_code)
        ccbs_data.set_code(ccbs.code)
        ccbs_data.set_ccbspercentage(ccbs.ccbspercentage)
        ccbs_data.set_glno(ccbs.glno)
        ccbs_data.set_amount(ccbs.amount)
        ccbs_data.set_remarks(ccbs.remarks)
        return ccbs_data