from masterservice.models.mastermodels import Grade, DesignationGradeMapping
from masterservice.data.response.graderesponse import GradeResponse, DesignationGradeMappingResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.designationservice import DesignationService
from masterservice.util.masterutil import Code_Gen_Type, Code_Gen_Value,ModifyStatus
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinsuccess import SuccessMessage, NWisefinSuccess, SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from django.db.models import Q

class GradeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_grade(self,grade_req,user_id):
        update = 0
        if not grade_req.get_id() is None:
            update = 1
            Grade.objects.using(self._current_app_schema()).filter(id= grade_req.get_id(),entity_id=self._entity_id()).update(name=grade_req.get_name(),points=grade_req.get_points(),updated_by=user_id)

        else:
            grade_update = Grade.objects.using(self._current_app_schema()).create(name=grade_req.get_name(),points=grade_req.get_points(),entity_id=self._entity_id(),created_by=user_id)

            code_ger = CodeGen(self._scope())
            code = code_ger.codegenerator(Code_Gen_Type.GRADE, self._entity_id(), user_id,
                                          Code_Gen_Value.GRADE)
            grade_update.code = code
            grade_update.save()


        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)

        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def del_grade(self,id):
            grade_del=Grade.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).delete()
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.SUCCESS)
            error_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return error_obj

    def srch_grade(self,name):
        grade_srch=Grade.objects.using(self._current_app_schema()).filter(name__icontains=name,entity_id=self._entity_id())
        srch_data = NWisefinList()
        for i in grade_srch:
            srch_resp=GradeResponse()
            srch_resp.set_id(i.id)
            srch_resp.set_name(i.name)
            srch_resp.set_is_active(i.is_active)
            srch_data.append(srch_resp)
        return srch_data



    def fetchgrade(self,id):
        grade_get = Grade.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id())
        for i in grade_get:
            get_resp = GradeResponse()
            get_resp.set_id(i.id)
            get_resp.set_name(i.name)
            get_resp.set_is_active(i.is_active)
            get_resp.set_points(i.points)
            get_resp.set_code(i.code)
            return get_resp

    def summary_grade(self,vys_page,query):
        cond = Q(entity_id=self._entity_id(), status=ModifyStatus.create)
        if query != None:
            cond &= Q(name__icontains=query)
        grade_get = Grade.objects.using(self._current_app_schema()).filter(cond)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        getover_data = NWisefinList()
        for i in grade_get:
            get_resp = GradeResponse()
            get_resp.set_id(i.id)
            get_resp.set_name(i.name)
            get_resp.set_code(i.code)
            get_resp.set_is_active(i.is_active)
            get_resp.set_points(i.points)
            getover_data.append(get_resp)
        vpage = NWisefinPaginator(grade_get, vys_page.get_index(), 10)
        getover_data.set_pagination(vpage)
        return getover_data


class DesignationGradeMappingService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)
    def create_designationgrademapping(self,design_request,user_id):
       update=0
       if design_request.get_id() is not None:
           update=1
           try:
               update_data=DesignationGradeMapping.objects.using(self._current_app_schema()).filter(
                 id= design_request.get_id(),entity_id=self._entity_id()).update(
                                                                                 designation_id=design_request.get_designation_id(),
                                                                                 grade_id=design_request.get_grade_id(),
                                                                                 updated_by=user_id)
               update_data=DesignationGradeMapping.objects.using(self._current_app_schema()).get(
                       id= design_request.get_id(),entity_id=self._entity_id())
           except:
               error_obj = MessageResponse()
               error_obj.set_status(StatusType.FAILED)
               error_obj.set_message(ErrorDescription.INVALID_designation_ID)
               return error_obj
       else:
           try:
               update_data=DesignationGradeMapping.objects.using(self._current_app_schema()).create(
                                                entity_id=self._entity_id(),
                                                designation_id=design_request.get_designation_id(),
                                                grade_id=design_request.get_grade_id(),
                                                created_by=user_id)


           except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
       success_obj = MessageResponse()
       success_obj.set_status(StatusType.SUCCESS)
       if update == 1:
           success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
       else:
           success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
       return success_obj


    def summary_designationgrademapping(self):
        try:
            mapping_get=DesignationGradeMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)
            getover_data = NWisefinList()
            for i in mapping_get:
                mapping_resp=DesignationGradeMappingResponse()
                # mapping_resp.set_grade_id(i.grade_id)
                # mapping_resp.set_status(i.status)
                # mapping_resp.set_id(i.id)
                # mapping_resp.set_created_by(i.created_by)
                serv = DesignationService(self._scope())
                design_details = serv.fetch_designation(i.designation_id)
                mapping_resp.set_designation_id(design_details)
                serv = GradeService(self._scope())
                Grade_details = serv.fetchgrade(i.grade_id)
                mapping_resp.set_grade_id(Grade_details)
                getover_data.append(mapping_resp)
            return getover_data
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj


    def del_designationgrademapping(self,id):
        try:
            del_mapping=DesignationGradeMapping.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).delete()
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.SUCCESS)
            error_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return error_obj

        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj



    def fetch_designationgrademapping(self,id):
        try:
            mapping=DesignationGradeMapping.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            mapping_resp = DesignationGradeMappingResponse()
            # mapping_resp.set_grade_id(mapping.grade_id)
            mapping_resp.set_id(mapping.id)
            mapping_resp.set_status(mapping.status)
            mapping_resp.set_created_by(mapping.created_by)
            serv=DesignationService(self._scope())
            design_details=serv.fetch_designation(mapping.designation_id)
            mapping_resp.set_designation_id(design_details)
            serv=GradeService(self._scope())
            Grade_details=serv.fetchgrade(mapping.grade_id)
            mapping_resp.set_grade_id(Grade_details)
            return mapping_resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

























