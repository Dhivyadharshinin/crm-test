import traceback

import django

from django.db import IntegrityError
from masterservice.models import BankBranch, Pincode, City, District, State, Bank
from masterservice.data.response.back_branch_response import BankBranchResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from datetime import datetime

from vendorservice.data.response.bankbranchresponse import bank_branch_Response

now = datetime.now()
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from masterservice.service.addressservice import AddressService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.Codegenerator import CodeGen


class BankBranchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_bankbranch(self, bankbranch_obj, add_id, user_id):
        if not bankbranch_obj.get_id() is None:
            try:
                logger.error('BANKBRANCH: BankBranch Update Started')
                bankbranch_update = BankBranch.objects.using(self._current_app_schema()).filter(
                    id=bankbranch_obj.get_id(), entity_id=self._entity_id()).update(
                    # code=bankbranch_obj.get_code(),
                    ifsccode=bankbranch_obj.get_ifsccode(),
                    microcode=bankbranch_obj.get_microcode(),
                    name=bankbranch_obj.get_name(),
                    bank_id=bankbranch_obj.get_bank_id(),
                    # address_id=add_id,
                    updated_date=now,
                    updated_by=user_id)

                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_obj.get_id(),
                                                                                          entity_id=self._entity_id())
                logger.error('BANKBRANCH: BankBranch Update Success' + str(bankbranch_update))
                bankbranch_auditdata = {'id': bankbranch_obj.get_id(),
                                        # 'code':bankbranch_obj.get_code(),
                                        'ifsccode': bankbranch_obj.get_ifsccode(),
                                        'microcode': bankbranch_obj.get_microcode(),
                                        'name': bankbranch_obj.get_name(),
                                        'bank_id': bankbranch_obj.get_bank_id(),
                                        'address_id': add_id,
                                        'updated_date': now,
                                        'updated_by': user_id}
                self.audit_function(bankbranch_auditdata, user_id, bankbranch_var.id, ModifyStatus.update)
                resp = NWisefinSuccess()
                resp.set_status(SuccessStatus.SUCCESS)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
                return resp
            except IntegrityError as error:
                logger.error('ERROR_BankBranch_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except BankBranch.DoesNotExist:
                logger.error('ERROR_BankBranch_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                logger.error('ERROR_BankBranch_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('BANKBRANCH: BankBranch Creation Started')
                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).create(
                    # code=bankbranch_obj.get_code(),
                    ifsccode=bankbranch_obj.get_ifsccode(),
                    microcode=bankbranch_obj.get_microcode(),
                    name=bankbranch_obj.get_name(),
                    bank_id=bankbranch_obj.get_bank_id(),
                    address_id=add_id, created_by=user_id, entity_id=self._entity_id())

                # code =
                bankbranch_var.code = bankbranch_var.id
                bankbranch_var.save()
                self.audit_function(bankbranch_var, user_id, bankbranch_var.id, ModifyStatus.create)
                logger.error('BANKBRANCH: BankBranch Creation Success' + str(bankbranch_var))
                resp = NWisefinSuccess()
                resp.set_status(SuccessStatus.SUCCESS)
                resp.set_message(SuccessMessage.CREATE_MESSAGE)
                return resp
            except IntegrityError as error:
                logger.error('ERROR_BankBranch_Create_EXCEPT:{}'.format(traceback.print_exc()))
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_BankBranch_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj



    def fetch_bankbranch_list(self, vys_page, query):
        try:
            conditions = Q(status=1) & Q(entity_id=self._entity_id())
            if query is not None:
                conditions &= Q(name__icontains=query)
            bankbranchlist = BankBranch.objects.using(self._current_app_schema()).filter(conditions).order_by(
                'created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(bankbranchlist)
            if list_length >= 0:
                bankbranch_list_data = NWisefinList()
                for bankobj in bankbranchlist:
                    bankbranch_data = BankBranchResponse()
                    addre_serv = AddressService(self._scope())  # changed
                    bankbranch_data.set_id(bankobj.id)
                    bankbranch_data.set_code(bankobj.code)
                    bankbranch_data.set_name(bankobj.name)
                    bankbranch_data.set_ifsccode(bankobj.ifsccode)
                    bankbranch_data.set_microcode(bankobj.microcode)
                    bankbranch_data.set_bank(bankobj.bank)
                    # add_data = AddressResponse()
                    if bankobj.address_id == None:
                        # data = {'line1': '', 'line2': '', 'line3': '', 'pincode_id': '', 'district_id': '', 'city_id': '','state_id': ''}
                        # bankbranch_data.set_address_id(data)
                        # bankbranch_data.set_address(bankobj.address)
                        bankbranch_data.set_address_id(None)
                    else:
                        bankbranch_data.set_address_id(addre_serv.fetch_address(bankobj.address_id, 1))
                    # bankbranch_data.set_address(bankobj.address)
                    bankbranch_list_data.append(bankbranch_data)
                vpage = NWisefinPaginator(bankbranchlist, vys_page.get_index(), 10)
                bankbranch_list_data.set_pagination(vpage)
                return bankbranch_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
                error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
                return error_obj
        except:
            logger.error('ERROR_BankBranch_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj

    def fetch_bankbranch(self, bankbranch_id, user_id):
        try:
            bankbranch_var = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_id,
                                                                                      entity_id=self._entity_id())
            bankbranch_data = BankBranchResponse()
            addre_serv = AddressService(self._scope())  # changed
            bankbranch_data.set_id(bankbranch_var.id)
            bankbranch_data.set_code(bankbranch_var.code)
            bankbranch_data.set_name(bankbranch_var.name)
            bankbranch_data.set_ifsccode(bankbranch_var.ifsccode)
            bankbranch_data.set_microcode(bankbranch_var.microcode)
            bankbranch_data.set_bank(bankbranch_var.bank)
            if bankbranch_var.address_id == None:
                data = {'line1': '', 'line2': '', 'line3': '', 'pincode_id': '', 'district_id': '', 'city_id': '',
                        'state_id': ''}
                bankbranch_data.set_address_id(data)
                # bankbranch_data.set_address_id(None)
            else:
                bankbranch_data.set_address_id(addre_serv.fetch_address(bankbranch_var.address_id, 1))
            # bankbranch_data.set_address(bankbranch_var.address)


            return bankbranch_data
        except BankBranch.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj

    def delete_bankbranch(self, bankbranch_id, user_id):
        bankbranch_obj = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_id,
                                                                                  entity_id=self._entity_id())
        address_id = bankbranch_obj.address_id
        bankbranch = BankBranch.objects.using(self._current_app_schema()).filter(id=bankbranch_id,
                                                                                 entity_id=self._entity_id()).delete()
        self.audit_function(bankbranch, user_id, bankbranch_id, ModifyStatus.delete)

        address_service = AddressService(self._scope())  # changed
        address_service.delete_address(address_id, user_id)

        if bankbranch[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changed
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.BANK_BRANCH)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def get_addressid_bankbranch(self, bankbranch_id):
        bankbranch_obj = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_id,
                                                                                  entity_id=self._entity_id())
        address_id = bankbranch_obj.address_id
        return address_id

    def fetch_bankbranch_search(self, query, bank_id, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if query:
            condition &= Q(name__icontains=query)

        if bank_id:
            condition &= Q(bank_id=bank_id)
        # if query is None:
        bankbranchlist = BankBranch.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     condition = Q(bank_id =bank_id) &Q(name__icontains=query)
        #     bankbranchlist = BankBranch.objects.filter(condition).order_by('created_date')[
        #                  vys_page.get_offset():vys_page.get_query_limit()]

        bankbranch_list_data = NWisefinList()
        for bankobj in bankbranchlist:
            bankbranch_data = BankBranchResponse()
            bankbranch_data.set_id(bankobj.id)
            bankbranch_data.set_code(bankobj.code)
            bankbranch_data.set_name(bankobj.name)
            bankbranch_data.set_ifsccode(bankobj.ifsccode)
            bankbranch_data.set_microcode(bankobj.microcode)
            bankbranch_data.set_bank(bankobj.bank)
            bankbranch_list_data.append(bankbranch_data)
            vpage = NWisefinPaginator(bankbranchlist, vys_page.get_index(), 10)
            bankbranch_list_data.set_pagination(vpage)
        return bankbranch_list_data


    def search_ifsc(self, bankid, query, vys_page):

        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if query:
            condition &= Q(ifsccode__icontains=query)

        # if bankid:
        #     condition &= Q(bank_id=bankid)
        bankbranchlist = BankBranch.objects.using(self._current_app_schema()).filter(condition).order_by(
            'created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        bankbranch_list_data = NWisefinList()
        for bankobj in bankbranchlist:
            bankbranch_data = BankBranchResponse()
            bankbranch_data.set_id(bankobj.id)
            # bankbranch_data.set_code(bankobj.code)
            bankbranch_data.set_name(bankobj.name)
            bankbranch_data.set_ifsccode(bankobj.ifsccode)
            # bankbranch_data.set_microcode(bankobj.microcode)
            bankbranch_data.set_bank(bankobj.bank)
            bankbranch_list_data.append(bankbranch_data)
            vpage = NWisefinPaginator(bankbranchlist, vys_page.get_index(), 10)
            bankbranch_list_data.set_pagination(vpage)
        return bankbranch_list_data

    def create_bankbranch_mtom(self, bankbranch_obj, add_id, user_id):
        bank_id = Bank.objects.get(code=bankbranch_obj.get_bank_code()).id
        if not bankbranch_obj.get_id() is None:
            try:
                bankbranch_update = BankBranch.objects.using(self._current_app_schema()).filter(
                    id=bankbranch_obj.get_id(), entity_id=self._entity_id()).update(
                    code=bankbranch_obj.get_code(),
                    ifsccode=bankbranch_obj.get_ifsccode(),
                    microcode=bankbranch_obj.get_microcode(),
                    name=bankbranch_obj.get_name(),
                    bank_id=bank_id,
                    # address_id=add_id,
                    updated_date=now,
                    updated_by=user_id)

                bankbranch_var = BankBranch.objects.using(self._current_app_schema()).get(id=bankbranch_obj.get_id(),
                                                                                          entity_id=self._entity_id())
                bankbranch_auditdata = {'id': bankbranch_obj.get_id(),
                                        'code': bankbranch_obj.get_code(),
                                        'ifsccode': bankbranch_obj.get_ifsccode(),
                                        'microcode': bankbranch_obj.get_microcode(),
                                        'name': bankbranch_obj.get_name(),
                                        'bank_id': bank_id,
                                        'address_id': add_id,
                                        'updated_date': now,
                                        'updated_by': user_id}
                self.audit_function(bankbranch_auditdata, user_id, bankbranch_var.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except BankBranch.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CATEGORY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CATEGORY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            # try:
            bankbranch_var = BankBranch.objects.using(self._current_app_schema()).create(code=bankbranch_obj.get_code(),
                                                                                         ifsccode=bankbranch_obj.get_ifsccode(),
                                                                                         microcode=bankbranch_obj.get_microcode(),
                                                                                         name=bankbranch_obj.get_name(),
                                                                                         bank_id=bank_id,
                                                                                         address_id=add_id,
                                                                                         created_by=user_id,
                                                                                         entity_id=self._entity_id())

            self.audit_function(bankbranch_var, user_id, bankbranch_var.id, ModifyStatus.create)

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

        bankbranch_data = BankBranchResponse()
        bankbranch_data.set_id(bankbranch_var.id)
        bankbranch_data.set_code(bankbranch_var.code)
        bankbranch_data.set_name(bankbranch_var.name)
        bankbranch_data.set_ifsccode(bankbranch_var.ifsccode)
        bankbranch_data.set_microcode(bankbranch_var.microcode)
        bankbranch_data.set_bank_id(bankbranch_var.bank_id)
        return bankbranch_data

    def address_details_get(self, bankbranch_data):

        city_id = City.objects.using(self._current_app_schema()).get(code=bankbranch_data['city_code'],
                                                                     entity_id=self._entity_id()).id
        district_id = District.objects.using(self._current_app_schema()).get(code=bankbranch_data['district_code'],
                                                                             entity_id=self._entity_id()).id
        pincode_id = \
        Pincode.objects.using(self._current_app_schema()).filter(no=bankbranch_data['pincode_code'], city_id=city_id,
                                                                 district_id=district_id, entity_id=self._entity_id())[
            0].id
        state_id = State.objects.using(self._current_app_schema()).get(code=bankbranch_data['state_code'],
                                                                       entity_id=self._entity_id()).id

        bankbranch_data['pincode_id'] = pincode_id
        bankbranch_data['city_id'] = city_id
        bankbranch_data['district_id'] = district_id
        bankbranch_data['state_id'] = state_id
        return bankbranch_data
    def bank_branch_summary(self,request,bank_id,vys_page):
        bankbranch_data=BankBranch.objects.using(self._current_app_schema()).filter(bank_id=bank_id).values('code','name','ifsccode','bank_id')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        data= len(bankbranch_data)
        branch_list = NWisefinList()
        if data<=0:
            vpage = NWisefinPaginator(bankbranch_data, vys_page.get_index(), 10)
            branch_list.set_pagination(vpage)
            return branch_list
        else:
            for i in bankbranch_data:
                response = bank_branch_Response()
                response.set_code(i['code'])
                response.set_name(i['name'])
                response.set_ifsc(i['ifsccode'])
                response.set_bank_id(i['bank_id'])
                branch_list.append(response)
            vpage = NWisefinPaginator(bankbranch_data, vys_page.get_index(), 10)
            branch_list.set_pagination(vpage)
            return branch_list


    def get_bank_branch_sync(self, bank_name,ifsccode):
        bank_var = BankBranch.objects.using(self._current_app_schema()).filter(name__iexact=bank_name,ifsccode__iexact=ifsccode)
        if len(bank_var) > 0:
            bank_id = bank_var[0].id
            return bank_id
        else:
            return 0

    def fetch_bankbranch_list_download(self, vys_page):
        try:
            bankbranchlist = BankBranch.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
            list_length = len(bankbranchlist)
            if list_length >= 0:
                bankbranch_list_data = NWisefinList()
                for bankobj in bankbranchlist:
                    bankbranch_data = BankBranchResponse()
                    addre_serv = AddressService(self._scope())  # changed
                    bankbranch_data.set_id(bankobj.id)
                    bankbranch_data.set_code(bankobj.code)
                    bankbranch_data.set_name(bankobj.name)
                    bankbranch_data.set_ifsccode(bankobj.ifsccode)
                    bankbranch_data.set_microcode(bankobj.microcode)
                    # bankbranch_data.set_bank(bankobj.bank)
                    # if bankobj.address_id == None:
                    #     bankbranch_data.set_address_id(None)
                    # else:
                    #     bankbranch_data.set_address_id(addre_serv.fetch_address(bankobj.address_id, 1))
                    bankbranch_list_data.append(bankbranch_data)
                return bankbranch_list_data
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
                error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
                return error_obj
        except:
            logger.error('ERROR_BankBranch_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_BANKBRANCH_ID)
            error_obj.set_description(ErrorDescription.INVALID_BANKBRANCH_ID)
            return error_obj
