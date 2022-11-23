import json
import math
from django.db.models import Q
from asgiref.local import Local
from nwisefin.settings import logger
from taservice.service.ta_email import ta_email
from utilityservice.data.response.nwisefinpaginator  import NWisefinPaginator

from utilityservice.data.response.nwisefinlist import NWisefinList

from taservice.data.request.tourapproved import TourApprovedbyRequest
from django.utils import timezone

from taservice.data.request.tourallowance import Allowancerequest,GradeEligibiltyrequest
from taservice.data.response.tourallowance import Allowanceresponse,GradeEligibiltyresponse
from django.db import IntegrityError
from django.db import transaction

from taservice.data.response.tourexpense import Dailydeim_Response
from taservice.models import Allowance, Gradeeligibility, TravelHistory, Lodging, Incidental, Dailydeim, Misc, \
    PackingMoving, Travel, Localconveyence, TourExpense, TourRequest, TourReason, ClaimRequest, Ccbs, Localdeputation
from taservice.data.response.tourexpense import Incidental_Response
from taservice.service.driver_data_ser import Driver_bata
from taservice.service.elligible_amount_ser import El_lod_ser
from taservice.service.emp_name_get import Expense_type_get, Tourno_details
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess, SuccessStatus, SuccessMessage
from taservice.data.response.tourallowance import Allowanceresponse
from taservice.service.holiday_deim import HolidayDeim
from datetime import datetime, timedelta, date
from taservice.util.ta_util import Status, App_type, App_level, Validation ,Timecalculation
from taservice.models.tamodels import Holidaydeim as holiday_deim_table, TourAdvance
# from utilityservice.service.dbutil import DataBase

# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d')
from utilityservice.permissions.util.dbutil import ModuleList, RoleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread
today=datetime.today()
time_function=Timecalculation()
class Tour_allowance(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_allowance(self,request_obj,user_id):

        for dtl in request_obj:
            request = Allowancerequest(dtl)
            if request.get_id() is not None:
                try:
                    allowance = Allowance.objects.using(self._current_app_schema()).filter(id=request.get_id(),entity_id=self._entity_id()).update(salarygrade = request.get_salarygrade(),
                                                                                         city = request.get_city(),
                                                                                         amount = request.get_amount(),
                                                                                         applicableto = request.get_applicableto(),
                                                                                         status = request.get_status(),
                                                                                         entity = request.get_entity(),
                                                                                         expense_id = request.get_expense_id(),
                                                                                         updated_by = user_id,
                                                                                         effectivefrom = request.effectivefrom,
                                                                                         effectiveto = request.effectiveto,entity_id=self._entity_id())


                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Allowance.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj


                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                # return success_obj
            else:
                try:

                    effective_from = datetime.strptime(request.effectivefrom[:10], '%Y-%m-%d')
                    allowance_table_update = Allowance.objects.using(self._current_app_schema()).filter(expense_id=request.get_expense_id(),salarygrade=request.get_salarygrade(), city=request.get_city(),applicableto=request.get_applicableto(),entity_id=self._entity_id()).last()

                    if allowance_table_update == None:
                        allowance_table_create = Allowance.objects.using(self._current_app_schema()).create(
                            salarygrade=request.get_salarygrade(), city=request.get_city(), amount=request.get_amount(),
                            applicableto=request.get_applicableto(), effectivefrom=request.effectivefrom,
                            expense_id=request.get_expense_id(), created_by=user_id, created_date=today,entity_id=self._entity_id())
                    else:
                        table_allowance_eff = datetime.strptime(str(allowance_table_update.effectivefrom)[:10],
                                                                '%Y-%m-%d')
                        if  table_allowance_eff >= effective_from:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.ALLOWANCE)
                            return error_obj
                        if allowance_table_update.effectiveto == None or allowance_table_update.effectiveto == "0000-00-00 00:00:00.000000" or allowance_table_update.effectiveto == 0:
                            allowance_table_updat = Allowance.objects.using(self._current_app_schema()).filter(id=allowance_table_update.id,entity_id=self._entity_id()).update(effectiveto=(effective_from - timedelta(days=1)),entity_id=self._entity_id())
                            allowance_table_create = Allowance.objects.using(self._current_app_schema()).create(salarygrade=request.get_salarygrade(),city=request.get_city(),amount=request.get_amount(),applicableto=request.get_applicableto(),effectivefrom=effective_from,expense_id=request.get_expense_id(),created_by=user_id,created_date=today,entity_id=self._entity_id())
                        else:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.ALLOWANCE)
                            return error_obj



            # resp_list = Allowanceresponse()
            # resp_list.set_salarygrade(allowance.salarygrade)
            # resp_list.set_applicableto(allowance.applicableto)
            # return resp_list

                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def get_allowance(self,vys_page,expense_name,employee_grade,city):
        condition=Q(status=1,entity_id=self._entity_id())
        if expense_name is not None:
            condition &= Q(expense_id__name__icontains=expense_name)
        if employee_grade is not None:
            condition &= Q(salarygrade__icontains=employee_grade)
        if city is not None:
            condition &= Q(city__icontains=city)
        allowance = Allowance.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        req_data = Allowanceresponse()
        res_list=NWisefinList()
        for i in allowance:
            resp_list = Allowanceresponse()
            resp_list.set_id(i.id)
            resp_list.set_salarygrade(i.salarygrade)
            resp_list.set_city(i.city)
            resp_list.set_amount(i.amount)
            resp_list.set_applicableto(i.applicableto)
            resp_list.set_status(i.status)
            resp_list.set_entity(i.entity)
            resp_list.set_effectivefrom(i.effectivefrom)
            resp_list.set_effectiveto(i.effectiveto)
            resp_list.set_expense_id(i.expense_id)
            exp_name=TourExpense.objects.using(self._current_app_schema()).filter(id=i.expense_id,entity_id=self._entity_id()).last()
            if exp_name is not None:
                resp_list.set_expense_name(exp_name.name)
            else:
                resp_list.set_expense_name(None)
            res_list.append(json.loads(resp_list.get()))
        req_data.set_data(res_list)
        vpage = NWisefinPaginator(allowance, vys_page.get_index(), 10)
        res_list.set_pagination(vpage)
        return res_list

    def delete_allowance(self, delete_id):
        try:
            allowance = Allowance.objects.using(self._current_app_schema()).get(id=delete_id,entity_id=self._entity_id()).delete()
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_allowance_id(self,employee_id):
        allowance = Allowance.objects.using(self._current_app_schema(),entity_id=self._entity_id()).get(id = employee_id)
        resp_list = Allowanceresponse()
        resp_list.set_id(allowance.id)
        resp_list.set_salarygrade(allowance.salarygrade)
        resp_list.set_city(allowance.city)
        resp_list.set_amount(allowance.amount)
        resp_list.set_applicableto(allowance.applicableto)
        resp_list.set_status(allowance.status)
        resp_list.set_entity(allowance.entity)
        resp_list.set_effectivefrom(allowance.effectivefrom)
        resp_list.set_effectiveto(allowance.effectiveto)
        resp_list.set_expense_id(allowance.expense_id)
        return resp_list

    def allowance_get_grade(self,expense,salarygrade,vys_page):
        resp_list = NWisefinList()
        if salarygrade is None:
            list = Allowance.objects.using(self._current_app_schema()).filter(expense_id=expense,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            list = Allowance.objects.using(self._current_app_schema()).filter(expense_id = expense,salarygrade=salarygrade,entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        for allowance in list:
            req_data = Allowanceresponse()
            req_data.set_id(allowance.id)
            req_data.set_salarygrade(allowance.salarygrade)
            req_data.set_city(allowance.city)
            req_data.set_amount(allowance.amount)
            req_data.set_applicableto(allowance.applicableto)
            req_data.set_status(allowance.status)
            req_data.set_entity(allowance.entity)
            req_data.set_expense_id(allowance.expense_id)
            resp_list.append(req_data)
        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def get_eligibleamount_misc(self,data):
        grade_service = Tourno_details(self._scope())
        grade = grade_service.grade_get_tourid(data.tourgid)
        service=Driver_bata(self._scope())
        designation = service.get_designation(grade)
        if data.center is not None:
            city = data.center
            expensegid = data.expense_id
            service=Tour_allowance(self._scope())
            if data.tourgid is not None:
                tourgid = data.tourgid
                out_data = service.elig_citytoamount(designation, city, expensegid, tourgid)
                amount = out_data[0].amount
                return json.dumps({"Eligible_amount":amount})
            # else:
            #     out_data = service.elig_citytoamount_tmp(designation, city, expensegid)
            #     amount = out_data[0].amount
            #     return json.dumps({"elligibleamount":amount})


        else:
            return json.dumps({"Eligible_amount":data.claimedamount})


    # def get_eligibleamount_misc(self,jsondata):
    #     service=Driver_bata()
    #     designation = service.get_designation(jsondata.salarygrade)
    #     city = jsondata.center
    #     expensegid = jsondata.expense_id
    #     amount_service=Tour_allowance()
    #     if jsondata.tourgid is not None:
    #         tourgid = jsondata.tourgid
    #         amount = amount_service.elig_citytoamount( designation, city, expensegid,tourgid)
    #     else:
    #         amount = amount_service.elig_citytoamount_tmp(designation, city, expensegid)
    #     eligible_value = {
    #         "Eligible_amount": amount,
    #     }
    #     return json.dumps(eligible_value)

    def get_eligibleamount(self, dtl, request):
        # grade_service = Tourno_details(self._scope())
        # grade = grade_service.grade_get_tourid(jsondata.tourgid)
        # service=Driver_bata(self._scope())
        # designation = service.get_designation(grade)
        # city = jsondata.center
        # expensegid = jsondata.expense_id
        # amount_service=Tour_allowance(self._scope())
        #
        # if jsondata.tourgid is not None:
        #     tourgid = jsondata.tourgid
        #     amount = amount_service.elig_citytoamount( designation, city, expensegid,tourgid)
        # else:
        #     amount = amount_service.elig_citytoamount_tmp(designation, city, expensegid)
        # eligible_value = {
        #     "Eligible_amount": amount[0].amount,
        # }
        try:
            modeoftravel = dtl['modeoftravel']
            distance = int(dtl['distance'])
            expense_id = dtl['expensegid']
            i = Allowance.objects.using(self._current_app_schema()).filter(
                citytype=modeoftravel,
                expense_id=expense_id,entity_id=self._entity_id())[0]

            eligible_amt = float(distance) * int(i.amount)
            # if modeoftravel == 'personal vehicle car':
            #     eligible_amt = int(distance) * int(list_data[0]['elgibleamount'])
            # elif modeoftravel == 'personal vehicle scooter':
            #     eligible_amt = int(distance) * int(list_data[0]['elgibleamount'])
        except:
            eligible_amt = dtl['claimedamount']
        # return round(eligible_amt)
        eligible_value = {
            "Eligible_amount": eligible_amt
        }
        return json.dumps(eligible_value)

    def elig_citytoamount(self, grade, city, expensegid, tourgid):
        service=Tour_allowance(self._scope())
        out_data = service.allowance_get_date(grade,city,expensegid)
        ld_out_message = TourRequest.objects.using(self._current_app_schema()).get(id=tourgid,entity_id=self._entity_id())
        startdate = ld_out_message.start_date
        sdate = str(startdate).split()
        sdate = sdate[0].split('-')
        day = date(int(sdate[0]), int(sdate[1]), int(sdate[2]))
        final_amount = []
        data = {}
        for j in out_data:
            # if j is not None:
            if j.effectiveto != '0' and j.effectiveto != '00-00-0000' and j.effectiveto is not None:
                efdate = str(j.effectivefrom).split()
                etdate = str(j.effectiveto).split()

                efdate = efdate[0].split('-')
                etdate = etdate[0].split('-')

                from_d = date(int(efdate[0]), int(efdate[1]), int(efdate[2]))  # start date
                to_d = date(int(etdate[0]), int(etdate[1]), int(etdate[2]))
                if from_d <= day <= to_d:
                    final_amount.append(j)

            else:
                efdate = str(j.effectivefrom).split()
                efdate = efdate[0].split('-')
                from_d = date(int(efdate[0]), int(efdate[1]), int(efdate[2]))  # start date
                if from_d <= day:
                    data = j
                    final_amount.append(j)

        return final_amount

    def elig_citytoamount_tmp(self, grade, city, expensegid):
        service=Tour_allowance(self._scope())
        ld_out_message = service.allowance_get_date(grade.upper(),city,expensegid)
        return ld_out_message


    def allowance_get_date(self,grade,city,expensegid):
        allowance = Allowance.objects.using(self._current_app_schema()).filter(city=city,
                                                 salarygrade = grade,
                                                 expense_id =expensegid,entity_id=self._entity_id())
        return allowance

    # def get_eligibleamount(self,request_obj):
    #     allowance = Allowance.objects.using(self._current_app_schema()).filter(city = request_obj.center,
    #                                          salarygrade = request_obj.get_salarygrade(),
    #                                          expense_id = request_obj.get_expense_id())
    #     req_data = Allowanceresponse()
    #     arr = []
    #     for i in allowance:
    #         resp_list = Allowanceresponse()
    #         resp_list.set_amount(i.amount)
    #         arr.append(json.loads(resp_list.get()))
    #     req_data.set_data(arr)
    #     return req_data


    def get_allowanceamount(self, request_obj):
        # allowance = Allowance.objects.using(self._current_app_schema()).get(city=request_obj.get_city(),
        #                                   salarygrade=request_obj.get_salarygrade(),
        #                                   expense_id=request_obj.get_expense_id(),
        #                                   applicableto=request_obj.get_applicableto())
        samedayreturn = int(request_obj.same_day_return)
        travel_mode = request_obj.travel_mode.upper()
        single_fare = request_obj.single_fare
        travelhours = request_obj.travel_hours

        response = Allowanceresponse()
        if travel_mode == "ROAD":
            amount = math.ceil(float(single_fare) * 1 / 3)
            if amount <= 10:
                amount = 10
            response.set_amount(amount)
            return response

        elif travel_mode == "TRAIN":
            if samedayreturn == 1:
                amount = 10
                response.set_amount(amount)
                return response

            elif samedayreturn == 0:
                tothour = int(travelhours)
                day = math.ceil(tothour / 24)
                if day == 1:
                    totamount = 15
                else:
                    amount = 20
                    totamount = amount * day
                response.set_amount(totamount)
                return response
        elif travel_mode == "OWN":
                amount = 0
                response.set_amount(amount)
                return response

    def excel_file(self,file,userid):
        arr=[]

        for data in file:
            expense_id=TourExpense.objects.using(self._current_app_schema()).filter(name=data['Expense Name'],entity_id=self._entity_id()).last()
            try:
                allowance_table_update =Allowance.objects.using(self._current_app_schema()).filter(expense_id=expense_id.id,salarygrade=data['Salarygrade'],city=data['City'],applicableto=data['Applicableto']).update(effectiveto=(data['Effective From']-timedelta(days=1)),entity_id=self._entity_id())
                allowance_table_create = Allowance(salarygrade=data['Salarygrade'],
                                                   city=data['City'],
                                                   amount=data['Amount'],
                                                   applicableto=data['Applicableto'],
                                                   effectivefrom=data['Effective From'],
                                                   effectiveto=data['Effective To'],
                                                   expense_id=expense_id.id,
                                                   created_by=userid,
                                                   created_date=today,entity_id=self._entity_id())
                arr.append(allowance_table_create)
            except:
                allowance_table_create=Allowance(salarygrade=data['Salarygrade'],city=data['City'],amount=data['Amount'],applicableto=data['Applicableto'],effectivefrom=data['Effective From'],effectiveto=data['Effective To'],expense_id=expense_id.id,created_by=userid,created_date= today,entity_id=self._entity_id())
                arr.append(allowance_table_create)
        allowance_create=Allowance.objects.using(self._current_app_schema()).bulk_create(arr)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    # def update_effectiveto(self,user_data,user_id):
    #
    #     if user_data['expence_id']not in user_data or user_data['expense_id']==0:
    #         allowance_update=Allowance.objects.using(self._current_app_schema()).filter(effectiveto=None).update(effectiveto=user_data['effective_to'],updated_by=user_id,updated_date=today)
    #     if user_data['expense_id'] in user_data:
    #         allowance_update=Allowance.objects.using(self._current_app_schema()).filter(expense_id=user_data['expense_id'],effectiveto=None).update(effectiveto=user_data['effectiveto'],updated_by=user_id,updated_date=today)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj

    # def holiday_file(self, file, userid):
    #     arr = []
    #
    #     for data in file:
    #         expense_id = TourExpense.objects.using(self._current_app_schema()).filter(name=data['Expense Name'],
    #                                                                                   entity_id=self._entity_id()).last()
    #         try:
    #             allowance_table_update = Allowance.objects.using(self._current_app_schema()).filter(
    #                 expense_id=expense_id.id, salarygrade=data['Salarygrade'], city=data['City'],
    #                 applicableto=data['Applicableto']).update(effectiveto=(data['Effective From'] - timedelta(days=1)),
    #                                                           entity_id=self._entity_id())
    #             allowance_table_create = Allowance(date=data['date'],
    #                                                holidayname=data['holidayname'],
    #                                                state=data['state'],
    #                                                status=data['status'],
    #                                                entity=data['entity'],
    #                                                effectiveto=data['Effective To'],
    #                                                created_by=userid,
    #                                                created_date=today, entity_id=self._entity_id())
    #             arr.append(table_create)
    #         except:
    #             table_create = Allowance(date=data['date'], holidayname=data['holidayname'],
    #                                                state=data['state'], status=data['status'],
    #                                                entity=data['entity'],
    #                                                created_by=userid, created_date=today, entity_id=self._entity_id())
    #             arr.append(table_create)
    #     allowance_create = Allowance.objects.using(self._current_app_schema()).bulk_create(arr)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj

class Tour_grade(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_grade(self,request_obj):
        for dtl in request_obj:
            request = GradeEligibiltyrequest(dtl)
            if request.get_id() is not None:
                try:
                    grade = Gradeeligibility.objects.using(self._current_app_schema()).filter(id=request.get_id(),entity_id=self._entity_id()).update(grade = request.get_grade(),
                                                                                        gradelevel = request.get_gradelevel(),
                                                                                        travelclass = request.get_travelclass(),
                                                                                        travelmode = request.get_travelmode(),
                                                                                        freight1000 = request.get_freight1000(),
                                                                                        freight1001 = request.get_freight1001(),
                                                                                        twowheller = request.get_twowheller(),
                                                                                        hillyregion = request.get_hillyregion(),
                                                                                        tonnagefamily = request.get_tonnagefamily(),
                                                                                        maxtonnage = request.get_maxtonnage(),entity_id=self._entity_id() )



                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Allowance.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
            else:
                try:
                    grade = Gradeeligibility.objects.using(self._current_app_schema()).create(grade=request.get_grade(),
                                                            gradelevel=request.get_gradelevel(),
                                                            travelclass=request.get_travelclass(),
                                                            travelmode=request.get_travelmode(),
                                                            freight1000=request.get_freight1000(),
                                                            freight1001=request.get_freight1001(),
                                                            twowheller=request.get_twowheller(),
                                                            hillyregion=request.get_hillyregion(),
                                                            tonnagefamily=request.get_tonnagefamily(),
                                                            maxtonnage=request.get_maxtonnage(),entity_id=self._entity_id())

                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def get_grades(self):
        grade = Gradeeligibility.objects.using(self._current_app_schema()).all()
        req_data = GradeEligibiltyresponse()
        arr = []
        for i in grade:
            resp_list = GradeEligibiltyresponse()
            resp_list.set_id(i.id)
            resp_list.set_grade(i.grade)
            resp_list.set_gradelevel(i.gradelevel)
            resp_list.set_travelclass(i.travelclass)
            resp_list.set_travelmode(i.travelmode)
            resp_list.set_freight1000(i.freight1000)
            resp_list.set_freight1001(i.freight1001)
            resp_list.set_twowheller(i.twowheller)
            resp_list.set_hillyregion(i.hillyregion)
            resp_list.set_tonnagefamily(i.tonnagefamily)
            resp_list.set_maxtonnage(i.maxtonnage)
            arr.append(json.loads(resp_list.get()))
        req_data.set_data(arr)
        return req_data

    def delete_grades(self, delete_id):
        try:
            grade = Gradeeligibility.objects.using(self._current_app_schema()).get(id=delete_id,entity_id=self._entity_id()).delete()
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_grade_id(self,employee_id):
        grade = Gradeeligibility.objects.using(self._current_app_schema()).get(id = employee_id,entity_id=self._entity_id())
        resp_list = GradeEligibiltyresponse()
        resp_list.set_id(grade.id)
        resp_list.set_grade(grade.grade)
        resp_list.set_gradelevel(grade.gradelevel)
        resp_list.set_travelclass(grade.travelclass)
        resp_list.set_travelmode(grade.travelmode)
        resp_list.set_freight1000(grade.freight1000)
        resp_list.set_freight1001(grade.freight1001)
        resp_list.set_twowheller(grade.twowheller)
        resp_list.set_hillyregion(grade.hillyregion)
        resp_list.set_tonnagefamily(grade.tonnagefamily)
        resp_list.set_maxtonnage(grade.maxtonnage)
        return resp_list

    @transaction.atomic
    def insert_forward(self, data,employee_id,request):
        logger.info('ta_ Tour_forward- '+str(employee_id)+str(data))
        # try:
        error_obj = NWisefinError()
        if data.get_appcomment() is None or data.get_appcomment() == "":
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        approver_data = (TravelHistory.objects.using(self._current_app_schema()).get(id=data.id, entity_id=self._entity_id()))
        if employee_id != approver_data.approvedby:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        validation_service = Validation(self._scope())
        # approver_check = validation_service.approver_validation(App_type.tour, approver_data.approvedby, request)
        # if approver_check is False:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
        #     return error_obj
        if approver_data.request_type.upper() != (data.request_type).upper() or approver_data.tour_id != \
                int(data.tour_id):
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID)
            return error_obj
        elif employee_id==int(data.approvedby) or int(data.approvedby)==0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.FORWARDER)
            return error_obj


        if data.request_type.upper()==App_type.TOUR:
            tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=data.tour_id,entity_id=self._entity_id())
            if tourrequest.tour_status == Status.DEFAULT or tourrequest.tour_status == Status.APPROVED or \
                    tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                return error_obj
            if int(data.approvedby)==tourrequest.empgid:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.FORWARDER)
                return error_obj
            TravelHistory.objects.using(self._current_app_schema()).create(approvedby=data.approvedby,
                                                                           # onbehalfof=0,
                                                                           approveddate=time_function.ist_time(),
                                                                           request_type=(data.get_apptype()).upper(),
                                                                           applevel=data.applevel,
                                                                           comment="",
                                                                           status=Status.PENDING,
                                                                           tour_id=data.get_tour_id(), entity_id=self._entity_id())

            TravelHistory.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).update(comment=data.get_appcomment(),
                                                                                                                           status=Status.FORWARDED,
                                                                                                                           approveddate=time_function.ist_time(), entity_id=self._entity_id())
            if int(data.applevel)==2:
                TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id,entity_id=self._entity_id()).update(tour_status=Status.FORWARDED,entity_id=self._entity_id())
            else:
                TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id,entity_id=self._entity_id()).update(tour_status=Status.PENDING,entity_id=self._entity_id())

            # elif data.apptype.upper()==App_type.CLAIM:
            #
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=data.tour_id)
            #     if tourrequest.claim_status == Status.REQUESTED or tourrequest.claim_status == Status.APPROVED or \
            #             tourrequest.claim_status == Status.REJECTED or tourrequest.claim_status == Status.RETURNED:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #         return error_obj
            #     TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id).update(claim_status=Status.FORWARDED)


        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except Exception as e:
        #     print(e)
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(str(e))
        #     return error_obj

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    @transaction.atomic
    def update_return(self, data,employee_id,request):
        logger.info('ta_ Tour_return- '+str(employee_id)+str(data))
        # try:
        if data.onbehalf is not None:
            login_emp = request.employee_id
            approver_nac = data.onbehalf
        else:
            login_emp = 0
            approver_nac = request.employee_id

        employee_id=approver_nac

        if data.get_appcomment() is None or data.get_appcomment() == "":
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.COMMENT)
            return error_obj
        approver_data = (TravelHistory.objects.using(self._current_app_schema()).get(id=data.id, entity_id=self._entity_id()))

        if approver_data.approvedby > 0:
            if approver_data.approvedby != approver_nac:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVER)
                return error_obj
        module_permission = ApiService(self._scope())
        role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_eclaim, request)
        ceo_get = module_permission.onb_permission(request, employee_id)
        if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:
            if employee_id != approver_data.approvedby:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
        elif approver_data.request_type.upper() != (data.apptype).upper() or approver_data.tour_id != \
                int(data.tour_id):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID)
            return error_obj

        if data.apptype.upper()==App_type.TOUR:
            tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=data.tour_id,entity_id=self._entity_id())

            if approver_data.applevel==App_level.THIRD_LEVEL:
                time_service=Timecalculation()
                if tourrequest.end_date.date()<time_service.ist_time_format().date():
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.TOUR_ENDED)
                    return error_obj
                if tourrequest.tour_status == Status.DEFAULT or \
                            tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
            else:
                if tourrequest.tour_status == Status.DEFAULT or tourrequest.tour_status == Status.APPROVED or \
                            tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
            TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id).update(tour_status=Status.RETURNED,entity_id=self._entity_id())
        # elif data.apptype.upper()==App_type.ADVANCE:
        #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=data.tour_id,entity_id=self._entity_id())
        #     if tourrequest.advance_status != Status.PENDING:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
        #         return error_obj
        #     adv_data = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=data.tour_id,entity_id=self._entity_id()).last()
        #
        #     if data.appamount is not None:
        #
        #         claimed_amount = adv_data.reqamount
        #         validation_service = Validation(self._scope())
        #         approved_amt_validation = validation_service.higher_approve_amount(claimed_amount,
        #                                                                            data.appamount)
        #         if approved_amt_validation != True:
        #             return approved_amt_validation
        #
        #         data.appamount = float(data.appamount)
        #         if data.appamount <= 0:
        #             error_obj = NWisefinError()
        #             error_obj.set_code(ErrorMessage.INVALID_DATA)
        #             error_obj.set_description(ErrorDescription.CLAIM_AMOUNT)
        #             return error_obj
        #         TourAdvance.objects.using(self._current_app_schema()).filter(id=adv_data.id,entity_id=self._entity_id()).update(
        #             appamount=data.appamount)
        #     TourAdvance.objects.using(self._current_app_schema()).filter(id=adv_data.id,entity_id=self._entity_id()).update(
        #         status=Status.RETURNED,
        #         updated_by=employee_id,
        #         updated_date=today)
        #     TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id,entity_id=self._entity_id()).update(advance_status=Status.RETURNED,entity_id=self._entity_id())
        elif data.apptype.upper()==App_type.CLAIM:
            tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=data.tour_id,entity_id=self._entity_id())
            if tourrequest.claim_status == Status.DEFAULT or tourrequest.claim_status == Status.APPROVED or \
                    tourrequest.claim_status == Status.REJECTED or tourrequest.claim_status == Status.RETURNED:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                return error_obj
            TourRequest.objects.using(self._current_app_schema()).filter(id=data.tour_id,entity_id=self._entity_id()).update(claim_status=Status.RETURNED,entity_id=self._entity_id())
            amount=0
            claimreq=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=data.tour_id,status=1,entity_id=self._entity_id())
            for i in claimreq:
                amount+=i.claimedamount
            ccbs_obj = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=data.tour_id, ccbs_type=2, status=1,entity_id=self._entity_id()).all()
            for each_ccbs in ccbs_obj:
                percentage = (amount *each_ccbs.percentage) / 100
                Ccbs.objects.using(self._current_app_schema()).filter(id=each_ccbs.id,entity_id=self._entity_id()).update(
                    amount=round((percentage), 2),
                    updated_by=employee_id, updated_date=today,entity_id=self._entity_id())


        approve = TravelHistory.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).update(comment=data.get_appcomment(),onbehalfof_approval = login_emp,
                                                                                                                                 status= Status.RETURNED, approveddate=time_function.ist_time(), entity_id=self._entity_id(),approvedby=employee_id)


        # except Exception as e:
        #     print(e)
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(str(e))
        #     return error_obj
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except ApprovedBy.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
        #     return error_obj
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj

        mail_service = ta_email(self._scope())
        mail_service.mail_data(data.tour_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    # 17/1- expense approver side amount and ccbs update
    def update_claimamount(self,list_data, emp_id,tourid,expense_id):
        logger.info('ta_ Update_claim_amount- '+str(emp_id)+str(list_data)+str(tourid)+str(expense_id))
        claim_status = TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id()).claim_status
        if claim_status != Status.PENDING:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.CANT_EDIT)
            return error_obj
        exp_approver = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=App_type.CLAIM,
                                                                                      applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).last()
        exp_approverid = exp_approver.approvedby
        if exp_approverid != int(emp_id):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        if int(expense_id) <= 0 or int(expense_id)> 8:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj

        for data in list_data:
            if data["amount"] <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.CLAIM_AMOUNT)
                return error_obj
            if data["id"] <= 0 :
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj
            service = Tour_grade(self._scope())
            msg = service.check_each_expense(expense_id, data['id'], data['amount'],tourid)
            if isinstance(msg, NWisefinError):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
                error_obj.set_description(msg.description)
                return error_obj
        total_approved_amount=0
        for data in list_data:
            service=Tour_grade(self._scope())
            total_approved_amount=service.update_each_expense(expense_id,data['id'], round(data['amount'],2),tourid)
        ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid,expensegid=expense_id,status=1).update(
            approvedamount=round(total_approved_amount,2),updated_date=today,updated_by=emp_id,entity_id=self._entity_id())
        # tourid=(ClaimRequest.objects.using(self._current_app_schema()).get(id=data['claim_id'])).tour_id
        # if msg.status=="success":
        #     ccbs_amount=0
        #     total_claimed_amount=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid, status=1)
        #     for amount in total_claimed_amount:
        #         ccbs_amount+=amount.approvedamount
        #     ccbs_obj = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=tourid,ccbs_type=2,status=1).all()
        #     for each_ccbs in ccbs_obj:
        #         percentage = each_ccbs.percentage / 100
        #         Ccbs.objects.using(self._current_app_schema()).filter(id=each_ccbs.id).update(amount=ccbs_amount * percentage,
        #                                                     updated_by=emp_id, updated_date=today)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    def app_amt_ccbs_update(self,tourid,emp_id):
        logger.info('ta_ App_ccbs_update- '+str(emp_id)+str(tourid))
        claim_statsus=(TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())).claim_status
        if claim_statsus!=Status.PENDING:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.NOT_PENDING)
            return error_obj
        approver_id=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=App_type.CLAIM, applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).last()
        if emp_id!=approver_id.approvedby:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        claims=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
        total_app_amount=0
        for each_claim in claims:
            total_app_amount+=each_claim.approvedamount
        ccbs_obj = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=tourid, ccbs_type=2, status=1,entity_id=self._entity_id()).all()
        for each_ccbs in ccbs_obj:
            percentage = each_ccbs.percentage / 100
            Ccbs.objects.using(self._current_app_schema()).filter(id=each_ccbs.id,entity_id=self._entity_id()).update(amount=round((total_app_amount * percentage),2),
                                                                              updated_by=emp_id, updated_date=today,entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj



    def update_each_expense(self, expense_id, table_id,amount,tourid):
        total_app_amount = 0
        # try:

        if expense_id == 1:
            # pre_amount=Travel.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount<amount:
            #     self.approver_amount_high_error()
            Travel.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims=Travel.objects.using(self._current_app_schema()).filter(tourid_id=tourid,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount+=each_cliam.approvedamount


        elif expense_id == 2:
            # pre_amount = Dailydeim.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Dailydeim.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Dailydeim.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 3:
            # pre_amount = Incidental.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Incidental.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Incidental.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 4:
            # pre_amount = Localconveyence.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Localconveyence.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Localconveyence.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 5:
            # pre_amount = Lodging.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Lodging.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Lodging.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 6:
            # pre_amount = Misc.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Misc.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Misc.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 7:
            # pre_amount = PackingMoving.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            PackingMoving.objects.using(self._current_app_schema()).filter(id=table_id,entity_id=self._entity_id()).update(approvedamount=amount,entity_id=self._entity_id())
            claims = PackingMoving.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        elif expense_id == 8:
            # pre_amount = Localdeputation.objects.using(self._current_app_schema()).filter(id=table_id).last().approvedamount
            # if pre_amount < amount:
            #     self.approver_amount_high_error()
            Localdeputation.objects.using(self._current_app_schema()).filter(id=table_id).update(approvedamount=amount,entity_id=self._entity_id())
            claims = Localdeputation.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,entity_id=self._entity_id())
            for each_cliam in claims:
                total_app_amount += each_cliam.approvedamount
        return total_app_amount


    def check_each_expense(self, expense_id, table_id,amount,tourid):
        # try:

        if expense_id == 1:
            pre_amount=Travel.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount<amount:
                higher_app_amt=self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tourid_id!=tourid:
                invalid_tour=self.invalid_tourid()
                return invalid_tour
        elif expense_id == 2:
            pre_amount = Dailydeim.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 3:
            pre_amount = Incidental.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 4:
            pre_amount = Localconveyence.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 5:
            pre_amount = Lodging.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 6:
            pre_amount = Misc.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 7:
            pre_amount = PackingMoving.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour
        elif expense_id == 8:
            pre_amount = Localdeputation.objects.using(self._current_app_schema()).get(id=table_id,status=1,entity_id=self._entity_id())
            if pre_amount.claimedamount < amount:
                higher_app_amt = self.approver_amount_high_error()
                return higher_app_amt
            if pre_amount.tour_id != tourid:
                invalid_tour = self.invalid_tourid()
                return invalid_tour


        # except Exception as e:
        #     print(e)
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(str(e))
        #     return error_obj
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        # except ApprovedBy.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
        #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
        #     return error_obj
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
        #     return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def approver_amount_high_error(self):
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(ErrorDescription.HIGHER_APPROVE_AMOUNT)
        return error_obj
    def invalid_tourid(self):
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
        return error_obj

    # def dailydiem_eligible_amount(self, request_obj):
    #     exp_get=Expense_type_get()
    #     allowance_amount = Allowance.objects.using(self._current_app_schema()).get(expense_id=exp_get.Expense_type("dailydeim"),
    #                                              city=request_obj['city'],
    #                                              salarygrade=request_obj['salarygrade'])
    #     amount = allowance_amount.amount
    #
    #     if amount is not None:
    #         # daily = Dailydeim.objects.using(self._current_app_schema()).get(visitcity=request_obj["city"])
    #         if (request_obj['accbybank'] == 1 and request_obj['boardingbybank'] == 0 and request_obj['declaration'] == 0):
    #             amount = amount * (95 / 100)
    #         if (request_obj['accbybank'] == 0 and request_obj['boardingbybank'] == 1 and request_obj['declaration'] == 0):
    #             amount = amount * (50 / 100)
    #         if (request_obj['accbybank'] == 1 and request_obj['boardingbybank'] == 1 and request_obj['declaration'] == 0):
    #             amount = amount * (25 / 100)
    #         if (request_obj['accbybank'] == 0 and request_obj['boardingbybank'] == 0 and request_obj['declaration'] == 1):
    #             amount = amount * (100 / 100)
    #
    #         leave = int(request_obj['isleave'])
    #         start = request_obj['fromdate']
    #         end = request_obj['todate']
    #         start_date = datetime.strptime(str(start), '%Y-%m-%d %H:%M:%S')
    #         end_date = datetime.strptime(str(end), '%Y-%m-%d %H:%M:%S')
    #         holiday_resp = HolidayDeim()
    #         holiday = holiday_resp.Holiday_check(start_date, end_date)
    #         date = abs((end_date - start_date).days)
    #
    #         days=date-holiday
    #         hours = (end_date.hour - start_date.hour)
    #         sys_hours = hours + (days * 24)
    #
    #         if holiday == 0:
    #             days = date - leave
    #             eligibleamount = int(days * amount)
    #
    #         else:
    #             days = date - int(holiday + leave)
    #             holiday_deim=holiday_deim_table.objects.using(self._current_app_schema()).get(city=request_obj['city'],entity=request_obj['entity']
    #                                                         ,salarygrade=request_obj['salarygrade'])
    #             eligibleamount = (days * amount) + (holiday * holiday_deim.amount)
    #         tour_id = request_obj['tourid']
    #         if tour_id != 0:
    #             tour_request = TourRequest.objects.using(self._current_app_schema()).get(id=tour_id)
    #             treason = tour_request.reason
    #             tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=treason)
    #             reason = tour_reason.name
    #             if reason.upper() == 'INSPECTION':
    #                 inspection_amount = days * 100
    #                 eligibleamount = eligibleamount + inspection_amount
    #         response = Allowanceresponse()
    #         response.set_eligible_amount(eligibleamount)
    #         response.set_sys_hours(sys_hours)
    #         return response

    # def dailydiem_eligible_amount(self, request_obj):
    #     # exp_get=Expense_type_get()
    #     # allowance_amount = Allowance.objects.using(self._current_app_schema()).get(expense_id=exp_get.Expense_type("dailydeim"),
    #     #                                          city=request_obj['city'],
    #     #                                          salarygrade=request_obj['salarygrade'])
    #     service=El_lod_ser()
    #     request_obj["exp_type"]="Dailydeim"
    #     request_obj["expensegid"]="2"
    #     isleave= request_obj["isleave"]
    #     amount_data = service.elig_citytoamount_effectivedate(request_obj)
    #
    #     for data in amount_data:
    #         if isleave == "" and isleave == None:
    #             amount_data[0]['isleave'] = 0
    #         else :
    #             amount_data[0]['isleave'] = isleave
    #         # if hour > 0:
    #         #     amount_data[len(amount_data)-1]['days'] = int(amount_data[len(amount_data)-1].get('days')) +1
    #         tot_days = 0
    #         for i in amount_data:
    #             tot_days = tot_days + int(i.get('days'))
    #         if tot_days > days:
    #             diff = tot_days - days
    #             if diff >0:
    #                 amount_data[len(amount_data) - 1]['days'] = int(amount_data[len(amount_data) - 1].get('days')) - diff
    #
    #         for i in amount_data:
    #             amount = i.get('amount')
    #             days = i.get('days')
    #             holiday = i.get('holiday')
    #
    #             if 'isleave' in i :
    #                 isleave = i.get('isleave')
    #             else:
    #                 isleave = 0
    #
    #         if amount is not None:
    #             # daily = Dailydeim.objects.using(self._current_app_schema()).get(visitcity=request_obj["city"])
    #             if (request_obj['accbybank'] == 1 and request_obj['boardingbybank'] == 0 and request_obj['declaration'] == 0):
    #                 amount = amount * (95 / 100)
    #             if (request_obj['accbybank'] == 0 and request_obj['boardingbybank'] == 1 and request_obj['declaration'] == 0):
    #                 amount = amount * (50 / 100)
    #             if (request_obj['accbybank'] == 1 and request_obj['boardingbybank'] == 1 and request_obj['declaration'] == 0):
    #                 amount = amount * (25 / 100)
    #             if (request_obj['accbybank'] == 0 and request_obj['boardingbybank'] == 0 and request_obj['declaration'] == 1):
    #                 amount = amount * (100 / 100)
    #
    #             leave = int(request_obj['isleave'])
    #             start = request_obj['fromdate']
    #             end = request_obj['todate']
    #             start_date = datetime.strptime(str(start), '%Y-%m-%d %H:%M:%S')
    #             end_date = datetime.strptime(str(end), '%Y-%m-%d %H:%M:%S')
    #             # holiday_resp = HolidayDeim()
    #             # holiday = holiday_resp.Holiday_check(start_date, end_date)
    #             # date = abs((end_date - start_date).days)
    #             #
    #             # days=date-holiday
    #             hours = (end_date.hour - start_date.hour)
    #             sys_hours = hours + (days * 24)
    #
    #             if holiday == 0:
    #                 days = date - leave
    #                 eligibleamount = int(days * amount)
    #
    #             else:
    #                 days = date - int(holiday + leave)
    #                 holiday_deim=holiday_deim_table.objects.using(self._current_app_schema()).get(city=request_obj['city'],entity=request_obj['entity']
    #                                                             ,salarygrade=request_obj['salarygrade'])
    #                 eligibleamount = (days * amount) + (holiday * holiday_deim.amount)
    #             tour_id = request_obj['tourid']
    #             if tour_id != 0:
    #                 tour_request = TourRequest.objects.using(self._current_app_schema()).get(id=tour_id)
    #                 treason = tour_request.reason
    #                 tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=treason)
    #                 reason = tour_reason.name
    #                 if reason.upper() == 'INSPECTION':
    #                     inspection_amount = days * 100
    #                     eligibleamount = eligibleamount + inspection_amount
    #             response = Allowanceresponse()
    #             response.set_eligible_amount(eligibleamount)
    #             response.set_sys_hours(sys_hours)
    #             return response


    def dailydiem_eligible_amount(self, dtl,request):
        # city = jsondata['city']
        # boardingbybank = int(jsondata['boardingbybank'])
        # accbybank = int(jsondata['accbybank'])
        # declaration = int(jsondata['declaration'])
        # isleave = int(jsondata['isleave'])
        # eligible_amount = 0
        # hour = 0
        # tourid=jsondata['tourgid']
        # ddlimit = ['Transfer-Reporting', 'Transfer without Family', 'Transfer with family']

        # tour_request = TourRequest.objects.using(self._current_app_schema()).get(id=jsondata['tourgid'],entity_id=self._entity_id())
        # treason = tour_request.reason
        # req_date=tour_request.request_date
        # tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=treason,entity_id=self._entity_id())
        # tourreason = tour_reason.name

        citytype = dtl['citytype']
        expense_id = dtl['expensegid']
        fromdate = dtl['fromdate']
        todate = dtl['todate']
        datetimeFormat = '%Y-%m-%d %H:%M:%S'

        diff = datetime.strptime(todate, datetimeFormat) - datetime.strptime(fromdate, datetimeFormat)
        day = str(diff).split()
        days = diff.days
        sec = diff.total_seconds()
        min = sec / 60
        hours = min // 60
        value = hours % 24
        if dtl["boardingbyorganiser"] == 'YES':
            i = Allowance.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                citytype=citytype,
                expense_id=expense_id)[0]

            eligible_amt1 = int(i.city) * days
            if value >= 9 and value < 24:
                eligible_amt2 = int(i.city)
            else:
                eligible_amt2 = 0

        elif dtl["boardingbyorganiser"] == 'NO' or dtl["citytype"] == 'DOMESTIC':
            i = Allowance.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                citytype=citytype,
                expense_id=expense_id)[0]
            eligible_amt1 = int(i.amount) * days
            if value >= 9 and value < 24:
                eligible_amt2 = int(i.amount)
            else:
                eligible_amt2 = 0

        eligible_amt = eligible_amt1 + eligible_amt2  # final amount
        eligible_value = {
            "Eligible_amount": eligible_amt,
            "noofdays": days,
            "noofhours": hours
        }
        return json.dumps(eligible_value)

        # return {"eliglible_value:",eligible_amt}




        # if citytype == 'DOMESTIC':
        #     if hours < 9:
        #         eligible_amt = 0
        #     elif hours >= 9 and hours < 24:
        #         eligible_amt = int(list_data[0]['elgibleamount'])
        #     elif hours > 24:
        #         eligible_amt1 = int(list_data[0]['elgibleamount']) * days
        #         if value < 9:
        #             eligible_amt2 = 0
        #         elif value >= 9 and value < 24:
        #             eligible_amt2 = int(list_data[0]['elgibleamount'])
        #         eligible_amt = eligible_amt1 + eligible_amt2
        # elif citytype == 'INTERNATIONAL(uk)':
        #     if hours < 9:
        #         eligible_amt = 0
        #     elif hours >= 9 and hours < 24:
        #         eligible_amt = int(list_data[0]['elgibleamount'])
        #     elif hours > 24:
        #         eligible_amt = int(list_data[0]['elgibleamount']) * days
        # elif citytype == 'INTERNATIONAL(US,EUROPE,JAPAN)':
        #     if hours < 9:
        #         eligible_amt = 0
        #     elif hours >= 9 and hours < 24:
        #         eligible_amt = int(list_data[0]['elgibleamount'])
        #     elif hours > 24:
        #         eligible_amt = int(list_data[0]['elgibleamount']) * days
        # elif citytype == 'OTHERCOUNTRIES':
        #     if hours < 9:
        #         eligible_amt = 0
        #     elif hours >= 9 and hours <= 24:
        #         eligible_amt = int(list_data[0]['elgibleamount'])
        #     elif hours > 24:
        #         eligible_amt = int(list_data[0]['elgibleamount']) * days
        #
        # if tourreason in ddlimit:
        #     days=7
        #     hours=(7*24)
        #     # jsondata['fromdate']=str(req_date)
        #     # jsondata['todate']=str(req_date)
        # else:
        #     from_date = jsondata['fromdate']
        #     to_date = jsondata['todate']
        #     datetimeFormat = '%Y-%m-%d %H:%M:%S'
        #     diff = datetime.strptime(to_date, datetimeFormat) - datetime.strptime(from_date,datetimeFormat)
        #     day = str(diff).split()
        #     days = diff.days
        #     sec = diff.total_seconds()
        #     min = sec / 60
        #     hours = min // 60
        #     if days > 0 :
        #         hour = day[2].split(':')
        #         tmp_hours = float(str(hour[0]) + '.' + str(hour[1]))
        #         hour = round(tmp_hours)
        #     else :
        #         hour = day[0].split(':')
        #         tmp_hours = float(str(hour[0]) + '.' + str(hour[1]))
        #         hour = round(tmp_hours)
        #     if hour > 0:
        #         days = days+1
        #
        # service = El_lod_ser(self._scope())
        # tour_duration_check=service.tour_duration(tourid)
        #
        # jsondata["exp_type"]="Dailydeim"
        # jsondata["expensegid"]="2"
        # if city != "":
        #
        #     grade_service = Tourno_details(self._scope())
        #     grade = grade_service.grade_get_tourid(jsondata['tourgid'])
        #     amount_data = service.elig_citytoamount_effectivedate(jsondata,grade,request)
        #     if isinstance(amount_data,NWisefinError):
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
        #         error_obj.set_description(amount_data.description)
        #         return error_obj
        #     if tourreason in ddlimit:
        #         amount_data[0]['days']=7
        #
        #     if isleave == "" and isleave == None:
        #         amount_data[0]['isleave'] = 0
        #     else :
        #         amount_data[0]['isleave'] = isleave
        #     # if hour > 0:
        #     #     amount_data[len(amount_data)-1]['days'] = int(amount_data[len(amount_data)-1].get('days')) +1
        #     tot_days = 0
        #     for i in amount_data:
        #         tot_days = tot_days + int(i.get('days'))
        #     if tot_days > days:
        #         diff = tot_days - days
        #         if diff >0:
        #             amount_data[len(amount_data) - 1]['days'] = int(amount_data[len(amount_data) - 1].get('days')) - diff
        #
        #     for i in amount_data:
        #         amount = i.get('amount')
        #         days = i.get('days')
        #         holiday = i.get('holiday')
        #
        #         if 'isleave' in i :
        #             isleave = i.get('isleave')
        #         else:
        #             isleave = 0
        #
        #         if boardingbybank != "" and accbybank != "" and declaration != "":
        #             if int(accbybank) == 1 and int(boardingbybank) == 0 and int(declaration) == 0:
        #                 amount = (amount / 100) * 75
        #
        #             elif int(accbybank) == 0 and int(boardingbybank) == 1 and int(declaration) == 0:
        #                 amount = (amount / 100) * 50
        #
        #             elif int(accbybank) == 1 and int(boardingbybank) == 1 and int(declaration) == 0:
        #                 amount = (amount / 100) * 25
        #
        #             elif int(accbybank) == 1 and int(boardingbybank) == 0 and int(declaration) == 1:
        #                 amount = (amount / 100) * 100
        #
        #         inspection_amount = 0
        #         if 'tourid' in jsondata:
        #             # tour_request = TourRequest.objects.using(self._current_app_schema()).get(id=jsondata['tourid'])
        #             # treason = tour_request.reason
        #             # tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=treason)
        #             # tourreason = tour_reason.name
        #             if tourreason.upper() == 'INSPECTION':
        #                 inspection_amount = days * 100
        #
        #         service = Driver_bata(self._scope())
        #         designation = service.get_designation(grade)
        #
        #         if tourreason not in ddlimit:
        #             if tour_duration_check == True:
        #                 if designation in ["EXECUTIVE", "OFFICER"]:
        #                     if int(hour) < 4:
        #                         days = 0.5
        #                     elif 8 >= int(hour) >= 4:
        #                         days = 0.5
        #                     else:
        #                         print("Fullday deim")
        #                 else:
        #                     spl_a = to_date.split(" ")
        #                     spl_b = from_date.split(" ")
        #                     totime = spl_a[1].split(":")
        #                     fromtime = spl_b[1].split(":")
        #                     if 10 <= int(fromtime[0]) and 17 >= int(totime[0]):
        #                         if int(hour) < 3:
        #                             days = 0.5
        #                         elif int(hour) >= 4:
        #                             print("Fullday deim")
        #                     else:
        #                         print("OutofOffice Hours")
        #             else:
        #                 print("Longterm tour")
        #
        #         grade_service=Tourno_details(self._scope())
        #         grade=grade_service.grade_get_tourid(jsondata['tourgid'])
        #
        #         if holiday != 0:
        #             holidaydeim=holiday_deim_table.objects.using(self._current_app_schema()).filter(salarygrade=grade,entity_id=self._entity_id())
        #             if holidaydeim is not None:
        #                 for i in holidaydeim:
        #                     if i.city.upper() == city.upper():
        #                         days = days - (int(holiday) + int(isleave))
        #                         eligible_amount = (days * amount) + int(i.amount) +inspection_amount
        #             else:
        #                 eligible_amount = (days * amount) + (int(isleave) * 0)+inspection_amount
        #         else:
        #             days = days - (int(holiday) + int(isleave))
        #             eligible_amount = (days * amount) + (holiday * amount * 1.25) +inspection_amount
        #
        # else:
        #     return {"MESSAGE": 'ERROR_OCCURED.' + "City Data Missing"}
        #
        # if float(eligible_amount)<0:
        #     eligible_amount=0
        # if float(hours)<0:
        #     hours=0
        # eligible_value = {
        #     "Eligible_amount": eligible_amount,
        #     "sys_hours": hours{"Eligible_amount": amount}
        #
        # }
