import json
import traceback

from django.db import IntegrityError
from masterservice.models.mastermodels import MasterBusinessSegment
from django.utils import timezone
from masterservice.data.response.masterbusinesssegmentresponse import MasterBusinessSegmentresponse
from django.db.models import Q

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.util.masterutil import Code_Gen_Type, Code_Gen_Value
from masterservice.service.Codegenerator import CodeGen
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus

class MasterBusinessSegmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_masterbusinesssegment(self, masterbusiness_obj, user_id, sync=None):
        if not masterbusiness_obj.get_id() is None:
            try:
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Update Started')
                masterbusiness = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(
                    id=masterbusiness_obj.get_id(), entity_id=self._entity_id()).update(
                    name=masterbusiness_obj.get_name(), sector_id=masterbusiness_obj.get_sector(),
                    description=masterbusiness_obj.get_description(),
                    remarks=masterbusiness_obj.get_remarks(), updated_by=user_id,
                    updated_date=timezone.now()
                )
                masterbusiness = MasterBusinessSegment.objects.using(self._current_app_schema()).get(
                    id=masterbusiness_obj.get_id(), entity_id=self._entity_id())
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Update Success' + str(masterbusiness))
            except IntegrityError as error:
                logger.error('ERROR_MasterBusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except MasterBusinessSegment.DoesNotExist:
                logger.error('ERROR_MasterBusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_costcentre_ID)
                error_obj.set_description(ErrorDescription.INVALID_costcentre_ID)
                return error_obj
            except:
                logger.error('ERROR_MasterBusinessSegment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Creation Started')
                masterbusiness = MasterBusinessSegment.objects.using(self._current_app_schema()).create(
                    no=masterbusiness_obj.get_no(),
                    sector_id=masterbusiness_obj.get_sector(),
                    name=masterbusiness_obj.get_name(),
                    description=masterbusiness_obj.get_description(),
                    remarks=masterbusiness_obj.get_remarks(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                try:
                    max_cat_code = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(code__icontains='BS').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "BS" + str(new_rnsl).zfill(2)
                # if sync == None:
                #     code_gen = CodeGen(self._scope())
                #     code = code_gen.codegenerator(Code_Gen_Type.master_businesssegment, self._entity_id(), user_id,
                #                                   Code_Gen_Value.master_businesssegment)
                #     # code = "BS" + str(masterbusiness.id).zfill(4)
                # else:
                #     code = masterbusiness_obj.bscode
                no = masterbusiness.id
                masterbusiness.code = code
                masterbusiness.no = no
                masterbusiness.save()
                logger.error('MASTERBUSINESSSEGMENT: MasterBusinessSegment Creation Success' + str(masterbusiness))
            except IntegrityError as error:
                logger.error('ERROR_MasterBusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_MasterBusinessSegment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        data_obj = MasterBusinessSegmentresponse()
        data_obj.set_id(masterbusiness.id)
        data_obj.set_code(masterbusiness.code)
        data_obj.set_sector(masterbusiness.sector_id)
        data_obj.set_no(masterbusiness.no)
        data_obj.set_name(masterbusiness.name)
        data_obj.set_description(masterbusiness.description)
        data_obj.set_remarks(masterbusiness.remarks)
        # return data_obj
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data
    def fetch_master_businesssegment_search_list(self, query, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())
        if query != None:
            condition = Q(name__icontains=query)
        masterbusiness = MasterBusinessSegment.objects.using(self._current_app_schema()).filter(condition).values('id',
                                                                                                                  'name',
                                                                                                                  "code",
                                                                                                                  "sector_id",
                                                                                                                  "no",
                                                                                                                  "description",
                                                                                                                  'remarks')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(masterbusiness)
        pro_list = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for i in masterbusiness:
                data_obj = MasterBusinessSegmentresponse()
                data_obj.set_id(i["id"])
                data_obj.set_code(i["code"])
                data_obj.set_sector(i["sector_id"])
                data_obj.set_no(i["no"])
                data_obj.set_name(i["name"])
                data_obj.set_description(i["description"])
                data_obj.set_remarks(i["remarks"])
                pro_list.append(data_obj)
        vpage = NWisefinPaginator(masterbusiness, vys_page.get_index(), 10)
        pro_list.set_pagination(vpage)
        return pro_list
