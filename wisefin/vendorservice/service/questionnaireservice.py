from vendorservice.models.vendormodels import VendorGrpAnswers, VendorModificationRel
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.vendor_outsourcing_questionnaire import QuestionService
from vendorservice.data.response.questionnaireresponse import QuestionnaireResponse
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from vendorservice.service.vendorservice import VendorService
from vendorservice.util.vendorutil import VendorRefType, ModifyStatus, RequestStatusUtil
from django.db.models import Q


class QuestionnaireService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def create_questions_bcp(self, vendor_id, question_type, response_obj, employee_id):
        if response_obj.get_ans_bool() == '' and response_obj.get_remarks() == '':
            value = ''
            return value
        else:
            if (response_obj.get_id() is not None) and (response_obj.get_id() != ''):
                VendorGrpAnswers.objects.using(self._current_app_schema()).filter(
                    id=response_obj.get_id()).update(vendor_id=vendor_id, ans_bool=response_obj.get_ans_bool(),
                                                     remarks=response_obj.get_remarks(), ques_type=question_type,
                                                     ques_id=response_obj.get_ques_id(), updated_by=employee_id,
                                                     updated_date=timezone.now(), entity_id=self._entity_id(),portal_flag=response_obj.get_portal_flag())
                print('updated------'+str(response_obj.get_ques_id()))
                quest = VendorGrpAnswers.objects.using(self._current_app_schema()).get(id=response_obj.get_id())
            else:
                quest = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                    vendor_id=vendor_id, ans_bool=response_obj.get_ans_bool(), remarks=response_obj.get_remarks(),
                    ques_type=question_type, ques_id=response_obj.get_ques_id(), created_by=employee_id,
                    entity_id=self._entity_id(),portal_flag=response_obj.get_portal_flag())
                print('created------' + str(response_obj.get_ques_id()))
            return quest.id

    def fetch_questionnaries_bcp(self, vendor_id, question_type):
        question_service = QuestionService(self._scope())
        questions = question_service.get_questions(question_type)
        question_list_data = NWisefinList()
        for question in questions:
            resp_obj = QuestionnaireResponse()
            resp_obj.set_question(question.questions)
            resp_obj.set_ques_id(question.ques_id)
            try:
                answer = VendorGrpAnswers.objects.using(self._current_app_schema()).get(vendor_id=vendor_id,
                                                                                        ques_type=question_type,
                                                                                        ques_id=question.ques_id,
                                                                                        entity_id=self._entity_id(),
                                                                                        modify_status=-1)
                resp_obj.set_id(answer.id)
                resp_obj.set_ans_bool(answer.ans_bool)
                resp_obj.set_remarks(answer.remarks)
                resp_obj.set_modify_status(answer.modify_status)
                resp_obj.set_portal_flag(answer.portal_flag)
            except:
                resp_obj.set_id('')
                resp_obj.set_ans_bool('')
                resp_obj.set_remarks('')
                resp_obj.set_modify_status('')
            question_list_data.append(resp_obj)
        return question_list_data

    def create_questions_due(self, vendor_id, question_type, response_obj, employee_id):
        if response_obj.get_direction() == '' and response_obj.get_remarks() == '':
            value = ''
            return value
        else:
            if (response_obj.get_id() is not None) and (response_obj.get_id() != ''):
                VendorGrpAnswers.objects.using(self._current_app_schema()).filter(
                    id=response_obj.get_id()).update(vendor_id=vendor_id, direction=response_obj.get_direction(),
                                                     remarks=response_obj.get_remarks(), ques_type=question_type,
                                                     ques_id=response_obj.get_ques_id(), updated_by=employee_id,
                                                     updated_date=timezone.now(), entity_id=self._entity_id(),portal_flag=response_obj.get_portal_flag())
                print('updated------'+str(response_obj.get_ques_id()))
                quest = VendorGrpAnswers.objects.using(self._current_app_schema()).get(id=response_obj.get_id())
            else:
                quest = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                    vendor_id=vendor_id, direction=response_obj.get_direction(), remarks=response_obj.get_remarks(),
                    ques_type=question_type, ques_id=response_obj.get_ques_id(), created_by=employee_id,
                    entity_id=self._entity_id(), portal_flag=response_obj.get_portal_flag())
                print('created------' + str(response_obj.get_ques_id()))
            return quest.id

    def fetch_questionnaries_due(self, vendor_id, question_type):
        question_service = QuestionService(self._scope())
        questions = question_service.get_questions(question_type)
        question_list_data = NWisefinList()
        for question in questions:
            resp_obj = QuestionnaireResponse()
            resp_obj.set_question(question.questions)
            resp_obj.set_ques_id(question.ques_id)
            try:
                answer = VendorGrpAnswers.objects.using(self._current_app_schema()).get(vendor_id=vendor_id,
                                                                                        ques_type=question_type,
                                                                                        ques_id=question.ques_id,
                                                                                        entity_id=self._entity_id(),
                                                                                        modify_status=-1)
                resp_obj.set_id(answer.id)
                resp_obj.set_direction(answer.direction)
                resp_obj.set_remarks(answer.remarks)
                resp_obj.set_modify_status(answer.modify_status)
                resp_obj.set_portal_flag(answer.portal_flag)
            except:
                resp_obj.set_id('')
                resp_obj.set_direction('')
                resp_obj.set_remarks('')
                resp_obj.set_modify_status('')
            question_list_data.append(resp_obj)
        return question_list_data

    # modification
    def modify_question_bcp(self, vendor_id, question_type, response_obj, employee_id):
        vendor_service = VendorService(self._scope())
        # ref_flag = vendor_service.checkmodify_rel(VendorRefType.BCP_QUESION, response_obj.get_id())
        if response_obj.get_ans_bool() == '' and response_obj.get_remarks() == '':
            value = ''
            return value
        else:
            if (response_obj.get_id() is not None) and (response_obj.get_id() != ''):
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.BCP_QUESION, response_obj.get_id())
                if ref_flag == True:
                    VendorGrpAnswers.objects.using(self._current_app_schema()).filter(
                        id=response_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id, ans_bool=response_obj.get_ans_bool(),
                                                         remarks=response_obj.get_remarks(), ques_type=question_type,
                                                         ques_id=response_obj.get_ques_id(), entity_id=self._entity_id(),portal_flag=response_obj.get_portal_flag())
                    print('mod-----update' + str(response_obj.get_ques_id()))
                    bcp = VendorGrpAnswers.objects.using(self._current_app_schema()).get(id=response_obj.get_id(),entity_id=self._entity_id())
                else:
                    bcp = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                        vendor_id=vendor_id, ans_bool=response_obj.get_ans_bool(),
                                                         remarks=response_obj.get_remarks(), ques_type=question_type,
                                                         ques_id=response_obj.get_ques_id(), created_by=employee_id,
                                                         entity_id=self._entity_id(),  modify_status=ModifyStatus.update,
                        modified_by=employee_id, modify_ref_id=response_obj.get_id(), portal_flag=response_obj.get_portal_flag())
                    due_update = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(
                        id=response_obj.get_id(), entity_id=self._entity_id()).update(
                        modify_ref_id=bcp.id)
                    print('mod-----create_update' + str(response_obj.get_ques_id()))
                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                           ref_id=response_obj.get_id(),
                                                                                           ref_type=VendorRefType.BCP_QUESION,
                                                                                           mod_status=ModifyStatus.update,
                                                                                           modify_ref_id=bcp.id,
                                                                                           entity_id=self._entity_id())
            else:
                bcp = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                    vendor_id=vendor_id, ans_bool=response_obj.get_ans_bool(), remarks=response_obj.get_remarks(),
                    ques_type=question_type, ques_id=response_obj.get_ques_id(), created_by=employee_id,
                    modify_status=ModifyStatus.create, modified_by=employee_id, entity_id=self._entity_id(), portal_flag=response_obj.get_portal_flag())
                print('mod-----create' + str(response_obj.get_ques_id()))

                bcp.modify_ref_id = bcp.id
                bcp.save()

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                       ref_id=bcp.id,
                                                                                       ref_type=VendorRefType.BCP_QUESION,
                                                                                       mod_status=ModifyStatus.create,
                                                                                       modify_ref_id=bcp.id,
                                                                                       entity_id=self._entity_id())
            return bcp.id

    def bcp_question_list(self, vendor_id, question_type):
        question_service = QuestionService(self._scope())
        questions = question_service.get_questions(question_type)
        question_list_data = NWisefinList()
        for question in questions:
            resp_obj = QuestionnaireResponse()
            resp_obj.set_question(question.questions)
            resp_obj.set_ques_id(question.ques_id)
            # resp_obj.set_portal_flag(question.portal_flag)
            condition = Q(vendor_id=vendor_id, ques_type=question_type, entity_id=self._entity_id(),
                          ques_id=question.ques_id)
            condition &= ~Q(modify_status=-1)
            answer = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(condition)
            old_data = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                           ques_type=question_type,
                                                                                           ques_id=question.ques_id,
                                                                                           entity_id=self._entity_id(),
                                                                                           modify_status=-1)
            if len(answer) == 0:
                old_answer = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                        ques_type=question_type,
                                                                                        ques_id=question.ques_id,
                                                                                        entity_id=self._entity_id(),
                                                                                        modify_status=-1)
                if len(old_answer) == 0:
                    resp_obj.set_id('')
                    resp_obj.set_ans_bool('')
                    resp_obj.set_remarks('')
                    resp_obj.set_modify_status('')
                    resp_obj.set_old_remarks('')
                    resp_obj.set_old_ans_bool('')
                else:
                    resp_obj.set_id(old_answer[0].id)
                    resp_obj.set_ans_bool(old_answer[0].ans_bool)
                    resp_obj.set_remarks(old_answer[0].remarks)
                    resp_obj.set_modify_status(old_answer[0].modify_status)
                    resp_obj.set_old_remarks(old_answer[0].remarks)
                    resp_obj.set_old_ans_bool(old_answer[0].ans_bool)
            else:
                resp_obj.set_id(answer[0].id)
                resp_obj.set_ans_bool(answer[0].ans_bool)
                resp_obj.set_remarks(answer[0].remarks)
                resp_obj.set_modify_status(answer[0].modify_status)
                if len(old_data) == 0:
                    resp_obj.set_old_remarks('')
                    resp_obj.set_old_ans_bool('')
                else:
                    resp_obj.set_old_remarks(old_data[0].remarks)
                    resp_obj.set_old_ans_bool(old_data[0].ans_bool)
            question_list_data.append(resp_obj)
        return question_list_data



    def modify_question_due(self, vendor_id, question_type, response_obj, employee_id):
        vendor_service = VendorService(self._scope())
        if response_obj.get_direction() == '' and response_obj.get_remarks() == '':
            value = ''
            return value
        else:
            if (response_obj.get_id() is not None) and (response_obj.get_id() != ''):
                ref_flag = vendor_service.checkmodify_rel(VendorRefType.DUE_DELIGENCE, response_obj.get_id())
                if ref_flag == True:
                    VendorGrpAnswers.objects.using(self._current_app_schema()).filter(
                        id=response_obj.get_id(), entity_id=self._entity_id()).update(vendor_id=vendor_id, direction=response_obj.get_direction(),
                                                         remarks=response_obj.get_remarks(), ques_type=question_type,
                                                         ques_id=response_obj.get_ques_id(), entity_id=self._entity_id(), portal_flag=response_obj.get_portal_flag())
                    due = VendorGrpAnswers.objects.using(self._current_app_schema()).get(id=response_obj.get_id(),entity_id=self._entity_id())
                    print('mod-----update'+str(response_obj.get_ques_id()))
                else:
                    due = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                        vendor_id=vendor_id, direction=response_obj.get_direction(),
                                                         remarks=response_obj.get_remarks(), ques_type=question_type,
                                                         ques_id=response_obj.get_ques_id(), created_by=employee_id,
                                                         entity_id=self._entity_id(), modify_status=ModifyStatus.update,
                        modified_by=employee_id, modify_ref_id=response_obj.get_id(), portal_flag=response_obj.get_portal_flag())
                    due_update = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=response_obj.get_id(), entity_id=self._entity_id()).update(
                    modify_ref_id=due.id)
                    print('mod-----create_update' + str(response_obj.get_ques_id()))

                    VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                           ref_id=response_obj.get_id(),
                                                                                           ref_type=VendorRefType.DUE_DELIGENCE,
                                                                                           mod_status=ModifyStatus.update,
                                                                                           modify_ref_id=due.id,
                                                                                           entity_id=self._entity_id())
            else:
                due = VendorGrpAnswers.objects.using(self._current_app_schema()).create(
                    vendor_id=vendor_id, direction=response_obj.get_direction(), remarks=response_obj.get_remarks(),
                    ques_type=question_type, ques_id=response_obj.get_ques_id(), created_by=employee_id,
                    modify_status=ModifyStatus.create, modified_by=employee_id, entity_id=self._entity_id(), portal_flag=response_obj.get_portal_flag())
                print('mod-----create' + str(response_obj.get_ques_id()))

                due.modify_ref_id = due.id
                due.save()

                VendorModificationRel.objects.using(self._current_app_schema()).create(vendor_id=vendor_id,
                                                                                       ref_id=due.id,
                                                                                       ref_type=VendorRefType.DUE_DELIGENCE,
                                                                                       mod_status=ModifyStatus.create,
                                                                                       modify_ref_id=due.id,
                                                                                       entity_id=self._entity_id())
            return due.id

    def due_question_list(self, vendor_id, question_type):
        question_service = QuestionService(self._scope())
        questions = question_service.get_questions(question_type)
        question_list_data = NWisefinList()

        for question in questions:
            resp_obj = QuestionnaireResponse()
            resp_obj.set_question(question.questions)
            resp_obj.set_ques_id(question.ques_id)
            # resp_obj.set_portal_flag(question.portal_flag)
            condition = Q(vendor_id=vendor_id, ques_type=question_type, entity_id=self._entity_id(), ques_id=question.ques_id)
            condition &= ~Q(modify_status=-1)
            answer = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(condition)
            old_data = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                           ques_type=question_type,
                                                                                           ques_id=question.ques_id,
                                                                                           entity_id=self._entity_id(),
                                                                                           modify_status=-1)
            if len(answer) == 0:
                old_answer = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(vendor_id=vendor_id,
                                                                                        ques_type=question_type,
                                                                                        ques_id=question.ques_id,
                                                                                        entity_id=self._entity_id(),
                                                                                        modify_status=-1)
                if len(old_answer) == 0:
                    resp_obj.set_id('')
                    resp_obj.set_direction('')
                    resp_obj.set_remarks('')
                    resp_obj.set_modify_status('')
                    resp_obj.set_old_remarks('')
                    resp_obj.set_old_direction('')
                else:
                    resp_obj.set_id(old_answer[0].id)
                    resp_obj.set_direction(old_answer[0].direction)
                    resp_obj.set_remarks(old_answer[0].remarks)
                    resp_obj.set_modify_status(old_answer[0].modify_status)
                    resp_obj.set_old_remarks(old_answer[0].remarks)
                    resp_obj.set_old_direction(old_answer[0].direction)
            else:
                resp_obj.set_id(answer[0].id)
                resp_obj.set_direction(answer[0].direction)
                resp_obj.set_remarks(answer[0].remarks)
                resp_obj.set_modify_status(answer[0].modify_status)
                if len(old_data) == 0:
                    resp_obj.set_old_remarks('')
                    resp_obj.set_old_direction('')
                else:
                    resp_obj.set_old_remarks(old_data[0].remarks)
                    resp_obj.set_old_direction(old_data[0].direction)
            question_list_data.append(resp_obj)
        return question_list_data

    def modification_action_bcp(self, vendor_id, question_type, employee_id):
        new_data = self.bcp_question_list(vendor_id,question_type)
        old_data = self.fetch_questionnaries_bcp(vendor_id, question_type)
        new_list = new_data.data
        old_list = old_data.data
        for new in new_list:
            for old in old_list:
                if new.ques_id == old.ques_id:
                    if (new.ans_bool == old.ans_bool) and (new.remarks == old.remarks):
                        pass
                    else:
                        if old.ans_bool == "":
                            created = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=new.id, entity_id=self._entity_id()).update(
                                modify_status=-1,
                                modify_ref_id=-1,
                                modified_by=-1)
                            print('created')
                        else:
                            updated = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=old.id, entity_id=self._entity_id()).update(
                                vendor_id=vendor_id, ans_bool=new.ans_bool,
                                remarks=new.remarks, ques_type=question_type,
                                ques_id=new.ques_id, updated_by=employee_id,
                                updated_date=timezone.now(), entity_id=self._entity_id()
                            )
                            print('updated')
                            delete = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=new.id, entity_id=self._entity_id()).delete()
                            print('deleted')
        return

    def modification_action_due(self, vendor_id, question_type, employee_id):
        new_data = self.due_question_list(vendor_id,question_type)
        old_data = self.fetch_questionnaries_due(vendor_id, question_type)
        new_list = new_data.data
        old_list = old_data.data
        for new in new_list:
            for old in old_list:
                if new.ques_id == old.ques_id:
                    if (new.direction == old.direction) and (new.remarks == old.remarks):
                        pass
                    else:
                        if old.direction == "":
                            created = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=new.id, entity_id=self._entity_id()).update(
                                modify_status=-1,
                                modify_ref_id=-1,
                                modified_by=-1)
                            print('created')
                        else:
                            updated = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=old.id, entity_id=self._entity_id()).update(
                                vendor_id=vendor_id, direction=new.direction,
                                remarks=new.remarks, ques_type=question_type,
                                ques_id=new.ques_id, updated_by=employee_id,
                                updated_date=timezone.now(), entity_id=self._entity_id()
                            )
                            print('updated')
                            delete = VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=new.id, entity_id=self._entity_id()).delete()
                            print('deleted')
        return

    def modification_reject_bcp(self, vendor_id, question_type):
        new_data = self.bcp_question_list(vendor_id, question_type)
        old_data = self.fetch_questionnaries_bcp(vendor_id, question_type)
        new_list = new_data.data
        old_list = old_data.data
        for data in new_list:
            if data.id == '' or data.id == None:
                pass
            else:
                if data.modify_status != -1:
                    VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).delete()
        for data in old_list:
            if data.id == '' or data.id == None:
                pass
            else:
                VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).update(modify_ref_id=-1)
        return

    def modification_reject_due(self, vendor_id, question_type):
        new_data = self.due_question_list(vendor_id, question_type)
        old_data = self.fetch_questionnaries_due(vendor_id, question_type)
        new_list = new_data.data
        old_list = old_data.data
        for data in new_list:
            if data.id == '' or data.id == None:
                pass
            else:
                if data.modify_status != -1:
                    VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).delete()
        for data in old_list:
            if data.id == '' or data.id == None:
                pass
            else:
                VendorGrpAnswers.objects.using(self._current_app_schema()).filter(id=data.id, entity_id=self._entity_id()).update(modify_ref_id=-1)
        return
