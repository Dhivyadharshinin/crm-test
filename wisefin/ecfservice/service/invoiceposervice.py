from ecfservice.data.response.ecfauditresponse import ECFAuditResponse
from ecfservice.models.ecfmodels import InvoicePO,InvoiceHeader,ECFQueue,ECFHeader
from ecfservice.service.ecfauditservice import ECFAuditService, now
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType
from ecfservice.data.response.invoiceporesponse import Invoiceporesponse
from django.db.models import Q
from datetime import datetime, timedelta, date

from masterservice.models import Product
# from prservice.data.response.grninwardresponse import GrndetailResponse, GrninwardResponse
# from prservice.data.response.poresponse import POHeaderResponse, PODetailsResponse
# from prservice.models import GRNDetail, POHeader, POPayment, GRNInward, PODetails
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorMessage, ErrorDescription
# from vysfinutility.data.success import Success, SuccessStatus, SuccessMessage
# from vysfinutility.data.vysfinlist import VysfinList
# from django.utils.timezone import now
# from django.db import IntegrityError
# from vysfinutility.data.vysfinpaginator import VysfinPaginator
# from prservice.service.poservice import Poservice
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class InvoicepoService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def invpocreate(self,invpo_obj,emp_id):
        if not invpo_obj.get_id() is None:
            invpo = InvoicePO.objects.using(self._current_app_schema()).filter(id=invpo_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        invoiceheader_id=invpo_obj.get_invoiceheader_id(),
                                                                        invoicedetail_id=invpo_obj.get_invoicedetail_id(),
                                                                        ponumber=invpo_obj.get_ponumber(),
                                                                        grnnumber=invpo_obj.get_grnnumber(),
                                                                        grndate=invpo_obj.get_grndate(),
                                                                        poquantity=invpo_obj.get_poquantity(),
                                                                        receivedqty=invpo_obj.get_receivedqty(),
                                                                        balanceqty=invpo_obj.get_balanceqty(),
                                                                        receiveddate=invpo_obj.get_receiveddate(),
                                                                        product_code=invpo_obj.get_product_code(),
                                                                        invoicedqty=invpo_obj.get_invoicedqty(),
                                                                        invoiceqty=invpo_obj.get_invoiceqty(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            invpo = InvoicePO.objects.using(self._current_app_schema()).get(id=invpo_obj.get_id())
            self.audit_function(invpo, invpo.id, invpo.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.INVOICEPO)

        else:
            invpo = InvoicePO.objects.using(self._current_app_schema()).create(
                                                invoiceheader_id=invpo_obj.get_invoiceheader_id(),
                                                invoicedetail_id=invpo_obj.get_invoicedetail_id(),
                                                ponumber=invpo_obj.get_ponumber(),
                                                grnnumber=invpo_obj.get_grnnumber(),
                                                grndate=invpo_obj.get_grndate(),
                                                poquantity=invpo_obj.get_poquantity(),
                                                receivedqty=invpo_obj.get_receivedqty(),
                                                balanceqty=invpo_obj.get_balanceqty(),
                                                receiveddate=invpo_obj.get_receiveddate(),
                                                product_code=invpo_obj.get_product_code(),
                                                invoicedqty=invpo_obj.get_invoicedqty(),
                                                invoiceqty=invpo_obj.get_invoiceqty(),
                                                created_by=emp_id,entity_id=self._entity_id())

            self.audit_function(invpo, invpo.id, invpo.id, emp_id,
                                ECFModifyStatus.CREATE, ECFRefType.INVOICEPO)


        inpo_data = Invoiceporesponse()
        inpo_data.set_id(invpo.id)
        inpo_data.set_invoiceheader(invpo.invoiceheader_id)
        inpo_data.set_invoicedetail(invpo.invoicedetail_id)
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
        return inpo_data

    # def po_list(self, vys_page, emp_id):
    #     condition = Q(flag="P") & (Q(poheader_id__poheader_status="APPROVED") | Q(poheader_id__poheader_status="RELEASE")) & Q(
    #         inwardheader_id__grn_status="APPROVED") & Q(status=1) & Q(poheader_id__type = 1)
    #     # obj = GRNDetail.objects.filter(condition).order_by('-created_date')[
    #           vys_page.get_offset():vys_page.get_query_limit()]
    #     list_len = len(obj)
    #     pro_list = VysfinList()
    #     if list_len > 0:
    #         for clos in obj:
    #             Occlodet_data = GrndetailResponse()
    #             Occlodet_data.set_id(clos.id)
    #             # Occlodet_data.set_inwardheader(clos.inwardheader)
    #             po_service= Poservice()
    #             po_no=(po_service.fetch_poheader(clos.poheader_id, emp_id))
    #             po_number=po_no.no
    #             Occlodet_data.set_poheader_id(po_number)
    #             # Occlodet_data.set_podetails(clos.podetails)
    #             # Occlodet_data.set_podelivery(clos.podelivery, emp_id)
    #             Occlodet_data.set_quantity(clos.quantity)
    #             Occlodet_data.set_branch_id(clos.branch_id)
    #             Occlodet_data.set_date(clos.date)
    #             pro_list.append(Occlodet_data)
    #         vpage = VysfinPaginator(obj, vys_page.get_index(), 10)
    #         pro_list.set_pagination(vpage)
    #     return pro_list

    # def search_pono_dtl(self,vys_page, query, emp_id):
    #     po = POHeader.objects.get(no = query)
    #     pohdr_id=po.id
    #     condition = Q(no__icontains=query) & Q(status=1)
    #     grn_list = GRNDetail.objects.filter(poheader_id=pohdr_id, status=1)
    #     grndtl_list = VysfinList()
    #     for grndetails in grn_list:
    #         grndetails_data = GrndetailResponse()
    #         grndetails_data.set_id(grndetails.id)
    #         grndetails_data.set_poheader(self.fetch_poheader(grndetails.poheader_id, emp_id))
    #         grndetails_data.set_inwardheader(self.fetch_grninward(grndetails.inwardheader_id,emp_id))
    #         grndetails_data.set_podetails_id(self.fetch_podetails(grndetails.podetails_id,emp_id))
    #         inv=(self.fetch_poheader(grndetails.poheader_id, emp_id))
    #         pono=inv.no
    #         podtl=(self.fetch_podetails(grndetails.podetails_id,emp_id))
    #         invpro=podtl.product_name
    #         inv_id=podtl.product_id
    #         pro = Product.objects.get(id=inv_id)
    #         pro_code= pro.code
    #         print('prod', inv_id)
    #         # if inv_id == None:
    #         #     con = Q(name=invpro)
    #         cond = Q(ponumber = pono)
    #         popay = POPayment.objects.filter(cond)
    #         paidqty = 0
    #         if len(popay) != 0:
    #             for popayment in popay:
    #                 paidqty += popayment.quantity
    #         poqty =podtl.qty
    #         condition= Q(ponumber=pono) & Q(product_code= pro_code)& Q(invoiceqty=0) &Q(status=1)
    #         invpo = InvoicePO.objects.filter(condition)
    #         invpoqty=0
    #         invid =''
    #         for invpodetails in invpo:
    #             invid = invpodetails.id
    #             invpoqty = invpodetails.invoicedqty
    #             invqty = invpodetails.invoiceqty
    #         grndetails_data.invpo_id = invid
    #         invoiceqty = (grndetails.quantity) - invpoqty
    #         grndetails_data.set_ecfpo_invoicedqty(invpoqty)
    #         grndetails_data.set_ecfpo_invoiceqty(invoiceqty)
    #         balance = poqty - (grndetails.quantity)
    #         grndetails_data.balance_quantity = balance
    #         grndetails_data.set_quantity(grndetails.quantity)
    #         grndetails_data.set_paidqty(paidqty)
    #         grndtl_list.append(grndetails_data)
    #         vpage = VysfinPaginator(grn_list, vys_page.get_index(), 10)
    #         grndtl_list.set_pagination(vpage)
    #     return grndtl_list

    # def fetch_poheader(self, po_id, emp_id):
    #     pohdr = POHeader.objects.get(id=po_id)
    #     po_data = POHeaderResponse()
    #     po_data.set_id(pohdr.id)
    #     po_data.set_no(pohdr.no)
    #     po_data.set_date(pohdr.date)
    #     po_data.set_supplierbranch(pohdr.supplierbranch_id)
    #     po_data.set_terms(pohdr.terms_id)
    #     po_data.set_amount(pohdr.amount)
    #     po_data.set_amendment(pohdr.amendment)
    #     po_data.set_version(pohdr.version)
    #     po_data.set_commodity(pohdr.commodity_id)
    #     po_data.set_branch(pohdr.branch_id)
    #     po_data.set_mepno(pohdr.mepno)
    #     po_data.set_poheader_status(pohdr.poheader_status)
    #     po_data.set_notepad(pohdr.notepad)
    #     po_data.set_validfrom(pohdr.validfrom)
    #     po_data.set_validto(pohdr.validto)
    #     po_data.set_onacceptance(pohdr.onacceptance)
    #     po_data.set_ondelivery(pohdr.ondelivery)
    #     po_data.set_oninstallation(pohdr.oninstallation)
    #     po_data.set_approvallater(pohdr.approvallater)
    #     po_data.set_close(pohdr.close)
    #     po_data.set_cancel(pohdr.cancel)
    #     po_data.set_rems_edit(pohdr.rems_edit)
    #     return po_data

    # def fetch_grninward(self, grn_id, emp_id):
    #     grninw = GRNInward.objects.get(id=grn_id)
    #     Occlodet_data = GrninwardResponse()
    #     Occlodet_data.set_id(grninw.id)
    #     Occlodet_data.set_code(grninw.code)
    #     Occlodet_data.set_dcnote(grninw.dcnote)
    #     Occlodet_data.set_invoiceno(grninw.invoiceno)
    #     Occlodet_data.set_date(grninw.date)
    #     return Occlodet_data
    #
    # def fetch_podetails(self, podtl_id,emp_id):
    #     podtl = PODetails.objects.get(id=podtl_id)
    #     podtl_data = PODetailsResponse()
    #     podtl_data.set_id(podtl.id)
    #     podtl_data.set_product(podtl.product_id)
    #     podtl_data.set_product_name(podtl.product_name)
    #     podtl_data.set_item(podtl.item)
    #     podtl_data.set_item_name(podtl.item_name)
    #     # pro = (product_service.fetch_product(podtl.product_id, emp_id))
    #     # productname=pro.name
    #     # podtl_data.set_product(product_service.fetch_product(podtl.product_id, emp_id))
    #     podtl_data.set_installationrequired(podtl.installationrequired)
    #     podtl_data.set_capitalized(podtl.capitalized)
    #     podtl_data.set_qty(podtl.qty)
    #     podtl_data.set_uom(podtl.uom)
    #     podtl_data.set_unitprice(podtl.unitprice)
    #     podtl_data.set_amount(podtl.amount)
    #     podtl_data.set_taxamount(podtl.taxamount)
    #     podtl_data.set_totalamount(podtl.totalamount)
    #     return podtl_data

    def Invpo_update(self, po_id,invdtl_id,po_qty, emp_id):
        try:
            invpo = InvoicePO.objects.using(self._current_app_schema()).get(id=po_id,entity_id=self._entity_id())
            invqty = invpo.invoicedqty
            invrecqty=invpo.receivedqty
            invceqty=invpo.invoiceqty
            invpoqty = po_qty

            invpoqty += invqty

            Ecfhdr = InvoicePO.objects.using(self._current_app_schema()).filter(id=po_id,entity_id=self._entity_id()).update(
                                                            invoicedetail=invdtl_id ,
                                                            invoicedqty=invpoqty,
                                                            invoiceqty = (invrecqty - invpoqty),
                                                            updated_by=emp_id,
                                                            updated_date=now())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.REJECTED_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            return error_obj

    def invpomodcreate(self,invpo_obj,emp_id):
        if not invpo_obj.get_id() is None:
            invpo = InvoicePO.objects.using(self._current_app_schema()).filter(id=invpo_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        invoiceheader_id=invpo_obj.get_invoiceheader_id(),
                                                                        invoicedetail_id=invpo_obj.get_invoicedetail_id(),
                                                                        ponumber=invpo_obj.get_ponumber(),
                                                                        grnnumber=invpo_obj.get_grnnumber(),
                                                                        grndate=invpo_obj.get_grndate(),
                                                                        poquantity=invpo_obj.get_poquantity(),
                                                                        receivedqty=invpo_obj.get_receivedqty(),
                                                                        balanceqty=invpo_obj.get_balanceqty(),
                                                                        receiveddate=invpo_obj.get_receiveddate(),
                                                                        product_code=invpo_obj.get_product_code(),
                                                                        invoicedqty=invpo_obj.get_invoicedqty(),
                                                                        invoiceqty=invpo_obj.get_invoiceqty(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            invpo = InvoicePO.objects.using(self._current_app_schema()).get(id=invpo_obj.get_id(),entity_id=self._entity_id())
            self.audit_function(invpo, invpo.id, invpo.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.INVOICEPO)

        else:
            invpo = InvoicePO.objects.using(self._current_app_schema()).create(
                                                invoiceheader_id=invpo_obj.get_invoiceheader_id(),
                                                invoicedetail_id=invpo_obj.get_invoicedetail_id(),
                                                ponumber=invpo_obj.get_ponumber(),
                                                grnnumber=invpo_obj.get_grnnumber(),
                                                grndate=invpo_obj.get_grndate(),
                                                poquantity=invpo_obj.get_poquantity(),
                                                receivedqty=invpo_obj.get_receivedqty(),
                                                balanceqty=invpo_obj.get_balanceqty(),
                                                receiveddate=invpo_obj.get_receiveddate(),
                                                product_code=invpo_obj.get_product_code(),
                                                invoicedqty=invpo_obj.get_invoicedqty(),
                                                invoiceqty=invpo_obj.get_invoiceqty(),
                                                created_by=emp_id,entity_id=self._entity_id())

            self.audit_function(invpo, invpo.id, invpo.id, emp_id,
                                ECFModifyStatus.CREATE, ECFRefType.INVOICEPO)
        invhdr1 = InvoiceHeader.objects.using(self._current_app_schema()).filter(id=invpo_obj.get_invoiceheader_id(),entity_id=self._entity_id())
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

        inpo_data = Invoiceporesponse()
        inpo_data.set_id(invpo.id)
        inpo_data.set_invoiceheader(invpo.invoiceheader_id)
        inpo_data.set_invoicedetail(invpo.invoicedetail_id)
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
        return inpo_data


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
        audit_obj.set_reftype(ECFRefType.INVOICEPO)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(ECFRefType.INVOICEPO)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)