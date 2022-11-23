import traceback
from configservice.service.configservice import ConfigService
from django.db.models import Q
from masterservice.models.mastermodels import City, State, Pincode, District, Tax, SubTax, TaxRate, PayMode, Bank, \
    BankBranch, Product, Apcategory, APsubcategory, DocumentGroup
from masterservice.service.stateservice import StateService
from masterservice.service.counrtyservice import CountryService
from masterservice.service.districtservice import DistrictService
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.docugroupservice import DocumentGroupService
from masterservice.util.masterutil import MasterStatus, VOWMasterTable
from nwisefin.settings import logger
from configservice.service.entityservice import EntityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.cityservice import CityService
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.models.mastermodels import RisksType
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
from django.db import IntegrityError
from masterservice.data.response.risktyperesponse import RiskTypeResponse
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.service.paymodeservice import PaymodeService


class VendorUtilService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_risk_type(self, risk_obj, employee_id):
        if risk_obj.get_id() is None:
            try:
                logger.error('RISKSTYPE: RisksType Creation Started')

                data_len = RisksType.objects.using(self._current_app_schema()).filter(name=risk_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj

                risk_type = RisksType.objects.using(self._current_app_schema()).create(name=risk_obj.get_name(),
                                                                                       entity_id=self._entity_id(),
                                                                                       created_by=employee_id)
                try:
                    max_cat_code = RisksType.objects.using(self._current_app_schema()).filter(code__icontains='RSK').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "RSK" + str(new_rnsl).zfill(5)
                risk_type.code = code
                risk_type.save()
                logger.error('RISKSTYPE: RisksType Creation Success' + str(risk_type))
            except IntegrityError as error:
                logger.error('ERROR_RisksType_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_RisksType_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('RISKSTYPE: RisksType Update Started')

                risk_type = RisksType.objects.using(self._current_app_schema()).filter(id=risk_obj.get_id()).update(name=risk_obj.get_name(),
                                                                                       updated_by=employee_id)
                risk_type = RisksType.objects.using(self._current_app_schema()).get(id=risk_obj.get_id(), entity_id=self._entity_id())
                logger.error('RISKSTYPE: RisksType Update Success' + str(risk_type))
            except IntegrityError as error:
                logger.info('ERROR_RisksType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except RisksType.DoesNotExist:
                logger.info('ERROR_RisksType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
                error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
                return error_obj
            except:
                logger.info('ERROR_RisksType_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        risk_data = RiskTypeResponse()
        risk_data.set_id(risk_type.id)
        risk_data.set_name(risk_type.name)
        risk_data.set_code(risk_type.code)
        risk_data.set_status(risk_type.status)
        return risk_data

    def fetch_risktype_list(self,query, vys_page):
        try:
            conditions=Q(entity_id=self._entity_id())
            if query is not None:
                conditions &= Q(name__icontains=query)
            risktype_list = RisksType.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                             vys_page.get_offset():vys_page.get_query_limit()]
            list_data = NWisefinList()
            for risktype in risktype_list:
                risk_data = RiskTypeResponse()
                risk_data.set_id(risktype.id)
                risk_data.set_name(risktype.name)
                risk_data.set_status(risktype.status)
                risk_data.set_code(risktype.code)
                list_data.append(risk_data)
            vpage = NWisefinPaginator(risktype_list, vys_page.get_index(), 10)
            list_data.set_pagination(vpage)
            return list_data
        except:
            logger.error('ERROR_RiskType_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
            error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
            return error_obj

    def fetch_risktype_download(self,request):
        try:
            conditions=Q(entity_id=self._entity_id())
            # if query is not None:
            #     conditions &= Q(name__icontains=query)
            risktype_list = RisksType.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')
            list_data = NWisefinList()
            for risktype in risktype_list:
                risk_data = RiskTypeResponse()
                risk_data.Code = risktype.code
                risk_data.Name = risktype.name
                status = MasterStatus()
                if risktype.status == status.Active:
                    risk_data.Status = status.Active_VALUE
                if risktype.status == status.Inactive:
                    risk_data.Status = status.Inactive_VALUE
                list_data.append(risk_data)
            return list_data
        except:
            logger.error('ERROR_RiskType_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
            error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
            return error_obj


    def fetch_risktype(self, risktype_id):
        try:
            risktype = RisksType.objects.using(self._current_app_schema()).get(id=risktype_id,
                                                                               entity_id=self._entity_id())
            risk_data = RiskTypeResponse()
            risk_data.set_id(risktype.id)
            risk_data.set_name(risktype.name)
            risk_data.set_status(risktype.status)
            risk_data.set_code(risktype.code)
            return risk_data
        except RisksType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
            error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
            return error_obj

    def delete_risktype(self, risktype_id):
        risk = RisksType.objects.using(self._current_app_schema()).filter(id=risktype_id,
                                                                          entity_id=self._entity_id()).delete()
        if risk[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
            error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


class MasterTableService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def get_masters_data(self, type, id):
        type = int(type)
        id = int(id)
        resp = None
        if type == VOWMasterTable.CITY:
            resp = self.get_city(id)
        elif type == VOWMasterTable.STATE:
            resp = self.get_state(id)
        elif type == VOWMasterTable.PINCODE:
            resp = self.get_pincode(id)
        elif type == VOWMasterTable.DISTRICT:
            resp = self.get_district(id)
        elif type == VOWMasterTable.TAX:
            resp = self.get_tax(id)
        elif type == VOWMasterTable.SUB_TAX:
            resp = self.get_sub_tax(id)
        elif type == VOWMasterTable.TAX_RATE:
            resp = self.get_tax_rate(id)
        elif type == VOWMasterTable.PAY_MODE:
            resp = self.get_paymode(id)
        elif type == VOWMasterTable.BANK:
            resp = self.get_bank(id)
        elif type == VOWMasterTable.BANK_BRANCH:
            resp = self.get_bank_branch(id)
        elif type == VOWMasterTable.PRODUCT:
            resp = self.get_product(id)
        elif type == VOWMasterTable.DOC_GROUP:
            resp = self.get_doc_group(id)
        if resp is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            return resp

    def get_city(self, id):
        resp = City.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.name = resp[0].name
            data.code = resp[0].code
            data.state_id = resp[0].state_id
            return data
        else:
            return

    def get_state(self, id):
        resp = State.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.name = resp[0].name
            data.code = resp[0].code
            return data
        else:
            return

    def get_pincode(self, id):
        resp = Pincode.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.number = resp[0].no
            data.district_id = resp[0].district_id
            data.city_id = resp[0].city_id
            return data
        else:
            return

    def get_district(self, id):
        resp = District.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.name = resp[0].name
            data.code = resp[0].code
            data.state_id = resp[0].state_id
            return data
        else:
            return

    def get_tax(self, id):
        resp = Tax.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.name = resp[0].name
            data.code = resp[0].code
            data.glno = resp[0].glno
            return data
        else:
            return

    def get_sub_tax(self, id):
        resp = SubTax.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.tax_id = resp[0].tax_id
            data.code = resp[0].code
            data.name = resp[0].name
            data.glno = resp[0].glno
            data.subtaxamount = str(resp[0].subtaxamount)
            data.category_id = resp[0].category_id
            data.subcategory_id = resp[0].subcategory_id
            return data
        else:
            return

    def get_tax_rate(self, id):
        resp = TaxRate.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.subtax_id = resp[0].subtax_id
            data.code = resp[0].code
            data.name = resp[0].name
            data.rate = resp[0].rate
            return data
        else:
            return

    def get_paymode(self, id):
        resp = PayMode.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.code = resp[0].code
            data.name = resp[0].name
            return data
        else:
            return

    def get_bank(self, id):
        resp = Bank.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.code = resp[0].code
            data.name = resp[0].name
            return data
        else:
            return

    def get_bank_branch(self, id):
        resp = BankBranch.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.bank_id = resp[0].bank_id
            data.address_id = resp[0].address_id
            data.code = resp[0].code
            data.ifsccode = resp[0].ifsccode
            data.microcode = resp[0].microcode
            data.name = resp[0].name
            return data
        else:
            return

    def get_product(self, id):
        resp = Product.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.hsn_id = resp[0].hsn_id
            data.uom_id = resp[0].uom_id
            data.category_id = resp[0].category_id
            data.subcategory_id = resp[0].subcategory_id
            data.productcategory_id = resp[0].productcategory_id
            data.producttype_id = resp[0].producttype_id
            data.code = resp[0].code
            data.name = resp[0].name
            data.productdisplayname = resp[0].productdisplayname
            data.producttradingitem = resp[0].producttradingitem
            data.weight = str(resp[0].weight)
            data.unitprice = str(resp[0].unitprice)
            return data
        else:
            return

    def get_doc_group(self, id):
        resp = DocumentGroup.objects.using(self._current_app_schema()).filter(id=id)
        if len(resp) != 0:
            data = NWisefinLiteList()
            data.set_id(resp[0].id)
            data.name = resp[0].name
            data.partnertype = resp[0].partnertype
            data.isparent = resp[0].isparent
            data.parent_id = resp[0].parent_id
            data.docname = resp[0].docname
            data.period = resp[0].period
            data.mand = resp[0].mand
            return data
        else:
            return

    def get_masters_data_list(self, type, id_arr):
        type = int(type)
        resp = None
        if type == VOWMasterTable.CITY:
            resp = self.get_city_list(id_arr)
        elif type == VOWMasterTable.STATE:
            resp = self.get_state_list(id_arr)
        elif type == VOWMasterTable.PINCODE:
            resp = self.get_pincode_list(id_arr)
        elif type == VOWMasterTable.DISTRICT:
            resp = self.get_district_list(id_arr)
        elif type == VOWMasterTable.TAX:
            resp = self.get_tax_list(id_arr)
        elif type == VOWMasterTable.SUB_TAX:
            resp = self.get_sub_tax_list(id_arr)
        elif type == VOWMasterTable.TAX_RATE:
            resp = self.get_tax_rate_list(id_arr)
        elif type == VOWMasterTable.PAY_MODE:
            resp = self.get_paymode_list(id_arr)
        elif type == VOWMasterTable.BANK:
            resp = self.get_bank_list(id_arr)
        elif type == VOWMasterTable.BANK_BRANCH:
            resp = self.get_bank_branch_list(id_arr)
        elif type == VOWMasterTable.PRODUCT:
            resp = self.get_product_list(id_arr)
        elif type == VOWMasterTable.DOC_GROUP:
            resp = self.get_doc_group_list(id_arr)
        if resp is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            return resp

    def get_city_list(self, id_arr):
        city_list = City.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for city in city_list:
            data = NWisefinLiteList()
            data.set_id(city.id)
            data.name = city.name
            data.code = city.code
            data.state_id = city.state_id
            list_data.append(data)
        return list_data

    def get_state_list(self, id_arr):
        state_list = State.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for state in state_list:
            data = NWisefinLiteList()
            data.set_id(state.id)
            data.name = state.name
            data.code = state.code
            list_data.append(data)
        return list_data

    def get_pincode_list(self, id_arr):
        pincode_list = Pincode.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for pincode in pincode_list:
            data = NWisefinLiteList()
            data.set_id(pincode.id)
            data.number = pincode.no
            data.district_id = pincode.district_id
            data.city_id = pincode.city_id
            list_data.append(data)
        return list_data

    def get_district_list(self, id_arr):
        district_list = District.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for district in district_list:
            data = NWisefinLiteList()
            data.set_id(district.id)
            data.name = district.name
            data.code = district.code
            data.state_id = district.state_id
            list_data.append(data)
        return list_data

    def get_tax_list(self, id_arr):
        tax_list = Tax.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for tax in tax_list:
            data = NWisefinLiteList()
            data.set_id(tax.id)
            data.name = tax.name
            data.code = tax.code
            data.glno = tax.glno
            list_data.append(data)
        return list_data

    def get_sub_tax_list(self, id_arr):
        sub_tax_list = SubTax.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for sub_tax in sub_tax_list:
            data = NWisefinLiteList()
            data.set_id(sub_tax.id)
            data.tax_id = sub_tax.tax_id
            data.code = sub_tax.code
            data.name = sub_tax.name
            data.glno = sub_tax.glno
            data.subtaxamount = str(sub_tax.subtaxamount)
            data.category_id = sub_tax.category_id
            data.subcategory_id = sub_tax.subcategory_id
            list_data.append(data)
        return list_data

    def get_tax_rate_list(self, id_arr):
        tax_rate_list = TaxRate.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for tax_rate in tax_rate_list:
            data = NWisefinLiteList()
            data.set_id(tax_rate.id)
            data.subtax_id = tax_rate.subtax_id
            data.code = tax_rate.code
            data.name = tax_rate.name
            data.rate = tax_rate.rate
            list_data.append(data)
        return list_data

    def get_paymode_list(self, id_arr):
        pay_mode_list = PayMode.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for pay_mode in pay_mode_list:
            data = NWisefinLiteList()
            data.set_id(pay_mode.id)
            data.code = pay_mode.code
            data.name = pay_mode.name
            list_data.append(data)
        return list_data

    def get_bank_list(self, id_arr):
        bank_list = Bank.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for bank in bank_list:
            data = NWisefinLiteList()
            data.set_id(bank.id)
            data.code = bank.code
            data.name = bank.name
            list_data.append(data)
        return list_data

    def get_bank_branch_list(self, id_arr):
        branch_list = BankBranch.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for branch in branch_list:
            data = NWisefinLiteList()
            data.set_id(branch.id)
            data.bank_id = branch.bank_id
            data.address_id = branch.address_id
            data.code = branch.code
            data.ifsccode = branch.ifsccode
            data.microcode = branch.microcode
            data.name = branch.name
            list_data.append(data)
        return list_data

    def get_product_list(self, id_arr):
        product_list = Product.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for product in product_list:
            data = NWisefinLiteList()
            data.set_id(product.id)
            data.hsn_id = product.hsn_id
            data.uom_id = product.uom_id
            data.category_id = product.category_id
            data.subcategory_id = product.subcategory_id
            data.productcategory_id = product.productcategory_id
            data.producttype_id = product.producttype_id
            data.code = product.code
            data.name = product.name
            data.productdisplayname = product.productdisplayname
            data.producttradingitem = product.producttradingitem
            data.weight = str(product.weight)
            data.unitprice = str(product.unitprice)
            list_data.append(data)
        return list_data

    def get_doc_group_list(self, id_arr):
        doc_list = DocumentGroup.objects.using(self._current_app_schema()).filter(id__in=id_arr)
        list_data = NWisefinList()
        for doc in doc_list:
            data = NWisefinLiteList()
            data.set_id(doc.id)
            data.name = doc.name
            data.partnertype = doc.partnertype
            data.isparent = doc.isparent
            data.parent_id = doc.parent_id
            data.docname = doc.docname
            data.period = doc.period
            data.mand = doc.mand
            list_data.append(data)
        return list_data

    # def get_ap_category(self, id):
    #     resp = Apcategory.objects.using(self.schema).filter(id=id)
    #     if len(resp) != 0:
    #         data = NWisefinLiteList()
    #         data.set_id(resp[0].id)
    #         data.code = resp[0].code
    #         data.no = resp[0].no
    #         data.name = resp[0].name
    #         data.glno = resp[0].glno
    #         return data
    #     else:
    #         return
    #
    # def get_ap_sub_category(self, id):
    #     resp = APsubcategory.objects.using(self.schema).filter(id=id)
    #     if len(resp) != 0:
    #         data = NWisefinLiteList()
    #         data.set_id(resp[0].id)
    #         data.code = resp[0].code
    #         data.no = resp[0].no
    #         data.name = resp[0].name
    #         data.category_id = resp[0].category_id
    #         data.glno = resp[0].glno
    #         data.gstblocked = resp[0].gstblocked
    #         data.gstrcm = resp[0].gstrcm
    #         data.assetcode = resp[0].assetcode
    #         return data
    #     else:
    #         return


class MasterDropDown(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def masters_drop_down(self, params):
        type = params['type']
        query = params['query']
        vys_page = params['vys_page']
        state_id = params['state_id']
        tax_id = params['tax_id']
        name = params['name']
        subtax_id = params['subtax_id']
        type = int(type)
        resp = None
        if type == VOWMasterTable.CITY:
            city_service = CityService(self._scope())
            city_resp = city_service.fetch_new_city_search(query, vys_page, state_id)
            resp = city_resp
        elif type == VOWMasterTable.STATE:
            state_service = StateService(self._scope())
            resp_obj = state_service.fetch_state_search(query, vys_page)
            country_service = CountryService(self._scope())
            x = resp_obj.data
            for i in x:
                if (i.country_id is not None) and (i.country_id != ''):
                    country_id = i.country_id
                    country = country_service.fetch_country(country_id, 1)
                    i.country_id = country
            resp = resp_obj
        elif type == VOWMasterTable.PINCODE:
            pincode_serv = PincodeService(self._scope())
            pincode_resp = pincode_serv.fetch_pincode_search(query, vys_page)
            resp = pincode_resp
        elif type == VOWMasterTable.DISTRICT:
            district_service = DistrictService(self._scope())
            resp_obj = district_service.fetch_district_search(query, vys_page, state_id)
            resp = resp_obj
        elif type == VOWMasterTable.TAX:
            tax_service = TaxMasterService(self._scope())
            resp_obj = tax_service.fetch_tax_search(query, vys_page)
            resp = resp_obj
        elif type == VOWMasterTable.SUB_TAX:
            subtax_service = SubTaxService(self._scope())
            resp_obj = subtax_service.fetch_subtax_search(query, tax_id, vys_page)
            resp = resp_obj
        elif type == VOWMasterTable.TAX_RATE:
            taxrate_service = TaxRateService(self._scope())
            resp_obj = taxrate_service.fetch_taxrate_search(vys_page, query, subtax_id, name)
            resp = resp_obj
        elif type == VOWMasterTable.PAY_MODE:
            paymode_service = PaymodeService(self._scope())
            paymode_resp = paymode_service.fetch_paymode_search(query, vys_page)
            resp = paymode_resp
        elif type == VOWMasterTable.BANK:
            resp = None
        elif type == VOWMasterTable.BANK_BRANCH:
            resp = None
        elif type == VOWMasterTable.PRODUCT:
            resp = None
        elif type == VOWMasterTable.DOC_GROUP:
            docugroup_service = DocumentGroupService(self._scope())
            resp_obj = docugroup_service.fetch_documentgroup_list(vys_page, query)
            resp = resp_obj
        elif type == VOWMasterTable.IFSC:
            bank_serv = BankBranchService(self._scope())
            bank_id = 0
            ifsc_resp = bank_serv.search_ifsc(bank_id, query, vys_page)
            resp = ifsc_resp
        elif type == VOWMasterTable.ENTITY:
            entity_service = EntityService()
            entity_resp = entity_service.fetch_entity_list()
            resp = entity_resp
        if resp is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            return resp
