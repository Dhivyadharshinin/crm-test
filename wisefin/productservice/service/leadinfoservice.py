from productservice.data.response.leadinforesponse import LeadFamilyInfoResponse,LeadContactInfoResponse,BankAccountResponse,CrmAddressResponse
from productservice.models.productmodels import LeadFamilyInfo,LeadContactInfo,BankAccount,CRMAddress
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from productservice.util.product_util import ActiveStatus

class LeadDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CRM_SERVICE)
#leadfamilyinfo
    def create_leadfamilyinfo(self, data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for vals in update_arr:
                LeadFamilyInfo.objects.using(self._current_app_schema()).filter(id=vals['id']).update(**vals)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            return resp
        if len(create_arr) > 0:
            llist = [LeadFamilyInfo(**vals) for vals in create_arr]
            LeadFamilyInfo.objects.using(self._current_app_schema()).bulk_create(llist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp


    def get_leadfamilyinfo(self, lead_id):
        family_info = LeadFamilyInfo.objects.using(self._current_app_schema()).filter(lead_id=lead_id,
                                                                                  status=ActiveStatus.Active)
        leadinfo = []
        for data in family_info:
            data_resp = LeadFamilyInfoResponse()
            data_resp.set_id(data.id)
            data_resp.set_name(data.name)
            data_resp.set_relationship(data.relationship)
            data_resp.set_dob(data.dob)
            leadinfo.append(data_resp)
        return leadinfo

#leadcontactinfo
    def create_leadcontactinfo(self, data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for vals in update_arr:
                LeadContactInfo.objects.using(self._current_app_schema()).filter(id=vals['id']).update(**vals)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            return resp
        if len(create_arr) > 0:
            llist = [LeadContactInfo(**vals) for vals in create_arr]
            LeadContactInfo.objects.using(self._current_app_schema()).bulk_create(llist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp


    def get_leadcontactinfo(self, lead_id):
        contact_details = LeadContactInfo.objects.using(self._current_app_schema()).filter(lead_id=lead_id,
                                                                                  status=ActiveStatus.Active)
        contactinfo = []
        for i in contact_details:
            contact_data = LeadContactInfoResponse()
            contact_data.set_id(i.id)
            contact_data.set_c_value(i.c_value)
            contact_data.set_type(i.type)
            contactinfo.append(contact_data)
        return contactinfo

#bankaccount
    def create_bankaccount(self, data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for vals in update_arr:
                BankAccount.objects.using(self._current_app_schema()).filter(id=vals['id']).update(**vals)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            return resp
        if len(create_arr) > 0:
            llist = [BankAccount(**vals) for vals in create_arr]
            BankAccount.objects.using(self._current_app_schema()).bulk_create(llist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp

    def get_bankaccount(self, lead_id):
        bank_details = BankAccount.objects.using(self._current_app_schema()).filter(lead_id=lead_id,
                                                                               status=ActiveStatus.Active)
        bankinfo = []
        for data in bank_details:
            bank_data = BankAccountResponse()
            bank_data.set_id(data.id)
            bank_data.set_bank_id(data.bank_id)
            bank_data.set_branch_id(data.branch_id)
            bank_data.set_account_number(data.account_number)
            bank_data.set_ifsc_code(data.ifsc_code)
            bankinfo.append(bank_data)
        return bankinfo

#crmaddressinfo
    def create_crmaddress(self, data_obj):
        resp = NWisefinSuccess()
        if 'id' in data_obj:
            CRMAddress.objects.using(self._current_app_schema()).filter(id=data_obj['id']).update(**data_obj)
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            address = CRMAddress.objects.using(self._current_app_schema()).create(**data_obj)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.id = address.id
        return resp

    def get_crmaddress(self, address_arr):
        address_details = CRMAddress.objects.using(self._current_app_schema()).filter(id__in=address_arr,
                                                                               status=ActiveStatus.Active)
        addressinfo = []
        for data in address_details:
            address_data = CrmAddressResponse()
            address_data.set_id(data.id)
            address_data.set_line1(data.line1)
            address_data.set_line2(data.line2)
            address_data.set_line3(data.line3)
            address_data.set_pincode_id(data.pincode_id)
            address_data.set_city_id(data.city_id)
            address_data.set_district_id(data.district_id)
            address_data.set_state_id(data.state_id)
            addressinfo.append(address_data)
        return addressinfo

