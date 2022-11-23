from masterservice.models import Codegenerator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from django.utils import timezone


class CodeGen(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def codegenerator(self, trans_type, entity_id, emp_id, trans_Value):
        generator = Codegenerator.objects.using(self._current_app_schema()).filter(trans_type=trans_type,
                                                                               entity_id=entity_id,
                                                                               status=1)

        if len(generator) == 0:
            c_gen = Codegenerator.objects.using(self._current_app_schema()).create(trans_type=trans_type,
                                                                               entity_id=entity_id,
                                                                               Updated_by=emp_id,
                                                                               Updated_date=timezone.now(), serial_no=1)
            serial_no = c_gen.serial_no
            tran = trans_Value+str(serial_no)
        else:
            old_serial_no = generator[0].serial_no
            serial_no = old_serial_no + 1
            Codegenerator.objects.using(self._current_app_schema()).filter(trans_type=trans_type,
                                                                           entity_id=entity_id).update(
                                                                           Updated_by=emp_id,
                                                                           Updated_date=timezone.now(),
                                                                           serial_no=serial_no)
            tran = trans_Value + str(serial_no)


        return tran
