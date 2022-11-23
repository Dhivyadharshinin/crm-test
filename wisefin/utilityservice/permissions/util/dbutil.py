class Status:
    create=1
    delete=0


class ModuleList :
    memo = 'e-Memo'
    master = 'Masters'
    vendor = 'Vendor'
    employee ='Employee'
    department = 'Department'
    permission = 'Permissions'
    role = 'Roles'
    module = 'Module'
    category='Category'
    subcategory='Sub Category'
    contact = 'Contact'
    address = 'Address'
    rems = 'REMS'
    security_guard ='Security Guard'
    sg_attendance ='Attendance'
    sg_branchcertification = 'Branch Certification'
    sg_invoice = 'Invoice Data Entry'
    sg_minimumwages ='Minimum Wages Master'
    sg_vendormarkup ='Vendor Markup Master'
    sg_holiday = 'Holiday Master'
    provision ='Provision'
    ppr_module = 'PPR Report'
    bgt_builder = 'Budget Builder'
    FA='FA'
    AP = 'AP'
    ECF = 'ECF'
    Ta_eclaim = "TA e-Claim"
    Ta_Expense = "Expense"
    Ta_Travel = "Travel"
    Hrms = 'HRMS'
    Attendance='Attendance Log'
    Leave_request='Leave Request'


class RoleList :
    maker = 'Maker'
    checker = 'Checker'
    header = 'Header'
    Viewer = 'Viewer'
    Compliance = 'Compliance'
    AP_Maker = 'AP Maker'
    AP_Approver = 'AP Approver'
    AP_Bounce_Checker = 'AP Bounce Checker'
    AP_Payment_Maker = 'AP Payment Maker'
    premise_identification_maker = 'Premise_Identification_Maker'
    premise_identification_approver = 'Premise_Identification_Approver'
    proposed_premise_maker = 'Proposed_Premise_Maker'
    proposed_premise_approver = 'Proposed_Premise_Approver'
    admin = 'Admin'
    branch_user = 'Branch_User'
    ONBEHALFOFF = "ONBEHALFOFF"

class SFTP_ModuleList :
    AP = "AP"
    ECF = "ECF"

    AP_VAL = 'Account Payable'
    ECF_VAL = 'Expense Claim Form'


    def get_val(self,data):
        if data==self.AP:
            return self.AP_VAL
        elif data==self.ECF:
            return self.ECF_VAL