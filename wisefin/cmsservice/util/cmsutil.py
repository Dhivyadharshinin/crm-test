from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
from masterservice.util.masterutil import Input_type
from docservice.util.docutil import DocPrefix

class ActiveStatus:
    Active = 1
    Delete = 0


# attach
class DocUtil:
    project = 1
    proposer = 2
    comments = 3
    project_identification = 4
    # project_strategy =5
    proposal_finalize = 5
    LegalClauses=6
    Questionnaire=7

    project_val = "Project"
    proposer_val = "Proposer"
    comments_val = "Comments"
    project_identification_val = "Project Identification"
    # project_strategy_val = "Project Strategy"
    proposal_finalize_val = "Proposer Finalize"
    LegalClauses_val = "Legal Clauses"
    Questionnaire_val ="Questionnaire"


# Covernote
class CovernoteUtil:
    project = 1
    proposer = 2
    proposal_finalize = 3
    project_identification = 4
    project_strategy = 5
    proposal_execution = 6
    proposal_financial = 7

    project_val = "Project"
    proposer_val = "Proposer"
    proposal_finalize_val = "Proposal Finalize"
    project_identification_val = "Project Identification"
    project_strategy_val = "Project Strategy"
    proposal_execution_val = "Project Execution"
    proposal_financial_val = "Financial"


class Trantype:
    creator = 1
    approver = 2
    collaborator = 3
    q_approver = 4
    proposal_approver = 5
    shortlist_approver = 6

class Mailtotypeutil:
    employee = 1
    group = 2
    vendor = 3

class TranApproverType:
    employee = 1
    group = 2

    employee_val = 'Employee'
    group_val = 'Group'


class TranStatus:
    creator = 0
    pending = 1
    awaiting = 2
    approved = 3
    rejected = 4
    reviwed = 5

    creator_val = 'Viewer'
    pending_val = 'Pending'
    awaiting_val = 'Awaiting'
    approved_val = 'Approved'
    rejected_val = 'Rejected'
    reviwed_val = 'Reviwed'


class ApprovalStatus:
    DRAFT = 1
    PENDING = 2
    APPROVED = 3
    REJECTED = 4
    REVIEW = 5
    SHORTLISTED = 6
    SHORTLISTED_UNDO = 7
    FINALIZED = 8
    EVALUATION=9

    DRAFT_VAL = "DRAFT"
    PENDING_VAL = "PENDING"
    APPROVED_VAL = "APPROVED"
    REJECTED_VAL = "REJECTED"
    REVIEW_VAL = "REVIEW"
    SHORTLISTED_VAL = "SHORTLISTED"
    SHORTLISTED_UNDO_VAL = "SHORTLISTED UNDO"
    FINALIZED_VAL = "FINALIZED"
    EVALUATION_VAL='UNDER EVALUATION'


def get_totype(number):
    if (number == TranApproverType.employee):
        d = {"id": TranApproverType.employee, "text": TranApproverType.employee_val}
    elif (number == TranApproverType.group):
        d = {"id": TranApproverType.group, "text": TranApproverType.group_val}
    else:
        d = {"id": None, "text": None}
    return d


def get_approvalstatus(number):
    if (number == ApprovalStatus.DRAFT):
        d = {"id": ApprovalStatus.DRAFT, "text": ApprovalStatus.DRAFT_VAL}
    elif (number == ApprovalStatus.PENDING):
        d = {"id": ApprovalStatus.PENDING, "text": ApprovalStatus.PENDING_VAL}
    elif (number == ApprovalStatus.EVALUATION):
        d = {"id": ApprovalStatus.EVALUATION, "text": ApprovalStatus.EVALUATION_VAL}
    elif (number == ApprovalStatus.APPROVED):
        d = {"id": ApprovalStatus.APPROVED, "text": ApprovalStatus.APPROVED_VAL}
    elif (number == ApprovalStatus.REJECTED):
        d = {"id": ApprovalStatus.REJECTED, "text": ApprovalStatus.REJECTED_VAL}
    elif (number == ApprovalStatus.REVIEW):
        d = {"id": ApprovalStatus.REVIEW, "text": ApprovalStatus.REVIEW_VAL}
    else:
        d = {"id": None, "text": None}
    return d


def get_transtatus(number):
    if (number == TranStatus.creator):
        d = {"id": TranStatus.creator, "text": TranStatus.creator_val}
    elif (number == TranStatus.pending):
        d = {"id": TranStatus.pending, "text": TranStatus.pending_val}
    elif (number == TranStatus.awaiting):
        d = {"id": TranStatus.awaiting, "text": TranStatus.awaiting_val}
    elif (number == TranStatus.approved):
        d = {"id": TranStatus.approved, "text": TranStatus.approved_val}
    elif (number == TranStatus.rejected):
        d = {"id": TranStatus.rejected, "text": TranStatus.rejected_val}
    elif (number == TranStatus.reviwed):
        d = {"id": TranStatus.reviwed, "text": TranStatus.reviwed_val}
    else:
        d = {"id": None, "text": None}
    return d


class CodePrefix:
    ProjectType = 1
    DocumentType = 2
    Project = 3
    Proposal = 4
    ProjectIdentification = 5
    AgreementType = 6

    ProjectType_VAL = "PTYPE"
    DocumentType_VAL = "DTYPE"
    Project_VAL = "PROJT"
    Proposal_VAL = "PROPO"
    ProjectIdentification_VAL = "PRJID"
    AgreementType_VAL = "AGRID"


def get_fileextension_val(extension):
    if extension in ['txt', 'TXT', 'doc', 'pdf', 'PDF', 'ppt', 'pot', 'pps', 'pptx', 'odt', 'odg', 'odp', 'ods', 'ODS',
                     'docx', 'docm', 'dotx', 'dotm', 'docb',
                     'xlsx', 'XLSX', 'xls', 'xlt', 'xlm', 'xlsm', 'xltx', 'xltm', 'jpg', 'JPG', 'jpeg', 'JPEG', 'tiff',
                     'TIFF', 'tif', 'TIF', 'png', 'PNG']:
        return True
    else:
        return False


class CommentsUtil:
    comments = 1
    approved = 2
    rejected = 3
    reviewed = 4
    reply = 5

    comments_val = 'Comments'
    approved_val = 'Approved'
    rejected_val = 'Rejected'
    reviewed_val = 'Reviewed'
    reply_val = 'Reply'

class CommentsRefTypeUtil:
    project =1
    proposal =2
    superscript=3


class SearchUtil:
    PendingApproval = 1
    CreatedByMe = 2
    ApprovedByMe = 3
    RejectedByMe = 4
    FullApproved = 5
    Draft = 6
    collaborator = 7
    ReturnByMe = 8
    PendingReview = 9
    CreatedByGroup = 10
    EVALUATION=11

    PendingApproval_val = 'Pending Approval'
    CreatedByMe_val = 'Created By Me'
    ApprovedByMe_val = 'Approved By Me'
    RejectedByMe_val = 'Rejected By Me'
    FullApproved_val = 'Approved'
    Draft_val = 'Draft'
    collaborator_val = 'collaborator'
    Return_val = "Return By Me"
    PendingReview_val = "Pending Review"
    CreatedByGroup_val = "Created By Group"
    EVALUATION_VAL='Under Evaluation'


def get_SearchUtil(number):
    if (number == SearchUtil.PendingApproval):
        d = {"id": SearchUtil.PendingApproval, "text": SearchUtil.PendingApproval_val}
    elif (number == SearchUtil.CreatedByMe):
        d = {"id": SearchUtil.CreatedByMe, "text": SearchUtil.CreatedByMe_val}
    elif (number == SearchUtil.ApprovedByMe):
        d = {"id": SearchUtil.ApprovedByMe, "text": SearchUtil.ApprovedByMe_val}
    elif (number == SearchUtil.RejectedByMe):
        d = {"id": SearchUtil.RejectedByMe, "text": SearchUtil.RejectedByMe_val}
    elif (number == SearchUtil.FullApproved):
        d = {"id": SearchUtil.FullApproved, "text": SearchUtil.FullApproved_val}
    elif (number == SearchUtil.ReturnByMe):
        d = {"id": SearchUtil.ReturnByMe, "text": SearchUtil.Return_val}
    elif (number == SearchUtil.PendingReview):
        d = {"id": SearchUtil.PendingReview, "text": SearchUtil.PendingReview_val}
    elif (number == SearchUtil.CreatedByGroup):
        d = {"id": SearchUtil.CreatedByGroup, "text": SearchUtil.CreatedByGroup_val}
    else:
        d = {"id": None, "text": None}
    return d


def dd_SearchUtil(id):
    if int(id) == DocUtil.proposer:
        idarr = [SearchUtil.PendingApproval, SearchUtil.ApprovedByMe,
                 SearchUtil.RejectedByMe, SearchUtil.FullApproved, SearchUtil.Draft]
        typearr = [SearchUtil.PendingApproval_val, SearchUtil.ApprovedByMe_val,
                   SearchUtil.RejectedByMe_val, SearchUtil.FullApproved_val, SearchUtil.Draft_val]
    else:
        idarr = [SearchUtil.PendingApproval, SearchUtil.CreatedByMe, SearchUtil.ApprovedByMe,
                 SearchUtil.RejectedByMe, SearchUtil.FullApproved, SearchUtil.ReturnByMe, SearchUtil.PendingReview,
                 SearchUtil.CreatedByGroup]

        typearr = [SearchUtil.PendingApproval_val, SearchUtil.CreatedByMe_val, SearchUtil.ApprovedByMe_val,
                   SearchUtil.RejectedByMe_val, SearchUtil.FullApproved_val, SearchUtil.Return_val,
                   SearchUtil.PendingReview_val, SearchUtil.CreatedByGroup_val]

    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist


class is_Closed:
    OPEN = 0
    CLOSED = 1

    OPEN_Type = "Open"
    CLOSED_Type = "Closed"


def get_commentstype(number):
    if number == CommentsUtil.comments:
        d = {"id": CommentsUtil.comments, "text": CommentsUtil.comments_val}
    elif number == CommentsUtil.approved:
        d = {"id": CommentsUtil.approved, "text": CommentsUtil.approved_val}
    elif number == CommentsUtil.rejected:
        d = {"id": CommentsUtil.rejected, "text": CommentsUtil.rejected_val}
    elif number == CommentsUtil.reviewed:
        d = {"id": CommentsUtil.reviewed, "text": CommentsUtil.reviewed_val}
    elif number == CommentsUtil.reply:
        d = {"id": CommentsUtil.reply, "text": CommentsUtil.reply_val}
    else:
        d = {"id": None, "text": None}
    return d


def get_commentsreftype(number):
    if number == DocUtil.project:
        d = {"id": DocUtil.project, "text": DocUtil.project_val}
    elif number == DocUtil.proposer:
        d = {"id": DocUtil.proposer, "text": DocUtil.proposer_val}
    elif number == DocUtil.comments:
        d = {"id": DocUtil.comments, "text": DocUtil.comments_val}
    elif number == DocUtil.project_identification:
        d = {"id": DocUtil.project_identification, "text": DocUtil.project_identification_val}
    else:
        d = {"id": None, "text": None}
    return d


def conversion(created_date):
    print(created_date)
    if created_date is not None:
        created_date1 = str(created_date)
        time = created_date1[10:]
        if (time == '') | (time == None):
            import time
            created_date = int(time.mktime(created_date.timetuple()) * 1000)
        else:
            created_date = int(created_date.timestamp() * 1000)
    else:
        created_date = None
    return created_date


class ViewType:
    ProspectiveVendor = 1
    ApprovedVendor = 2
    ApprovedAndProspectiveVendor = 3
    InternalOnly = 4

    ProspectiveVendor_val = 'Prospective Vendor'
    ApprovedVendor_val = 'Approved Vendor'
    ApprovedAndProspectiveVendor_val = 'Approved And Prospective Vendor'
    InternalOnly_val = 'Internal Only'


def project_viewtype():
    idarr = [ViewType.ProspectiveVendor, ViewType.ApprovedVendor, ViewType.ApprovedAndProspectiveVendor,
             ViewType.InternalOnly]
    typearr = [ViewType.ProspectiveVendor_val, ViewType.ApprovedVendor_val, ViewType.ApprovedAndProspectiveVendor_val,
               ViewType.InternalOnly_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)
    return vyslist


def get_viewtype(number):
    if number == ViewType.ProspectiveVendor:
        d = {"id": ViewType.ProspectiveVendor, "text": ViewType.ProspectiveVendor_val}
    elif number == ViewType.ApprovedVendor:
        d = {"id": ViewType.ApprovedVendor, "text": ViewType.ApprovedVendor_val}
    elif number == ViewType.ApprovedAndProspectiveVendor:
        d = {"id": ViewType.ApprovedAndProspectiveVendor, "text": ViewType.ApprovedAndProspectiveVendor_val}
    elif number == ViewType.InternalOnly:
        d = {"id": ViewType.InternalOnly, "text": ViewType.InternalOnly_val}
    else:
        d = {"id": None, "text": None}
    return d


class AnswerRefType:
    supplier = 1
    group = 2


class ShortlistedTran:
    shortlisted = 1
    finalized = 2
    released = 3
    approved = 4


class ProjectQuestionType:
    project_execution = 1
    Financial = 2

    project_execution_val = "Project Execution"
    financial_val = "Financial"
def get_projectquestiontype(number):
    if (number == ProjectQuestionType.project_execution):
        d = {"id": ProjectQuestionType.project_execution, "text": ProjectQuestionType.project_execution_val}
    elif (number == ProjectQuestionType.Financial):
        d = {"id": ProjectQuestionType.Financial, "text": ProjectQuestionType.financial_val}
    return d


class HistoryStatus:
    CREATED = 0
    DRAFT = 1
    PENDING = 2
    APPROVED = 3
    REJECTED = 4
    REVIEW = 5
    SHORTLISTED = 6
    SHORTLISTED_UNDO = 7
    FINALIZED = 8
    RESUBMITTED = 9
    MOVE_TO_APPROVAL=10

    DRAFT_VAL = "DRAFT"
    PENDING_VAL = "PENDING"
    APPROVED_VAL = "APPROVED"
    REJECTED_VAL = "REJECTED"
    REVIEW_VAL = "REVIEW"
    SHORTLISTED_VAL = "SHORTLISTED"
    SHORTLISTED_UNDO_VAL = "SHORTLISTED UNDO"
    FINALIZED_VAL = "FINALIZED"
    CREATED_VAL = "CREATED"
    RESUBMITTED_VAL = "RESUBMITTED"
    MOVE_TO_APPROVAL_val="MOVED TO APPROVAL GROUP"


def get_historystatus(number):
    if (number == HistoryStatus.DRAFT):
        d = {"id": HistoryStatus.DRAFT, "text": HistoryStatus.DRAFT_VAL}
    elif (number == HistoryStatus.PENDING):
        d = {"id": HistoryStatus.PENDING, "text": HistoryStatus.PENDING_VAL}
    elif (number == HistoryStatus.APPROVED):
        d = {"id": HistoryStatus.APPROVED, "text": HistoryStatus.APPROVED_VAL}
    elif (number == HistoryStatus.REJECTED):
        d = {"id": HistoryStatus.REJECTED, "text": HistoryStatus.REJECTED_VAL}
    elif (number == HistoryStatus.REVIEW):
        d = {"id": HistoryStatus.REVIEW, "text": HistoryStatus.REVIEW_VAL}
    elif (number == HistoryStatus.CREATED):
        d = {"id": HistoryStatus.CREATED, "text": HistoryStatus.CREATED_VAL}
    elif (number == HistoryStatus.RESUBMITTED):
        d = {"id": HistoryStatus.RESUBMITTED, "text": HistoryStatus.RESUBMITTED_VAL}
    elif (number == HistoryStatus.SHORTLISTED):
        d = {"id": HistoryStatus.SHORTLISTED, "text": HistoryStatus.SHORTLISTED_VAL}
    elif (number == HistoryStatus.SHORTLISTED_UNDO):
        d = {"id": HistoryStatus.SHORTLISTED_UNDO, "text": HistoryStatus.SHORTLISTED_UNDO_VAL}
    elif (number == HistoryStatus.FINALIZED):
        d = {"id": HistoryStatus.FINALIZED, "text": HistoryStatus.FINALIZED_VAL}
    elif (number == HistoryStatus.MOVE_TO_APPROVAL):
        d = {"id": HistoryStatus.MOVE_TO_APPROVAL, "text": HistoryStatus.MOVE_TO_APPROVAL_val}
    else:
        d={"id":None,"text":None}
    return d

class Mail_Reltype:
    project=1
    proposal=2
    project_identification = 3

    project_val = "Project"
    proposer_val = "Proposer"
    project_identification_val = "Project Identification"

class Mail_TranType:
    CREATED=1
    APPROVED=3
    REJECTED=4
    RETURNED=5
    FORWARDED=6
    INVITATION=7

    CREATED_VAL = "CREATED"
    APPROVED_VAL = "APPROVED"
    REJECTED_VAL = "REJECTED"
    RETURNED_VAL = "RETURNED"
    FORWARDED_VAL = "FORWARDED"
    INVITATION_VAL = "INVITATION"

class Mail_ToType:
    MAKER=1
    APPROVER=2
    COLLABORATORS=3
    VENDOR=4

    MAKER_VAL = "MAKER"
    APPROVER_VAL = "APPROVER"
    COLLABORATORS_VAL = "COLLABORATORS"
    VENDOR_VAL = "VENDOR"

class Mail_Is_user:
    VOW=0
    CMS=1

    VOW_VAL="VOW"
    CMS_VAL="CMS"

class CMSValUtil:
    gst=1
    panno=2

class ClausesUtil:
    company_name={"id":1,"text":"company_name"}
    proposer_name={"id":2,"text":"proposer_name"}
    project_name={"id":3,"text":"project_name"}
    address_name={"id":4,"text":"address_name"}

    drop_down_arr=[company_name,proposer_name,project_name,address_name]


class VersionDataType:
    ProjectInvitation = 1
    ProjectCollaborator = 2
    ProjectApprover = 3
    ProposalApprover = 4
    ProjectIdentification = 5
    
class UpdateHistoryUtil:
    project=1
    proposal=2

class AgreementTemplateUtil:
    template={"id":1,"name":"Template"}
    clauses={"id":2,"name":"Clauses"}
    arr=[template,clauses]

def get_agreementtemplate_util(type):
    if type == AgreementTemplateUtil.template["id"]:
        type_name = AgreementTemplateUtil.template["name"]
    elif type == AgreementTemplateUtil.clauses["id"]:
        type_name = AgreementTemplateUtil.clauses["name"]
    else:
        type_name=None
    return type_name

class SuperScriptUtil:
    original =1
    span_tag =2

def get_question_input_type():
    data=Input_type()
    return data

def get_file_name(file_id):
    file_key = DocPrefix.CMS +"_"+str(file_id)
    return file_key

def cms_file_key():
    file_key = DocPrefix.CMS + "_"
    return file_key