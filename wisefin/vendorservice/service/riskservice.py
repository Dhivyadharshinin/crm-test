from vendorservice.models.vendormodels import VendorRiskInfo, Vendor, VendorModificationRel
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.db import IntegrityError
from vendorservice.data.response.riskresponse import RiskResponse
from masterservice.service.vendorutilservice import VendorUtilService
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.db.models import Q
from django.utils import timezone
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.data.response.vendorauditresponse import VendorAuditResponse
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.utilityservice import NWisefinUtilityService


class RiskService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_vendor_risk(self, risk_obj, vendor_id, employee_id):
        if risk_obj.get_id() is None:
            try:
                vendor = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id)
                vendorid=vendor[0].id
                vendor_risk = VendorRiskInfo.objects.using(self._current_app_schema()).create(vendor_id=vendorid,
                                                                                              risktype_id=risk_obj.get_risktype_id(),
                                                                                              risktype_description=risk_obj.get_risktype_description(),
                                                                                              risk_mitigant=risk_obj.get_risk_mitigant(),
                                                                                              risk_mitigant_review=risk_obj.get_risk_mitigant_review(),
                                                                                              created_by=employee_id,
                                                                                              entity_id=self._entity_id(), portal_flag=risk_obj.get_portal_flag())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                vendor_risk = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=risk_obj.get_id()).update(vendor_id=vendor_id,
                                                                                                                           risktype_id=risk_obj.get_risktype_id(),
                                                                                                                           risktype_description = risk_obj.get_risktype_description(),
                                                                                                                           risk_mitigant=risk_obj.get_risk_mitigant(),
                                                                                                                           risk_mitigant_review=risk_obj.get_risk_mitigant_review(),
                                                                                                                           updated_by=employee_id,updated_date=timezone.now())
                vendor_risk = VendorRiskInfo.objects.using(self._current_app_schema()).get(id=risk_obj.get_id(), entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorRiskInfo.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
                error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        risk_data = RiskResponse()
        risk_data.set_id(vendor_risk.id)
        risk_data.set_risktype_id(vendor_risk.risktype_id)
        risk_data.set_risktype_description(vendor_risk.risktype_description)
        risk_data.set_risk_mitigant(vendor_risk.risk_mitigant)
        risk_data.set_risk_mitigant_review(vendor_risk.risk_mitigant_review)
        return risk_data

    def fetch_risk_list(self, request, vys_page,vendor_id):

        queue_arr = VendorRiskInfo.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id, entity_id=self._entity_id()).values('id')
        condition = None
        for vendor in queue_arr:
            if condition is None:
                condition = (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
            else:
                condition |= (Q(id__exact=vendor['id'])& (Q(modify_status__exact=-1) |Q(modify_status__exact=0))& Q(modified_by=-1))&Q(entity_id=self._entity_id())
        if condition is not None:
            risklist = VendorRiskInfo.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        else:
            risklist = []

        vlist = NWisefinList()
        user_list = []
        for vendor in risklist:
            user_list.append(vendor.created_by)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_user_info(request, user_list)

        for risk in risklist:
            risk_data = RiskResponse()
            risk_data.set_id(risk.id)
            risk_service = VendorUtilService(self._scope())
            risktype = risk_service.fetch_risktype(risk.risktype_id)
            risk_data.set_risktype_id(risktype)
            risk_data.set_risktype_description(risk.risktype_description)
            risk_data.set_risk_mitigant(risk.risk_mitigant)
            risk_data.set_risk_mitigant_review(risk.risk_mitigant_review)
            risk_data.set_modify_ref_id(risk.modify_ref_id)
            risk_data.set_modify_status(risk.modify_status)
            risk_data.set_created_by(risk.created_by)
            risk_data.set_portal_flag(risk.portal_flag)

            for ul in user_list_obj['data']:
                if ul['id'] == VendorRiskInfo.created_by:
                    risk_data.set_created_by(ul)
            vlist.append(risk_data)
        vpage = NWisefinPaginator(risklist, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist

    def fetch_risk(self, vendor_id, risk_id):
        try:
            risk = VendorRiskInfo.objects.using(self._current_app_schema()).get(id=risk_id, entity_id=self._entity_id(), vendor_id=vendor_id)
            risk_data = RiskResponse()
            risk_data.set_id(risk.id)
            risk_service = VendorUtilService(self._scope())
            risktype = risk_service.fetch_risktype(risk.risktype_id)
            risk_data.set_risktype_id(risktype)
            risk_data.set_risktype_description(risk.risktype_description)
            risk_data.set_risk_mitigant(risk.risk_mitigant)
            risk_data.set_risk_mitigant_review(risk.risk_mitigant_review)
            risk_data.set_modify_ref_id(risk.modify_ref_id)
            risk_data.set_modify_status(risk.modify_status)
            risk_data.set_created_by(risk.created_by)
            risk_data.set_portal_flag(risk.portal_flag)
            return risk_data
        except VendorRiskInfo.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
            error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
            return error_obj

    def delete_risk(self, risk_id):
            risk = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=risk_id, entity_id=self._entity_id()).delete()
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

    # modification
    def modification_create_risk(self, risk_obj, employee_id, vendor_id):

        vendor_service = VendorService(self._scope())
        if not risk_obj.get_id() is None:
            try:
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_RISK, risk_obj.get_id())
                if ref_flag == True:
                    risk_var = VendorRiskInfo.objects.using(self._current_app_schema()).filter(
                        id=risk_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id,
                                                                                              risktype_id=risk_obj.get_risktype_id(),
                                                                                              risktype_description=risk_obj.get_risktype_description(),
                                                                                              risk_mitigant=risk_obj.get_risk_mitigant(),
                                                                                              risk_mitigant_review=risk_obj.get_risk_mitigant_review(),
                                                                                              portal_flag=risk_obj.get_portal_flag()
                                                                                      )
                    risk_var = VendorRiskInfo.objects.using(self._current_app_schema()).get(
                        id=risk_obj.get_id(), entity_id=self._entity_id())
                else:

                    risk_var = VendorRiskInfo.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                              risktype_id=risk_obj.get_risktype_id(),
                                                                                              risktype_description=risk_obj.get_risktype_description(),
                                                                                              risk_mitigant=risk_obj.get_risk_mitigant(),
                                                                                              risk_mitigant_review=risk_obj.get_risk_mitigant_review(),
                                                                                              created_by=employee_id,
                                                                                                   modify_status=ModifyStatus.update,
                                                                                                   modified_by=employee_id,
                                                                                                   modify_ref_id=risk_obj.get_id(),
                                                                                                   entity_id=self._entity_id(), portal_flag=risk_obj.get_portal_flag())

                    risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(
                        id=risk_obj.get_id(), entity_id=self._entity_id()).update(
                        modify_ref_id=risk_var.id)


                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                           ref_id=risk_obj.get_id(),
                                                                                           ref_type=VendorRefType.VENDOR_RISK,
                                                                                           mod_status=ModifyStatus.update,
                                                                                           modify_ref_id=risk_var.id,
                                                                                           entity_id=self._entity_id())


                req_status = RequestStatusUtil.MODIFICATION
                risk_id = risk_obj.get_id()
                self.audit_function(risk_var, vendor_id, employee_id, req_status, risk_var.id, ModifyStatus.create)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorRiskInfo.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
                error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            try:
                risk_var = VendorRiskInfo.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                              risktype_id=risk_obj.get_risktype_id(),
                                                                                              risktype_description=risk_obj.get_risktype_description(),
                                                                                              risk_mitigant=risk_obj.get_risk_mitigant(),
                                                                                              risk_mitigant_review=risk_obj.get_risk_mitigant_review(),
                                                                                              created_by=employee_id,
                                                                                               modify_status=ModifyStatus.create,
                                                                                               modified_by=employee_id,
                                                                                               entity_id=self._entity_id(),portal_flag=risk_obj.get_portal_flag())

                risk_var.modify_ref_id = risk_var.id
                risk_var.save()

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                       ref_id=risk_var.id,
                                                                                       ref_type=VendorRefType.VENDOR_RISK,
                                                                                       mod_status=ModifyStatus.create,
                                                                                       modify_ref_id=risk_var.id,
                                                                                       entity_id=self._entity_id())

                req_status = RequestStatusUtil.MODIFICATION
                self.audit_function(risk_var, vendor_id, employee_id, req_status, risk_var.id, ModifyStatus.create)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except VendorRiskInfo.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_RISK_ID)
                error_obj.set_description(ErrorDescription.INVALID_RISK_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        risk_data = RiskResponse()
        risk_data.set_id(risk_var.id)
        risk_data.set_risktype_description(risk_var.risktype_description)
        risk_data.set_risk_mitigant(risk_var.risk_mitigant)
        risk_data.set_risk_mitigant_review(risk_var.risk_mitigant_review)
        return risk_data

    def modification_delete_risk(self, risk_id, vendor_id, employee_id):
        try:
            vendor_service = VendorService(self._scope())
            risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=risk_id,
                                                                                              entity_id=self._entity_id()).update(
                modify_ref_id=risk_id, modify_status=ModifyStatus.delete)
            ref_flag = vendor_service.checkmodify_rel(VendorRefType.VENDOR_RISK, risk_id)
            if ref_flag == True:
                flag_obj = VendorModificationRel.objects.using(self._current_app_schema()).filter(Q(modify_ref_id=risk_id) & Q(ref_type=VendorRefType.VENDOR_RISK) & Q(
                        entity_id=self._entity_id())).update(mod_status=ModifyStatus.delete)
            else:
                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                       ref_id=risk_id,
                                                                                       ref_type=VendorRefType.VENDOR_RISK,
                                                                                       mod_status=ModifyStatus.delete,
                                                                                       modify_ref_id=risk_id,
                                                                                       entity_id=self._entity_id())
            req_status = RequestStatusUtil.MODIFICATION
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def modification_action_risk(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            risk_obj = self.fetch_risk(vendor_id,new_id)
            risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                              entity_id=self._entity_id()).update(
                vendor_id=vendor_id,
                risktype_id=risk_obj.get_risktype_id().id,
                risktype_description=risk_obj.get_risktype_description(),
                risk_mitigant=risk_obj.get_risk_mitigant(),
                risk_mitigant_review=risk_obj.get_risk_mitigant_review(), modify_status=-1,
                modified_by=-1,
                modify_ref_id=-1, portal_flag=risk_obj.get_portal_flag())

            self.audit_function(risk_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
            # self.audit_function(document, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)

        elif mod_status == ModifyStatus.create:
            risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=new_id,
                                                                                              entity_id=self._entity_id()).update(
                modify_status=-1,
                modify_ref_id=-1, modified_by=-1)

            self.audit_function(risk_update, vendor_id, user_id, req_status, new_id, ModifyStatus.update)

        else:
            risk = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                       entity_id=self._entity_id()).delete()

            self.audit_function(risk, vendor_id, user_id, req_status, old_id, ModifyStatus.delete)
        return

    def modification_reject_risk(self, mod_status, old_id, new_id, vendor_id, user_id):

        req_status = RequestStatusUtil.MODIFICATION
        if mod_status == ModifyStatus.update:
            risk = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=new_id,
                                                                                       entity_id=self._entity_id()).delete()
            risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                              entity_id=self._entity_id()).update(
                modify_ref_id=-1)

            self.audit_function(risk, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
            self.audit_function(risk_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)

        elif mod_status == ModifyStatus.create:
            risk = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=new_id,
                                                                                       entity_id=self._entity_id()).delete()

            self.audit_function(risk, vendor_id, user_id, req_status, new_id, ModifyStatus.delete)
        else:
            risk_update = VendorRiskInfo.objects.using(self._current_app_schema()).filter(id=old_id,
                                                                                              entity_id=self._entity_id()).update(
                modify_ref_id=-1)

            self.audit_function(risk_update, vendor_id, user_id, req_status, old_id, ModifyStatus.update)
        return

    def audit_function(self, risk, vendor_id, user_id, req_status, id, action):

        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = risk
        else:
            data = risk.__dict__
            del data['_state']
        audit_service = VendorAuditService(self._scope())
        audit_obj = VendorAuditResponse()
        audit_obj.set_refid(vendor_id)
        audit_obj.set_reftype(VendorRefType.VENDOR)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(VendorRefType.VENDOR_RISK)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_vendoraudit(audit_obj)
        return
