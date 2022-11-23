from ecfservice.models.ecfmodels import PPXLiquidation
from ecfservice.util.ecfutil import ECFModifyStatus, ECFRefType
from ecfservice.data.response.ppxliquidationresponse import ppxliquidationresponse
from django.utils.timezone import now

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class PpxliquationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def ppxliquationcreate(self,request,ppxliq_obj,emp_id):
        if not ppxliq_obj.get_id() is None:
            ppxliq = PPXLiquidation.objects.using(self._current_app_schema()).filter(id=ppxliq_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        credit_id=ppxliq_obj.get_creditr_id(),
                                                                        ppx_number=ppxliq_obj.get_ppx_number(),
                                                                        ppx_amount=ppxliq_obj.get_ppx_amount(),
                                                                        amount=ppxliq_obj.get_amount(),
                                                                        ecf_number=ppxliq_obj.get_ecf_number(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
            ppxliq = PPXLiquidation.objects.using(self._current_app_schema()).get(id=ppxliq_obj.get_id(),entity_id=self._entity_id())
            self.audit_function(ppxliq, ppxliq.id, ppxliq.id, emp_id,
                                ECFModifyStatus.UPDATE, ECFRefType.PPXLIQUIDATION)

        else:
            ppxliq = PPXLiquidation.objects.using(self._current_app_schema()).create(
                                                credit_id=ppxliq_obj.get_credit_id(),
                                                ppx_number=ppxliq_obj.get_ppx_number(),
                                                ppx_amount=ppxliq_obj.get_ppx_amount(),
                                                amount=ppxliq_obj.get_amount(),
                                                ecf_number=ppxliq_obj.get_ecf_number(),
                                                created_by=emp_id,entity_id=self._entity_id())

            self.audit_function(ppxliq, ppxliq.id, ppxliq.id, emp_id,
                                ECFModifyStatus.CREATE, ECFRefType.PPXLIQUIDATION)


        ppxliq_data = ppxliquidationresponse()
        ppxliq_data.set_id(ppxliq.id)
        ppxliq_data.set_credit_id(ppxliq.credit_id)
        ppxliq_data.set_ppx_number(ppxliq.ppx_number)
        ppxliq_data.set_ppx_amount(ppxliq.ppx_amount)
        ppxliq_data.set_amount(ppxliq.amount)
        ppxliq_data.set_ecf_number(ppxliq.ecf_number)
        return ppxliq_data

