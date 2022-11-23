from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from cmsservice.controller import projecttypecontroller, projectcontroller, documenttypecontroller, \
    projectcmtcontroller, proposercontroller, cmsapprovalcontroller, projectidentification_controller,quesanscontroller, cmsquestiontypecontroller, vowcontroller, projectquestioncontroller,Legalclausecontroller,cmsemailcontroller

urlpatterns = [

    # master - Projecttype
    path('projecttype', projecttypecontroller.create_projecttype, name='projecttype'),
    path('projecttype/<projecttype_id>', projecttypecontroller.fetch_projecttype, name='projecttype'),

    # master - Documenttype
    path('documenttype', documenttypecontroller.Documenttype, name='creat_documenttype'),
    path('documenttype/<doctype_id>', documenttypecontroller.fetch_doctype, name='fetch_documenttype'),

    # project
    path('project', projectcontroller.create_project, name='project'),
    path('project/<project_id>', projectcontroller.fetch_project, name='fetch_project'),
    path('updateprojectclose/<project_id>', projectcontroller.updateprojectclose, name='updateprojectclose'),
    path('get_approvalstatus/<id>', projectcontroller.get_approvalstatus, name='get_approvalstatus'),
    path('project_approval/<project_id>',cmsapprovalcontroller.project_status_update,name='project_status_update'),
    path('project_approval_history/<project_id>',cmsapprovalcontroller.project_approval_history,name='project_approval_history'),
    path('project_parallel_app/<project_id>', projectcontroller.project_parallel_app, name='project_identification_approval'),
    path('get_viewtype',projectcontroller.get_viewtype,name='get_viewtype'),
    path('vow_project', projectcontroller.vow_project, name='project'),
    path('vow_fetchproject/<project_id>', projectcontroller.vow_fetchproject, name='vow_fetchproject'),
    path('project_finalcovernote/<project_id>', projectcontroller.project_finalizecovernote, name='project_finalizecovernote'),
    path('project_questiontype/<project_id>', projectcontroller.project_qtype, name='project_qtype'),

    # comments:
    path('comments/<ref_id>', projectcmtcontroller.create_comments, name='comments'),
    path('reply/<ref_id>', projectcmtcontroller.create_reply, name='reply'),
    # vowcomments:
    path('vowcomments/<ref_id>', projectcmtcontroller.vow_create_comments, name='vow_comments'),
    path('vowreply/<ref_id>', projectcmtcontroller.vow_create_reply, name='vowreply'),
    #questionanswer:
    path('quesans', quesanscontroller.create_answer, name='quesanswer'),
    path('quesansmap', quesanscontroller.create_answermapp, name='quesanswermapping'),
    path('cmsquestype', cmsquestiontypecontroller.create_cmsquestype, name='cmsquestype'),
    path('cmsquestypemap', cmsquestiontypecontroller.create_cmsquestypemap, name='cmsquestypemapping'),
    path('cmsquesansmap', quesanscontroller.create_ansmapp, name='cmsquesansmapping'),
    path('quesclassify', quesanscontroller.create_quesclassify, name='quesansclassification'),
    # project related question answer
    path('project_question/<project_id>', projectquestioncontroller.create_projquestion, name='projectquestion'),
    path('vow_projectanswer/<project_id>', projectquestioncontroller.proposal_answer, name='proposal_answer'),
    path('project_qtype_mapping/<project_id>', quesanscontroller.create_projansmap, name='projectquesmap'),
    path('cms_questionnaire/<pro_id>',quesanscontroller.fetch_questype,name='question_type_info'),
    path('cms_evaluation/<prop_id>',quesanscontroller.fetch_evaluation,name='answer_evaluation'),
    # catalog
    path('proposal_catalog/<proposal_id>',projectquestioncontroller.create_Catalog,name='activity_catlog'),
    # vowquestionanswer:
    path('vow_quesans/<project_id>', quesanscontroller.vow_create_answer, name='vowquesanswer'),
    path('vow_answer_migration/<proposer_id>', quesanscontroller.prop_create_answer, name='vowquesanswer'),
    path('vowquesansmap', quesanscontroller.vow_create_answermapp, name='vowquesanswermapping'),
    path('vowcmsquestype', cmsquestiontypecontroller.vow_create_cmsquestype, name='vowcmsquestype'),
    path('vowcmsquestypemap', cmsquestiontypecontroller.vow_create_cmsquestypemap, name='vowcmsquestypemapping'),
    path('vowcmsquesansmap', quesanscontroller.vow_createansmap, name='vowcmsquestypemapping'),
    path('vow_answer_response', quesanscontroller.vow_quesclassify, name='vowquesansclassification'),
    path('vow_questionnaire/<pro_id>', quesanscontroller.fetch_vow_questype, name='question_type_info'),
    # proposal
    path('proposal/<project_id>', proposercontroller.create_proposer, name='create_proposer'),
    path('get_proposal/<proposal_id>',proposercontroller.fetch_proposer, name='fetch_proposer'),
    path('vow_proposal/<project_id>', proposercontroller.vow_create_proposer, name='vow_create_project'),
    path('vow_get_proposal/<project_id>', proposercontroller.vow_fetch_proposer, name='vow_fetch_proposer'),
    path('proposal_approval/<proposal_id>',cmsapprovalcontroller.proposed_status_update, name='proposer_status_update'),
    path('proposal_approval_history/<proposed_id>',cmsapprovalcontroller.proposed_approval_history, name='proposer_approval_history'),
    path('assign_proposal/<project_id>',cmsapprovalcontroller.assign_proposed, name='assign_proposed'),
    path('proposal_parallel_approver/<project_id>',cmsapprovalcontroller.proposal_parallel_approver, name='assign_proposed'),
    path('vendor_get', vowcontroller.vendor_get, name='vendor_get'),
    #  cms to vendor push
    path('proposal_vendorcreate/<proposal_id>', vowcontroller.proposal_vendorcreate, name='proposal_vendorcreate'),
    path('proposal_submit/<project_id>', proposercontroller.proposal_submit, name='proposal_submit'),

    path('conv_dt/<id>', projectcontroller.conv_dt, name='conv_dt'),
    path('proposal_shortlist', cmsapprovalcontroller.proposal_shortlist, name='proposal_shortlist'),
    path('proposal_shortlistfinalize', cmsapprovalcontroller.proposal_shortlistfinalize, name='proposal_shortlistfinalize'),
    path('shortlist_proposer_list/<project_id>', cmsapprovalcontroller.shortlist_proposer_list, name='shortlist_proposer_list'),
    path('cms_notepad/<proposal_id>', proposercontroller.cms_notepad, name='cms_notepad'),
    path('vow_cms_notepad/<proposal_id>', proposercontroller.vow_cms_notepad, name='vow_cms_notepad'),
    # project identification
    path('projectidentification', projectidentification_controller.projectidentification, name='projectidentification'),
    path('project_identification_approval/<project_id>',projectidentification_controller.project_identification_approval,name='project_identification_approval'),
    path('projectidentification_parallel_app/<project_id>',projectidentification_controller.projectidentification_parallel_app,name='project_identification_approval'),
    path('projectidentification_get/<project_iden_id>',projectidentification_controller.projectidentification_get,name='project_identification_approval'),
    path('projectidentificationclosure/<project_id>',projectidentification_controller.project_identification_closure,name='project_identiofication_closure'),
    # version api
    path('project_viewsummary/<project_id>', projectcontroller.project_viewsummary, name='project_viewsummary'),
    path('proposal_viewsummary/<proposal_id>', proposercontroller.proposal_viewsummary, name='proposal_viewsummary'),
    path('project_version/<project_id>', projectcontroller.project_version, name='project_version'),
    path('proposal_version/<proposal_id>', proposercontroller.proposal_version, name='proposal_version'),
    path('vow_proposal_version/<proposal_id>', proposercontroller.vow_proposal_version, name='vow_proposal_version'),
    path('vow_proposal_viewsummary/<proposal_id>', proposercontroller.vow_proposal_viewsummary, name='vow_proposal_viewsummary'),
    path('vow_proposal_tranhistory/<proposal_id>', cmsapprovalcontroller.vow_proposal_tranhistory, name='vow_proposal_tranhistory'),

    # path('project_proposal_approval/<project_id>',cmsapprovalcontroller.project_proposal_approval,name='project_proposal_approval'),
    #  filter approval status
    path('approval_status_search',projectcontroller.approval_status_search,name='approval_status_search'),
    # path('questionary_group_permission/<proposal_id>',proposercontroller.questionary_group_list,name='questionary_group_list'),
    path('questionary_group_approval/<proposal_id>',proposercontroller.questionary_group_approve,name='questionary_group_approve'),
    # questionary resubmit
    path('vow_questionary_resubmit/<proposal_id>',proposercontroller.vow_questionary_resubmit,name='vow_questionary_resubmit'),

    path('project_identification_resubmit/<identification_id>',projectidentification_controller.project_identification_resubmit,name='project_identification_resubmit'),
    path('project_resubmit/<project_id>', projectcontroller.project_resubmit, name='project_resubmit'),
    path('new_evaluator/<project_id>', projectcontroller.new_evaluator, name='question_answer'),
     # final evaluation
    path('final_evaluation/<project_id>', quesanscontroller.final_evaluation, name='final_evaluation'),
    path('move_to_finalapprover/<project_id>', cmsapprovalcontroller.move_to_finalapprover,name='move_to_finalapprover'),
    # questionary status check vow /cms
    path('q_status_check/<proposal_id>', quesanscontroller.q_approval_status_check,name='q_approval_status_check'),

    #legal clause
    path('legal_clause_insert', Legalclausecontroller.legal_clause_insert,name='legal_clause_insert'),
    path('legal_clause_get/<legal_clause_id>', Legalclausecontroller.legal_clause_get,name='legal_clause_insert'),
    path('subclause/<parent_id>',Legalclausecontroller.subclause,name='legal_insert'),
    # path('legal_clause_approve/<legal_clause_id>', Legalclausecontroller.legal_clause_approval,name='legal_clause_approve'),
    path('proposal_legal_Mapping/<proposal_id>', Legalclausecontroller.proposal_legal_Mapping,name='proposal_legal_Mapping'),
    path('legal_agreement/<proposal_id>', Legalclausecontroller.legal_agreement,name='legal_agreement'),
    path('proposal_agreement/<proposal_id>', Legalclausecontroller.proposal_agreement,name='legal_agreement'),
    path('clause_get', Legalclausecontroller.clause_get,name='clause_get'),

    #  agreement move to vendor
    path('agreement_moveto_vendor/<proposal_agreement_id>', Legalclausecontroller.agreement_moveto_vendor,name='agreement_moveto_vendor'),
    #  vow agreement accept
    path('vow_agreement_accepted/<proposal_agreement_id>', Legalclausecontroller.vow_agreement_accepted,name='agreement_moveto_vendor'),
    # vow agreement return
    path('vow_agreement_return/<proposal_agreement_id>', Legalclausecontroller.vow_agreement_return,name='agreement_return_to_vendor'),

    path('vow_legal_agreement_get/<proposal_id>', Legalclausecontroller.vow_legal_agreement_get,name='agreement_moveto_vendor'),
    path('legal_agreement_download/<legal_clause_id>', Legalclausecontroller.legal_agreement_download,name='legal_agreement_download'),
    path('vow_legal_agreement_download/<legal_clause_id>', Legalclausecontroller.vow_legal_agreement_download,name='legal_agreement_download'),
    path('legal_clause_typedropdown', Legalclausecontroller.legal_clause_typedropdown,name='legal_clause_typedropdown'),
    path('agreement_superscript/<proposal_id>',Legalclausecontroller.agreement_superscript_comments,name='agreement_superscript'),
    path('vow_agreement_superscript/<agreement_id>',Legalclausecontroller.vow_agreement_superscript,name='agreement_superscript'),

    path('proposal_return/<proposal_id>', proposercontroller.proposal_return, name='create_proposer'),
    path('proposal_report', proposercontroller.proposal_report, name='proposal_report'),
    path('approved_proposal', proposercontroller.approved_proposal, name='approved_proposal'),

    path('cms_superscript_comments/<superscript_id>', Legalclausecontroller.cms_superscript_comments,name='superscriptcomments'),
    path('vow_superscript_comments/<superscript_id>', Legalclausecontroller. vow_superscript_comments,name='superscriptcomments'),
    path('agreementtype',projecttypecontroller.create_agreementtype,name='agreementtype'),
    path('agreementtype/<agreementtype_id>',projecttypecontroller.agreementtype,name='agreementtype'),
    path('mailScheduler',cmsemailcontroller.mailScheduler,name='emailscheduler')
              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)