from taservice.models import Holidaydeim, Holiday
from django.utils import timezone
from django.db import IntegrityError
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from taservice.data.response.holidaydeim_resp import Holidaydeim_resp
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.db.models import Q
from taservice.data.request.holidaydeim import Holidaydeim_req
from taservice.util.ta_util import Filterstatus
from datetime import datetime, timedelta

# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
class HolidayDeim(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_hol_deim(self,request_obj,employee_id):
        for dtl in request_obj:
            data = Holidaydeim_req(dtl)
            if data.id is not None:
                try:
                    hol_deim=Holidaydeim.objects.using(self._current_app_schema()).filter(id=data.id,entity_id=self._entity_id()).update(
                        salarygrade=data.get_salarygrade(),city=data.get_city(),
                        amount=data.get_amount(),applicableto=data.get_applicableto(),
                        entity=data.get_entity(),
                        updated_by=employee_id,
                        updated_date=timezone.now())


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
                # except Holidaydeim.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj

            else:
                try:
                    hol_deim=Holidaydeim.objects.using(self._current_app_schema()).create(city=data.get_city(),salarygrade=data.get_salarygrade(),
                                                        amount=data.get_amount(), applicableto=data.get_applicableto(),
                                                         entity=data.get_entity(),
                                                        created_by=employee_id,entity_id=self._entity_id())


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
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj


        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def get_hol_deim(self):
        hol_deim = Holidaydeim.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()
        user_list_data = NWisefinList()
        for user in hol_deim:
            holiday=Holidaydeim_resp()
            holiday.set_id(user.id)
            holiday.set_salarygrade(user.salarygrade)
            holiday.set_city(user.city)
            holiday.set_amount(user.amount)
            holiday.set_applicableto(user.applicableto)
            holiday.set_status(user.status)
            holiday.set_entity(user.entity)
            user_list_data.append(holiday)
        return user_list_data


    def fetch_hol_deim(self,id):
        condition = Q(status=Filterstatus.one,entity_id=self._entity_id())
        if id is not None:
            condition &= Q(id=id)

        user = Holidaydeim.objects.using(self._current_app_schema()).get(condition)
        holiday = Holidaydeim_resp()
        holiday.set_id(user.id)
        holiday.set_salarygrade(user.salarygrade)
        holiday.set_city(user.city)
        holiday.set_amount(user.amount)
        holiday.set_applicableto(user.applicableto)
        holiday.set_entity(user.entity)
        return holiday

    def deleteid(self,id):
        try:
            adr = Holidaydeim.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).delete()
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        # except Holidaydeim.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj

    # def Holiday_check(self,sdate,edate):
    #     startingdate = (datetime.strptime(str(sdate), '%Y-%m-%d %H:%M:%S')).date()
    #     endingdate = (datetime.strptime(str(edate), '%Y-%m-%d %H:%M:%S')).date()
    #     day_count = (endingdate - startingdate).days + 1
    #     holiday=0
    #     totaldays=day_count
    #     for single_date in (startingdate + timedelta(n) for n in range(day_count)):
    #         try:
    #             # condition = Q(date__icontains=single_date)
    #             Namelist = Holiday.objects.using(self._current_app_schema()).get(date = single_date)
    #             if single_date==Namelist.date.date():
    #                 holiday+=1
    #         except:
    #             pass
    #     working_days = day_count - holiday
    #     return holiday



