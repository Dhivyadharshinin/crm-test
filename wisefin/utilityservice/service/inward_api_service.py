import json

from docservice.service.documentservice import DocumentsService
from masterservice.service.channelservice import ChannelService
from masterservice.service.courierservice import CourierService
from masterservice.service.documenttypeservice import DocumenttypeService
from nwisefin.settings import logger
from userservice.service import employeeservice
from userservice.service.branchservice import EmployeeBranchService
from userservice.service.departmentservice import DepartmentService
from userservice.service.employeeservice import EmployeeService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from wisefinapi.docservapi import DocAPI
from wisefinapi.employeeapi import EmployeeAPI
from wisefinapi.masterapi import MasterAPI


class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    MICRO_SERVICE = True

#user
    def get_emp_id(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(emp_id)
            print('get_emp_id serv',emp)
            emp=emp.__dict__
            emp['name']=emp['full_name']
            print('get_emp_id',emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, emp_id)
            print('get_emp_id api',emp)
            return emp

    def fetch_employeebranchdata(self, request, empbr_id):
        if self.MICRO_SERVICE:
            pose_ser = EmployeeService(self._scope())
            pose = pose_ser.fetch_empbranch(empbr_id)
            logger.info("fetch_employeebranchdata - serv" + str(pose))
            print("fetch_employeebranchdata - serv", pose)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.fetch_employeebranchdata(request, empbr_id)
            logger.info("fetch_employeebranchdata - api" + str(user_employeebranch))
            print("fetch_employeebranchdata - api", user_employeebranch)
            return user_employeebranch

    def get_courier(self, request, courier_id):
        if self.MICRO_SERVICE:
            courier_ids = {"courier_id": courier_id}
            pos_ser = CourierService(self._scope())
            pos = pos_ser.get_courier(courier_ids)
            logger.info("get_courier - serv" + str(pos))
            print("get_courier - serv", pos)
            pos = json.loads(pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_courier = master_apicall.get_courier(request, courier_id)
            logger.info("get_courier - api" + str(master_courier))
            print("get_courier - api", master_courier)
            return master_courier

    def fetch_courierdata(self, request, courier_id):
        if self.MICRO_SERVICE:
            pos_ser = CourierService(self._scope())
            pos = pos_ser.fetch_courierdata(courier_id)
            logger.info("fetch_courierdata - serv" + str(pos))
            print("fetch_courierdata - serv", pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_courier = master_apicall.fetch_courierdata(request, courier_id)
            logger.info("fetch_courier - api" + str(master_courier))
            print("fetch_courier - api", master_courier)
            return master_courier

    def get_channel(self, request, channel_id):
        if self.MICRO_SERVICE:
            channel_ids = {"channel_id": channel_id}
            pos_ser = ChannelService(self._scope())
            pos = pos_ser.get_channel(channel_ids)
            logger.info("get_channel - serv" + str(pos))
            print("get_channel - serv", pos)
            pos = json.loads(pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_channel = master_apicall.get_channel(request, channel_id)
            logger.info("get_channel - api" + str(master_channel))
            print("get_channel - api", master_channel)
            return master_channel

    def fetch_channeldata(self, request, channel_id):
        if self.MICRO_SERVICE:
            chennel_serv = ChannelService(self._scope())
            channel = chennel_serv.fetch_channeldata(channel_id)
            logger.info("fetch_channeldata - serv" + str(channel))
            print("fetch_channeldata - serv", channel)
            return channel
        else:
            master_api = MasterAPI()
            channel = master_api.fetch_channeldata(request, channel_id)
            logger.info("fetch_channeldata - api" + str(channel))
            print("fetch_channeldata - api", channel)
            return channel

    def get_doctype(self, request, doctype_id):
        if self.MICRO_SERVICE:
            doctype_ids = {"doctype_id": doctype_id}
            doc_ser = DocumenttypeService(self._scope())
            pos = doc_ser.get_doctype(doctype_ids)
            logger.info("get_doctype - serv" + str(pos))
            print("get_doctype - serv", pos)
            pos = json.loads(pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_doctype = master_apicall.get_doctype(request, doctype_id)
            logger.info("get_courier - api" + str(master_doctype))
            print("get_courier - api", master_doctype)
            return master_doctype


    def fetch_doctypedata(self, request, doctype_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumenttypeService(self._scope())
            pos = doc_ser.fetch_doctypedata(doctype_id)
            logger.info("fetch_doctypedata - serv" + str(pos))
            print("fetch_doctypedata - serv", pos)
            return pos
        else:
            master_apicall = MasterAPI()
            master_doctype = master_apicall.fetch_doctypedata(request, doctype_id)
            logger.info("fetch_doctypedata - api" + str(master_doctype))
            print("fetch_doctypedata - api", master_doctype)
            return master_doctype

    def get_employee(self, request, employee_id):
        if self.MICRO_SERVICE:
            employee_ids = {"employee_id": employee_id}
            po_ser = EmployeeService(self._scope())
            po = po_ser.employee_get(employee_ids)
            logger.info("get_employee - serv" + str(po))
            print("get_employee - serv", po)
            po = json.loads(po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.get_employee_data(request, employee_id)
            logger.info("get_employee - api" + str(po))
            print('get_employee - api', po)
            return po


    def fetch_employeedata(self, request, employee_id):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService(self._scope())
            po = po_ser.fetch_employeedata(employee_id)
            logger.info("fetch_employeedata - serv" + str(po))
            print("fetch_employeedata serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.fetch_employeedata(request, employee_id)
            logger.info("fetch_employeedata - api" + str(po))
            print("fetch_employeedata - api", po)
            return po

    def fetch_emp_ebranchdata(self, request, employee_id):
        if self.MICRO_SERVICE:
            po_ser = EmployeeService(self._scope())
            po = po_ser.fetch_employeedata(employee_id)
            logger.info("fetch_emp_ebranchdata - serv" + str(po))
            print("fetch_emp_ebranchdata - serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.fetch_emp_ebranchdata(request, employee_id)
            logger.info("fetch_emp_ebranchdata - api" + str(po))
            print("fetch_emp_ebranchdata - api", po)
            return po

    def fetch_branch(self, request, employeebranch_id):
        if self.MICRO_SERVICE:
            empbr_ser = EmployeeBranchService(self._scope())
            empbr = empbr_ser.fetch_branch_using_code(employeebranch_id)
            logger.info("fetch_branch - serv")
            # print('get_branch serv', empbr)
            print("fetch_branch - serv", empbr)
            # empbr = empbr.__dict__
            # # empbr['code'] = empbr['code']
            # print('get_branch', empbr)
            empbr = json.loads(empbr)
            return empbr
        else:
            emp_api = EmployeeAPI()
            empbr = emp_api.fetch_employee_branch(request, employeebranch_id)
            logger.info("fetch_branch - api" + str(empbr))
            # print("get_branch", empbr)
            print("fetch_branch", empbr)
            return empbr

    def doc_upload(self, request, module_id):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.document_upload(request, module_id)
            print("doc_upload serv ", p)
            logger.info("doc_upload serv " + str(p))
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_module(request, module_id)
            print("doc_module", doc_module)
            params = doc_module
            #s3 bucket
            document_uploadbucket = vendor_apicall.document_uploadbucket(request, params)
            print("document_uploadbucket", document_uploadbucket)
            document_uploadbucket=json.loads(document_uploadbucket.get())
            #doc
            doc_upload = vendor_apicall.doc_upload(request, document_uploadbucket)
            print("doc_upload", doc_upload)
            return doc_upload

    def get_emp_by_userid_queryparams(self, request, emp_id):
        if self.MICRO_SERVICE:
            emp_ser = employeeservice.EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(emp_id)
            logger.info("get_emp_by_userid_queryparams - serv" + str(emp))
            print("get_emp_by_userid_queryparams - serv", emp)
            emp = emp.__dict__
            emp['name']=emp['full_name']
            print('get_emp_by_userid_queryparams data',emp)
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid_queryparams(request, emp_id)
            logger.info("get_emp_by_userid_queryparams - api" + str(emp))
            print('get_emp_by_userid_queryparams - api', emp)
            return emp

    def download_m2m_queryparams(self, request, file_id, emp_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService(self._scope())
            doc = doc_ser.download(file_id, emp_id)
            print("download_m2m_queryparams serv ", doc)
            logger.info("download_m2m_queryparams serv " + str(doc))
            return doc
        else:
            doc_apicall = DocAPI()
            download_m2m = doc_apicall.download_m2m_queryparams(request, file_id)
            print("download_m2m_queryparams", download_m2m)
            logger.info("download_m2m_queryparams api " + str(download_m2m))
            #doc doc_download
            doc_download = doc_apicall.doc_download(download_m2m)
            print("download_m2m_queryparams", doc_download)
            logger.info("download_m2m_queryparams api " + str(doc_download))
            return doc_download


    def doc_upload_key(self, request, module_id, filekey):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.document_upload_key(request, module_id, filekey)
            logger.info("doc_upload_key - serv" + str(p))
            print("doc_upload_key - serv", p)
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_module(request, module_id)
            print("doc_module api ", doc_module)
            logger.info("doc_module api "+ str(doc_module))
            params = doc_module
            #s3 bucket
            doc_upload_key = vendor_apicall.document_uploadbucket_key(request, params, filekey)
            print("document_uploadbucket_key api ", doc_upload_key)
            logger.info("document_uploadbucket_key api " + str(doc_module))
            doc_upload_key=json.loads(doc_upload_key.get())
            logger.info("document_uploadbucket_key" +str(doc_upload_key))
            #doc
            doc_tableupload = vendor_apicall.doc_upload(request, doc_upload_key)
            print("doc_tableupload api ", doc_tableupload)
            logger.info("doc_tableupload api " + str(doc_tableupload))
            return doc_tableupload


    def get_employeebranch(self, request, branch_id):
        if self.MICRO_SERVICE:
            branch_ids = {"employeebranch_id": branch_id}
            pose_ser = EmployeeService(self._scope())
            pose = pose_ser.employeebranch_get(branch_ids)
            logger.info("get_employeebranch - serv" + str(pose))
            print("get_employeebranch - serv", pose)
            pose = json.loads(pose)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.get_empolyeebranch_data(request, branch_id)
            logger.info("get_employeebranch - api" + str(user_employeebranch))
            print("user_employeebranch - api", user_employeebranch)
            return user_employeebranch


    def get_department(self, request, branch_id):
        if self.MICRO_SERVICE:
            branch_ids = {"dept_id": branch_id}
            pose_ser = DepartmentService(self._scope())
            pose = pose_ser.department_get(branch_ids)
            logger.info("get_employeebranch - serv" + str(pose))
            print("get_employeebranch - serv", pose)
            pose = json.loads(pose)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.department_get(request, branch_id)
            logger.info("get_employeebranch - api" + str(user_employeebranch))
            print("user_employeebranch - api", user_employeebranch)
            return user_employeebranch

    def fetch_departmentdata(self, request, department_id):
        if self.MICRO_SERVICE:
            po_ser = DepartmentService(self._scope())
            po = po_ser.fetch_departmentdata(department_id)
            logger.info("fetch_departmentdata - serv" + str(po))
            print("fetch_departmentdata serv", po)
            return po
        else:
            emp_api = EmployeeAPI()
            po = emp_api.fetch_departmentdata(request, department_id)
            logger.info("fetch_departmentdata - api" + str(po))
            print("fetch_departmentdata - api", po)
            return po


    def download_m2m(self, request, file_id, emp_id):
        if self.MICRO_SERVICE:
            doc_ser = DocumentsService(self._scope())
            doc = doc_ser.download(file_id, emp_id)
            print("download_m2m serv ", doc)
            logger.info("download_m2m serv " + str(doc))
            return doc
        else:
            doc_apicall = DocAPI()
            download_m2m = doc_apicall.download_m2m(request, file_id)
            print("download_m2m  api", download_m2m)
            logger.info("download_m2m api " + str(download_m2m))
            #doc doc_download
            doc_download = doc_apicall.doc_download(download_m2m)
            print("doc_download", doc_download)
            logger.info("doc_download api " + str(doc_download))
            return doc_download


    def file_get(self, request, module_id, file_id):
        if self.MICRO_SERVICE:
            p_ser = DocumentsService(self._scope())
            p = p_ser.file_get(module_id, file_id)
            logger.info("doc_upload_key - serv" + str(p))
            print("doc_upload_key - serv", p)
            p = json.loads(p.get())
            return p
        else:
            vendor_apicall = DocAPI()
            #module, prefix
            doc_module = vendor_apicall.doc_module(request, module_id)
            print("doc_module api ", doc_module)
            logger.info("doc_module api "+ str(doc_module))
            params = doc_module
            filekey = None
            #s3 bucket
            doc_upload_key = vendor_apicall.document_uploadbucket_key(request, params, filekey)
            print("document_uploadbucket_key api ", doc_upload_key)
            logger.info("document_uploadbucket_key api " + str(doc_module))
            doc_upload_key=json.loads(doc_upload_key.get())
            logger.info("document_uploadbucket_key" +str(doc_upload_key))
            #doc
            doc_tableupload = vendor_apicall.doc_upload(request, doc_upload_key)
            print("doc_tableupload api ", doc_tableupload)
            logger.info("doc_tableupload api " + str(doc_tableupload))
            return doc_tableupload