from utilityservice.permissions.util.memopermutil import MemoUrlDict
from utilityservice.permissions.util.masterpermutil import MasterUrlDict
from utilityservice.permissions.util.userpermutil import UserUrlDict
from utilityservice.permissions.util.pdperutil import RemsUrlDict
from utilityservice.permissions.util.pprpermutil import PPRUrlDict

class AssignModule:
    module_serv={"mstserv":MasterUrlDict.DATA,"memserv":MemoUrlDict.DATA,"usrserv":UserUrlDict.DATA,"pdserv":RemsUrlDict.DATA,"pprservice":PPRUrlDict.DATA}


    def module_mapping(self,module):
        if module in self.module_serv :
            return self.module_serv[module]


class QueryStatusUtil:
    DRAFT = 1
    PENDING_RM = 2
    PENDING_CHECKER = 3
    PENDING_HEADER = 4
    APPROVED = 5
    REJECTED = 0
    DRAFT_VAL = "Draft"
    PENDING_RM_VAL = "Pending RM"
    PENDING_CHECKER_VAL = "Pending Checker"
    PENDING_HEADER_VAL = "Pending Header"
    APPROVED_VAL = "Approved"
    REJECTED_VAL = "Rejected"


def getQueryStatus(number):
    if (number == QueryStatusUtil.DRAFT):
        return QueryStatusUtil.DRAFT_VAL

    elif (number == QueryStatusUtil.PENDING_RM):
        return QueryStatusUtil.PENDING_RM_VAL

    elif (number == QueryStatusUtil.PENDING_CHECKER):
        return QueryStatusUtil.PENDING_CHECKER_VAL

    elif (number == QueryStatusUtil.PENDING_HEADER):
        return QueryStatusUtil.PENDING_HEADER_VAL

    elif (number == QueryStatusUtil.APPROVED):
        return QueryStatusUtil.APPROVED_VAL

    elif (number == QueryStatusUtil.REJECTED):
        return QueryStatusUtil.REJECTED_VAL

class MainStatusUtil:
    DRAFT = 1
    APPROVED = 2
    DEACTIVATED = 3
    TERMINATED = 4
    DRAFT_VAL = "Draft"
    APPROVED_VAL = "Approved"
    DEACTIVATED_VAL = "Deactivated"
    TERMINATED_VAL = "Terminated"
