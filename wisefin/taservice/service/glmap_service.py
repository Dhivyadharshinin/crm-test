from taservice.models import Glmapping
from django.utils import timezone
from django.db import IntegrityError
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage,ErrorDescription
from taservice.data.response.glmap_res import Glmap_res
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.db.models import Q
from taservice.data.request.glmap_req import Glmap_req
from taservice.util.ta_util import Filterstatus
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

class Glmap_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_glmapping(self,request_obj,employee_id):
        for dtl in request_obj:
            data = Glmap_req(dtl)
            if data.id is not None:
                try:
                    glmap=Glmapping.objects.using(self._current_app_schema()).filter(id=data.id,entity_id=self._entity_id()).update(
                            glno=data.get_glno(),gl_description=data.get_gl_description(),
                            tourreason=data.get_tourreason(),gender=data.get_gender(),
                            categorycode=data.get_categorycode(),
                            category_description=data.get_category_description(),
                            subcategorycode=data.get_subcategorycode(),
                            subcategory_description=data.get_subcategory_description(),
                            entity=data.get_entity(),
                            updated_by=employee_id,
                            updated_date=timezone.now(),entity_id=self._entity_id())



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
                # except Glmapping.DoesNotExist:
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
                    glmap=Glmapping.objects.using(self._current_app_schema()).create(
                                glno=data.get_glno(),gl_description=data.get_gl_description(),
                                tourreason=data.get_tourreason(),gender=data.get_gender(),
                                categorycode=data.get_categorycode(),
                                category_description=data.get_category_description(),
                                subcategorycode=data.get_subcategorycode(),
                                subcategory_description=data.get_subcategory_description(),
                                entity=data.get_entity(),created_by=employee_id,entity_id=self._entity_id())



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


    def get_glmapping(self):
        list=Glmapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()
        arr=NWisefinList()
        for gl_id in list:
            glmap_res=Glmap_res()
            glmap_res.set_id(gl_id.id)
            glmap_res.set_glno(gl_id.glno)
            glmap_res.set_tourreason(gl_id.tourreason)
            glmap_res.set_gender(gl_id.gender)
            glmap_res.set_categorycode(gl_id.categorycode)
            glmap_res.set_gl_description(gl_id.gl_description)
            glmap_res.set_category_description(gl_id.category_description)
            glmap_res.set_subcategorycode(gl_id.subcategorycode)
            glmap_res.set_subcategory_description(gl_id.subcategory_description)
            glmap_res.set_status(gl_id.status)
            glmap_res.set_entity(gl_id.entity)
            arr.append(glmap_res)
        return arr


    def fetch_glmapping(self,fetch_id):
        condition = Q(status=Filterstatus.one,id=fetch_id,entity_id=self._entity_id())

        gl_id = Glmapping.objects.using(self._current_app_schema()).get(condition)

        glmap_res=Glmap_res()
        glmap_res.set_id(gl_id.id)
        glmap_res.set_glno(gl_id.glno)
        glmap_res.set_gl_description(gl_id.gl_description)
        glmap_res.set_tourreason(gl_id.tourreason)
        glmap_res.set_gender(gl_id.gender)
        glmap_res.set_categorycode(gl_id.categorycode)
        glmap_res.set_category_description(gl_id.category_description)
        glmap_res.set_subcategorycode(gl_id.subcategorycode)
        glmap_res.set_subcategory_description(gl_id.subcategory_description)
        glmap_res.set_status(gl_id.status)
        glmap_res.set_entity(gl_id.entity)

        return glmap_res

    def glmapping_get(self,description,reason,gender):
        condition = Q(status=Filterstatus.one,gl_description=description,tourreason=reason,gender=gender,entity_id=self._entity_id())
        gl_id = Glmapping.objects.using(self._current_app_schema()).get(condition)
        glmap_res=Glmap_res()
        glmap_res.set_id(gl_id.id)
        glmap_res.set_glno(gl_id.glno)
        glmap_res.set_categorycode(gl_id.categorycode)
        glmap_res.set_category_description(gl_id.category_description)
        glmap_res.set_subcategorycode(gl_id.subcategorycode)
        glmap_res.set_subcategory_description(gl_id.subcategory_description)
        glmap_res.set_entity(gl_id.entity)
        return glmap_res


    def delete_glmapping(self,id):
        try:
            adr = Glmapping.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).delete()
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        # except Glmapping.DoesNotExist:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj




