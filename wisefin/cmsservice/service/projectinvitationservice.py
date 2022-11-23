from django.utils import timezone
from userservice.controller.vowusercontroller import VowUser
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from cmsservice.data.response.projectresponse import ProjectInvitationResponse
from cmsservice.models import CMSProjectInvitation
from cmsservice.util.cmsutil import ActiveStatus


class ProjectInvitationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def projectinvitation(self, project_id, inv_data, emp_id):
        print("inv_data", inv_data)
        invite_arr = []
        for d_i in inv_data:
            if 'id' in d_i:
                cmsdoc_update = CMSProjectInvitation.objects.using(self._current_app_schema()
                                                            ).filter(
                                                            id=d_i['id']).update(
                                                            project_id=project_id,
                                                            email_id=d_i['email_id'],
                                                            v_code=d_i['v_code'],
                                                            v_name=d_i['v_name'],
                                                            updated_by=emp_id,
                                                            updated_date=timezone.now())
                cmsdoc = CMSProjectInvitation.objects.using(self._current_app_schema()
                                                            ).get(id=d_i['id'])

            else:
                cmsdoc = CMSProjectInvitation.objects.using(self._current_app_schema()).create(
                    project_id=project_id,
                    email_id=d_i['email_id'],
                    v_code=d_i['v_code'],
                    v_name=d_i['v_name'],
                    created_by=emp_id,
                    created_date=timezone.now())

            # print("cmsdoc", cmsdoc)
            # print("cmsdoc", cmsdoc.__dict__)
            # cmsdoc_data = cmsdoc.__dict__
            # invite_arr.append(cmsdoc_data)
            # return invite_arr
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def invitation_project(self, project_id):
        invite_arr = []
        projectty_list = CMSProjectInvitation.objects.using(self._current_app_schema()).filter(project_id=project_id, status=ActiveStatus.Active)
        for projectty in projectty_list:
            projectty_data = ProjectInvitationResponse()
            projectty_data.set_id(projectty.id)
            projectty_data.set_email_id(projectty.email_id)
            projectty_data.set_v_code(projectty.v_code)
            projectty_data.set_v_name(projectty.v_name)
            invite_arr.append(projectty_data)
        return invite_arr

    # version invitation get
    def invitation_projectget(self, project_id):
        invite_arr = []
        projectty_list = CMSProjectInvitation.objects.using(self._current_app_schema()).filter(project_id=project_id, status=ActiveStatus.Active)
        for projectty in projectty_list:
            invite_arr.append(projectty.__dict__)
        return invite_arr


class VowProjectInvitationService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    # def summary_vowproject(self, vys_page, obj_data):
    #     print("obj_data", obj_data)
    #     condition = Q(status=ActiveStatus.Active) \
    #                 & Q(project__status=ActiveStatus.Active) & Q(project__approval_status=ApprovalStatus.APPROVED) & Q(project__is_closed=0)
    #     if 'email_id' in obj_data:
    #         condition &= Q(email_id__icontains=obj_data['email_id'])
    #     if 'v_code' in obj_data:
    #         condition &= Q(v_code__icontains=obj_data['v_code'])
    #
    #     prjlist = CMSProjectInvitation.objects.using(self.schema).filter(condition).order_by('-created_date')[
    #               vys_page.get_offset():vys_page.get_query_limit()]
    #     # print(prjlist.query)
    #     list_length = len(prjlist)
    #     print("vow_proj summary", list_length)
    #     pr_list_data = NWisefinList()
    #     for prhdr in prjlist:
    #         pr_data = ProjectResponse()
    #         pr_data.set_id(prhdr.project.id)
    #         pr_data.set_code(prhdr.project.code)
    #         pr_data.set_title(prhdr.project.title)
    #         pr_data.set_description(prhdr.project.description)
    #         pr_data.set_submission_start_date(prhdr.project.submission_start_date)
    #         pr_data.set_submission_end_date(prhdr.project.submission_end_date)
    #         pr_data.set_is_user(prhdr.project.is_user)
    #         pr_data.entity_id = prhdr.project.entity_id
    #         pr_list_data.append(pr_data)
    #     vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
    #     pr_list_data.set_pagination(vpage)
    #     return pr_list_data

    def vow_invitation_project(self, project_id):
        invite_arr = []
        projectty_list = CMSProjectInvitation.objects.using(self.schema).filter(project_id=project_id, status=ActiveStatus.Active)
        for projectty in projectty_list:
            projectty_data = ProjectInvitationResponse()
            projectty_data.set_id(projectty.id)
            projectty_data.set_email_id(projectty.email_id)
            projectty_data.set_v_code(projectty.v_code)
            projectty_data.set_v_name(projectty.v_name)
            invite_arr.append(projectty_data)
        return invite_arr
