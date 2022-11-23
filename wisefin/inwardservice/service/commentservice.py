from django.utils.timezone import now

from inwardservice.data.response.commentdocresponse import CommentDocResponse
from inwardservice.models import CommentDoc
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CommentDocService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_commentdoc(self, request, arr_obj, details_id, emp_id):
        print(emp_id,details_id,arr_obj.get_branch(),arr_obj.get_comment())
        cmnt_doc = CommentDoc.objects.using(self._current_app_schema()).create(employee_id=emp_id,
                                            inwarddetails_id=details_id,
                                            branch_id=arr_obj.get_branch(),
                                            comment=arr_obj.get_comment(),
                                            created_by=emp_id,
                                            created_date=now())

        # cmnt_doc = CommentDoc.objects.using(self._current_app_schema()).get(id=cmnt_doc.id)
        print("comm", cmnt_doc.id)
        cmnt_resp = CommentDocResponse()
        cmnt_resp.set_id(cmnt_doc.id)
        cmnt_resp.set_branch(cmnt_doc.branch_id)
        cmnt_resp.set_comment(cmnt_doc.comment)
        return cmnt_resp