import json

import numpy as np
from django.db.models import Q
from django.http.response import HttpResponse
from six import BytesIO

from taservice.data.response.report_res import Report_res
from taservice.models import TourRequest, TourDetail, TourAdvance, ClaimRequest, TourReason, Travel, Dailydeim, \
    Incidental, Localconveyence, Lodging, Misc, PackingMoving, TravelHistory, AirBookingInfo, TrainBookingInfo, \
    BusBookingInfo, CabBookingInfo, TourExpense as TourExpenseModel, Ccbs
# from taservice.service.emp_name_get import emp_dtl
from taservice.service.common_dropdown_ser import Common_dropdown_ser
from taservice.service.tourexpense import TourExpense
from taservice.service.tourmaker import TourMaker
from taservice.util.ta_util import tour_summary_status, Status, App_type, status_get, App_level, Claim_status, \
    claim_summary_status, Travel_requirements
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist  import NWisefinList
import pandas as pd
from datetime import datetime, timezone

from utilityservice.data.response.nwisefinpage  import NWisefinPage
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService

today = datetime.now(timezone.utc)

from utilityservice.service.threadlocal import NWisefinThread
class Report_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def get_tour_report(self,tourno,empgid,from_date,to_date,month,request,vys_page):
        if tourno == None  and empgid ==None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]

        if tourno !=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(id=tourno,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        elif empgid != None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empgid,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        elif from_date !=None and to_date!=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date__gte=from_date,end_date__lte=to_date,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]
        elif from_date !=None and to_date==None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date=from_date,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]

        elif month!=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date__month=month,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]

        # elif branchid != None:
        #     list = TourRequest.objects.using(self._current_app_schema()).filter(empbranchgid=branchid)[vys_page.get_offset():vys_page.get_query_limit()]
        res_list=NWisefinList()
        req_data=Report_res()
        for tour_detail in list:
            report_res = Report_res()
            # report_res.set_requestno(tour_detail.requestno)
            report_res.set_tourid(tour_detail.id)
            report_res.set_requestdate(tour_detail.request_date)
            report_res.set_empgid(tour_detail.empgid)
            empdtl=ApiService(self._scope())
            employee=empdtl.employee_details_get(tour_detail.empgid, request)
            report_res.set_employee_name(employee.full_name)
            # code=empdtl.employee_code_get(tour_detail.empgid)
            report_res.set_employee_code(employee.code)

            report_res.set_empdesignation(tour_detail.empdesignation)
            report_res.set_empgrade(tour_detail.empgrade)
            report_res.set_empbranchgid(tour_detail.empbranchgid)
            detail=self.get_tour_detail(tour_detail.id,request)
            report_res.set_detail(detail)
            branch=empdtl.get_branch_data(tour_detail.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode=empdtl.get_branch_code(tour_detail.empbranchgid)
            report_res.set_branch_code(branch.code)

            reason=Report_ser.get_reason_name(self,tour_detail.reason)
            report_res.set_reason(reason)
            permitted=empdtl.employee_details_get(tour_detail.permittedby,request)
            report_res.set_permittedby(permitted.full_name)
            report_res.set_startdate(tour_detail.start_date)
            report_res.set_enddate(tour_detail.end_date)
            report_res.set_durationdays(tour_detail.durationdays)
            # report_res.set_eligiblemodeoftravel(tour_detail.eligiblemodeoftravel)
            report_res.set_ordernoremarks(tour_detail.remarks)
            if tour_detail.onbehalfof > 0:
                onbehalf=empdtl.employee_details_get(tour_detail.onbehalfof,request)
                report_res.set_onbehalfof(onbehalf.full_name)

            summary_status=claim_summary_status(tour_detail.claim_status)
            # report_res.set_advance_status(tour_detail.advance_status)
            report_res.set_claim_status(summary_status)
            # report_res.set_tour_status(tour_detail.tour_status)

            app_amount = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            approvedamount=0
            claimedamount=0
            for app_detail in app_amount:
                approvedamount+=app_detail.approvedamount
                claimedamount+=app_detail.claimedamount
            report_res.set_approvedamount(approvedamount)
            report_res.set_claimedamount(claimedamount)

            adv_amount = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            advanceamount = 0
            for adv_detail in adv_amount:
                advanceamount+=adv_detail.appamount
            report_res.set_advanceamount(advanceamount)
            res_list.append(report_res)
            # req_data.set_data(res_list)
            vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
            res_list.set_pagination(vpage)
        return res_list



    def tour_report_view(self,tourno,empgid,from_date,to_date,month,request,vys_page):
        if tourno == None  and empgid ==None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]

        if tourno !=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(id=tourno,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        elif empgid != None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empgid,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        elif from_date !=None and to_date!=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date__gte=from_date,end_date__lte=to_date,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]
        elif from_date !=None and to_date==None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date=from_date,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]

        elif month!=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(start_date__month=month,
                                                                                entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]

        # elif branchid != None:
        #     list = TourRequest.objects.using(self._current_app_schema()).filter(empbranchgid=branchid)[vys_page.get_offset():vys_page.get_query_limit()]
        res_list=NWisefinList()
        req_data=Report_res()
        for tour_detail in list:
            report_res = Report_res()
            # report_res.set_requestno(tour_detail.requestno)
            report_res.set_tourid(tour_detail.id)
            report_res.set_requestdate(tour_detail.request_date)
            report_res.set_empgid(tour_detail.empgid)
            empdtl=ApiService(self._scope())
            employee=empdtl.employee_details_get(tour_detail.empgid, request)
            report_res.set_employee_name(employee.full_name)
            # code=empdtl.employee_code_get(tour_detail.empgid)
            report_res.set_employee_code(employee.code)

            report_res.set_empdesignation(tour_detail.empdesignation)
            report_res.set_empgrade(tour_detail.empgrade)
            report_res.set_empbranchgid(tour_detail.empbranchgid)
            detail=self.get_tour_detail(tour_detail.id,request)
            report_res.set_detail(detail)
            branch=empdtl.get_branch_data(tour_detail.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode=empdtl.get_branch_code(tour_detail.empbranchgid)
            report_res.set_branch_code(branch.code)

            reason=Report_ser.get_reason_name(self,tour_detail.reason)
            report_res.set_reason(reason)
            permitted=empdtl.employee_details_get(tour_detail.permittedby,request)
            report_res.set_permittedby(permitted.full_name)
            report_res.set_startdate(tour_detail.start_date)
            report_res.set_enddate(tour_detail.end_date)
            report_res.set_durationdays(tour_detail.durationdays)
            # report_res.set_eligiblemodeoftravel(tour_detail.eligiblemodeoftravel)
            report_res.set_ordernoremarks(tour_detail.remarks)
            if tour_detail.onbehalfof > 0:
                onbehalf=empdtl.employee_details_get(tour_detail.onbehalfof,request)
                report_res.set_onbehalfof(onbehalf.full_name)

            summary_status=claim_summary_status(tour_detail.claim_status)
            # report_res.set_advance_status(tour_detail.advance_status)
            report_res.set_claim_status(summary_status)
            # report_res.set_tour_status(tour_detail.tour_status)

            app_amount = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            approvedamount=0
            claimedamount=0
            for app_detail in app_amount:
                approvedamount+=app_detail.approvedamount
                claimedamount+=app_detail.claimedamount
            report_res.set_approvedamount(approvedamount)
            report_res.set_claimedamount(claimedamount)

            adv_amount = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            advanceamount = 0
            for adv_detail in adv_amount:
                advanceamount+=adv_detail.appamount
            report_res.set_advanceamount(advanceamount)
            res_list.append(report_res)
            # req_data.set_data(res_list)
            vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
            res_list.set_pagination(vpage)
        return res_list


    def claim_report_view(self,tourno,empgid,from_date,to_date,request,vys_page):
        condition=Q(entity_id=self._entity_id(),status=1)
        start_date=from_date
        end_date=to_date
        if empgid is not None:
            condition &= Q(tour__empgid=empgid)
        if tourno is not None:
            condition &= Q(tour__id=tourno)
        if start_date != None:
            try:
                start_date = int(start_date)
                start_date = str(datetime.fromtimestamp(int(start_date) / 1000.0))
                start_date = (datetime.strptime(start_date[:10], '%Y-%m-%d')).date()
            except:
                start_date = (datetime.strptime(start_date, '%d-%b-%Y')).date()

            condition &= Q(tour__start_date__gte=start_date)

        if end_date != None:
            try:
                end_date = int(end_date)
                end_date = str(datetime.fromtimestamp(int(end_date) / 1000.0))
                end_date = (datetime.strptime(end_date[:10], '%Y-%m-%d')).date()
            except:
                end_date = (datetime.strptime(end_date, '%d-%b-%Y')).date()

            condition &= Q(tour__end_date__lte=end_date)
        claim_data=ClaimRequest.objects.using(self._current_app_schema()).filter(condition).order_by("-tour_id")[
                   vys_page.get_offset():vys_page.get_query_limit()]
        res_list = NWisefinList()
        for each_claim in claim_data:
            report_res = Report_res()
            tour=each_claim.tour_id
            ccbs_service=Common_dropdown_ser(self._scope())
            ccbs_data=ccbs_service.ccbs_get(tour,2,request,0)
            expense_name=TourExpenseModel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=each_claim.expensegid)

            report_res.set_travel_no(tour)
            report_res.set_ccbs_data(ccbs_data)
            report_res.set_expense_name(expense_name.name)
            report_res.set_claimed_amount(each_claim.claimedamount)
            report_res.set_comment(each_claim.requestercomment)
            res_list.append(report_res)
            vpage = NWisefinPaginator(claim_data, vys_page.get_index(), 10)
            res_list.set_pagination(vpage)
        return res_list


    def claim_report_download(self,tourno,empgid,from_date,to_date):
        condition = Q(entity_id=self._entity_id(), status=1)
        start_date = from_date
        end_date = to_date
        if empgid is not None:
            condition &= Q(tour__empgid=empgid)
        if tourno is not None:
            condition &= Q(tour__id=tourno)
        if start_date != None:
            try:
                start_date = int(start_date)
                start_date = str(datetime.fromtimestamp(int(start_date) / 1000.0))
                start_date = (datetime.strptime(start_date[:10], '%Y-%m-%d')).date()
            except:
                start_date = (datetime.strptime(start_date, '%d-%b-%Y')).date()

            condition &= Q(tour__start_date__gte=start_date)

        if end_date != None:
            try:
                end_date = int(end_date)
                end_date = str(datetime.fromtimestamp(int(end_date) / 1000.0))
                end_date = (datetime.strptime(end_date[:10], '%Y-%m-%d')).date()
            except:
                end_date = (datetime.strptime(end_date, '%d-%b-%Y')).date()

            condition &= Q(tour__end_date__lte=end_date)
        claim_data=ClaimRequest.objects.using(self._current_app_schema()).filter(condition).values("tour_id","expensegid",
                                                                                                                              "claimedamount").order_by("-tour_id")
        ccbs_data=Ccbs.objects.using(self._current_app_schema()).filter(ccbs_type=2,status=1,entity_id=self._entity_id()).values("tour_id","ccid","bsid",
                                                                                                                              "percentage","amount")

        expense_name_data = TourExpenseModel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).values("id","name")
        claim_data_df = pd.DataFrame(claim_data)
        ccbs_data_df = pd.DataFrame(ccbs_data)
        expense_name_df = pd.DataFrame(expense_name_data)

        df1 = pd.merge(claim_data_df, ccbs_data_df, how='left',
                       left_on=['tour_id'], right_on=['tour_id'])
        df1 = pd.merge(df1, expense_name_df, how='left',
                       left_on=['expensegid'], right_on=['id'])

        api_service=ApiService(self._scope())
        cc_data=api_service.cc_data()
        bs_data=api_service.bs_data()

        cc_df = pd.DataFrame(cc_data)
        bs_df = pd.DataFrame(bs_data)

        df1 = pd.merge(df1, cc_df, how='left',
                       left_on=['ccid'], right_on=['id'])

        df1 = pd.merge(df1, bs_df, how='left',
                       left_on=['bsid'], right_on=['id'])

        df1=df1.drop(['ccid'], axis=1)
        df1=df1.drop(['bsid'], axis=1)
        df1=df1.drop(['expensegid'], axis=1)
        df1=df1.drop(['id'], axis=1)
        df1=df1.drop(['id_x'], axis=1)
        df1=df1.drop(['id_y'], axis=1)

        df1=df1.rename({'name_x': 'Expense name'}, axis=1)
        df1=df1.rename({'name': 'CC name'}, axis=1)
        df1=df1.rename({'name_y': 'BS name'}, axis=1)
        df1=df1.rename({'tour_id': 'Travel No'}, axis=1)
        df1=df1.rename({'claimedamount': 'Claimed Amount'}, axis=1)
        df1=df1.rename({'percentage': 'BS CC Percentage'}, axis=1)
        df1=df1.rename({'amount': 'BS CC Amount'}, axis=1)

        # df1 = df1.replace({np.nan: None})

        # df1=df1.round(2)
        # print(df1)
        # response=df1.to_excel('Claim Report.xlsx', index=False, header=True, encoding='utf-8')
        # # response=df1.to_excel(r'Claim Report.xlsx', index=False)
        #
        # return HttpResponse(response)

        with BytesIO() as b:
            # Use the StringIO object as the filehandle.
            writer = pd.ExcelWriter(b, engine='xlsxwriter')
            df1.to_excel(writer, sheet_name='Sheet1')
            writer.save()
            filename = 'claim_report'
            content_type = 'application/vnd.ms-excel'
            response = HttpResponse(b.getvalue(), content_type=content_type)
            response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
            return response


        # res_list = NWisefinList()
        # for each_claim in claim_data:
        #     report_res = Report_res()
        #     tour=each_claim.tour_id
        #     ccbs_service=Common_dropdown_ser(self._scope())
        #     ccbs_data=ccbs_service.ccbs_get(tour,2,request,0)
        #     expense_name=TourExpenseModel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=each_claim.expensegid)
        #
        #     report_res.set_travel_no(tour)
        #     report_res.set_ccbs_data(ccbs_data)
        #     report_res.set_expense_name(expense_name.name)
        #     report_res.set_claimed_amount(each_claim.claimedamount)
        #     report_res.set_comment(each_claim.requestercomment)
        #     res_list.append(report_res)
        #     vpage = NWisefinPaginator(claim_data, vys_page.get_index(), 10)
        #     res_list.set_pagination(vpage)
        # return res_list


    def get_all_tour_report(self,tourno,empgid,request):
        if tourno == None  and empgid ==None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().order_by("-id")

        if tourno !=None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(id=tourno,entity_id=self._entity_id())
        elif empgid != None:
            list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empgid,entity_id=self._entity_id())
        # elif branchid != None:
        #     list = TourRequest.objects.using(self._current_app_schema()).filter(empbranchgid=branchid)[vys_page.get_offset():vys_page.get_query_limit()]
        res_list=NWisefinList()
        req_data=Report_res()
        for tour_detail in list:
            report_res = Report_res()
            # report_res.set_requestno(tour_detail.requestno)
            report_res.set_tourid(tour_detail.id)
            report_res.set_requestdate(tour_detail.request_date)
            report_res.set_empgid(tour_detail.empgid)
            empdtl=ApiService(self._scope())
            employee=empdtl.employee_details_get(tour_detail.empgid, request)
            report_res.set_employee_name(employee.full_name)
            # code=empdtl.employee_code_get(tour_detail.empgid)
            report_res.set_employee_code(employee.code)

            report_res.set_empdesignation(tour_detail.empdesignation)
            report_res.set_empgrade(tour_detail.empgrade)
            report_res.set_empbranchgid(tour_detail.empbranchgid)

            branch=empdtl.get_branch_data(tour_detail.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode=empdtl.get_branch_code(tour_detail.empbranchgid)
            report_res.set_branch_code(branch.code)

            reason=Report_ser.get_reason_name(self,tour_detail.reason)
            report_res.set_reason(reason)
            permitted=empdtl.employee_details_get(tour_detail.permittedby,request)
            report_res.set_permittedby(permitted.full_name)
            report_res.set_startdate(tour_detail.start_date)
            report_res.set_enddate(tour_detail.end_date)
            report_res.set_durationdays(tour_detail.durationdays)
            # report_res.set_eligiblemodeoftravel(tour_detail.eligiblemodeoftravel)
            report_res.set_ordernoremarks(tour_detail.remarks)
            if tour_detail.onbehalfof > 0:
                onbehalf=empdtl.employee_details_get(tour_detail.onbehalfof,request)
                report_res.set_onbehalfof(onbehalf.full_name)

            summary_status=claim_summary_status(tour_detail.claim_status)
            # report_res.set_advance_status(tour_detail.advance_status)
            report_res.set_claim_status(summary_status)
            # report_res.set_tour_status(tour_detail.tour_status)

            app_amount = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            approvedamount=0
            claimedamount=0
            for app_detail in app_amount:
                approvedamount+=app_detail.approvedamount
                claimedamount+=app_detail.claimedamount
            report_res.set_approvedamount(approvedamount)
            report_res.set_claimedamount(claimedamount)

            adv_amount = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            advanceamount = 0
            for adv_detail in adv_amount:
                advanceamount+=adv_detail.appamount
            report_res.set_advanceamount(advanceamount)
            res_list.append(report_res)
            # req_data.set_data(res_list)
            # vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
            # res_list.set_pagination(vpage)
        return res_list

    def get_tourid_report(self,tourid, empid, request,vys_page):
        res_list = NWisefinList()
        # if int(tourid)==0 and request.GET.get('all_report')!=0:
        #     list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid).order_by("-id")
        res_list = NWisefinList()
        if int(tourid) == 0:
            list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid,entity_id=self._entity_id()).order_by("-id")[
                   vys_page.get_offset():vys_page.get_query_limit()]

        else:
            list = TourRequest.objects.using(self._current_app_schema()).filter(id=tourid, empgid=empid,entity_id=self._entity_id())


        for tour_detail in list:
            report_res = Report_res()
            report_res.set_tourid(tour_detail.id)
            # report_res.set_requestno(tour_detail.requestno)
            report_res.set_requestdate(tour_detail.request_date)
            report_res.set_empgid(tour_detail.empgid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(tour_detail.empgid, request)
            report_res.set_employee_name(employee.full_name)
            # code = empdtl.employee_code_get(tour_detail.empgid)
            report_res.set_employee_code(employee.code)
            report_res.set_empdesignation(tour_detail.empdesignation)
            report_res.set_empbranchgid(tour_detail.empbranchgid)
            branch=empdtl.get_branch_data(tour_detail.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode=empdtl.get_branch_code(tour_detail.empbranchgid)
            report_res.set_branch_code(branch.code)

            reason=Report_ser.get_reason_name(self,tour_detail.reason)
            report_res.set_reason(reason)
            report_res.set_startdate(tour_detail.start_date)
            report_res.set_enddate(tour_detail.end_date)
            if tour_detail.onbehalfof>0:
                onbehalfof = empdtl.employee_details_get(tour_detail.onbehalfof,request)
                report_res.set_onbehalfof(onbehalfof)

            app_amount = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            approvedamount=0
            for app_detail in app_amount:
                approvedamount+=app_detail.approvedamount
            report_res.set_claimedamount(approvedamount)

            adv_amount = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            advanceamount = 0
            for adv_detail in adv_amount:
                advanceamount+=adv_detail.appamount
            report_res.set_advanceamount(advanceamount)

            t_status = status_get(tour_detail.tour_status)
            report_res.set_tour_status("TOUR "+ t_status)

            # a_status = status_get(tour_detail.advance_status)
            # report_res.set_advance_status("ADVANCE " +a_status)

            # c_status = status_get(tour_detail.claim_status)
            # report_res.set_claim_status(c_status)
            summary_status = claim_summary_status(tour_detail.claim_status)
            report_res.set_claim_status(summary_status)

            tour_status=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.TOUR,applevel=App_level.FIRST_LEVEL ,tour_id=tour_detail.id, entity_id=self._entity_id()).order_by("-id")
            if len(tour_status)!=0:
                tour_status=tour_status[0]
                approvedby = empdtl.employee_details_get(tour_status.approvedby,request)
                report_res.set_approvedby(approvedby.full_name)
                report_res.set_approvedby_code(approvedby.code)
            else:
                report_res.set_approvedby(None)
                report_res.set_approvedby_code(None)

            res_list.append(json.loads(report_res.get()))
            # # req_data.set_data(res_list)
        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        res_list.set_pagination(vpage)


        return res_list

    def get_alltourid_report(self, empid, request):
        res_list = NWisefinList()
        list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid,entity_id=self._entity_id()).order_by("-id")

        # list = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]

        # else:
        #     list = TourRequest.objects.using(self._current_app_schema()).filter(id=tourid, empgid=empid)


        for tour_detail in list:
            report_res = Report_res()
            report_res.set_tourid(tour_detail.id)
            # report_res.set_requestno(tour_detail.requestno)
            report_res.set_requestdate(tour_detail.request_date)
            report_res.set_empgid(tour_detail.empgid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(tour_detail.empgid, request)
            report_res.set_employee_name(employee.full_name)
            # code = empdtl.employee_code_get(tour_detail.empgid)
            report_res.set_employee_code(employee.code)
            report_res.set_empdesignation(tour_detail.empdesignation)
            report_res.set_empbranchgid(tour_detail.empbranchgid)
            branch=empdtl.get_branch_data(tour_detail.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode=empdtl.get_branch_code(tour_detail.empbranchgid)
            report_res.set_branch_code(branch.code)

            reason=Report_ser.get_reason_name(self,tour_detail.reason)
            report_res.set_reason(reason)
            report_res.set_startdate(tour_detail.start_date)
            report_res.set_enddate(tour_detail.end_date)
            if tour_detail.onbehalfof>0:
                onbehalfof = empdtl.employee_details_get(tour_detail.onbehalfof,request)
                report_res.set_onbehalfof(onbehalfof)

            app_amount = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            approvedamount=0
            for app_detail in app_amount:
                approvedamount+=app_detail.approvedamount
            report_res.set_claimedamount(approvedamount)

            adv_amount = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_detail.id,entity_id=self._entity_id())
            advanceamount = 0
            for adv_detail in adv_amount:
                advanceamount+=adv_detail.appamount
            report_res.set_advanceamount(advanceamount)

            t_status = status_get(tour_detail.tour_status)
            report_res.set_tour_status("TOUR "+ t_status)

            # a_status = status_get(tour_detail.advance_status)
            # report_res.set_advance_status("ADVANCE " +a_status)

            # c_status = status_get(tour_detail.claim_status)
            # report_res.set_claim_status(c_status)
            summary_status = claim_summary_status(tour_detail.claim_status)
            report_res.set_claim_status(summary_status)

            tour_status=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.TOUR, tour_id=tour_detail.id, entity_id=self._entity_id()).order_by("-id")
            if len(tour_status)!=0:
                tour_status=tour_status[0]
                approvedby = empdtl.employee_details_get(tour_status.approvedby,request)
                report_res.set_approvedby(approvedby.full_name)
                report_res.set_approvedby_code(approvedby.code)
            else:
                report_res.set_approvedby(None)
                report_res.set_approvedby_code(None)

            res_list.append(json.loads(report_res.get()))
            # # req_data.set_data(res_list)
        # vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        # res_list.set_pagination(vpage)


        return res_list

    def get_reason_name(self,reason):
        try:
            tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=reason,entity_id=self._entity_id())
            return tour_reason.name
        except:
            pass


    def get_tour_report_download(self,tourno,empgid,from_date,to_date,month,request,vys_page,all_report):
        service=Report_ser(self._scope())
        if all_report is not None:
            data=service.get_all_tour_report(tourno,empgid,request)
        else:
            data=service.get_tour_report(tourno,empgid,from_date,to_date,month,request,vys_page)
        exldata=json.dumps(data, default=lambda o: o.__dict__)
        response_data = pd.read_json(json.dumps(json.loads(exldata)['data']))
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_Report.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['tourid','empgid','employee_name','employee_code','empdesignation','empbranchgid','branch_name','branch_code','reason','requestdate','startdate',
                                  'enddate','claim_status','approvedamount','advanceamount','claimedamount']]
        final_df.columns = ['Tour No','Employee id','Employe Name','Employee Code','Employee Designation','BranchID','Branch Name','Branch Code','Tour Reason','Request Date','Start date','End date',
                            'Claim status','Approved amount','Advance amount','Totat Claimed Amount']

        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)

    def get_tourid_download(self,tourid, empid,request,vys_page,all_report):
        service=Report_ser(self._scope())
        if all_report is not None:
            data = service.get_alltourid_report(empid, request)
        else:
            data = service.get_tourid_report(tourid, empid, request, vys_page)
        if data.data ==[]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_TOURID)
            return HttpResponse(error_obj.get(), content_type='application/json')
        exldata=json.dumps(data, default=lambda o: o.__dict__)
        response_data = pd.read_json(json.dumps(json.loads(exldata)['data']))
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_ID_Report.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['empgid','employee_name','empdesignation','empbranchgid','branch_name','branch_code','tourid','approvedby','reason','requestdate','startdate',
                                  'enddate','tour_status','claim_status','advanceamount','claimedamount']]
        final_df.columns = ['Emp id','Employee Name','Designation','BranchID','Branch Name','Branch Code','Tour No','Approved By','Reason','Request Date','From date','To date',
                            'Tour status','Advance status','Claim status','Advance amount','Approved amount']

        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)

    def get_tour_detail(self, tour,request):
        empdtl = ApiService(self._scope())
        tour = TourRequest.objects.using(self._current_app_schema()).get(id=tour,entity_id=self._entity_id())
        list = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tour.id,entity_id=self._entity_id())
        reason = TourReason.objects.using(self._current_app_schema()).get(id=tour.reason,entity_id=self._entity_id())
        approver =TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.TOUR, applevel = App_level.FIRST_LEVEL, tour_id=tour.id, entity_id=self._entity_id()).last()
        permitted = empdtl.employee_details_get(tour.permittedby,request)
        approved = empdtl.employee_details_get(approver.approvedby, request)
        arr = []
        all_report=None
        vys_page=None
        from_date=None
        to_date=None
        tour_id=None
        for tour_detail in list:
            report_res = Report_res()
            report_res.set_empgid(tour.empgid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(tour.empgid,request)
            report_res.set_employee_name(employee.full_name)
            # code = empdtl.employee_code_get(tour.empgid)
            report_res.set_employee_code(employee.code)
            report_res.set_empdesignation(tour.empdesignation)
            report_res.set_empbranchgid(tour.empbranchgid)
            report_res.set_tourno(tour.id)
            maker=TourMaker(self._scope())
            requirement=maker.get_all_adminrequirements([tour_detail.id],request,all_report,vys_page,from_date,to_date,tour_id)
            report_res.set_requirement(requirement)
            report_res.set_official(tour_detail.official)
            report_res.set_reason(reason.name)
            report_res.set_requestdate(tour.request_date)
            report_res.set_permittedby(tour.permittedby)
            report_res.set_permittedby_name(permitted.full_name)
            report_res.set_permittedby_code(permitted.code)
            report_res.set_approvedby(approver.approvedby)
            report_res.set_approvedby_name(approved.full_name)
            report_res.set_approvedby_code(approved.code)
            report_res.set_tour_startdate(tour.start_date)
            report_res.set_tour_enddate(tour.end_date)

            branch = empdtl.get_branch_data(tour.empbranchgid,request)
            report_res.set_branch_name(branch.name)
            # brcode = empdtl.get_branch_code(tour.empbranchgid)
            report_res.set_branch_code(branch.code)

            report_res.set_startdate(tour_detail.startdate)
            report_res.set_enddate(tour_detail.enddate)
            report_res.set_starting_point(tour_detail.startingpoint)
            report_res.set_place_of_visit(tour_detail.placeofvisit)
            report_res.set_purpose_of_visit(tour_detail.purposeofvisit)
            arr.append(report_res)

        return arr

    def get_tour_detail_download(self,tour,request):
        service=Report_ser(self._scope())
        data=service.get_tour_detail(tour,request)
        exldata=json.dumps(data, default=lambda o: o.__dict__)
        response_data = pd.read_json(exldata)
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_detail.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['empgid','employee_name','employee_code','empdesignation','empbranchgid','branch_name','branch_code','tourno','reason','requestdate','tour_startdate','tour_enddate','startdate',
                                  'enddate','starting_point','place_of_visit','purpose_of_visit','permittedby_name','permittedby_code','approvedby_name','approvedby_code']]
        final_df.columns = ['Employee id','Employee Name','Employee Code','Designation','BranchID','Branch Name','Branch Code','Tour No','Tour Reason','Request Date','Tour StartDate','Tour Enddate','Details Start date','Details End date','Starting Point','Place of visit','Purpose of visit','PermittedBy Name','PermittedBy Code','Approver Name','Approver Code']

        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)

    def get_tour_advance(self, tour):
        adv_tour = TourRequest.objects.using(self._current_app_schema()).get(id=tour,entity_id=self._entity_id())
        list = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=adv_tour.id,entity_id=self._entity_id())
        arr = []
        for tour_detail in list:

            report_res = Report_res()
            report_res.set_tourno(tour)
            report_res.set_reqamount(tour_detail.reqamount)
            report_res.set_appamount(tour_detail.appamount)
            report_res.set_invoiceheadergid(tour_detail.invoiceheadergid)
            report_res.set_status(tour_detail.status)

            report_res.set_startdate(adv_tour.start_date)
            report_res.set_enddate(adv_tour.end_date)
            report_res.set_reason(adv_tour.reason)
            report_res.set_requestdate(adv_tour.request_date)
            # report_res.set_advance_status(adv_tour.advance_status)
            report_res.set_claim_status(adv_tour.claim_status)
            report_res.set_tour_status(adv_tour.tour_status)
            arr.append(report_res)
        return arr

    def get_download_tour_advance(self,tour):
        service=Report_ser(self._scope())
        data=service.get_tour_advance(tour)
        exldata=json.dumps(data, default=lambda o: o.__dict__)
        response_data = pd.read_json(exldata)
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_advance.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['tourno','reason',
                                  'reqamount','appamount','status']]
        final_df.columns = ['Tour No','Reason','Request amount','Approve amount','Advance status','Status']

        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)


    def get_download_tour_expense(self,tour,request):
        service=TourExpense(self._scope())
        data=service.get_claimreq_tour(tour,request)
        exldata=json.dumps(data.data, default=lambda o: o.__dict__)
        response_data = pd.read_json(exldata)
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_expense.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['employee_name','employee_code','designation','branch_name','tourid','reason','requestdate','tour_startdate','tour_enddate','expensename','expensecode','eligibleamount','claimedamount','approvedamount','approvercomment','requestercomment','forwarder_name','forwarder_code','approver_name','approver_code']]
        final_df.columns = ['Employee Name','Employee Code','Employee Designation','Branch','Tour NO','Tour Reason','Request Date','Tour Start Date','Tour End Date','Expense Name','Expense Code','Eligible amount','Claimed amount','Approved amount','Approver comment', 'Requestor comment','Forwarder Name','Forwarder Code','Approver Name','Approver Code']
        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)

    def consolidate_report(self,tour,request):
        arr=[]
        list=TourRequest.objects.using(self._current_app_schema()).get(id=tour,entity_id=self._entity_id())
        report_res = Report_res()
        report_res.set_tourno(tour)
        report_res.set_empgid(list.empgid)
        empdtl = ApiService(self._scope())
        employee = empdtl.employee_details_get(list.empgid,request)
        report_res.set_employee_name(employee.full_name)
        # code = empdtl.employee_code_get(list.empgid)
        report_res.set_employee_code(employee.code)
        report_res.set_empdesignation(list.empdesignation)
        report_res.set_empbranchgid(list.empbranchgid)

        branch = empdtl.get_branch_data(list.empbranchgid,request)
        report_res.set_branch_name(branch.name)
        # brcode = empdtl.get_branch_code(list.empbranchgid)
        report_res.set_branch_code(branch.code)
        report_res.set_startdate(list.start_date)
        report_res.set_requestdate(list.request_date)
        report_res.set_enddate(list.end_date)
        report_res.set_durationdays(list.durationdays)

        reason = Report_ser.get_reason_name(self, list.reason)
        report_res.set_reason(reason)

        total_amount=Report_ser.get_total_amount(self, tour)
        report_res.set_total_amount(total_amount)

        travel_exp=Report_ser.travel(self,tour)
        report_res.set_travel_amount(travel_exp)
        daily_exp=Report_ser.dailydeim(self,tour)
        report_res.set_dailydeim_amount(daily_exp)
        incidental_exp=Report_ser.incidental(self,tour)
        report_res.set_incidental_amount(incidental_exp)
        local_exp=Report_ser.local(self,tour)
        report_res.set_local_amount(local_exp)
        lodging_exp=Report_ser.lodging(self,tour)
        report_res.set_lodging_amount(lodging_exp)
        misc_exp=Report_ser.misc(self,tour)
        report_res.set_misc_amount(misc_exp)
        packing_exp=Report_ser.packing(self,tour)
        report_res.set_packing_amount(packing_exp)

        arr.append(report_res)
        return arr


    def travel(self,tour):
        travel_amount=0
        list=Travel.objects.using(self._current_app_schema()).filter(tourid_id=tour,entity_id=self._entity_id())
        for exp in list:
            travel_amount+=exp.claimedamount
        return travel_amount
    def dailydeim(self,tour):
        daily_amount=0
        list=Dailydeim.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            daily_amount+=exp.claimedamount
        return daily_amount
    def incidental(self,tour):
        incidental_amount=0
        list=Incidental.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            incidental_amount+=exp.claimedamount
        return incidental_amount
    def local(self,tour):
        local_amount=0
        list=Localconveyence.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            local_amount+=exp.claimedamount
        return local_amount
    def lodging(self,tour):
        lodging_amount=0
        list=Lodging.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            lodging_amount+=exp.claimedamount
        return lodging_amount
    def misc(self,tour):
        misc_amount=0
        list=Misc.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            misc_amount+=exp.claimedamount
        return misc_amount
    def packing(self,tour):
        packing_amount=0
        list=PackingMoving.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for exp in list:
            packing_amount+=exp.claimedamount
        return packing_amount


    def get_total_amount(self,tour):
        total=0
        list=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour,entity_id=self._entity_id())
        for amount in list:
            total+= amount.claimedamount
        return total

    def branchwise_pending(self,empgid,request,vys_page):
        arr=[]
        uniquetour=[]
        uniquebranch = []
        if int(empgid)==0:
            list=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=(App_type.CLAIM or App_type.claim), status=Status.PENDING,
                                                                                applevel=2, tour__start_date__icontains='', entity_id=self._entity_id()).order_by("-id")
        else:
            list=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=(App_type.CLAIM or App_type.claim), status=Status.PENDING,
                                                                                applevel=2, approvedby=empgid, tour__start_date__icontains='', entity_id=self._entity_id()).order_by("-id")
        for data in list:
            if data.tour_id not in uniquetour:
                # if data.tour.start_date is not None:
                diff_days = (today.date()-(data.tour.start_date).date()).days
                one_two = 0
                three_ten = 0
                eleven_thirty = 0
                thirtyone_sixty = 0
                above_sixty = 0
                if diff_days <=2:
                    one_two=1
                elif 3<=diff_days <=10:
                    three_ten=1
                elif 11<=diff_days <=30:
                    eleven_thirty=1
                elif 31<=diff_days <=60:
                    thirtyone_sixty=1
                elif 61<=diff_days :
                    above_sixty=1

                report_res = Report_res()
                report_res.set_empbranchgid(data.tour.empbranchgid)
                details=ApiService(self._scope())
                branch = details.get_branch_data(data.tour.empbranchgid,request)
                report_res.set_branch_name(branch.name)
                # brcode = details.get_branch_code(data.tour.empbranchgid)
                report_res.set_branch_code(branch.code)
                report_res.set_one_two(one_two)
                report_res.set_three_ten(three_ten)
                report_res.set_eleven_thirty(eleven_thirty)
                report_res.set_thirtyone_sixty(thirtyone_sixty)
                report_res.set_above_sixty(above_sixty)
                if data.tour.empbranchgid in uniquebranch:

                    for n in range (0,len(arr)):
                        if arr[n].empbranchgid==data.tour.empbranchgid:
                            arr[n].one_two+=one_two
                            arr[n].three_ten+=three_ten
                            arr[n].eleven_thirty+=eleven_thirty
                            arr[n].thirtyone_sixty+=thirtyone_sixty
                            arr[n].above_sixty+=above_sixty
                else:
                    uniquebranch.append(data.tour.empbranchgid)
                    arr.append(report_res)
                uniquetour.append(data.tour_id)
        # return arr
        resp_list = NWisefinList()
        arr_pagination=arr[vys_page.get_offset():vys_page.get_query_limit()]
        for each_list in arr_pagination:
            report_res = Report_res()
            report_res.set_empbranchgid(each_list.empbranchgid)
            report_res.set_branch_name(each_list.branch_name)
            report_res.set_branch_code(each_list.branch_code)
            report_res.set_one_two(each_list.one_two)
            report_res.set_three_ten(each_list.three_ten)
            report_res.set_eleven_thirty(each_list.eleven_thirty)
            report_res.set_thirtyone_sixty(each_list.thirtyone_sixty)
            report_res.set_above_sixty(each_list.above_sixty)
            resp_list.append(report_res)
        vpage = NWisefinPaginator(arr_pagination, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list
    def report_tour_requirements(self,request,tour_id,vys_page,all_report,booking_type,from_date,to_date,emp_id):
        booking_type=int(booking_type)



        if all_report==None:
            condition=Q(entity_id=self._entity_id(),status=1,tour__tour_status=Status.APPROVED)
            if tour_id!=None:
                condition&=Q(tour_id=tour_id)
        #     if emp_id!=None:
        #         condition&=Q(tour__empgid=emp_id)
            if booking_type!=None:
                if booking_type == Travel_requirements.accomodation:
                    condition &= Q(tour__accomodation_status__in=[-2,3,4])
                elif booking_type == Travel_requirements.cab:
                    condition &= Q(tour__cab_status__in=[-2,3,4])
                elif booking_type == Travel_requirements.air:
                    condition &= Q(tour__air_status__in=[-2,3,4])
        else:
            condition = Q(entity_id=self._entity_id(), status=1, tour__tour_status=Status.APPROVED)
            if tour_id != None:
                condition &= Q(tour_id=tour_id)
        #     if emp_id != None:
        #         condition &= Q(tour__empgid=emp_id)
        #     if emp_id != None:
        #         condition &= Q(tour__empgid=emp_id)
            if booking_type != None:
                if booking_type == Travel_requirements.accomodation:
                    condition &= Q(tour__accomodation_status__in=[-2,3,4])
                elif booking_type == Travel_requirements.cab:
                    condition &= Q(tour__cab_status__in=[-2,3,4])
                elif booking_type == Travel_requirements.air:
                    condition &= Q(tour__air_status__in=[-2,3,4])
        detail_table = TourDetail.objects.using(self._current_app_schema()).filter(condition).order_by("-tour_id")
        # resp_list = NWisefinList()
        # api_service = ApiService(self._scope())
        detail_array=[]
        # report_res = Report_res()
        for data in detail_table:
            detail_array.append(data.id)
        maker = TourMaker(self._scope())
        # detail_array=None
        requirement = maker.get_all_adminrequirements(detail_array,request,booking_type,all_report,vys_page,from_date,to_date,tour_id)


        # if all_report == None:
        #     report_res.set_requirement(requirement)
        #     resp_list.append(report_res)
        #     vpage = NWisefinPaginator(requirement, vys_page.get_index(), 10)
        #     resp_list.set_pagination(vpage)
        # else:
        #     return requirement
        return requirement
    def report_requirement_download(self,request,tour_id,vys_page,all_report,booking_type,from_date,to_date,emp_id):
        service = Report_ser(self._scope())
        all_report="all"
        vys_page=None
        data=self.report_tour_requirements(request,tour_id,vys_page,all_report,booking_type,from_date,to_date,emp_id)
        data.replace({np.nan: None,pd.NaT:None}, inplace=True)

        # if int(booking_type) != 5:
        #     if data.data == []:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.INVALID_TOURID)
        #         return HttpResponse(error_obj.get(), content_type='application/json')
        #
        #     exldata = json.dumps(data, default=lambda o: o.__dict__)
        #     response_data = pd.read_json(json.dumps(json.loads(exldata)['data'][0]["requirement"]))
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_ID_Report.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        # print(['data'][0]["requirement"])
        # for i in range(len((json.loads(exldata)['data'][0]["requirement"]))):
        #     if json.loads(exldata)['data'][0]["requirement"][i]["booking_needed"]=="ACCOMENDATION BOOKING":
        if int(booking_type) == Travel_requirements.accomodation:
            final_df = data[
                ["travel_detail__tour__id","request_date", "booking date","booking time", "code", "full_name","department__name", "travel_detail__purposeofvisit", "client_name", "travel_detail__tour__tour_status",
                 "difference_in_days", "travel_detail__tour__international_travel", "place_of_stay", "checkin time", "checkout_time",
                 "travel_detail__official", "comments"]]
            final_df.columns = ["Travel NO","Request Date", "Booking Date","Booking Time", "Employee ID", "Employee name","Team", "Purpose",
                                "Client", "APPROVAL STATUS ", "Difference in days ("
                                                                                    "Booking date Vs DOT)",
                                "Domestic/International", "Place of Stay", "Checkin Time",
                                "Checkout Time",
                                "Official", "Remarks"]
        elif int(booking_type)==Travel_requirements.air:
            final_df = data[
                ["tour_id", "booking date","booking time", "Maker code", "Maker Full name","department__name", "travel_detail__purposeofvisit", "client_name", "travel_detail__tour__tour_status",
                 'from_time', "difference_in_days", "travel_detail__tour__international_travel", "from_place", "to_place", "from time", "to time",
                 "vendor_name", "PNR", "Approval Full name", "ticket_amount", "ticket_amount","ticket_amount_personal",
                  "travel_detail__tour__week_end_travel", "website", "issuance_type", "ticket_no", "booking_status",
                 "cancelled_date", "loss_of_cancelation", "refund_amount", "refund_date", "cancel_reason",
                 "travel_detail__official", "comments","ref_no"]]

            final_df.columns = ["Travel NO", "Booking Date","Booking Time", "Employee ID", "Employee name","Team", "Purpose",
                                "Client", "APPROVAL STATUS ", 'Date of Travel', "Difference in days ("
                                                                                    "Booking date Vs DOT)",
                                "Domestic/International", "From Place", "To Place", "From Time",
                                "To Time", "Airline", "PNR", "Approved By", "Cost Per Pax", "Ticket Cost","Ticket amount for personal",
                                 "Reason for weekend Travel", "Website",
                                "Issuance Type", "Ticket No", "Booking Status", "Cancelled Date",
                                "Loss of cancelation", "Refund amount", "Refund date", "Reason for Cancel/No-show",
                                "Official", "Remarks","Reference Number"]

            # elif json.loads(exldata)['data'][0]["requirement"][i]["booking_needed"]=="CAB BOOKING":
        elif int(booking_type) == Travel_requirements.cab:
            final_df = data[
                ["travel_detail__tour__id","travel_detail__tour__request_date" ,"booking date", "booking time","code", "full_name", "department__name","travel_detail__purposeofvisit", "client_name", "travel_detail__tour__tour_status","from_place","from_time","to_place","to_time",
                 "vendor_name",
                 "travel_detail__official", "comments","travel_type_cab"]]

            final_df.columns = ["Travel NO","Request Date","Booking Date","Booking Time", "Employee ID", "Employee name","Team", "Purpose",
                                "Client", "APPROVAL STATUS ", "Location","Pick Up date(DD/MM/YYYY)","Reporting Place","Reporting Time" ,
                                "Vendor name",
                                "Official", "Remarks","Cab Type"]


        final_df.to_excel(writer,sheet_name='Travel Report', startrow=1, header=False, index=False)
        workbook = writer.book
        worksheet = writer.sheets['Travel Report']

        header_format = workbook.add_format({
            'bold': True,
            'fg_color': '21CBE5',
            'border': 1})
        for col_num, value in enumerate(final_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

            column_len = final_df[value].astype(str).str.len().max()
            column_len = max(column_len, len(value)) + 3
            worksheet.set_column(col_num, col_num, column_len)
        writer.save()
        return HttpResponse(response)



