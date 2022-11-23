# from django.db import IntegrityError
# from vendorservice.data.response.contacttyperesponse import contactTypeResponse
# from vysfinutility.data.error import Error
# from vysfinutility.data.error_const import ErrorMessage, ErrorDescription
# from vysfinutility.data.success import Success, SuccessStatus, SuccessMessage
# from vysfinutility.data.vysfinlist import VysfinList
# from django.utils import timezone
#
#
# class ContactTypeService:
#     def create_contacttype(self, contacttype_obj,user_id):
#         if not contacttype_obj.get_id() is None:
#             try:
#                 contacttype = ContactType.objects.filter(id=contacttype_obj.get_id()).update(code =contacttype_obj.get_code (),
#                 name  =contacttype_obj.get_name  (),remarks =contacttype_obj.get_remarks (),
#                 updated_by=user_id,updated_date=timezone.now())
#
#                 contacttype = ContactType.objects.get(id=contacttype_obj.get_id())
#             except IntegrityError as error:
#                 error_obj = Error()
#                 error_obj.set_code(ErrorMessage.INVALID_DATA)
#                 error_obj.set_description(ErrorDescription.INVALID_DATA)
#                 return error_obj
#             except ContactType.DoesNotExist:
#                 error_obj = Error()
#                 error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
#                 error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
#                 return error_obj
#             except:
#                 error_obj = Error()
#                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
#                 return error_obj
#         else:
#             try:
#                 contacttype = ContactType.objects.create(code =contacttype_obj.get_code (),
#                 name  =contacttype_obj.get_name  (),remarks =contacttype_obj.get_remarks (),
#                 created_by =user_id
#                 )
#             except IntegrityError as error:
#                 error_obj = Error()
#                 error_obj.set_code(ErrorMessage.INVALID_DATA)
#                 error_obj.set_description(ErrorDescription.INVALID_DATA)
#                 return error_obj
#             except:
#                 error_obj = Error()
#                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
#                 return error_obj
#
#         contacttype_data = contactTypeResponse()
#         contacttype_data.set_id(contacttype.id)
#         contacttype_data.set_code(contacttype.code)
#         contacttype_data.set_name(contacttype.name)
#         contacttype_data.set_remarks(contacttype.remarks)
#         return contacttype_data
#
#     def fetch_contacttype_list(self,user_id):
#         contacttypelist = ContactType.objects.all()
#         list_length = len(contacttypelist)
#         logger.info(list_length)
#         if list_length <= 0:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
#             error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
#             return error_obj
#         else:
#             contacttype_list_data = VysfinList()
#             for contacttype in contacttypelist:
#                 contacttype_data = contactTypeResponse()
#                 contacttype_data.set_id(contacttype.id)
#                 contacttype_data.set_code(contacttype.code)
#                 contacttype_data.set_name(contacttype.name)
#                 contacttype_data.set_remarks (contacttype.remarks)
#                 contacttype_list_data.append(contacttype_data)
#             return contacttype_list_data
#
#     def fetch_contacttype(self, contacttype_id,user_id):
#         try:
#             contacttype = ContactType.objects.get(id=contacttype_id)
#             contacttype_data = contactTypeResponse()
#             contacttype_data.set_id(contacttype.id)
#             contacttype_data.set_code (contacttype.code )
#             contacttype_data.set_name  (contacttype.name  )
#             contacttype_data.set_remarks (contacttype.remarks )
#             return contacttype_data
#
#         except contacttype.DoesNotExist:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
#             error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
#             return error_obj
#
#     def delete_contacttype(self, contacttype_id,user_id):
#         contacttype = ContactType.objects.filter(id=contacttype_id).delete()
#         if contacttype[0] == 0:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_contacttype_ID)
#             error_obj.set_description(ErrorDescription.INVALID_contacttype_ID)
#             return error_obj
#         else:
#             success_obj = Success()
#             success_obj.set_status(SuccessStatus.SUCCESS)
#             success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
#             return success_obj
