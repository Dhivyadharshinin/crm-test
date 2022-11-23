import json

# from taservice.data.request.eligible_amount_req import allowance_req
from taservice.data.response.tourallowance import Allowanceresponse
from taservice.models.tamodels import Allowance, Holiday, TourRequest, Common_dropdown_details, TourDetail, \
    AccomodationBookingDetails, AirBookingDetails, TrainBookingDetails,Ta_City, BusBookingDetails, CabBookingDetails, CabMapping
from datetime import *
from taservice.data.response.el_lod_res import El_lod_res
from taservice.service.emp_name_get import Tourno_details
from taservice.util.ta_util import Filterstatus
# from utilityservice.service.dbutil import DataBase
from django.utils.timezone import now

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription

from utilityservice.service.threadlocal import NWisefinThread
class El_lod_ser(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    # def get_elligible_amount(self,data,amount):
    #     checkin=data.get_checkindate()
    #     checkout=data.get_checkoutdate()
    #     checkin = datetime.strptime(checkin, '%Y-%m-%d %H:%M:%S')
    #     checkout = datetime.strptime(checkout, '%Y-%m-%d %H:%M:%S')
    #     days=((checkout.date())-(checkin.date())).days
    #     if checkout.hour - checkin.hour >= 1:
    #         days += 1
    #     elligible_amount= days*amount
    #     amount_resp=El_lod_res()
    #     amount_resp.set_no_of_days(days)
    #     amount_resp.set_elligible_amount(elligible_amount)
    #     return amount_resp

    def get_elligible_amount(self, dtl, request):
        fromdate = dtl['fromdate']
        todate = dtl['todate']
        citytype = dtl['Lodge_Homestay']
        if citytype == 'Lodging':
            try:
                list = Ta_City.objects.using(self._current_app_schema()).filter(
                    name=dtl['city'], entity_id=self._entity_id(), status=1)[0]
                if list.metro_non == 1:
                    metro_nonmetro = "metro"
                elif list.metro_non == 0:
                    metro_nonmetro = "nonmetro"
            except:
                metro_nonmetro = "nonmetro"
            city = metro_nonmetro
        else:
            city = None
        expense_id = int(dtl['expensegid'])
        datetimeFormat = '%Y-%m-%d %H:%M:%S'

        diff = datetime.strptime(todate, datetimeFormat) - datetime.strptime(fromdate, datetimeFormat)
        day = str(diff).split()
        days = diff.days
        sec = diff.total_seconds()
        min = sec / 60
        hours = min // 60
        value = hours % 24
        if value > 0:
            days = days + 1
        else:
            days = days

        i = Allowance.objects.using(self._current_app_schema()).filter(
            citytype=citytype,
            city=city,
            expense_id=expense_id,entity_id=self._entity_id())[0]
        eligible_amt = int(i.amount) * days

        eligible_value = {
            "Eligible_amount": eligible_amt
        }
        return json.dumps(eligible_value)

        # if Lodge_Homestay == 'lodging' and metro_nonmetro == 'metro':
        #     # tax = 500 * days
        #     eligible_amt = int(list_data[0]['elgibleamount']) * days
        #     # ttl_amt = int(bill_amt) + tax
        #
        # elif Lodge_Homestay == 'lodging' and metro_nonmetro == 'nonmetro':
        #     # tax = 200 * days
        #     eligible_amt = int(list_data[0]['elgibleamount']) * days
        #     # ttl_amt = int(bill_amt) + tax
        #
        # else:
        #     eligible_amt = int(list_data[0]['elgibleamount']) * days
        #     # ttl_amt = int(bill_amount)

        # city = jsondata['city']
        # # grade = jsondata['salarygrade']
        # expensegid = jsondata['expensegid']
        # frdt = jsondata['fromdate']
        # todt = jsondata['todate']
        # grade_service = Tourno_details(self._scope())
        # grade = grade_service.grade_get_tourid(jsondata['tourgid'])
        # if 'taxonly' not in jsondata:
        #     jsondata['taxonly']=0
        #
        # datetimeFormat = '%Y-%m-%d %H:%M:%S'
        # diff = datetime.strptime(todt, datetimeFormat) - datetime.strptime(frdt, datetimeFormat)
        # day = str(diff).split()
        # days = diff.days
        # if days == 0:
        #     hour = day[0].split(':')
        #     hour = int(hour[0])
        # else:
        #     hour = day[2].split(':')
        #     hour = int(hour[0])
        # if hour > 0:
        #     days = days+1
        # noofdays = days
        # tot_amount =0
        # service=El_lod_ser(self._scope())
        # jsondata['exp_type']="Lodge"
        # amount_data = service.elig_citytoamount_effectivedate(jsondata,grade,request)
        # holidays = 0
        # tot_days =0
        # tot_amount =0
        # for i in amount_data:
        #     tot_days = tot_days + i.get('days')
        #     tot_amount = tot_amount+float(i.get('amount'))
        #     holidays = holidays + int(i.get('holiday'))
        # final_days = 0
        # if tot_days > days:
        #     diff = tot_days - days
        #     if diff > 0:
        #         final_days = int(amount_data[len(amount_data) - 1].get('days')) - diff
        # else:
        #     final_days = noofdays
        # tot_amount = (final_days + holidays) * tot_amount
        # if int(jsondata['accbybank'])==1:
        #     tot_amount=0
        #
        # if float(tot_amount)<0:
        #     tot_amount=0
        # if float(noofdays)<0:
        #     noofdays=0
        # eligible_value = {
        #     "Eligible_amount_without_tax": tot_amount,
        #     "Eligible_amount": float(tot_amount),
        #     "noofdays": noofdays
        # }

    def get_amount(self,data):
        amo= Allowance.objects.using(self._current_app_schema()).get(city=data.city, expense_id=data.expense_id, status=Filterstatus.one, salarygrade=data.designation,entity_id=self._entity_id())
        return amo.amount

    # def elig_citytoamount_effectivedate(self, grade, city, from_dt, to_dt, expensegid, entity_gid, exp_type):
    #     claim_allowance= Allowance.objects.using(self._current_app_schema()).get(city=city,salarygrade=grade, expense_id=expensegid)
    #
    #     start_date = datetime.strptime(str(from_dt), '%Y-%m-%d %H:%M:%S')
    #     end_date = datetime.strptime(str(to_dt), '%Y-%m-%d %H:%M:%S')
    #     delta = abs((end_date - start_date).days)
    #     totholiday_a = 0
    #     final_amount = []
    #     date_a = -1
    #     date_b = -1
    #     totholiday_b = 0
    #     data_a = {}
    #     data_b = {}
    #     if exp_type =="Dailydeim":
    #         pass

    # def elig_citytoamount_effectivedate(self, grade, city, from_dt, to_dt, expensegid, entity_gid, exp_type):
    def elig_citytoamount_effectivedate(self, data,grade,request):
        # grade_service = Tourno_details()
        # grade = grade_service.grade_get_tourid(data['tourgid'])
        from_dt=data['fromdate']
        to_dt=data['todate']
        expensegid=data['expensegid']
        exp_type=data['exp_type']
        city=data['city']

        out_data=Allowance.objects.using(self._current_app_schema()).filter(city=city,salarygrade=grade, expense_id=expensegid,entity_id=self._entity_id())
        sdate = from_dt.split()
        edate = to_dt.split()

        sdate = sdate[0].split('-')
        edate = edate[0].split('-')

        sdate = date(int(sdate[0]), int(sdate[1]), int(sdate[2]))  # start date
        edate = date(int(edate[0]), int(edate[1]), int(edate[2]))  # end date

        delta = edate - sdate  # as timedelta
        totholiday_a = 0
        final_amount = []
        date_a = 0
        date_b = 0
        totholiday_b = 0
        data_a = {}
        data_b = {}
        if exp_type == "Dailydeim":
            # state_get = {
            #     "City": city.upper(),
            #     "Entity_Gid": entity_gid
            # }
            # obj_claim.filter_json = json.dumps(state_get)
            # ld_out_message = obj_claim.eClaim_citytostate_get()
            # state_data = json.loads(ld_out_message.get("DATA").to_json(orient='records'))
            # state_gid = state_data[0].get('state_gid')
            status_id_get=ApiService(self._scope())
            # 13/1 state id- Ste
            state_id=status_id_get.state_id(city,request)


            if  state_id=="False" or state_id is False :
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
                error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
                return error_obj
            try:
                state_id=int(state_id)
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
                error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
                return error_obj
            # if state is None:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_CUSTOMER_ID)
            #     return error_obj
            # else:
            #     state_id=state.state_id



        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            for j in out_data:
                if j.effectiveto != '0' and j.effectiveto != '00-00-0000' and j.effectiveto is not None:
                    efdate = str(j.effectivefrom).split()
                    etdate = str(j.effectiveto).split()

                    efdate = efdate[0].split('-')
                    etdate = etdate[0].split('-')

                    from_d = date(int(efdate[0]), int(efdate[1]), int(efdate[2]))  # start date
                    to_d = date(int(etdate[0]), int(etdate[1]), int(etdate[2]))
                    holiday = 0
                    if from_d <= day <= to_d:
                        if exp_type == "Dailydeim":
                            # holiday = 0
                            # totholiday_a=0
                            # get_holiday = {
                            #     "Stategid": state_gid,
                            #     "Entity_Gid": entity_gid,
                            #     "Date": str(day)
                            # }
                            # obj_claim.filter_json = json.dumps(get_holiday)
                            # ld_out_holiday = obj_claim.eClaim_statetoholiday_get()
                            # holiday = json.loads(ld_out_holiday.get("DATA").to_json(orient='records'))

                            holiday_get=Holiday.objects.using(self._current_app_schema()).filter(date=str(day),state=state_id,entity_id=self._entity_id())
                            if len(holiday_get)==0:
                                holiday=0
                            else:
                                holiday=1

                        totholiday_a = totholiday_a + holiday
                        date_a = date_a - holiday + 1
                        data_a['days'] = date_a
                        data_a['holiday'] = totholiday_a
                        data_a['amount'] = j.amount

                else:
                    efdate = str(j.effectivefrom).split()
                    efdate = efdate[0].split('-')
                    from_d = date(int(efdate[0]), int(efdate[1]), int(efdate[2]))  # start date
                    holiday=0
                    if from_d <= day:
                        if exp_type == "Dailydeim":

                            # holiday = 0
                            # totholiday_b=0
                            # get_holiday = {
                            #     "Stategid": state_gid,
                            #     "Entity_Gid": entity_gid,
                            #     "Date": str(day)
                            # }
                            # obj_claim.filter_json = json.dumps(get_holiday)
                            # ld_out_holiday = obj_claim.eClaim_statetoholiday_get()
                            # holiday = json.loads(ld_out_holiday.get("DATA").to_json(orient='records'))
                            # totholiday_a = totholiday_a + int(holiday[0].get('Data'))

                            holiday_get = Holiday.objects.using(self._current_app_schema()).filter(date=str(day), state=state_id,entity_id=self._entity_id())
                            if len(holiday_get)==0:
                                holiday = 0
                            else:
                                holiday = 1
                            totholiday_a = totholiday_a + holiday

                            # totholiday_b = totholiday_b + holiday

                        date_b = date_b - holiday + 1
                        data_b['days'] = date_b
                        data_b['holiday'] = totholiday_b
                        data_b['amount'] = j.amount
        if len(data_a) != 0:
            final_amount.append(data_a)
        if len(data_b) != 0:
            final_amount.append(data_b)
        return final_amount


    def tour_duration(self,tourid):
        duration=TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())
        if duration.durationdays > 1:
            return False
        else:
            return True

    def create_elligible_amount(self,request_obj):
        for dtl in request_obj['data']:
            # data = allowance_req(dtl)
            effectiveto = dtl['effectiveto'] - 1
            exist_record = Allowance.objects.using(self._current_app_schema()).filter(citytype=dtl['citytype'],
                                                                                      entity_id=self._entity_id()).update(
                effectiveto=effectiveto).last()

            create_record = Allowance.objects.using(self._current_app_schema()).create(
                citytype=dtl['citytype'],
                city=dtl['city'],
                amount=dtl['amount'],
                expense=dtl['expense'],
                applicableto=dtl['applicableto'],
                status=1,
                entity=1,
                created_date=now(),
                effectivefrom=dtl['effectivefrom'],
                effectiveto=None)

