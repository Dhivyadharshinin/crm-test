from vendorservice.service.activityservice import ActivityService
from vendorservice.service.questionanswerservice import QuestionanswerService
from wisefinapi.employeeapi import EmployeeAPI
from masterservice.service.vendorclassficationprofileservice import VendorclassficationService

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
class Vendormaster(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)
    MICRO_SERVICE = True

    def get_vendorclassfication_type_api(self,data):
        if self.MICRO_SERVICE:
            vendor_master = VendorclassficationService(self._scope())
            resp = vendor_master.get_vendorclassfication_type(data)
            return resp
        else:
            pass

    def get_vendorclassfication_doc_api(self, data,paginationdata,query):
        if self.MICRO_SERVICE:
            vendor_master = VendorclassficationService(self._scope())
            resp = vendor_master.get_vendor_documents(data,paginationdata,query)
            return resp
        else:
            pass

    def get_vendortypemapping(self,vendor_id,type_id):
        if self.MICRO_SERVICE:
            vendor_master = QuestionanswerService(self._scope())
            resp = vendor_master.answermapping(vendor_id,type_id)
            return resp
        else:
            pass

    def get_vendortypemapping1(self, vendor_id, type_id,activity_id):
        if self.MICRO_SERVICE:
            vendor_master = QuestionanswerService(self._scope())
            resp = vendor_master.answermapping1(vendor_id, type_id,activity_id)
            return resp
        else:
            pass

    def get_supplieractivity(self,data):
        if self.MICRO_SERVICE:
            vendor_master = ActivityService(self._scope())
            resp = vendor_master.activity_mapping(data)
            return resp
        else:
            pass

    def get_vendorclassfication_mapping(self,data):
        if self.MICRO_SERVICE:
            vendor_master = VendorclassficationService(self._scope())
            resp = vendor_master.get_vendorclassfication_mapping(data)
            return resp
        else:
            pass