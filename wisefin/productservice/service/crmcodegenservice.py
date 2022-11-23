from productservice.models.productmodels import CodeGenHistory
from productservice.util.product_util import CodePrefix, ActiveStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils import timezone

class Codegenservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CRM_SERVICE)

    def codegen(self, ref_table, emp_id):
        default_last_id = 1
        codegen = CodeGenHistory.objects.using(self._current_app_schema()).filter(
                                                    ref_table=ref_table,
                                                    status=ActiveStatus.Active)
        if len(codegen) > 0:
            codegene = codegen[0]
            print(codegene.last_id)
            now_id = int(codegene.last_id) + default_last_id
            codegen = CodeGenHistory.objects.using(self._current_app_schema()).filter(
                                                    ref_table=ref_table,
                                                    status=ActiveStatus.Active).update(
                                                    last_id=now_id,
                                                    updated_by=emp_id,
                                                    updated_date=timezone.now())
            last_code = str(codegene.ref_code) + str(now_id)
        else:
            if CodePrefix.product == ref_table:
                code = CodePrefix.product_VAL
            elif CodePrefix.source == ref_table:
                code = CodePrefix.source_VAL
            elif CodePrefix.lead == ref_table:
                code = CodePrefix.lead_VAL

            codegene = CodeGenHistory.objects.using(self._current_app_schema()).create(
                                            ref_table=ref_table,
                                            ref_code=code,
                                            last_id=default_last_id,
                                            created_by=emp_id,
                                            created_date=timezone.now())
            last_code = str(code) + str(default_last_id)
        return last_code
