import math

from taservice.models import Gradeeligibility
from taservice.data.response.tourallowance import GradeEligibiltyresponse
from taservice.service.elligible_amount_ser import El_lod_ser
from taservice.service.driver_data_ser import Driver_bata
# from taservice.service.breakage_amount_ser import Breakage_amount_ser
import json

from taservice.service.emp_name_get import Tourno_details
from taservice.service.tourallowance import Tour_allowance
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace

from utilityservice.service.threadlocal import NWisefinThread
class Packing_moving_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def get_grade_elligibility(self,salarygrade):
        grade = Gradeeligibility.objects.using(self._current_app_schema()).filter(grade=salarygrade,entity_id=self._entity_id())
        return grade

    # def packing_moving_amount(self,data,grade_data):
    #     totaldisttrans=data.totaldisttrans
    #     twowheelertrans=data.twowheelertrans
    #     if data.totaldisttrans< 1000:
    #         rupeeforton=grade_data.freight1000
    #     else:
    #         rupeeforton=grade_data.freight1001
    #
    #     if data.tonnagehhgood<grade_data.maxtonnage:
    #         tonnage=grade_data.maxtonnage
    #     else:
    #         tonnage=data.tonnagehhgood
    #
    #     if grade_data.twowheller==1:
    #         twowheeler= [0,1]
    #     elif grade_data.twowheller==0:
    #         twowheeler=[0]
    #
    #     if data.distinhilly is not None:
    #         distinhilly=data.distinhilly
    #     else:
    #         distinhilly=0
    #
    #     tot_amt = 0
    #     if int(twowheelertrans) in twowheeler:
    #         if int(distinhilly) != 0:
    #             tot_amt = tot_amt + int(distinhilly) * tonnage * rupeeforton * grade_data.hillyregion
    #         if int(totaldisttrans) - int(distinhilly) != 0:
    #             tot_amt = tot_amt + (int(totaldisttrans) - int(distinhilly)) * tonnage * rupeeforton
    #     return "{:.2f}".format(tot_amt)


    def total_amount(self,json_param):

        grade_service = Tourno_details(self._scope())
        grade = grade_service.grade_get_tourid(json_param.tourgid)
        pkg_moving=Packing_moving_ser(self._scope())
        eligible_value = pkg_moving.validate_data(json_param, grade)
        driverbatta = 0
        daysdrivereng = 0
        if json_param.traveltime is not None:
            traveltime = json_param.traveltime
        else:
            traveltime = ""
        if traveltime != "":
            amountandadys = pkg_moving.calck_driverbata( json_param, grade)
            if amountandadys != 0:
                if 'driverbatta' in amountandadys and 'daysdrivereng' in amountandadys:
                    driverbatta = amountandadys['driverbatta']
                    daysdrivereng = amountandadys['daysdrivereng']
        breakagecharge = pkg_moving.calc_breakage( json_param, grade)
        if float(eligible_value)<0:
            eligible_value=0
        if float(driverbatta)<0:
            driverbatta=0
        if float(daysdrivereng)<0:
            daysdrivereng=0
        if float(breakagecharge)<0:
            breakagecharge=0
        eligible = {
            "transportation_amount": eligible_value,
            "driverbatta": str(driverbatta),
            "daysdrivereng": str(daysdrivereng),
            "breakagecharge": str(breakagecharge),
            "Eligible_amount":driverbatta +breakagecharge + float(eligible_value)
        }
        return json.dumps(eligible)

    def calc_breakage(self, jsondata, grades):
        receipt = int(jsondata.receipt_loss)
        expensegid = int(jsondata.expense_id)
        service=Driver_bata(self._scope())
        designation = service.get_designation(grades)
        service=Tour_allowance(self._scope())
        if jsondata.tourgid is not None:
            tourgid = jsondata.tourgid
            data = service.elig_citytoamount( designation, "Lumpsum", expensegid,tourgid)
        # else:
        #     data = service.elig_citytoamount_tmp( designation, "Lumpsum", expensegid)
        if data !=[]:
            for each_data in data:
                if receipt == int(each_data.applicableto):
                    return each_data.amount
        else:
            return 0


    def validate_data(self, jsondata, grade):
        totaldisttrans = float(jsondata.totaldisttrans)
        tonnagehhgood = float(jsondata.tonnagehhgood)
        distinhilly = float(jsondata.distinhilly)
        twowheelertrans = float(jsondata.twowheelertrans)

        service=Packing_moving_ser(self._scope())
        ld_elig = service.get_grade_elligibility(grade.upper())
        if int(totaldisttrans) in range(0, 1000):
            rupeeforton = ld_elig[0].freight1000
        else:
            rupeeforton = ld_elig[0].freight1001
        if int(tonnagehhgood) <= ld_elig[0].maxtonnage:
            tonnage = int(tonnagehhgood)
        else:
            tonnage = int(ld_elig[0].maxtonnage)

        if ld_elig[0].twowheller == 1:
            twowheeler = [0, 1]
        else:
            twowheeler = [0]

        tot_amt = 0
        if int(twowheelertrans) in twowheeler:
            if int(distinhilly) != 0:
                tot_amt = tot_amt + int(distinhilly) * tonnage * rupeeforton * ld_elig[0].hillyregion

            if int(totaldisttrans) - int(distinhilly) != 0:
                tot_amt = tot_amt + (int(totaldisttrans) - int(distinhilly)) * tonnage * rupeeforton

            formatted_float = "{:.2f}".format(tot_amt)
            return formatted_float
        else:
            logic = "false"
            ld_dict = {"MESSAGE": "Not Eligible In Two wheeler"}
            return logic, ld_dict

    def calck_driverbata(self, jsondata, grades):
        traveltime = float(jsondata.traveltime)
        expensegid = float(jsondata.expense_id)
        tothour = int(traveltime)
        # driver_bata_set_to_zero if vehicletransbydriver=0
        if int(jsondata.vehicletransbydriver)==0:
            data = {
                "driverbatta": 0,
                "daysdrivereng": 0
            }
            return data
        if tothour==0:
            data = {
                "driverbatta": 0,
                "daysdrivereng": 0
            }
            return data
        day = math.ceil(tothour / 24)
        service=Driver_bata(self._scope())
        designation = service.get_designation(grades)
        service=Tour_allowance(self._scope())
        if jsondata.tourgid is not None:
            tourgid = jsondata.tourgid
            out_data = service.elig_citytoamount(designation, "driverbata", expensegid, tourgid)
        # else:
        #     out_data = service.elig_citytoamount_tmp( designation, "driverbata", expensegid)
        if out_data != []:
            if day == 1:
                data = {
                    "driverbatta": out_data[0].amount,
                    "daysdrivereng": day
                }
                return data
            else:
                data = {
                    "driverbatta": out_data[0].amount + out_data[0].amount,
                    "daysdrivereng": day
                }
                return data
        else:
            return 0


        # total=0
        # list={}
        # max_ton=grade.maxtonnage
        # list["max_tonnage"] = max_ton
        # if data.totaldisttrans is not None:
        #     service=Packing_moving_ser()
        #     packing_amount=service.packing_moving_amount(data,grade)
        #     packing_amount=float(packing_amount)
        # else:
        #     packing_amount=0
        # total+=packing_amount
        # list["packing_amount"]=packing_amount
        #
        #
        # if data.traveltime is not None:
        #     service = Driver_bata()
        #     designation = service.get_designation(data.salarygrade)
        #     data.designation = designation
        #     data.city = "driverbata"
        #     elservice = El_lod_ser()
        #     amount = elservice.get_amount(data)
        #     driver_bata = service.cal_bata(data.traveltime, amount)
        #     driver_bata=driver_bata.driverbata
        # else:
        #     driver_bata=0
        # total+=driver_bata
        # list["driver_bata"]=driver_bata
        #
        # if data.receipt_loss is not None:
        #     bata_service = Driver_bata()
        #     designation = bata_service.get_designation(data.salarygrade)
        #     data.designation = designation
        #     data.city = "Lumpsum"
        #     brk_service = Breakage_amount_ser()
        #     breakage_amount = brk_service.get_breakage_amount(data)
        # else:
        #     breakage_amount=0
        # total+=breakage_amount
        # list["breakage_amount"]=breakage_amount
        # list["total_amount"]=breakage_amount+driver_bata+packing_amount
        # return json.dumps(list)
