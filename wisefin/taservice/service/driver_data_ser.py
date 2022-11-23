import json
from taservice.models import Employeemapping, Allowance
from django.db.models import Q
from taservice.data.response.driver_bata_res import Designation_get
from taservice.service.elligible_amount_ser import El_lod_ser
from taservice.service.emp_name_get import Tourno_details
from taservice.service.holiday_deim import HolidayDeim
from taservice.util.ta_util import Filterstatus
from datetime import datetime

# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

class Driver_bata(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def get_designation(self,data_grade):
        condition=Q(grade=data_grade, status=Filterstatus.two,entity_id=self._entity_id())
        des=Employeemapping.objects.using(self._current_app_schema()).get(condition)
        return des.designation


    # def cal_bata(self,traveltime,amount):
    #     if traveltime>24:
    #         days=2
    #     else:
    #         days=1
    #     driverbata=days*amount
    #     response=Designation_get()
    #     response.set_driverbata(driverbata)
    #     response.set_daysdrivereng(days)
    #     return response

    def deputation_amount(self,data,request):
        grade_service = Tourno_details(self._scope())
        grade = grade_service.grade_get_tourid(data.tourgid)
        expensegid = data.expense_id
        city = data.city
        isleave = int(data.leave)
        from_date = data.startdate
        to_date = data.enddate
        entity = data.entity
        # Entity_Gid = int(data.get('Params').get('FILTER').get('Entity_Gid'))
        # tourgid = data.get('Params').get('FILTER').get('tourgid')
        eligible_amount = 0
        datetimeFormat = '%Y-%m-%d'
        diff = datetime.strptime(to_date, datetimeFormat) - datetime.strptime(from_date,datetimeFormat)
        days = diff.days
        if days == 0:
            days = 1


        service=Driver_bata(self._scope())
        designation = service.get_designation(grade)

        service=El_lod_ser(self._scope())
        jsondata={}
        jsondata['exp_type'] = "Dailydeim"
        jsondata['fromdate'] = from_date
        jsondata['todate'] = to_date
        jsondata['expensegid'] = expensegid
        jsondata['city'] = city
        jsondata['entity'] = entity
        jsondata['salarygrade'] = designation
        jsondata['tourgid'] = data.tourgid
        amount_data = service.elig_citytoamount_effectivedate(jsondata,designation,request)
        tot_amount = 0
        holidays=0
        tot_days=0
        for i in amount_data:
            # amount = i.get('amount')
            tot_days = i.get('days')+ tot_days
            holidays = i.get('holiday')+ holidays
            tot_amount = tot_amount + i.get('amount')
            # days = int(i.get('days')) - int(i.get('holiday'))
        final_days=tot_days-holidays
        final_amount =0
        if int(data.no_of_days) != 0:
            final_amount = (int(data.no_of_days) - int(isleave)) * tot_amount
        else :
            final_amount = (final_days - int(isleave)) * tot_amount
        if float(final_amount)<0:
            final_amount=0
        if float(final_days)<0:
            final_days=0
        eligible_value = {
            "Eligible_amount": final_amount,
            "noofdays": final_days
        }
        return json.dumps(eligible_value)


