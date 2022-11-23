from cmsservice.models import CodeGenHistory
from cmsservice.util.cmsutil import CodePrefix, ActiveStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils import timezone

class Codegenservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

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
            if CodePrefix.ProjectType == ref_table:
                code = CodePrefix.ProjectType_VAL
            elif CodePrefix.DocumentType == ref_table:
                code = CodePrefix.DocumentType_VAL
            elif CodePrefix.Project == ref_table:
                code = CodePrefix.Project_VAL
            elif CodePrefix.Proposal == ref_table:
                code = CodePrefix.Proposal_VAL
            elif CodePrefix.ProjectIdentification == ref_table:
                code = CodePrefix.ProjectIdentification_VAL

            codegene = CodeGenHistory.objects.using(self._current_app_schema()).create(
                                            ref_table=ref_table,
                                            ref_code=code,
                                            last_id=default_last_id,
                                            created_by=emp_id,
                                            created_date=timezone.now())
            last_code = str(code) + str(default_last_id)
        return last_code



#vow
from userservice.controller.vowusercontroller import VowUser

class VowCodegenservice:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)
        self.emp_id = vowuser_info['user_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']


    def vow_codegen(self, ref_table, emp_id):
        default_last_id = 1
        codegen = CodeGenHistory.objects.using(self.schema).filter(
            ref_table=ref_table,
            status=ActiveStatus.Active)
        if len(codegen) > 0:
            codegene = codegen[0]
            print(codegene.last_id)
            now_id = int(codegene.last_id) + default_last_id
            codegen = CodeGenHistory.objects.using(self.schema).filter(
                ref_table=ref_table,
                status=ActiveStatus.Active).update(
                last_id=now_id,
                updated_by=emp_id,
                updated_date=timezone.now())
            last_code = str(codegene.ref_code) + str(now_id)
        else:
            if CodePrefix.ProjectType == ref_table:
                code = CodePrefix.ProjectType_VAL
            elif CodePrefix.DocumentType == ref_table:
                code = CodePrefix.DocumentType_VAL
            elif CodePrefix.Project == ref_table:
                code = CodePrefix.Project_VAL
            elif CodePrefix.Proposal == ref_table:
                code = CodePrefix.Proposal_VAL
            elif CodePrefix.ProjectIdentification == ref_table:
                code = CodePrefix.ProjectIdentification_VAL

            codegene = CodeGenHistory.objects.using(self.schema).create(
                ref_table=ref_table,
                ref_code=code,
                last_id=default_last_id,
                created_by=emp_id,
                created_date=timezone.now())
            last_code = str(code) + str(default_last_id)
        return last_code