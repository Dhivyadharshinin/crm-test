import json
from datetime import datetime
from io import BytesIO

from django.db.models import Q
from django.http import StreamingHttpResponse

from ecfservice.data.response.ecfheaderresponse import ECFHeaderresponse
from ecfservice.data.response.invoiceheaderresponse import Invoiceheaderresponse
from ecfservice.models.ecfmodels import ECFHeader, InvoiceHeader, InvoicePO, ECFQueue
from ecfservice.util.ecfutil import ECFStatus, PPX, Pay, get_Ppx, get_Pay, Type, SupplierType
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service import api_service
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

import json

class Ecfcoservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def ecfco_list(self, request,vys_page,emp_id):
        condition = Q(ecfstatus__in=[2, 3, 4, 5]) & Q(status=1)
        ecfco = ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_len = len(ecfco)
        pro_list = NWisefinList()
        if list_len > 0:
            for obj in ecfco:
                ecf_data = ECFHeaderresponse()
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                commodity = api_serv.get_commosingle_id(request, obj.commodity_id)
                # ven_service = VendorAPI()
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_branch = emp['employee_branch']
                try:
                    bnch_name = obj.approvedby
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
                employeebranch = api_serv.get_empbranch_id(request, obj.raiserbranch)
                branch_co = api_serv.get_empbranch_id(request, obj.branch)
                # disp_name = branch_co['code'] + '--' + branch_co['name']
                print("branch", branch_co)
                ecf_data.set_id(obj.id)
                ecf_data.set_crno(obj.crno)
                ecf_data.set_commodity(commodity)
                if obj.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if obj.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if obj.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if obj.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(obj.ecfdate)
                ecf_data.set_ecftype_id(obj.ecftype)
                ecf_data.set_ecfamount(obj.ecfamount)
                ecf_data.set_ecfstatus_id(obj.ecfstatus)
                if obj.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if obj.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if obj.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if obj.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if obj.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION:
                    ecf_data.set_ecfstatus(ECFStatus.Pending_For_Approval_Modification)
                if obj.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                if obj.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if obj.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx_id(Ecfhdr.ppx)
                ecf_data.set_notename(obj.notename)
                ecf_data.set_remark(obj.remark)
                if obj.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if obj.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if obj.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto_id(Ecfhdr.payto)
                ecf_data.set_payto_id(get_Pay(obj.payto))
                ecf_data.set_ppx_id(get_Ppx(obj.ppx))
                # emp_api = NWisefinUtilityService()
                # branch = emp_api.get_employee_branch(obj.branch)
                # if len(branch) > 0:
                ecf_data.set_branch(branch_co)
                ecf_data.set_raisedby(obj.raisedby)
                ecf_data.set_raiserbranch(employeebranch)
                ecf_data.set_raisername(obj.raisername)
                ecf_data.set_data({"approvedby": bnch_name, "approvername": emp_name, "approverbranch": appbranch_name})
                ecf_data.set_approvedby(bnch_name)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_approverbranch(appbranch_name)
                ecf_data.set_branch(branch_co)
                ecf_data.set_supplier_type_id(obj.supplier_type)
                ecf_data.set_ap_status(obj.ap_status)
                aph = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=obj.id,status=1,entity_id=self._entity_id()).all()
                # print("state1", aph.supplierstate_id)
                # print("state2", aph.supplier_id)
                invheader_list = []
                for inhdr in aph:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    # commodity = api_serv.get_commosingle_id(request, inhdr.commodity_id)
                    try:
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    except:
                        state = None
                        supp = None
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_branch = emp['employee_branch']
                    empbranch = api_serv.get_empbranch_id(request, emp_branch)
                    # employeebranch = api_serv.get_empbranch_id(request, inhdr.raiserbranch)
                    gstdtl = empbranch['gstin']
                    gstno = gstdtl[:2]
                    if inhdr.supplier_id != '':
                        try:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            supgst = supp['gstno']
                        except:
                            supp = None
                            supgst = None
                        try:
                            supgstno = supgst[:2]
                        except:
                            supgstno = None
                        if supgstno != gstno:
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
                    ecf_data.set_invoiceheader(inhdr_data)
                pro_list.append(ecf_data)
            vpage = NWisefinPaginator(ecfco, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
        return pro_list

    def ecf_queuedetails(self,request,ecfhdr_id):
        from utilityservice.service import api_service
        ecf_que=ECFQueue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,entity_id=self._entity_id())
        vysfin_list = NWisefinList()
        stop_count=len(ecf_que)
        if len(ecf_que) > 0:
            for ecfque in ecf_que:
                # if  stop_count > 2:
                #     stop_count=stop_count-1
                #     continue
                api_serv = api_service.ApiService(self._scope())
                ecfque_json=dict()
                ecfque_json['from_user'] = api_serv.get_empsingle_id(request,ecfque.from_user_id)
                ecfque_json['to_user'] = api_serv.get_empsingle_id(request,ecfque.to_user_id)
                ecfque_json['status'] = ecfque.comments
                ecfque_json['remarks'] = ecfque.remarks
                ecfque_json['created_date'] = str(ecfque.created_date.date())
                vysfin_list.append(ecfque_json)
        return vysfin_list

    # def download_excel(self,emp_id):
    #     import pandas as pd
    #     from django.http import StreamingHttpResponse
    #     import io
    #     BytesIO = io.BytesIO()
    #     # collection = ({'fruits': ['Mango', 'Guava', 'Pineapple', 'Apple', 'Watermelon', 'Strawberry', 'Orange'],
    #     #                'states_grown': ['Madhya Pradesh', 'Maharashtra', 'Karnataka', 'Jammu & Kashmir', 'Gujarat',
    #     #                                 'Himachal Pradesh', 'Kerala'],
    #     #                'quantity': ['150', '200', '390', '545', '273', '250', '175']})
    #     collection = self.schedule_query_report(emp_id)
    #     #print('collection',collection)
    #     output = BytesIO
    #     df = pd.DataFrame(collection)#, columns=['fruits', 'states_grown', 'quantity'])
    #     writer = pd.ExcelWriter(output, engine='xlsxwriter')
    #     df.to_excel(writer, sheet_name='Sheet1', index=False)
    #     writer.save()
    #     output.seek(0)
    #     print(datetime.now().strftime("%y%m%d_%H%M%S"))
    #     file_name = 'SCHEDULE_REPORT-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    #     response = StreamingHttpResponse(output, content_type='application/octet-stream')
    #     response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
    #     return response

    def empqlist(self, request,No,emp_id):
        emqu = ECFHeader.objects.using(self._current_app_schema()).get(id=No,entity_id=self._entity_id())
        print("ecfco",emqu)
        ecf_data = ECFHeaderresponse()
        from utilityservice.service import api_service
        api_serv = api_service.ApiService(self._scope())
        commodity = api_serv.get_commosingle_id(request,emqu.commodity_id)
        # ven_service = VendorAPI()
        emp = api_serv.get_empsingle_id(request, emp_id)
        emp_branch = emp['employee_branch']
        try:
            bnch_name = emqu.approvedby
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
        employeebranch = api_serv.get_empbranch_id(request, emqu.raiserbranch)
        try:
            branch_co = api_serv.get_empbranch_id(request, emqu.branch)
        except:
            branch_co = None
        # disp_name = branch_co['code'] + '--' + branch_co['name']
        print("branch", branch_co)
        ecf_data.set_id(emqu.id)
        ecf_data.set_crno(emqu.crno)
        ecf_data.set_commodity(commodity)
        if emqu.ecftype == Type.PO:
            ecf_data.set_ecftype(Type.PO_Type)
        if emqu.ecftype == Type.NON_PO:
            ecf_data.set_ecftype(Type.NON_PO_Type)
        if emqu.ecftype == Type.ADVANCE:
            ecf_data.set_ecftype(Type.ADVANCE_Type)
        if emqu.ecftype == Type.ERA:
            ecf_data.set_ecftype(Type.ERA_Type)
        ecf_data.set_ecfdate(emqu.ecfdate)
        ecf_data.set_ecftype_id(emqu.ecftype)
        ecf_data.set_ecfamount(emqu.ecfamount)
        ecf_data.set_ecfstatus_id(emqu.ecfstatus)
        if emqu.ecfstatus == ECFStatus.DRAFT:
            ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
        if emqu.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
            ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
        if emqu.ecfstatus == ECFStatus.APPROVED:
            ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
        if emqu.ecfstatus == ECFStatus.REJECT:
            ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
        if emqu.ecfstatus == ECFStatus.DELETE:
            ecf_data.set_ecfstatus(ECFStatus.Delete)
        if emqu.ppx == PPX.EMPLOYEE:
            ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
        if emqu.ppx == PPX.SUPPLIER:
            ecf_data.set_ppx(PPX.SUPPLIER_PPX)
        # ecf_data.set_ppx_id(Ecfhdr.ppx)
        ecf_data.set_notename(emqu.notename)
        ecf_data.set_remark(emqu.remark)
        if emqu.payto == Pay.EMPLOYEE:
            ecf_data.set_payto(Pay.EMPLOYEE_Pay)
        if emqu.payto == Pay.SUPPLIER:
            ecf_data.set_payto(Pay.SUPPLIER_Pay)
        if emqu.payto == Pay.BRANCH_PETTYCASH:
            ecf_data.set_payto(Pay.BRANCH_Pay)
        # ecf_data.set_payto_id(Ecfhdr.payto)
        ecf_data.set_payto_id(get_Pay(emqu.payto))
        ecf_data.set_ppx_id(get_Ppx(emqu.ppx))
        emp_api = NWisefinUtilityService()
        branch = emp_api.get_employee_branch(emqu.branch)
        if len(branch) > 0:
            ecf_data.set_branch(branch)
        ecf_data.set_raisedby(emqu.raisedby)
        ecf_data.set_raiserbranch(employeebranch)
        ecf_data.set_raisername(emqu.raisername)
        ecf_data.set_data({"approvedby": bnch_name, "approvername": emp_name, "approverbranch": appbranch_name})
        ecf_data.set_approvedby(bnch_name)
        ecf_data.set_approvername(emp_name)
        ecf_data.set_approverbranch(appbranch_name)
        ecf_data.set_branch(branch_co)
        ecf_data.set_supplier_type_id(emqu.supplier_type)
        if emqu.supplier_type == SupplierType.SINGLE:
            ecf_data.set_supplier_type(SupplierType.SINGLE_Type)
        if emqu.supplier_type == SupplierType.MULTIPLE:
            ecf_data.set_supplier_type(SupplierType.MULTIPLE_Type)
        return ecf_data

    def ecfco_search(self, request,vys_page,grn_obj,emp_id):
        try:
            print(grn_obj)
            condition = Q(status=1)
            if grn_obj['crno'] != '':
                condition &= Q(ecfheader_id__crno__icontains=grn_obj['crno'])
                print("1")
            if grn_obj['ecftype'] != '':
                condition &= Q(ecfheader_id__ecftype__icontains=grn_obj['ecftype'])
            if grn_obj['ecfstatus'] != '':
                condition &= Q(ecfheader_id__ecfstatus__icontains=grn_obj['ecfstatus'])
            if grn_obj['branch'] != '':
                condition &= Q(ecfheader_id__branch__icontains=grn_obj['branch'])
            if grn_obj['invoiceno'] != '':
                condition &= Q(invoiceno__icontains=grn_obj['invoiceno'])
            if grn_obj['supplier_id'] != '':
                condition &= Q(supplier_id__icontains=grn_obj['supplier_id'])
            if grn_obj['fromdate'] != '':
                condition &= Q(ecfheader_id__ecfdate__range=(grn_obj['fromdate'], grn_obj['todate']))
            if grn_obj['maxamount'] != '':
                condition &= Q(ecfheader_id__ecfamount__range=(grn_obj['minamount'], grn_obj['maxamount']))
            inh = InvoiceHeader.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            print(inh)
            list_len = len(inh)
            pro_list = NWisefinList()
            if list_len > 0:
                # for inhdr in inh:
                for inhdr in inh:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    # commodity = api_serv.get_commosingle_id(request, inhdr.commodity_id)
                    try:
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    except:
                        state = None
                        supp = None
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    empp = emp['id']
                    print("emp",empp)
                    emp_branch = emp['employee_branch']
                    print("branch",emp_branch)
                    empbranch = api_serv.get_empbranch_id(request, emp_branch)
                    # employeebranch = api_serv.get_empbranch_id(request, inhdr.raiserbranch)
                    gstdtl = empbranch['gstin']
                    gstno = gstdtl[:2]
                    if inhdr.supplier_id != '':
                        try:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            supgst = supp['gstno']
                        except:
                            supp = None
                            supgst = None
                        try:
                            supgstno = supgst[:2]
                        except:
                            supgstno = None
                        if supgstno != gstno:
                            gsttype = 'IGST'
                        else:
                            gsttype = 'SGST & CGST'
                    inhdr_data = Invoiceheaderresponse()
                    inhdr_data.set_id(inhdr.id)
                    inhdr_data.set_ecfheader(self.empqlist(request,inhdr.ecfheader_id,emp_id))
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
                pro_list.append(inhdr_data)
            vpage = NWisefinPaginator(inh, vys_page.get_index(), 10)
            pro_list.set_pagination(vpage)
            return pro_list
        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(ex))
            return error_obj

    def ecfco_download(self, request,vys_page,emp_id):
        condition = Q(ecfstatus__in=[2, 3, 4, 5]) & Q(status=1)
        ecfco = ECFHeader.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')
        list_len = len(ecfco)
        pro_list = NWisefinList()
        if list_len > 0:
            for obj in ecfco:
                ecf_data = ECFHeaderresponse()
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                commodity = api_serv.get_commosingle_id(request, obj.commodity_id)
                # ven_service = VendorAPI()
                emp = api_serv.get_empsingle_id(request, emp_id)
                emp_branch = emp['employee_branch']
                try:
                    bnch_name = obj.approvedby
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
                employeebranch = api_serv.get_empbranch_id(request, obj.raiserbranch)
                branch_co = api_serv.get_empbranch_id(request, obj.branch)
                # disp_name = branch_co['code'] + '--' + branch_co['name']
                print("branch", branch_co)
                ecf_data.set_id(obj.id)
                ecf_data.set_crno(obj.crno)
                ecf_data.set_commodity(commodity)
                if obj.ecftype == Type.PO:
                    ecf_data.set_ecftype(Type.PO_Type)
                if obj.ecftype == Type.NON_PO:
                    ecf_data.set_ecftype(Type.NON_PO_Type)
                if obj.ecftype == Type.ADVANCE:
                    ecf_data.set_ecftype(Type.ADVANCE_Type)
                if obj.ecftype == Type.ERA:
                    ecf_data.set_ecftype(Type.ERA_Type)
                ecf_data.set_ecfdate(obj.ecfdate)
                ecf_data.set_ecftype_id(obj.ecftype)
                ecf_data.set_ecfamount(obj.ecfamount)
                ecf_data.set_ecfstatus_id(obj.ecfstatus)
                if obj.ecfstatus == ECFStatus.DRAFT:
                    ecf_data.set_ecfstatus(ECFStatus.DRAFT_ECFStatus)
                if obj.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL:
                    ecf_data.set_ecfstatus(ECFStatus.PENDING_FOR_APPROVAL_ECFStatus)
                if obj.ecfstatus == ECFStatus.APPROVED:
                    ecf_data.set_ecfstatus(ECFStatus.APPROVED_ECFStatus)
                if obj.ecfstatus == ECFStatus.REJECT:
                    ecf_data.set_ecfstatus(ECFStatus.REJECT_ECFStatus)
                if obj.ecfstatus == ECFStatus.PENDING_FOR_APPROVAL_MODIFICATION:
                    ecf_data.set_ecfstatus(ECFStatus.Pending_For_Approval_Modification)
                if obj.ecfstatus == ECFStatus.DELETE:
                    ecf_data.set_ecfstatus(ECFStatus.Delete)
                if obj.ppx == PPX.EMPLOYEE:
                    ecf_data.set_ppx(PPX.EMPLOYEE_PPX)
                if obj.ppx == PPX.SUPPLIER:
                    ecf_data.set_ppx(PPX.SUPPLIER_PPX)
                # ecf_data.set_ppx_id(Ecfhdr.ppx)
                ecf_data.set_notename(obj.notename)
                ecf_data.set_remark(obj.remark)
                if obj.payto == Pay.EMPLOYEE:
                    ecf_data.set_payto(Pay.EMPLOYEE_Pay)
                if obj.payto == Pay.SUPPLIER:
                    ecf_data.set_payto(Pay.SUPPLIER_Pay)
                if obj.payto == Pay.BRANCH_PETTYCASH:
                    ecf_data.set_payto(Pay.BRANCH_Pay)
                # ecf_data.set_payto_id(Ecfhdr.payto)
                ecf_data.set_payto_id(get_Pay(obj.payto))
                ecf_data.set_ppx_id(get_Ppx(obj.ppx))
                emp_api = NWisefinUtilityService()
                branch = emp_api.get_employee_branch(obj.branch)
                if len(branch) > 0:
                    ecf_data.set_branch(branch)
                ecf_data.set_raisedby(obj.raisedby)
                ecf_data.set_raiserbranch(employeebranch)
                ecf_data.set_raisername(obj.raisername)
                # ecf_data.set_data({"approvedby": bnch_name, "approvername": emp_name, "approverbranch": appbranch_name})
                ecf_data.set_approvedby(bnch_name)
                ecf_data.set_approvername(emp_name)
                ecf_data.set_approverbranch(appbranch_name)
                ecf_data.set_branch(branch_co)
                ecf_data.set_supplier_type_id(obj.supplier_type)
                aph = InvoiceHeader.objects.using(self._current_app_schema()).filter(ecfheader_id=obj.id,status=1,entity_id=self._entity_id()).all()
                # print("state1", aph.supplierstate_id)
                # print("state2", aph.supplier_id)
                invheader_list = []
                for inhdr in aph:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    # commodity = api_serv.get_commosingle_id(request, inhdr.commodity_id)
                    try:
                        state = api_serv.get_statesingle_id(request, inhdr.supplierstate_id)
                        supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                    except:
                        state = None
                        supp = None
                    emp = api_serv.get_empsingle_id(request, emp_id)
                    emp_branch = emp['employee_branch']
                    empbranch = api_serv.get_empbranch_id(request, emp_branch)
                    # employeebranch = api_serv.get_empbranch_id(request, inhdr.raiserbranch)
                    gstdtl = empbranch['gstin']
                    gstno = gstdtl[:2]
                    if inhdr.supplier_id != '':
                        try:
                            supp = api_serv.get_supliersingle_id(request, inhdr.supplier_id)
                            supgst = supp['gstno']
                        except:
                            supp = None
                            supgst = None
                        try:
                            supgstno = supgst[:2]
                        except:
                            supgstno = None
                        if supgstno != gstno:
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
                    ecf_data.set_invoiceheader(inhdr_data)
                pro_list.append(json.loads(ecf_data.get()))
            return pro_list.data