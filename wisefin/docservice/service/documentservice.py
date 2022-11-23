import datetime
import traceback

from nwisefin.settings import logger
from django.http import StreamingHttpResponse, HttpResponse
from django.utils.timezone import now
import boto3
from docservice.models.docmodels import MemoDocuments, VendorDocuments, InwardDocuments, ProofingDocuments, PdDocuments, \
    PrDocuments, SgDocuments, TADocs, DtpcDocuments, FADocs, APDocuments, ReportDocuments, EcfDocuments, JVDocuments, \
    MasterDocuments, CMSDocuments, QuesDocuments, AttendanceDocuments
from docservice.data.response.documentresponse import DocumentsResponse
from docservice.util.docutil import DocModule, DocPrefix
# from pdservice.data.response.premisefileresponse import PremisefileResponse
# from pdservice.models import PremiseFiles
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.utilityservice import NWisefinUtilityService
from datetime import datetime
from django.conf import settings
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.controller.vowusercontroller import VowUser
from django.db.models import Q


class DocumentsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.DCO_SERVICE)

    def upload(self, request, params):
        if not request.FILES['file'] is None:
            try:
                logger.info("s3 starts")
                file_count = len(request.FILES.getlist('file'))
                module = params['module']
                ref_id=params['ref_id']
                ref_type=params['ref_type']
                docprefix_obj = DocPrefix()
                docmodule_obj = DocModule()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist('file')[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    file.name =file_name_new
                    contents = file
                    logger.info("s31" + str(file_name))
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file_name, document=contents,gen_file_name=file_name_new,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size, entity_id=self._entity_id())

                    logger.info("s3 document" + str(document))
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix+str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    resp_list.append(doc_data)
                    logger.info("after s3" + str(doc_data))
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')

    def fetch_documents(self, file_id, user_id,module):
        dbobj = self.get_table(module)
        document = dbobj.get(id=file_id,entity_id=self._entity_id())
        doc_resp = DocumentsResponse()
        doc_resp.set_id(document.id)
        doc_resp.set_file_name(document.file_name)
        return doc_resp


    def doc_download(self, file_id, user_id):
        try:
            doc_id = file_id
            obj_id = doc_id.split('_')[-1]
            module_split = doc_id.split('_')[0]
            module_prefix = module_split + '_'
            doc_module = DocModule()
            module_id = doc_module.get_prefix_modulenum_(module_prefix)
            dbobj = self.get_table(module_id)
            doc_obj = dbobj.get(id=obj_id,entity_id=self._entity_id())
            file = doc_obj.document
            file_name=doc_obj.file_name
            response = HttpResponse(file)
            response['Content-Disposition'] = 'attachments; filename="{}"'.format(file_name)
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def mail_doc_download(self, file_id, user_id):
        doc_id = file_id
        obj_id = doc_id.split('_')[-1]
        module_split = doc_id.split('_')[0]
        module_prefix = module_split + '_'
        doc_module = DocModule()
        module_id = doc_module.get_prefix_modulenum_(module_prefix)
        dbobj = self.get_table(module_id)
        doc_obj = dbobj.get(id=obj_id, entity_id=self._entity_id())
        file = doc_obj.document
        file_name = doc_obj.file_name
        # response = HttpResponse(file)
        # response['Content-Disposition'] = 'attachments; filename="{}"'.format(file_name)
        return file

    def file_view_extention(self,extension,body):
        try:
            logger.info("extension  " + str(extension)+" "+str(type(extension)))
            print("extension  " + str(extension)+ " "+str(type(extension)))

            if extension == 'PDF' or extension == 'pdf':
                logger.info("PDF WORKING")
                print("PDF WORKING")
                return StreamingHttpResponse(body, content_type='application/pdf')
            elif extension == 'JPEG' or extension == 'jpeg' or extension == 'JPG'  or extension == 'jpg':
                logger.info("JPEG WORKING")
                print("JPEG WORKING")
                return StreamingHttpResponse(body, content_type='image/jpeg')
            elif extension == 'PNG' or extension == 'png' :
                logger.info("PNG WORKING")
                print("PNG WORKING")
                return StreamingHttpResponse(body, content_type='image/png')
            elif extension == 'TIFF' or extension == 'tiff' or extension == 'TIF'  or extension == 'tif':
                return StreamingHttpResponse(body, content_type='image/tiff')
            else:
                logger.info("Else WORKING" + "application/octet-stream")
                print("else WORKING","application/octet-stream")
                return StreamingHttpResponse(body, content_type='application/octet-stream')
        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(ex))
            return error_obj


    def get_fileinfo(self, array_data, module):
        resp_list = NWisefinList()
        for file_id in array_data:
            dbobj = self.get_table(module)
            document = dbobj.get(id=file_id,entity_id=self._entity_id())
            doc_resp = DocumentsResponse()
            doc_resp.set_id(document.id)
            doc_resp.set_file_name(document.file_name)
            doc_resp.set_size(document.size)
            resp_list.append(doc_resp)
        return resp_list

    def get_file_info_by_reltype(self,departmentdocumentid,rel_type,module):
        arr=[]
        dbobj = self.get_table(module)
        document = dbobj.filter(Q(rel_id__in=departmentdocumentid) & Q(rel_type=rel_type))
        for i in document:
            doc_resp = DocumentsResponse()
            doc_resp.set_id(i.id)
            doc_resp.set_file_name(i.file_name)
            doc_resp.set_rel_id(i.rel_id)
            arr.append(doc_resp)
        return arr

    def get_table(self, module):
        if module == DocModule.MEMO:
            return MemoDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.VENDOR:
            return VendorDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.INWARD:
            return InwardDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.PROOFING:
            return ProofingDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.PD:
            return PdDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.PR:
            return PrDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.SG:
            return SgDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.DTPC:
            return DtpcDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.TA:
            return TADocs.objects.using(self._current_app_schema())
        elif module == DocModule.FA:
            return FADocs.objects.using(self._current_app_schema())
        elif module == DocModule.AP:
            return APDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.ECF:
            return EcfDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.REPORT:
            return ReportDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.JV:
            return JVDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.MASTER:
            return MasterDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.CMS:
            return CMSDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.QUES:
            return QuesDocuments.objects.using(self._current_app_schema())
        elif module == DocModule.ATD:
            return AttendanceDocuments.objects.using(self._current_app_schema())

    def delete_document(self, file_id, user_id):
        module=file_id
        logger.info(str(file_id))
        file_id = file_id.split('_')[-1]
        module_split = module.split('_')[0]
        module_prefix = module_split + '_'
        doc_module = DocModule()
        module = doc_module.get_prefix_modulenum_(module_prefix)
        dbobj = self.get_table(module)
        doc_obj = dbobj.get(id=file_id)
        gen_file_name = doc_obj.gen_file_name
        docdel_obj = dbobj.get(id=file_id).delete()
        if docdel_obj[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOC_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOC_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def upload_single_doc(self, file, params):
        try:
            module = params['module']
            ref_id = params['ref_id']
            ref_type = params['ref_type']
            docprefix_obj = DocPrefix()
            prefix = docprefix_obj.get_prefix(module)
            file_name = file.name
            file_size = file.size
            file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
            file.name = file_name_new
            contents = file
            dbobj = self.get_table(module)
            document = dbobj.create(file_name=file_name, document=contents, gen_file_name=file_name_new,
                                    rel_id=ref_id, rel_type=ref_type, size=file_size, entity_id=self._entity_id())
            doc_data = DocumentsResponse()
            doc_data.set_id(prefix + str(document.id))
            doc_data.set_file_name(document.file_name)
            doc_data.set_gen_file_name(document.gen_file_name)
            return doc_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def document_upload_ta(self, request, module,ta_id):
        if not request.FILES['file'] is None:
            try:
                file_count = len(request.FILES.getlist('file'))
                module = module
                # ref_id = params
                ref_type = module
                docprefix_obj = DocPrefix()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist('file')[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    s3 = boto3.resource('s3')
                    s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
                    s3_obj.put(Body=contents)
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new,
                                            rel_id=ta_id, rel_type=ref_type, size=file_size, entity_id=self._entity_id())
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ta_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')
    def doc_upload_ta(self, request, params):
        try:
            arr = params['data']
            resp_list = NWisefinList()
            for params in arr:
                rel_id = params['rel_id']
                rel_type = params['rel_type']
                prefix = params['prefix']
                file_name = params['file_name']
                gen_file_name = params['gen_file_name']
                file_size = params['size']
                dbobj = self.get_table(int(rel_type))
                document = dbobj.create(file_name=file_name, gen_file_name=gen_file_name,
                                        rel_id=rel_id, rel_type=rel_type, size=file_size, entity_id=self._entity_id())
                doc_data = DocumentsResponse()
                doc_data.set_id(prefix + str(document.id))
                doc_data.set_file_name(document.file_name)
                doc_data.set_gen_file_name(document.gen_file_name)
                doc_data.rel_id = rel_id
                doc_data.rel_type = rel_id
                doc_data.size = file_size
                resp_list.append(doc_data)
                logger.info('uploaded file :' + str(file_name))
                print("uploaded file :", file_name)
            return resp_list
        except KeyError:
            logger.info('Kindly pass det file information')


    def document_upload_ecf(self, request, params, x):
        if not request.FILES[x] is None:
            try:
                file_count = len(request.FILES.getlist(x))
                module = params
                ref_id = params
                ref_type = params
                docprefix_obj = DocPrefix()
                docmodule_obj = DocModule()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist(x)[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    logger.info("s31" + str(file_name))
                    # s3 = boto3.resource('s3')
                    # s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
                    # s3_obj.put(Body=contents)
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new,document=contents,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size,entity_id=self._entity_id())
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ref_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list
            except KeyError:
                logger.info('Kindly pass det file information')

    def document_upload_ap(self, request, params, x):
        if not request.FILES[x] is None:
                file_count = len(request.FILES.getlist(x))
                print('file_count ',file_count)
                module = params
                ref_id = params
                ref_type = params
                docprefix_obj = DocPrefix()

                prefix = docprefix_obj.get_prefix(module)
                print('module ',module)
                print('prefix ',prefix)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist(x)[i]
                    file_name = file.name
                    file_size = file.size
                    print('file ', file)
                    print('file_name ', file_name)
                    print('file_size ', file_size)
                    logger.info('file ',file)
                    logger.info('file_name ',file_name)
                    logger.info('file_size ', file_size)
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    logger.info("file_name" + str(file_name))
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new, document=contents,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size,
                                            entity_id=self._entity_id())
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ref_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list


    def download(self, file_id, user_id):
        module = file_id
        file_id = file_id.split('_')[-1]
        module_split = module.split('_')[0]
        module_prefix = module_split + '_'
        doc_module = DocModule()
        module = doc_module.get_prefix_modulenum_(module_prefix)
        dbobj = self.get_table(module)
        doc_obj = dbobj.get(id=file_id)
        file_name = doc_obj.file_name
        gen_file_name = doc_obj.gen_file_name
        s3 = boto3.resource('s3')
        s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=gen_file_name)
        body = s3_obj.get()['Body']
        extension=file_name.split('.')[-1]
        response = self.file_view_extention(extension,body)
        response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        return response

    def document_upload_key(self, request, params, x):
        if not request.FILES[x] is None:
            try:
                file_count = len(request.FILES.getlist(x))
                module = params
                ref_id = params
                ref_type = params
                docprefix_obj = DocPrefix()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist(x)[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    # s3 = boto3.resource('s3')
                    # s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
                    # s3_obj.put(Body=contents)
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size,
                                            document=contents, entity_id=self._entity_id())
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ref_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')

    # inward & vendor file view
    def file_download(self, file_id, user_id):
        #try:
            doc_id = file_id
            obj_id = doc_id.split('_')[-1]
            module_split = doc_id.split('_')[0]
            module_prefix = module_split + '_'
            doc_module = DocModule()
            module_id = doc_module.get_prefix_modulenum_(module_prefix)
            dbobj = self.get_table(module_id)
            doc_obj = dbobj.get(id=obj_id, entity_id=self._entity_id())
            file = doc_obj.document
            file_name = doc_obj.file_name
            logger.info("view file" + str(file_name))
            contentType = file_name.split('.')[-1]
            response = HttpResponse(file)
            response['Content-Disposition'] = 'attachments; filename="{}"'.format(file_name)
            doc_view = self.file_view_extention(contentType, response)
            return doc_view
        # except Exception as ex:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(str(ex))
        #     return error_obj
    def file_get(self, params, file_id):
        try:
            module = params
            dbobj = self.get_table(module)
            doc_obj = dbobj.get(id=file_id)
            doc_data = DocumentsResponse()
            doc_data.set_id(doc_obj.id)
            doc_data.set_file_name(doc_obj.file_name)
            doc_data.set_gen_file_name(doc_obj.gen_file_name)
            return doc_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def upload_single_Doc_Report(self, file, params):
        try:
            module = params['module']
            ref_id = params['ref_id']
            ref_type = params['ref_type']
            docprefix_obj = DocPrefix()
            prefix = docprefix_obj.get_prefix(module)
            file_name = file.name
            file_size = file.size
            file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
            file.name = file_name_new
            contents = file
            dbobj = self.get_table(module)
            document = dbobj.create(file_name=file_name, document=contents.name, gen_file_name=file_name_new,
                                    rel_id=ref_id, rel_type=ref_type, size=file_size, entity_id=self._entity_id())
            document.save()
            doc_data = DocumentsResponse()
            doc_data.set_id(prefix + str(document.id))
            doc_data.set_file_name(document.file_name)
            doc_data.set_gen_file_name(document.gen_file_name)
            return doc_data
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def multiple_upload(self, request, params, attachment):
        if not request.FILES[attachment] is None:
            try:
                logger.info("s3 starts")
                file_count = len(request.FILES.getlist(attachment))
                module = params['module']
                ref_id = params['ref_id']
                ref_type = params['ref_type']
                print(module)
                docprefix_obj = DocPrefix()
                docmodule_obj = DocModule()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist(attachment)[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    file.name = file_name_new
                    contents = file
                    logger.info("s31" + str(file_name))
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file_name, document=contents, gen_file_name=file_name_new,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size,
                                            entity_id=self._entity_id())

                    logger.info("s3 document" + str(document))
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    resp_list.append(doc_data)
                    logger.info("after s3" + str(doc_data))
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')

    def document_upload_by_reftype(self, request, params, x):
        if not request.FILES[x] is None:
            try:
                file_count = len(request.FILES.getlist(x))
                module = params['module']
                ref_id = params['ref_id']
                ref_type = params['ref_type']
                docprefix_obj = DocPrefix()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = []
                for i in range(0, file_count):
                    file = request.FILES.getlist(x)[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new,document=contents, rel_id=ref_id, rel_type=ref_type, size=file_size,entity_id=self._entity_id())
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ref_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list
            except KeyError:
                logger.info('Kindly pass det file information')

    def content_upload(self, file_name, params, content):
        logger.info("before content_upload" + str(params))
        module = params['module']
        ref_id = params['ref_id']
        ref_type = params['ref_type']
        txt = '.txt'
        contents = content + str(txt)
        dbobj = self.get_table(module)
        document = dbobj.create(file_name=file_name, document=contents, gen_file_name=file_name,rel_id=ref_id, rel_type=ref_type, entity_id=self._entity_id())
        logger.info("after content_upload" + str(document.id))
        print("after content_upload", document.id)
        return True


class VowDocumentsService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']


    def upload(self, request, params):
        if not request.FILES['file'] is None:
            try:
                logger.info("s3 starts")
                file_count = len(request.FILES.getlist('file'))
                module = params['module']
                ref_id=params['ref_id']
                ref_type=params['ref_type']
                docprefix_obj = DocPrefix()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist('file')[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    file.name =file_name_new
                    contents = file
                    logger.info("s31" + str(file_name))
                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file_name, document=contents,gen_file_name=file_name_new,rel_id=ref_id, rel_type=ref_type, size=file_size, entity_id=self.entity_id)

                    logger.info("s3 document" + str(document))
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix+str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    resp_list.append(doc_data)
                    logger.info("after s3" + str(doc_data))
                return resp_list
            except KeyError:
                logger.info('Kindly pass file information')

    def get_table(self, module):
        if module == DocModule.MEMO:
            return MemoDocuments.objects.using(self.schema)
        elif module == DocModule.VENDOR:
            return VendorDocuments.objects.using(self.schema)
        elif module == DocModule.INWARD:
            return InwardDocuments.objects.using(self.schema)
        elif module == DocModule.PROOFING:
            return ProofingDocuments.objects.using(self.schema)
        elif module == DocModule.PD:
            return PdDocuments.objects.using(self.schema)
        elif module == DocModule.PR:
            return PrDocuments.objects.using(self.schema)
        elif module == DocModule.SG:
            return SgDocuments.objects.using(self.schema)
        elif module == DocModule.DTPC:
            return DtpcDocuments.objects.using(self.schema)
        elif module == DocModule.TA:
            return TADocs.objects.using(self.schema)
        elif module == DocModule.FA:
            return FADocs.objects.using(self.schema)
        elif module == DocModule.AP:
            return APDocuments.objects.using(self.schema)
        elif module == DocModule.ECF:
            return EcfDocuments.objects.using(self.schema)
        elif module == DocModule.REPORT:
            return ReportDocuments.objects.using(self.schema)
        elif module == DocModule.JV:
            return JVDocuments.objects.using(self.schema)
        elif module == DocModule.MASTER:
            return MasterDocuments.objects.using(self.schema)
        elif module == DocModule.CMS:
            return CMSDocuments.objects.using(self.schema)
        elif module == DocModule.ATD:
            return AttendanceDocuments.objects.using(self.schema)

    def content_upload(self, file_name, params, content):
        logger.info("before content_upload" + str(params))
        module = params['module']
        ref_id = params['ref_id']
        ref_type = params['ref_type']
        txt = '.txt'
        contents = content + str(txt)
        dbobj = self.get_table(module)
        document = dbobj.create(file_name=file_name, document=contents, gen_file_name=file_name,rel_id=ref_id, rel_type=ref_type, entity_id=self.entity_id)

        logger.info("after content_upload" + str(document.id))
        return True

    def vow_doc_download(self, file_id):
        try:
            doc_id = file_id
            obj_id = doc_id.split('_')[-1]
            module_split = doc_id.split('_')[0]
            module_prefix = module_split + '_'
            doc_module = DocModule()
            module_id = doc_module.get_prefix_modulenum_(module_prefix)
            dbobj = self.get_table(module_id)
            doc_obj = dbobj.get(id=obj_id)
            file = doc_obj.document
            file_name = doc_obj.file_name
            response = HttpResponse(file)
            response['Content-Disposition'] = 'attachments; filename="{}"'.format(file_name)
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def vow_document_upload_key(self, request, params, x):
        try:
            if not request.FILES[x] is None:
                file_count = len(request.FILES.getlist(x))
                module = params['module']
                ref_id = params['ref_id']
                ref_type = params['ref_type']
                docprefix_obj = DocPrefix()
                prefix = docprefix_obj.get_prefix(module)
                resp_list = NWisefinList()
                for i in range(0, file_count):
                    file = request.FILES.getlist(x)[i]
                    file_name = file.name
                    file_size = file.size
                    file_name_new = prefix + str(datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    contents = file

                    dbobj = self.get_table(module)
                    document = dbobj.create(file_name=file.name, gen_file_name=file_name_new,
                                            rel_id=ref_id, rel_type=ref_type, size=file_size,
                                            document=contents, entity_id=self.entity_id)
                    doc_data = DocumentsResponse()
                    doc_data.set_id(prefix + str(document.id))
                    doc_data.set_file_name(document.file_name)
                    doc_data.set_gen_file_name(document.gen_file_name)
                    doc_data.rel_id = ref_id
                    doc_data.rel_type = ref_type
                    doc_data.size = file_size
                    resp_list.append(doc_data)
                    logger.info('uploaded file :' + str(file_name))
                    print("uploaded file :", file_name)
                return resp_list
        except KeyError:
            logger.info('Kindly pass file information')