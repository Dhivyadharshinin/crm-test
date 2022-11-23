# from masterservice.models import Apcategory, APsubcategory
# from masterservice.service.productservice import ProductService
# from masterservice.service.stateservice import StateService
# from prservice.service.supplierproductservice import SupplierproductService
# from sgservice.controller.sgecfcontroller import ecf_pdf_generate
# from taservice.data.response.touradvance import TourAdvanceResponse
from taservice.service.tourexpense import TourExpense#
from taservice.util.ta_util import App_type
from nwisefin.settings import logger, SERVER_IP
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist  import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
# from utilityservice.service.dbutil import DataBase
from utilityservice.service.ta_api_service import ApiService

# state_service = StateService()
# suppro_service = SupplierproductService()
# product_service = ProductService()
import json
from datetime import datetime
from taservice.data.response.ecf_resp import RcnResponse, EcfResponse, CreditResponse, DebitResponse, \
    HeaderDetailResponse, ApHeaderDetailsResponse, ApDebitResponse, ApDetailsResponse, ApCreditResponse, \
    ClassificationResponse, CcbsResponse, Ccbs_Response
import requests
from nwisefin import settings
from taservice.models import Glmapping, TourRequest, Employeemapping
from taservice.models import TourAdvance as TourAdvacne_model
from taservice.service.common_dropdown_ser import Common_dropdown_ser
from taservice.service.emp_name_get import Tourno_details, emp_dtl
from taservice.service.touradvance import TourAdvance
# from userservice.controller.authcontroller import get_authtoken
# from userservice.models import Employee

# ip='http://emc-vysfin-sit.kvbank.in/'
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
class Ecf_entry(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)

    def invoice_entry(self,jsondata,request,approver_code,maker_code,approver_id):
        # ecf_service=ApiService(self._scope())
        # token = "Bearer  "
        # token = "Bearer  " + ecf_service.get_authtoken(request)
        # print(token)
        # headers = {"content-type": "application/json", "Authorization": "" + token + ""}

        token_name = request.headers['Authorization']
        # token_split= token_name.split()
        # token = token_split[1]
        headers = {'Authorization': token_name}


        resp_data = self.ecf_data_frame(jsondata,request,approver_code,maker_code,approver_id)  # json frame

        print("RCN_JSON", resp_data)
        vysfin_url = settings.VYSFIN_URL
        params = ''
        logger.info('ta_ Ecf Before - '+str(resp_data)+str(approver_code)+str(jsondata))
        if isinstance(resp_data, NWisefinError):
            return resp_data



        # SERVER_IP="http://143.110.244.51:8185"
        # SERVER_IP="http://192.168.1.67:8001"
        ecf_post_url=SERVER_IP+str("/ecfserv/ecfheader")
        # print("ecf_post_url",ecf_post_url)
        resp = requests.post(ecf_post_url, params=params, data=resp_data, headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        results = json.loads(results)
        logger.info('ta_ Ecf After - ' + str(results) + str(maker_code))
        return results

    def ecf_data_frame(self, jsondata,request,approver_code,maker_code,approver_id):
        tourgid = jsondata.tourgid
        rcn_data = RcnResponse()
        ecf_data = EcfResponse()
        credit_list = CreditResponse()
        debit_list = DebitResponse()
        ccbs_list = CcbsResponse()
        header_list = HeaderDetailResponse()
        # INWARD_DETAILS = []
        debit_list2 = []
        inward_list = ApDetailsResponse()
        typ = jsondata.type



        tour_details = TourRequest.objects.using(self._current_app_schema()).get(id=jsondata.tourgid,entity_id=self._entity_id())
        emp_service=ApiService(self._scope())
        employee_details = emp_service.emp_all_details(tour_details.empgid,request)
        approver_details = emp_service.emp_all_details(approver_id,request)
        raisor_branch_gst=approver_details.branch_gst
        # acc_no = employee_details.accountnumber
        # if acc_no == None:
        #     acc_no = 1234567890123456

        acc_no_details = emp_service.emp_accountno_ta(tour_details.empgid, request)
        acc_no=acc_no_details.accountnumber
        if acc_no!=employee_details.accountnumber:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_ACCOUNTNO_TA)
            return error_obj




        all_exp_total_amount = 0
        if typ == "CLAIM":
            sno = 0
            product_name = ""
            product_code = ""
            HSN_Code = '1'
            service = TourExpense(self._scope())
            details_exp = service.get_each_expense(tourgid,request)
            aphd_data = ApHeaderDetailsResponse()

            for d in details_exp.data:
                all_exp_total_amount+=float(d.claimedamount)

            tour_reason_id = tour_details.reason
            reason_service = emp_dtl(self._scope())
            tour_reason = reason_service.get_reason_name(tour_reason_id)

            # full_tour_reason = tour_reason

            # if "training" in tour_reason:
            #     tour_reason = "TRAVEL TRAINING"
            # else:
            #     tour_reason = str(tour_reason).split()[1]
            #
            # if "international" in full_tour_reason:
            #     cat_data = emp_service.ta_reason_catagory(tour_reason).last()
            # else:
            #     cat_data = emp_service.ta_reason_catagory(tour_reason)[0]

            # reason_name="Travel"
            if tour_details.reason==1:
                reason_name="Travel Business domestic"
                commodity_name_fetch="Travel Business"
            elif tour_details.reason==2:
                reason_name="Travel Monitering/supervision Dom"
                commodity_name_fetch = "Travel Supervisory"
            elif tour_details.reason==3:
                reason_name="Travel-due deligence/regulatory dom"
                commodity_name_fetch = "Travel Regulatory"
            elif tour_details.reason==4:
                reason_name="Travel training dom"
                commodity_name_fetch = "Travel Training"
            elif tour_details.reason==5:
                reason_name="Travel relocaion dom"
                commodity_name_fetch = "Travel Business"
            elif tour_details.reason==8:
                reason_name="Travel support dom"
                commodity_name_fetch = "Travel Business"
            elif tour_details.reason==9:
                reason_name="Travel Business Intl"
                commodity_name_fetch = "Travel Business"
            elif tour_details.reason==10:
                reason_name="Travel Training Intl"
                commodity_name_fetch = "Travel Training"
            elif tour_details.reason==11:
                reason_name="Travel Business domestic"
                commodity_name_fetch = "Travel Business"
            else :
                reason_name="Travel Business domestic"
                commodity_name_fetch = "Travel Business"
            cat_data = emp_service.ta_reason_catagory(reason_name)[0]

            debit_cat_code = cat_data.code
            # print("debit_cat_code ", debit_cat_code)

            itenary=-1
            for d in details_exp.data:
                aphd_data = ApHeaderDetailsResponse()
                itenary+=1
                sno = sno + 1
                vendor_name=None
                # if d.exp_name == 'Travelling Expenses' or d.exp_name== 'Lodging' or d.exp_name== 'Packaging/Freight':
                #     # vendor_code = d.get('vendorcode')
                #     vendor_name = d.vendorname
                #     # branchgstno = d.get('bankgstno')
                #     # suppliergstno = d.get('vendorgstno')
                #     # IGST = d.get('igst')
                #     # CGST = d.get('cgst')
                #     # SGST = d.get('sgst')
                #     HSN_Code = d.hsncode['code']
                #     # HSN_Code = None
                #
                # if d.exp_name=="Travelling Expenses" or d.exp_name=="Incidental Expenses" or d.exp_name=="Lodging" or d.exp_name=="Miscellaneous Charges":
                #     product_name="Travel - Training Food/Lodging/Air/Ground Transport"
                #     product_code="P01006"
                # elif d.exp_name=="Daily Diem" or d.exp_name=="Local Deputation Allowance":
                #     product_name="Employee Travel Allowance"
                #     product_code="P01346"
                # elif d.exp_name=="Packaging/Freight":
                #     product_name="Packing and Moving (Employee Shifting Expense)"
                #     product_code="P01347"
                # elif d.exp_name=="Local Conveyance":
                #     if d.subcatogory=="Auto":
                #         product_name="Auto Rickshaws"
                #         product_code="P00827"
                #     elif d.subcatogory=="Train":
                #         product_name="Metro Train"
                #         product_code="P00972"
                #     # elif d.subcatogory=="Bus":
                #     else:
                #         product_name="Public Transport"
                #         product_code="P00823"
                # else:
                #     product_name = "Public Transport"
                #     product_code = "P00823"

                # try:
                #     if d.exp_id ==1:
                #         debit_sub_cat_code="TRAIN&BUS"
                #         debit_gl_no=446202
                #     elif d.exp_id==2 or d.exp_id==9:
                #         debit_sub_cat_code="OTHERS"
                #         debit_gl_no=446206
                #     elif d.exp_id==4:
                #         debit_sub_cat_code="CONVEYANCE"
                #         debit_gl_no=446203
                #     elif d.exp_id==5:
                #         debit_sub_cat_code="LODGING"
                #         debit_gl_no=446205
                #     else:
                #         debit_sub_cat_code="OTHERS"
                #         debit_gl_no=446206
                # except:
                #     debit_sub_cat_code = "OTHERS"
                #     debit_gl_no = 446206


                total_amount = float(d.claimedamount)


                # aphd_data.set_Debits(Debits_lists)
                aphd_data.set_dtltotalamt(all_exp_total_amount)
                aphd_data.set_invoice_po("")
                aphd_data.set_productcode("")
                aphd_data.set_productname("")
                aphd_data.set_description(tour_reason)
                aphd_data.set_hsn("00000000")
                aphd_data.set_hsn_percentage(0)
                aphd_data.set_uom("Number")
                aphd_data.set_unitprice(total_amount)
                aphd_data.set_quantity(1)
                aphd_data.set_amount(total_amount)
                aphd_data.set_discount(0)
                aphd_data.set_sgst(0)
                aphd_data.set_cgst(0)
                aphd_data.set_igst(0)
                aphd_data.set_taxamount(0)
                aphd_data.set_otheramount(0)
                aphd_data.set_roundoffamt(0)
                aphd_data.set_totalamount(total_amount)

                header_list.append(aphd_data)

                # if typ == "CLAIM":
                sno = 0
                service = Common_dropdown_ser(self._scope())
                ccbs_data = service.ccbs_get(tourgid, 2,request,0)
                service = TourExpense(self._scope())
                details_exp = service.get_each_expense(tourgid,request)
                # for d in details_exp.data:
                #
                #     sno = sno + 1
                #
                #     if ccbs_data is not None:
                #         for ccbsdtl in ccbs_data:

                # subcat_description = d.exp_name
                # subcat_description = ('%.9s' % subcat_description)

                gender = employee_details.gender
                if gender == None:
                    gender = "Male"
                # gl_mapping = self.glmapping_get_claim(tour_reason, gender, subcat_description)
                # ecf_service=Ecf_entry()
                # common_service = ApiService(self._scope())
                # 13/1 common api-Ste
                # category_data = common_service.cat_no_get(gl_mapping.categorycode, request)
                # category_data = json.loads(category_data)
                # sub_category_code = common_service.sub_cat_no_get(gl_mapping.subcategorycode, category_data['id'],
                #                                                   request)
                # category_code = category_data['code']


                # if tour_reason=="TRAVEL BUSINESS DOMESTIC":
                #     debit_cat_code="TRABUS DOM"
                # elif tour_reason=="TRAVEL MONITERING DOMESTIC":
                #     debit_cat_code="TRASUPER DOM"
                # elif tour_reason=="TRAVEL DUE DELIGENCE DOMESTIC":
                #     debit_cat_code="TRAREG DOM"
                # elif tour_reason=="TRAVEL TRAINING DOMESTIC":
                #     debit_cat_code="TRATRNG DOM"
                # elif tour_reason=="TRAVEL RELOCATION DOMESTIC":
                #     debit_cat_code="TRATRANSFER DOM"
                # elif tour_reason=="TRAVEL SUPPORT TEAM DOMESTIC":
                #     debit_cat_code="TRASUPPORT DOM"
                # elif tour_reason=="TRAVEL BUSINESS INTERNATIONAL":
                #     debit_cat_code="TRABUS INTL"
                # elif tour_reason=="TRAVEL TRAINING INTERNATIONAL" :
                #     debit_cat_code="TRATRNG INTL"
                # # elif tour_reason=="TRAVEL BORROWING RELATED DOMESTIC":
                # #     debit_cat_code="TRABUS DOM"
                # # elif tour_reason=="TRAVEL EQUITY RAISING DOMESTIC":
                # #     debit_cat_code="TRABUS DOM"
                # else :
                #     debit_cat_code="TRABUS DOM"
                # else :
                #     debit_cat_code="TRABUS DOM"



                if d.exp_id==1:
                    sub_cat_data = emp_service.sub_category(cat_data.id, d.actualmode)[0]
                elif d.exp_id==5:
                    sub_cat_data = emp_service.sub_category(cat_data.id, d.exp_name.split()[0])[0]

                else:
                    sub_cat_data=emp_service.sub_category(cat_data.id,d.exp_name)[0]

                debit_sub_cat_code=sub_cat_data.code
                debit_gl_no=sub_cat_data.glno
                # print("exp ", d.__dict__)
                # print("debit_sub_cat_code ", debit_sub_cat_code)
                # print("debit_gl_no ", debit_gl_no)


                sno+=1
                deb_data = ApDebitResponse()
                # amount = int(d.claimedamount) / 100 * int(ccbsdtl.percentage)

                deb_data.set_category_code(debit_cat_code)
                deb_data.set_subcategory_code(debit_sub_cat_code)
                deb_data.set_debitglno(debit_gl_no)
                deb_data.set_amount(total_amount)
                deb_data.set_debittotal(total_amount)
                deb_data.set_deductionamount(0)
                deb_data.set_ccbspercentage(100)
                deb_data.set_remarks("")

                ccbs_list=[]
                for ccbsdtl in ccbs_data:

                    ccbs_data_resp = Ccbs_Response()
                    ccbs_data_resp.set_remarks("")
                    ccbs_data_resp.set_cc_code(ccbsdtl.cc_data.code)
                    # ccbs_data_resp.set_cc_code('101')
                    ccbs_data_resp.set_bs_code(ccbsdtl.bs_data.code)
                    # ccbs_data_resp.set_bs_code('10')
                    ccbs_data_resp.set_code(1)
                    ccbs_data_resp.set_ccbspercentage(ccbsdtl.percentage)
                    ccbs_data_resp.set_glno(debit_gl_no)
                    # ccbs_data_resp.set_amount(ccbsdtl.amount)
                    ccbs_data_resp.set_amount(total_amount*ccbsdtl.percentage/100)
                    ccbs_data_resp.set_debit(0)

                    ccbs_list.append(ccbs_data_resp)

                deb_data.set_Ccbs(ccbs_list)

                debit_list.append(deb_data)
                debit_list2=[]
                debit_list2.append(debit_list.DEBIT[itenary])
                aphd_data.set_Debits(debit_list2)


        if typ == "CLAIM":
            claim_tot = 0
            service = TourExpense(self._scope())
            details_exp = service.get_claimreq_tour(tourgid, request)
            for d in details_exp.data:
                total_amount = float(d.claimedamount)
                claim_tot = float(claim_tot) + float(total_amount)
            sum_amount=claim_tot
            service = TourAdvance(self._scope())
            # out_advdata = service.get_tour_advance(tourgid,request)
            totadv_amt = 0

            credit_amt = float(sum_amount) - float(totadv_amt)
            if credit_amt == 0:
                credit_amt = 0
            elif credit_amt > 0:
                credit_amt = credit_amt
            else:
                credit_amt = 0
            if credit_amt != 0:

                cred_data = ApCreditResponse()

                cred_data.set_paymode_id(4)
                # cred_data.set_creditbank_id(1)
                cred_data.set_suppliertax_id(0)
                cred_data.set_creditglno(0)
                cred_data.set_creditrefno(acc_no)
                cred_data.set_suppliertaxtype(0)
                cred_data.set_suppliertaxrate(0)
                cred_data.set_taxexcempted("N")
                cred_data.set_amount(all_exp_total_amount)
                cred_data.set_taxableamount(0)
                cred_data.set_ddtranbranch(0)
                cred_data.set_ddpaybranch(0)
                cred_data.set_category_code("TRABUS DOM")
                cred_data.set_subcategory_code("OTHERS")
                cred_data.set_credittotal(all_exp_total_amount)
                # cred_data.set_bank("HDFC BANK")
                # cred_data.set_branch("NEW DELHI  SURYA KIRAN  K G MARG")
                # cred_data.set_ifsccode("HDFC0000003")
                # cred_data.set_benificiary("MEENAKSHI")
                credit_list.append(cred_data)


        ecf_data.set_Credit(credit_list.CREDIT)
        # ecf_data.set_DEBIT_JSON(debit_list)

        tour_no = tour_details.id

        branch_code=1

        if typ == "CLAIM":
            claim_tot = 0
            service = TourExpense(self._scope())
            details_exp = service.get_claimreq_tour(tourgid,request)
            for d in details_exp.data:
                total_amount = float(d.approvedamount)
                claim_tot = float(claim_tot) + float(total_amount)
            reason = details_exp.data[0].approvercomment

            ecf_data.set_invoicedate(str(datetime.today().date()))
            ecf_data.set_dedupinvoiceno(0)
            ecf_data.set_invoiceamount(all_exp_total_amount)
            ecf_data.set_invoicegst("N")
            ecf_data.set_invoiceno("TOUR_"+str(tour_no))
            ecf_data.set_invtotalamt(all_exp_total_amount)
            ecf_data.set_otheramount(0)
            ecf_data.set_raisorbranchgst(raisor_branch_gst)
            ecf_data.set_roundoffamt(0)
            # ecf_data.set_supplier_id(1)
            # ecf_data.set_suppliergst(0)
            # ecf_data.set_supplierstate_id(1)
            ecf_data.set_taxamount(0)
            ecf_data.set_totalamount(all_exp_total_amount)

            ecf_data.set_Invoicedetails(header_list.HEADERDETAIL)

        # header_list.set_INWARD_DETAILS(INWARD_DETAILS)

        # Debits_lists = []
        # for i in header_list.HEADERDETAIL:
        #     Debits_lists.append(header_list.HEADERDETAIL[i].Debits)

        # ecf_data.set_Invoicedetails(header_list.HEADERDETAIL)

        InvoiceHeaders_list=[]
        InvoiceHeaders_list.append(ecf_data)
        rcn_data.set_InvoiceHeaders(InvoiceHeaders_list)
        clas_data = ClassificationResponse()
        clas_data.set_Create_By(approver_code)
        clas_data.set_Entity_Gid(1)
        # rcn_data.set_Classification(clas_data)
        commodityid=emp_service.ta_commodity(commodity_name_fetch)
        rcn_data.set_commodity_id(commodityid)
        rcn_data.set_ecfamount(all_exp_total_amount)
        rcn_data.set_ecfdate(str(datetime.today().date()))
        rcn_data.set_ecftype(8)
        rcn_data.set_notename("")
        rcn_data.set_payto("E")
        rcn_data.set_raisedby(tour_details.empgid)
        rcn_data.set_approvedby_id(request.employee_id)
        rcn_data.set_ppx("")
        rcn_data.set_remark("general")
        rcn_data.set_supplier_type(1)
        rcn_data.set_branch(1)
        rcn_data.set_rmcode(1)
        rcn_data.set_client_code(341)
        return rcn_data.get()




    def glmapping_get_claim(self,tour_reason,gender,subcat_description):
        gl_obj=Glmapping.objects.using(self._current_app_schema()).filter(tourreason__icontains=tour_reason,gender=gender,subcategory_description__icontains=subcat_description,status=1,entity_id=self._entity_id())
        if len(gl_obj)>0:
            return gl_obj[0]
        else:
            return Glmapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[0]

    def glmappinng_get_advance(self,description):
        gl_obj=Glmapping.objects.using(self._current_app_schema()).filter(gl_description__icontains=description,entity_id=self._entity_id())
        return gl_obj[0]

    # def ap_cat_get(self,no):
    #     category=Apcategory.objects.filter(no=no)[0]
    #     return category
    #
    # def ap_subcat_get(self,no,cat_id):
    #     subcategory=APsubcategory.objects.filter(no=no,category_id=cat_id)[0]
    #     return subcategory.code

    # def advance_get(self,tour_id):
    #     Tour=TourAdvacne_model.objects.using(self._current_app_schema()).filter(tour_id=tour_id)
    #     resp_list = NWisefinList
    #     for advacne in Tour:
    #         req_data = TourAdvanceResponse()
    #         req_data.set_tourgid(advacne.tour_id)
    #         req_data.set_reason(advacne.reason)
    #         req_data.set_reqamount(advacne.reqamount)
    #         req_data.set_appamount(advacne.appamount)
    #         req_data.set_invoiceheadergid(advacne.invoiceheadergid)
    #         req_data.set_adjustamount(advacne.adjustamount)
    #         req_data.set_crnno(advacne.crnno)
    #         req_data.set_debit_categorygid(advacne.debit_categorygid)
    #         req_data.set_debit_subcategorygid(advacne.debit_subcategorygid)
    #         req_data.set_ppx_headergid(advacne.ppx_headergid)

            # tour=advacne.tour
            # req_data.set_requestno(tour.requestno)
            # req_data.set_id(tour.id)
            # req_data.set_requestdate(tour.requestdate)
            # req_data.set_empgid(tour.empgid)
            # empdtl = emp_dtl()
            # name = empdtl.employee_name_get(tour.empgid)
            # req_data.set_employee_name(name)
            # code = empdtl.employee_code_get(tour.empgid)
            # req_data.set_employee_code(code)
            # req_data.set_empdesignation(tour.empdesignation)
            # req_data.set_empgrade(tour.empgrade)


        #     resp_list.append(req_data)
        # return resp_list


    #     def invoice_header(self,request,jsondata):
    #         tourgid = jsondata.tourgid
    #         entity_gid = jsondata.Entity_Gid
    #         out_data = 0
    #         if jsondata.apptype.upper() == "TOURADV":
    #             service= TourAdvance()
    #             out_data = service.get_tour_advance(tourgid)
    #             # out_data = json.loads(out_data[0].get('advance'))
    #
    #         elif jsondata.apptype.upper()== "CLAIM":
    #             obj_claim.filter_json = json.dumps({"Claimrequest_Tourgid": tourgid, "Entity_Gid": entity_gid})
    #             out_data = obj_claim.eClaim_claimedexpense_get()
    #             out_data = json.loads(out_data.get("DATA").to_json(orient='records'))
    #
    #         service=Tourno_details()
    #         ld_out_emp = service.requestno_get(tourgid)
    #         ld_dict = json.loads(ld_out_emp)
    #         emp_gid = ld_dict['employee_id']
    #         tour_no = ld_dict['request_no']
    #
    #         tot = 0
    #         advancegid = 0
    #         sno = ''
    #         if jsondata.apptype == "TOURADV":
    #             for ot in out_data.detail:
    #                 if ot.status == 0:
    #                     tot = ot.appamount
    #                     advancegid = ot.id
    #             sno = "_" + str(len(out_data))
    #             reason = out_data.approve[0].get('comment')
    #         elif jsondata.apptype == "CLAIM":
    #             total_amount = 0
    #             for ot in out_data:
    #                 details_exp = get_expensedetails(self, ot, entity_gid)
    #                 for d in details_exp:
    #                     amount = d.get('appamt')
    #                     total_amount = int(d.get('appamt'))
    #                     branchgstno = ''
    #                     suppliergstno = ''
    #                     IGST = 0
    #                     CGST = 0
    #                     SGST = 0
    #                     HSN_Code = '1'
    #
    #                     tot = float(tot) + float(total_amount)
    #             reason = out_data[0].get('requestorcomment')
    #
    #         emp_data = {
    #             "empids": emp_gid
    #         }
    #         service=emp_dtl()
    #         branch_gid = service.employee_bracnh_get(emp_gid)
    #         # employee_gender = employee_data[0].get('employee_gender')
    #         params = {"action": "INSERT",
    #                   "type": "INVOICE_HEADER",
    #                   "entity_gid": jsondata.Entity_Gid,
    #                   "employee_gid": emp_gid}
    #         tk = str(request.auth.token)
    #         token = "Bearer  " + tk[2:len(tk) - 1]
    #         headers = {"content-type": "application/json", "Authorization": "" + token + ""}
    #         # obj_claim.date = 'DATE'
    #         date = datetime.today()
    #         requestdate = date
    #         comodity_table = {
    #             "Table_name": "ap_mst_tcommodity",
    #             "Column_1": "commodity_gid,commodity_code,commodity_name",
    #             "Column_2": "",
    #             "Where_Common": "commodity",
    #             "Where_Primary": "name",
    #             "Primary_Value": "Tour ClaimStaff",
    #             "Order_by": "gid"
    #         }
    #         service=Ecf_entry()
    #         comodity = service.alltable(comodity_table, entity_gid, token)
    #         if comodity.get("MESSAGE") == 'FOUND':
    #             comoditygid = comodity.get("DATA")[0].get('commodity_gid')
    #         else:
    #             data = {"MESSAGE":"Comodity Missing"}
    #             return data
    #         if jsondata.apptype == "TOURADV":
    #             tmp_data = {
    #                 "IsTa": "Y",
    #                 "Invoice_Type": "ADVANCE",
    #                 "Supplier_gid": 0,
    #                 "Sup_state_gid": 1,
    #                 "Inwarddetails_gid": 1,
    #                 "Is_GST": "N",
    #                 "Invoice_Date": requestdate,
    #                 "Invoice_No": "TOUR" + str(tour_no) + str(sno),
    #                 "Invoice_Tot_Amount": tot,
    #                 "invoicetaxamount": tot,
    #                 "Supplier_GST_No": "",
    #                 "Header_Status": "NEW",
    #                 "Reprocessed": "",
    #                 "Remark": reason,
    #                 "Employee_gid": emp_gid,
    #                 "GROUP": "INWARD",
    #                 "branch_gid": branch_gid,
    #                 "Advance_incr": "E",
    #                 "Commodity_gid": comoditygid
    #             }
    #         elif jsondata.apptype == "CLAIM":
    #             tmp_data = {
    #                 "IsTa": "Y",
    #                 "Invoice_Type": "TCF",
    #                 "Supplier_gid": 0,
    #                 "Sup_state_gid": 1,
    #                 "Inwarddetails_gid": 1,
    #                 "Is_GST": "N",
    #                 "Invoice_Date": requestdate,
    #                 "Invoice_No": "TOUR" + str(tour_no) + "Exp",
    #                 "Invoice_Tot_Amount": tot,
    #                 "invoicetaxamount": tot,
    #                 "Supplier_GST_No": "",
    #                 "Header_Status": "NEW",
    #                 "Reprocessed": "",
    #                 "Remark": reason,
    #                 "Employee_gid": emp_gid,
    #                 "GROUP": "INWARD",
    #                 "branch_gid": branch_gid,
    #                 "Advance_incr": "E",
    #                 "Commodity_gid": comoditygid
    #             }
    #         header = []
    #         header.append(tmp_data)
    #         tmp = {
    #             "params": {
    #                 "header_json": {"HEADER": header},
    #                 "detail_json": {},
    #                 "invoice_json": {},
    #                 "debit_json": {},
    #                 "credit_json": {},
    #                 "status_json": {}
    #             }
    #         }
    #         datas = json.dumps(tmp)
    #         resp = requests.post("" + ip + "/ECFInvoice", params=params, data=datas, headers=headers,
    #                              verify=False)
    #         response = resp.content.decode("utf-8")
    #         response = json.loads(response)
    #         response['advancegid'] = advancegid
    #         return response

    # def glmapping_get(self,gl_desc, tour_reason, gender, entitygid):
    #     gl_map=Glmapping.objects.using(self._current_app_schema()).filter(gl_description=gl_desc,
    #                                     tourreason=tour_reason,gender=gender,entity=entitygid)
    #     return gl_map
    #
    #
    # def tourreqdata_get(self,tourgid):
    #     data= TourRequest.objects.using(self._current_app_schema()).filter(id=tourgid)
    #     return data
    #
    # def empwise_grade_get(self,grade):
    #     data=Employeemapping.objects.using(self._current_app_schema()).filter(grade=grade)
    #     return data

    # def get_expensedetails(self, dt, entity_gid):
    #     subcat = dt.get('description')
    #     # filter = {
    #     #     "Claimreqgid": dt.get('claimreq_gid'),
    #     #     "Entity_Gid": entity_gid
    #     # }
    #     if subcat == 'Travelling Expenses':
    #         ld_out_message = obj_eclaim.eClaim_travelexp_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Daily Diem':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_dailydiem_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Incidental Expenses':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_incidental_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Local Conveyance':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_loccon_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Lodging':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_lodging_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Miscellaneous Charges':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_miscellaneous_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Packaging/Freight':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_packingmoving_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #     elif subcat == 'Local Deputation Allowance':
    #         obj_eclaim.filter_json = json.dumps(filter)
    #         ld_out_message = obj_eclaim.eClaim_localdeputation_get()
    #         if ld_out_message.get("MESSAGE") == 'FOUND':
    #             dict = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
    #             return dict
    #
    #
    # def invoice_detail(self, request, jsondata):
    #     try:
    #         # obj_claim = meClaim.eClaim_Model()
    #         tourgid = jsondata.tourgid
    #         entity_gid = jsondata.Entity_Gid
    #         out_data = 0
    #         if jsondata.apptype == "TOURADV":
    #             service= TourAdvance()
    #             out_data = service.get_tour_advance(tourgid)
    #             # out_data = json.loads(out_data[0].get('advance'))
    #
    #         elif jsondata.apptype == "CLAIM":
    #             obj_claim.filter_json = json.dumps({"Claimrequest_Tourgid": tourgid, "Entity_Gid": entity_gid})
    #             out_data = obj_claim.eClaim_claimedexpense_get()
    #             out_data = json.loads(out_data.get("DATA").to_json(orient='records'))
    #
    #         service = Tourno_details()
    #         ld_out_emp = service.requestno_get(tourgid)
    #         ld_dict = json.loads(ld_out_emp)
    #         emp_gid = ld_dict['employee_id']
    #         tour_no = ld_dict['request_no']
    #         empgrade = ld_dict['employee_grade']
    #         service=emp_dtl()
    #         branchgid = service.employee_bracnh_get(emp_gid)
    #         date = datetime.today()
    #         requestdate = date
    #         tot = 0
    #         reason = 0
    #         advancecat_gid = 0
    #         advance_subcat_gid = 0
    #         advance_subcat_gl = 0
    #         if jsondata.apptype == "CLAIM":
    #             emp_data = {
    #                 "empids": emp_gid
    #             }
    #             # obj_claim.filter_json = json.dumps(emp_data)
    #             # obj_claim.json_classification = json.dumps(jsondata.get('Params').get('CLASSIFICATION'))
    #             service=Ecf_entry()
    #             emp_out_message = service.tourreqdata_get(tourgid)
    #             if emp_out_message is not None:
    #                 employee_gender = emp_out_message[0].employee_gender
    #             else:
    #                 data = {"MESSAGE": "Employee Gender Missing"}
    #                 return data
    #             # obj_claim.filter_json = json.dumps({"Tour_Gid": tourgid, "Entity_Gid": entity_gid})
    #             service=Ecf_entry()
    #             tourreason_data = service.tourreqdata_get(tourgid)
    #             if tourreason_data is not None:
    #                 tour_reason = tourreason_data[0].reason
    #             else:
    #                 data = {"MESSAGE": "Tour Reason Missing"}
    #                 return data
    #             if "General" in str(tour_reason):
    #                 reason = tour_reason.split('-')
    #                 tour_reason = reason[1]
    #             # obj_claim.filter_json = json.dumps({"Grade": empgrade})
    #             sservice=Ecf_entry()
    #             designation_data = service.empwise_grade_get(empgrade)
    #             if designation_data is not None:
    #                 designation = designation_data[0].get('designation')
    #             else:
    #                 data = {"MESSAGE": "Employee Designation Mapping Data Missing"}
    #                 return data
    #             if designation == "EXECUTIVE" or designation == "OFFICER":
    #                 designation = designation + 'S'
    #             gl_description = "TRAVEL EXPENSES-- " + designation
    #             if employee_gender == 'M':
    #                 gender_data = 'Male'
    #             elif employee_gender == 'F':
    #                 gender_data = 'Female'
    #             gl_mapping = service.glmapping_get(gl_description,tour_reason,gender_data,entity_gid)
    #             if gl_mapping is not None:
    #                 cat_code = gl_mapping[0].get('categorycode')
    #             else:
    #                 data = {"MESSAGE": "GL Mapping Data Missing"}
    #                 return data
    #             service=Ecf_entry
    #             cat_data = service.cat_apicall( request, cat_code, entity_gid)
    #             if cat_data is not None:
    #                 cat_gid = cat_data.get('DATA')[0].get('category_gid')
    #             else:
    #                 data = {"MESSAGE": "Catogory Data Missing"}
    #                 return data
    #             subcatogry_data = service.subcat_apicall(request, cat_gid, entity_gid)
    #             if subcatogry_data is not None:
    #                 subcat_data = subcatogry_data.get('DATA')
    #             else:
    #                 data = {"MESSAGE": "SubCatogory Data Missing"}
    #                 return data
    #         elif jsondata.apptype == "TOURADV":
    #             # obj_claim.filter_json = json.dumps(
    #             #     {"Gl_Desc": "ADVANCE", "Tour_Reason": "ADVANCE", "Gender": "Other",
    #             #      "Entity_Gid": entity_gid})
    #             service=Ecf_entry()
    #             # gl_desc, tour_reason, gender, entitygid
    #             gl_mapping = service.glmapping_get("ADVANCE","ADVANCE","Other",entity_gid)
    #             if gl_mapping is not None:
    #                 cat_code = gl_mapping[0].categorycode
    #                 subcat_code = gl_mapping[0].subcategorycode
    #             else:
    #                 data = {"MESSAGE": "GL Mapping Data Missing"}
    #                 return data
    #             service=Ecf_entry
    #             cat_data = service.cat_apicall(request, cat_code, entity_gid)
    #             if cat_data.get("MESSAGE") == 'FOUND':
    #                 advancecat_gid = cat_data.get('DATA')[0].get('category_gid')
    #             else:
    #                 data = {"MESSAGE": "Catogory Data Missing"}
    #                 return data
    #             subcatogry_data = service.subcat_apicall(request, advancecat_gid, entity_gid)
    #             if subcatogry_data.get("MESSAGE") == 'FOUND':
    #                 subcat_data = subcatogry_data.get('DATA')
    #             else:
    #                 data = {"MESSAGE": "SubCatogory Data Missing"}
    #                 return data
    #             for d in subcat_data:
    #                 if int(d.get('subcategory_no')) == int(subcat_code):
    #                     advance_subcat_gid = d.get('subcategory_gid')
    #                     advance_subcat_gl = d.get('subcategory_glno')
    #
    #         adv_gid = 0
    #         if jsondata.apptype == "TOURADV":
    #             for ot in out_data:
    #                 if ot.get('status') == 0:
    #                     adv_gid = ot.get('gid')
    #                     tot = ot.get('appamount')
    #             sno = "_" + str(len(out_data))
    #         elif jsondata.apptype == "CLAIM":
    #             for d in out_data:
    #                 tot = tot + d.get('approvedamount')
    #             reason = out_data[0].get('requestorcomment')
    #
    #
    #         bank_data = service.bank_details_get(emp_gid)
    #         header_gid = response.get('Header_Gid')
    #         detail = 0
    #         debit = 0
    #         claim_details = []
    #         claim_debit = []
    #         adv_debit = []
    #         if len(bank_data) != 0:
    #             service=Common_dropdown_ser()
    #             ccbs_data = service.ccbs_get(tourgid ,1) #tourgid, ccbs_type
    #             if ccbs_data is not None:
    #                 ccbs_detail = json.loads(ccbs_data.get("DATA").to_json(orient='records'))
    #                 for ccbsdtl in ccbs_detail:
    #                     if adv_gid == ccbsdtl.get('claimreqgid'):
    #                         data = {
    #                             "Invoice_Header_Gid": header_gid,
    #                             "Invoice_Details_Gid": "0",
    #                             "Category_Gid": advancecat_gid,
    #                             "Sub_Category_Gid": advance_subcat_gid,
    #                             # "Category_Gid": 122,
    #                             # "Sub_Category_Gid": 776,
    #                             "GL_No": advance_subcat_gl,
    #                             "Debit_Amount": round(ccbsdtl.get('amount'), 2),
    #                             # "Debit_Amount": tot,
    #                             "Debit_Gid": "0",
    #                             "Invoice_Sno": 1,
    #                             "cc_id": ccbsdtl.get('ccgid'),
    #                             "bs_id": ccbsdtl.get('bsgid'),
    #                             "Debit_percentage": ccbsdtl.get('percentage')}
    #                         adv_debit.append(data)
    #
    #             else:
    #                 data = {
    #                     "Invoice_Header_Gid": header_gid,
    #                     "Invoice_Details_Gid": "0",
    #                     "Category_Gid": advancecat_gid,
    #                     "Sub_Category_Gid": advance_subcat_gid,
    #                     # "Category_Gid": 122,
    #                     # "Sub_Category_Gid": 776,
    #                     "GL_No": advance_subcat_gl,
    #                     "Debit_Amount": round(tot, 2),
    #                     "Debit_Gid": "0",
    #                     "Invoice_Sno": 1,
    #                     "cc_id": 141,
    #                     "bs_id": 49,
    #                     "Debit_percentage": 100}
    #                 adv_debit.append(data)
    #
    #             empBank = bank_data[0].get('bankdetails_gid')
    #             accno = bank_data[0].get('bankdetails_acno')
    #         else:
    #             data = {"MESSAGE": "Employee Bank Data Missing"}
    #             return data
    #
    #         if jsondata.get('Params').get('DETAILS').get('apptype') == "TOURADV":
    #             detail = {
    #                 "DETAIL": [{
    #                     "Item_Name": "ADVANCE",
    #                     "Description": "ADVANCE",
    #                     "HSN_Code": "1",
    #                     "Unit_Price":round(tot, 2),
    #                     "Quantity": "1",
    #                     "Amount": round(tot, 2),
    #                     "Discount": 0,
    #                     "IGST": 0,
    #                     "CGST": 0,
    #                     "SGST": 0,
    #                     "Total_Amount": round(tot, 2),
    #                     "PO_Header_Gid": "0",
    #                     "PO_Detail_Gid": 0,
    #                     "GRN_Header_Gid": 0,
    #                     "GRN_Detail_Gid": 0,
    #                     "Invoice_Header_gid": header_gid,
    #                     "Invoice_Sno": 1,
    #                     "Invoice_Other_Amount": 0
    #                 }
    #                 ]}
    #             debit = {"DEBIT": adv_debit}
    #         elif jsondata.get('Params').get('DETAILS').get('apptype') == "CLAIM":
    #             sno = 1
    #             tmp = 0
    #             for ot in out_data:
    #                 details_exp = get_expensedetails(self, ot, entity_gid)
    #                 for d in details_exp:
    #                     if tmp == sno:
    #                         sno = sno + 1
    #                     amount = d.get('appamt')
    #                     total_amount = int(d.get('appamt'))
    #                     vendor_name = ''
    #                     vendor_code = ''
    #                     branchgstno = ''
    #                     suppliergstno = ''
    #                     IGST = 0
    #                     CGST = 0
    #                     SGST = 0
    #                     HSN_Code = '1'
    #                     gst = False
    #                     gst_igst = False
    #                     if ot.get('description') == 'Travelling Expenses' or ot.get(
    #                             'description') == 'Lodging' or ot.get('description') == 'Packaging/Freight':
    #                         vendor_code = d.get('vendorcode')
    #                         vendor_name = d.get('vendorname')
    #                         branchgstno = d.get('bankgstno')
    #                         suppliergstno = d.get('vendorgstno')
    #                         IGST = d.get('igst')
    #                         CGST = d.get('cgst')
    #                         SGST = d.get('sgst')
    #                         HSN_Code = d.get('hsncode')
    #                         if branchgstno != '' and suppliergstno != '' and branchgstno != 'NA' and suppliergstno != 'NA':
    #                             gst = True
    #                             if branchgstno[0:2] == suppliergstno[0:2]:
    #                                 percent = int(CGST) + int(SGST)
    #                                 amt = int(d.get('appamt')) * percent / 100
    #                                 IGST = 0
    #                                 CGST = "{:.2f}".format(amt / 2)
    #                                 SGST = "{:.2f}".format(amt / 2)
    #                                 # total_amount = "{:.2f}".format(int(amount) + amt)
    #                             else:
    #                                 gst_igst = True
    #                                 amt = int(d.get('appamt')) * int(IGST) / 100
    #                                 IGST = "{:.2f}".format(amt)
    #                                 CGST = 0
    #                                 SGST = 0
    #                                 # total_amount = "{:.2f}".format(int(amount) + amt)
    #                     dt = {
    #                         "Item_Name": ot.get('description'),
    #                         "Description": ot.get('description'),
    #                         "HSN_Code": HSN_Code,
    #                         "Unit_Price": d.get('appamt'),
    #                         "Quantity": "1",
    #                         # "Amount": amount,
    #                         "Amount": round(total_amount, 2),
    #                         "Discount": 0,
    #                         "IGST": 0,
    #                         "CGST": 0,
    #                         "SGST": 0,
    #                         "Total_Amount": round(total_amount, 2),
    #                         "PO_Header_Gid": "0",
    #                         "PO_Detail_Gid": 0,
    #                         "GRN_Header_Gid": 0,
    #                         "GRN_Detail_Gid": 0,
    #                         "Invoice_Header_gid": header_gid,
    #                         "Invoice_Sno": sno,
    #                         "Invoice_Other_Amount": 0,
    #                         "_branchgstno": branchgstno,
    #                         "_invoiceno": "TOUR" + str(tour_no),
    #                         "_suppliercode": vendor_code,
    #                         "_suppliername": vendor_name,
    #                         "_suppliergstno": suppliergstno,
    #                         "_branchgid": branchgid,
    #                         "_invoicedate": requestdate
    #                     }
    #                     claim_details.append(dt)
    #                     service=Ecf_entry()
    #                     subcatogry = service.get_subcat( subcat_data, ot.get('description'))
    #
    #                     # obj_claim.filter_json = json.dumps({"Tour_Gid": tourgid, "CCBS_Type": 2})
    #                     service=Common_dropdown_ser()
    #                     ccbs_data = service.ccbs_get(tourgid,2)
    #                     if ccbs_data.get("MESSAGE") == 'FOUND':
    #                         ccbs_detail = json.loads(ccbs_data.get("DATA").to_json(orient='records'))
    #                         for ccbsdtl in ccbs_detail:
    #                             amount = int(d.get('appamt'))/100 * int(ccbsdtl.get('percentage'))
    #                             debit = {
    #                                 "Invoice_Header_Gid": header_gid,
    #                                 "Invoice_Details_Gid": "0",
    #                                 "Category_Gid": cat_gid,
    #                                 "Sub_Category_Gid": subcatogry.get('subcat_gid'),
    #                                 "GL_No": subcatogry.get('gl_no'),
    #                                 "Debit_Amount": round(amount, 2),
    #                                 # "Debit_Amount": ccbsdtl.get('amount'),
    #                                 "Debit_Gid": "0",
    #                                 "Invoice_Sno": sno,
    #                                 "cc_id": ccbsdtl.get('ccgid'),
    #                                 "bs_id": ccbsdtl.get('bsgid'),
    #                                 "Debit_percentage": ccbsdtl.get('percentage')
    #                             }
    #                             claim_debit.append(debit)
    #
    #
    #                     tmp = int(sno)
    #                 sno = int(sno) + 1
    #
    #             detail = {
    #                 "DETAIL": claim_details
    #             }
    #             debit = {
    #                 "DEBIT": claim_debit
    #             }
    #         sum_amount = 0
    #         for dtl in detail.get('DETAIL'):
    #             sum_amount = float(dtl.get('Total_Amount')) + sum_amount
    #         claim_credit = []
    #         service=Ecf_entry
    #         paymode_data = service.paymode_apicall( request, entity_gid)
    #         if paymode_data is not None:
    #             paymodedata = paymode_data.get('DATA')
    #         else:
    #             data = {"MESSAGE": "Paymode Data  Missing"}
    #             return data
    #         for pay in paymodedata:
    #             if pay.get('Paymode_name') == "ERA":
    #                 era_gid = pay.get('paymode_gid')
    #             elif pay.get('Paymode_name') == "PPX":
    #                 ppx_gid = pay.get('paymode_gid')
    #         if jsondata.get('Params').get('DETAILS').get('apptype') == "TOURADV":
    #             credit = {"CREDIT":
    #                 [{
    #                     "Invoice_Header_Gid": header_gid,
    #                     "Paymode_Gid": era_gid,
    #                     "Paymode_name": "ERA",
    #                     "GL_No": accno,
    #                     "Bank_Gid": empBank,
    #                     "Ref_No": accno,
    #                     "Tax_Gid": "",
    #                     "Tax_Type": "",
    #                     "Tax_Rate": "",
    #                     "TDS_Exempt": "N",
    #                     "Credit_Amount": round(sum_amount, 2),
    #                     "Credit_Gid": "0",
    #                     "taxable_amt": 0,
    #                     "ppx_headergid": 0,
    #                     "Is_due": "false",
    #                     "supplier_gid": ""
    #                 }]
    #             }
    #         elif jsondata.get('Params').get('DETAILS').get('apptype') == "CLAIM":
    #             # Advance Liqudation so that this code Commented
    #             service= TourAdvance()
    #             out_advdata = service.advance_get(tourgid)
    #             out_adv = json.loads(out_advdata.get("DATA").to_json(orient='records'))
    #             totadv_amt = 0
    #             if out_adv[0].get('advance') != None:
    #                 advance = json.loads(out_adv[0].get('advance'))
    #                 for adv in advance:
    #                     if adv.get('adjustamount') != None:
    #                         totadv_amt = float(totadv_amt) + float(adv.get('adjustamount'))
    #
    #             credit_amt = float(sum_amount) - float(totadv_amt)
    #             if credit_amt == 0:
    #                 credit_amt = 0
    #             elif credit_amt > 0:
    #                 credit_amt = credit_amt
    #             else:
    #                 credit_amt = 0
    #             if credit_amt !=0:
    #                 credit = {
    #                     "Invoice_Header_Gid": header_gid,
    #                     "Paymode_Gid": era_gid,
    #                     "Paymode_name": "ERA",
    #                     "GL_No": accno,
    #                     "Bank_Gid": empBank,
    #                     "Ref_No": accno,
    #                     "Tax_Gid": "",
    #                     "Tax_Type": "",
    #                     "Tax_Rate": "",
    #                     "TDS_Exempt": "N",
    #                     "Credit_Amount": round(credit_amt, 2),
    #                     "Credit_Gid": "0",
    #                     "taxable_amt": 0,
    #                     "ppx_headergid": 0,
    #                     "Is_due": "false",
    #                     "supplier_gid": ""
    #                 }
    #                 claim_credit.append(credit)
    #             if out_adv[0].get('advance') != None:
    #                 advance = json.loads(out_adv[0].get('advance'))
    #                 # obj_claim.filter_json = json.dumps(
    #                 #     {"Gl_Desc": "ADVANCE", "Tour_Reason": "ADVANCE", "Gender": "Other",
    #                 #      "Entity_Gid": entity_gid})
    #                 service=Ecf_entry()
    #                 gl_mapping = service.glmapping_get("ADVANCE","ADVANCE","Other",entity_gid)
    #                 if gl_mapping.get("MESSAGE") == 'FOUND':
    #                     gl_mapping = json.loads(gl_mapping.get("DATA").to_json(orient='records'))
    #                     cat_code = gl_mapping[0].get('categorycode')
    #                     subcat_code = gl_mapping[0].get('subcategorycode')
    #                 else:
    #                     data = {"MESSAGE": "GL Mapping Data Missing"}
    #                     return data
    #                 service=Ecf_entry()
    #                 cat_data = service.cat_apicall( request, cat_code, entity_gid)
    #                 if cat_data.get("MESSAGE") == 'FOUND':
    #                     advancecat_gid = cat_data.get('DATA')[0].get('category_gid')
    #                 else:
    #                     data = {"MESSAGE": "Catogory Data Missing"}
    #                     return data
    #                 subcatogry_data = service.subcat_apicall( request, advancecat_gid, entity_gid)
    #                 if subcatogry_data.get("MESSAGE") == 'FOUND':
    #                     subcat_data = subcatogry_data.get('DATA')
    #                 else:
    #                     data = {"MESSAGE": "SubCatogory Data Missing"}
    #                     return data
    #                 for d in subcat_data:
    #                     if int(d.get('subcategory_no')) == int(subcat_code):
    #                         advance_subcat_gid = d.get('subcategory_gid')
    #                         advance_subcat_gl = d.get('subcategory_glno')
    #                 remaining_adv = float(sum_amount)
    #                 for adv in advance:
    #                     if adv.get('adjustamount') != None:
    #                         adjustamount = 0
    #                         credit_amt = remaining_adv - float(adv.get('adjustamount'))
    #                         if credit_amt == 0:
    #                             adjustamount = adv.get('adjustamount')
    #                         elif credit_amt > 0:
    #                             remaining_adv = credit_amt
    #                             adjustamount = adv.get('adjustamount')
    #                         else:
    #                             adjustamount = float(adv.get('adjustamount')) - remaining_adv
    #                             remaining_adv = 0
    #
    #                         credit = {
    #                             "Invoice_Header_Gid": header_gid,
    #                             "Paymode_Gid": ppx_gid,
    #                             "Paymode_name": "PPX",
    #                             "GL_No": advance_subcat_gl,
    #                             "Bank_Gid": 0,
    #                             "Ref_No": adv.get('crnno'),
    #                             "Tax_Gid": "",
    #                             "Tax_Type": "",
    #                             "Tax_Rate": "",
    #                             "TDS_Exempt": "N",
    #                             "trnbranch": "",
    #                             "paybranch": "",
    #                             "Credit_Amount": round(adjustamount, 2),
    #                             "Credit_Gid": "0",
    #                             "taxable_amt": 0,
    #                             "ppx_headergid": adv.get('ppx_headergid'),
    #                             "Is_due": "false",
    #                             "supplier_gid": 0,
    #                             "Credit_catgid": adv.get('debit_categorygid'),
    #                             "Credit_subcatgid": adv.get('debit_subcategorygid')
    #                         }
    #                         claim_credit.append(credit)
    #
    #             credit = {
    #                 "CREDIT": claim_credit
    #             }
    #
    #         obj_claim.filter_json = json.dumps({"Tour_gid": tourgid})
    #         ld_out_file = obj_claim.eClaim_file_get()
    #         file = json.loads(ld_out_file.get("DATA").to_json(orient='records'))
    #         filedata = []
    #         if file != []:
    #             for i in file:
    #                 data = {
    #                     "file_key": i.get('file_path'),
    #                     "file_path": i.get('file_name'),
    #                 }
    #                 filedata.append(data)
    #
    #         status = {
    #             "Invoice_Header_Gid": header_gid,
    #             "Status": "APPROVED",
    #             "Emp_id": jsondata.get('Params').get('DETAILS').get('processedby'),
    #             "Individual_approval": "Y",
    #             "file_data": filedata
    #         }
    #         params = {"action": "INSERT",
    #                   "type": "INVOICE_DETAILS",
    #                   "entity_gid": jsondata.get('Params').get('DETAILS').get('Entity_Gid'),
    #                   "employee_gid": jsondata.get('Params').get('DETAILS').get('processedby')}
    #         tmp_dtl = {
    #             "params": {
    #                 "header_json": {},
    #                 "detail_json": detail,
    #                 "invoice_json": {},
    #                 "debit_json": debit,
    #                 "credit_json": credit,
    #                 "status_json": status
    #             }
    #         }
    #         tk = str(request.auth.token)
    #         token = "Bearer  " + tk[2:len(tk) - 1]
    #         headers = {"content-type": "application/json", "Authorization": "" + token + ""}
    #         data_dtl = json.dumps(tmp_dtl)
    #         resp = requests.post("" + ip + "/ECFInvoice", params=params, data=data_dtl, headers=headers,
    #                              verify=False)
    #         response_data = resp.content.decode("utf-8")
    #         response_data = json.loads(response_data)
    #         return response_data
    #     except Exception as e:
    #         er = "Erro Line no :" + str(format(sys.exc_info()[-1].tb_lineno)) + " " + "Error :" + str(e)
    #         return er


