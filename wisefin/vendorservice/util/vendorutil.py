from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
import re

class VendorTypeUtil:
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    HIGH_VAL = "HIGH"
    MEDIUM_VAL = "MEDIUM"
    LOW_VAL = "LOW"


class VendorGroupUtil:
    OUTSOURCING = 1
    OTHER = 2
    OUTSOURCING_VAL = 'Outsourced services'
    OTHER_VAL = 'Other services'
    # CUSTOMER = 1
    # SUPPLIER = 2
    # CUSTOMER_VAL = "CUSTOMER"
    # SUPPLIER_VAL = "SUPPLIER"


class VendorOrgtypeUtil:
    INDIVIDUAL = 1
    SOLE_PROPRIETORSHIP = 2
    PRIVATE_LIMITED = 3
    PUBLIC_LIMITED_UNLISTED = 4
    PUBLIC_LIMITED_LISTED = 5
    PARTNERSHIP_FIRM = 6
    LIMITED_LIABILITY_PARTNERSHIP = 7
    TRUST = 8
    SOCIETY = 9
    GOVERNMENT_ENTITY = 10
    OTHERS = 11
    # SOLE_PROPERTIERS = 1
    # PARTERNSHIP = 2
    # PRIVATE_LTD = 3
    # PUBLIC_LTD = 4
    # INDIVIDUAL = 5
    # TRUST = 6
    # OTHERS = 7
    # Government_Entity=8
    INDIVIDUAL_val = 'Individual'
    SOLE_PROPRIETORSHIP_val = 'Sole Proprietorship'
    PRIVATE_LIMITED_val = 'Private Limited'
    PUBLIC_LIMITED_UNLISTED_val = 'Public Limited (unlisted)'
    PUBLIC_LIMITED_LISTED_val = 'Public Limited (listed)'
    PARTNERSHIP_FIRM_val = 'Partnership Firm'
    LIMITED_LIABILITY_PARTNERSHIP_val = 'Limited Liability Partnership'
    TRUST_val = 'Trust'
    SOCIETY_val = 'Society'
    GOVERNMENT_ENTITY_val = 'Government Entity'
    OTHERS_val = 'Others'
    # SOLE_PROPERTIERS_VAL = "SOLE_PROPERTIERS"
    # PARTERNSHIP_VAL = "PARTERNSHIP"
    # PRIVATE_LTD_VAL = "PRIVATE_LTD"
    # PUBLIC_LTD_VAL = "PUBLIC_LTD"
    # INDIVIDUAL_VAL = "INDIVIDUAL"
    # TRUST_VAL = "TRUST"
    # OTHERS_VAL = "OTHERS"
    # Government_Entity_VAL="GOVERNMENT ENTITY"


class VendorClassificationUtil:
    ONE_TIME = 1
    REGULAR = 2
    ONE_TIME_VAL = "ONE_TIME"
    REGULAR_VAL = "REGULAR"


class VendorCompositeUtil:
    REGISTER_COMPOSITE = 1
    REGISTER_REGULAR = 2
    UNREGISTER = 3
    OTHERS = 4
    REGISTER_COMPOSITE_VAL = "REGISTERED COMPOSITE"
    REGISTER_REGULAR_VAL = "REGISTERED REGULAR"
    UNREGISTER_VAL = "UNREGISTERED"
    OTHERS_VAL = "OTHERS"



def getComposite(number):
    if (number == VendorCompositeUtil.REGISTER_COMPOSITE):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'REGISTERED COMPOSITE'
        return vyslite
    if (number == VendorCompositeUtil.REGISTER_REGULAR):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'REGISTERED REGULAR'
        return vyslite
    if (number == VendorCompositeUtil.UNREGISTER):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'UNREGISTERED'
        return vyslite
    if (number == VendorCompositeUtil.OTHERS):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'OTHERS'
        return vyslite


def getClassification(number):
    if (number == VendorClassificationUtil.ONE_TIME):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'ONE_TIME'
        return vyslite

    elif (number == VendorClassificationUtil.REGULAR):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'REGULAR'
        return vyslite


def getOrgType(number):
    if (number == VendorOrgtypeUtil.INDIVIDUAL):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.INDIVIDUAL_val
        return vyslite

    elif (number == VendorOrgtypeUtil.SOLE_PROPRIETORSHIP):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.SOLE_PROPRIETORSHIP_val
        return vyslite

    elif (number == VendorOrgtypeUtil.PRIVATE_LIMITED):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.PRIVATE_LIMITED_val
        return vyslite

    elif (number == VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED_val
        return vyslite

    elif (number == VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED_val
        return vyslite
    elif (number == VendorOrgtypeUtil.PARTNERSHIP_FIRM):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.PARTNERSHIP_FIRM_val
        return vyslite
    elif (number == VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP_val
        return vyslite
    elif (number == VendorOrgtypeUtil.TRUST):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.TRUST_val
        return vyslite
    elif (number == VendorOrgtypeUtil.SOCIETY):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.SOCIETY_val
        return vyslite
    elif (number == VendorOrgtypeUtil.GOVERNMENT_ENTITY):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.GOVERNMENT_ENTITY_val
        return vyslite
    elif (number == VendorOrgtypeUtil.OTHERS):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorOrgtypeUtil.OTHERS_val
        return vyslite

def getGroup(number):
    if (number == VendorGroupUtil.OUTSOURCING):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorGroupUtil.OUTSOURCING_VAL
        return vyslite

    elif (number == VendorGroupUtil.OTHER):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = VendorGroupUtil.OTHER_VAL
        return vyslite


def getType(number):
    if (number == VendorTypeUtil.HIGH):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'HIGH'
        return vyslite

    elif (number == VendorTypeUtil.MEDIUM):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'MEDIUM'
        return vyslite

    elif (number == VendorTypeUtil.LOW):
        vyslite = NWisefinLiteList()
        vyslite.id = number
        vyslite.text = 'LOW'
        return vyslite

def get_org_type_list():
    idarr = [VendorOrgtypeUtil.INDIVIDUAL, VendorOrgtypeUtil.SOLE_PROPRIETORSHIP, VendorOrgtypeUtil.PRIVATE_LIMITED,
             VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED, VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED,
             VendorOrgtypeUtil.PARTNERSHIP_FIRM,VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP,
             VendorOrgtypeUtil.TRUST,VendorOrgtypeUtil.SOCIETY,VendorOrgtypeUtil.GOVERNMENT_ENTITY,VendorOrgtypeUtil.OTHERS]
    typearr = [VendorOrgtypeUtil.INDIVIDUAL_val, VendorOrgtypeUtil.SOLE_PROPRIETORSHIP_val, VendorOrgtypeUtil.PRIVATE_LIMITED_val,
             VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED_val, VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED_val,
             VendorOrgtypeUtil.PARTNERSHIP_FIRM_val,VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP_val,
             VendorOrgtypeUtil.TRUST_val,VendorOrgtypeUtil.SOCIETY_val,VendorOrgtypeUtil.GOVERNMENT_ENTITY_val,
               VendorOrgtypeUtil.OTHERS_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist

def search_org_type(query):
    idarr = [VendorOrgtypeUtil.INDIVIDUAL, VendorOrgtypeUtil.SOLE_PROPRIETORSHIP, VendorOrgtypeUtil.PRIVATE_LIMITED,
             VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED, VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED,
             VendorOrgtypeUtil.PARTNERSHIP_FIRM, VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP,
             VendorOrgtypeUtil.TRUST, VendorOrgtypeUtil.SOCIETY, VendorOrgtypeUtil.GOVERNMENT_ENTITY,
             VendorOrgtypeUtil.OTHERS]
    typearr = [VendorOrgtypeUtil.INDIVIDUAL_val, VendorOrgtypeUtil.SOLE_PROPRIETORSHIP_val,
               VendorOrgtypeUtil.PRIVATE_LIMITED_val,
               VendorOrgtypeUtil.PUBLIC_LIMITED_UNLISTED_val, VendorOrgtypeUtil.PUBLIC_LIMITED_LISTED_val,
               VendorOrgtypeUtil.PARTNERSHIP_FIRM_val, VendorOrgtypeUtil.LIMITED_LIABILITY_PARTNERSHIP_val,
               VendorOrgtypeUtil.TRUST_val, VendorOrgtypeUtil.SOCIETY_val, VendorOrgtypeUtil.GOVERNMENT_ENTITY_val,
               VendorOrgtypeUtil.OTHERS_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        seach = re.search(query.lower(), vyslite.text.lower())
        if seach is not None:
            vyslist.append(vyslite)

    return vyslist


def get_composite_list():
    idarr = [VendorCompositeUtil.REGISTER_COMPOSITE, VendorCompositeUtil.REGISTER_REGULAR,
             VendorCompositeUtil.UNREGISTER,VendorCompositeUtil.OTHERS]

    typearr = [VendorCompositeUtil.REGISTER_COMPOSITE_VAL, VendorCompositeUtil.REGISTER_REGULAR_VAL,
               VendorCompositeUtil.UNREGISTER_VAL,VendorCompositeUtil.OTHERS_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist

def search_composite_list(query):
    idarr = [VendorCompositeUtil.REGISTER_COMPOSITE, VendorCompositeUtil.REGISTER_REGULAR,
             VendorCompositeUtil.UNREGISTER,VendorCompositeUtil.OTHERS]

    typearr = [VendorCompositeUtil.REGISTER_COMPOSITE_VAL, VendorCompositeUtil.REGISTER_REGULAR_VAL,
               VendorCompositeUtil.UNREGISTER_VAL,VendorCompositeUtil.OTHERS_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        seach = re.search(query.lower(), vyslite.text.lower())
        if seach is not None:
            vyslist.append(vyslite)

    return vyslist


def get_classification_list():
    idarr = [VendorClassificationUtil.ONE_TIME, VendorClassificationUtil.REGULAR]
    typearr = [VendorClassificationUtil.ONE_TIME_VAL, VendorClassificationUtil.REGULAR_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist


def get_type_list():
    idarr = [VendorTypeUtil.HIGH, VendorTypeUtil.MEDIUM, VendorTypeUtil.LOW]
    typearr = [VendorTypeUtil.HIGH_VAL, VendorTypeUtil.MEDIUM_VAL,VendorTypeUtil.LOW_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist


def get_group_list():
    idarr = [VendorGroupUtil.OUTSOURCING, VendorGroupUtil.OTHER]
    typearr = [VendorGroupUtil.OUTSOURCING_VAL, VendorGroupUtil.OTHER_VAL]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist


class VendorStatusUtil:
    DRAFT = 1
    PENDING_RM = 2
    PENDING_CHECKER = 3
    PENDING_HEADER = 4
    APPROVED = 5
    RENEWAL_APPROVED = 6
    REJECTED = 0
    RETURN = 7
    PENDING_COMPLIANCE = 8
    DRAFT_VAL = "Draft"
    PENDING_RM_VAL = "Pending RM"
    PENDING_CHECKER_VAL = "Pending_Checker"
    PENDING_HEADER_VAL = "Pending_Header"
    APPROVED_VAL = "Approved"
    REJECTED_VAL = "Rejected"
    RENEWAL_APPROVED_VAL = "Renewal_Approved"
    RETURN_VAL = 'Returned'
    PENDING_COMPLIANCE_VAL = 'pending_compliance'


class MainStatusUtil:
    DRAFT = 1
    APPROVED = 2
    DEACTIVATED = 3
    TERMINATED = 4
    DRAFT_VAL = "Draft"
    APPROVED_VAL = "Approved"
    DEACTIVATED_VAL = "Deactivated"
    TERMINATED_VAL = "Terminated"


class StatusUtil:
    ACTIVITY = 1
    INACTIVITY = 2
    ACTIVITY_VAL = "ACTIVITY"
    INACTIVITY_VAL = "INACTIVITY"


class RequestStatusUtil:
    ONBOARD = 1
    MODIFICATION = 2
    ACTIVATION = 3
    DEACTIVATION = 4
    RENEWAL = 5
    TERMINATION = 6
    ONBOARD_VAL = "Onboard"
    MODIFICATION_VAL = "Modification"
    ACTIVATION_VAL = "Activation"
    DEACTIVATION_VAL = "Deactivation"
    RENEWAL_VAL = "Renewal Process"
    TERMINATION_VAL = "Termination"


# class Vendorstatus:

def getVendorStatus(number):
    if (number == VendorStatusUtil.DRAFT):
        return VendorStatusUtil.DRAFT_VAL

    elif (number == VendorStatusUtil.PENDING_RM):
        return VendorStatusUtil.PENDING_RM_VAL

    elif (number == VendorStatusUtil.PENDING_CHECKER):
        return VendorStatusUtil.PENDING_CHECKER_VAL

    elif (number == VendorStatusUtil.PENDING_HEADER):
        return VendorStatusUtil.PENDING_HEADER_VAL

    elif (number == VendorStatusUtil.APPROVED):
        return VendorStatusUtil.APPROVED_VAL

    elif (number == VendorStatusUtil.REJECTED):
        return VendorStatusUtil.REJECTED_VAL

    elif (number == VendorStatusUtil.RENEWAL_APPROVED):
        return VendorStatusUtil.RENEWAL_APPROVED_VAL

    elif (number == VendorStatusUtil.RETURN):
        return VendorStatusUtil.RETURN_VAL

    elif (number == VendorStatusUtil.PENDING_COMPLIANCE):
        return VendorStatusUtil.PENDING_COMPLIANCE_VAL


class VendorRefType:
    VENDOR = 1
    VENDOR_ADDRESS = 2
    VENDOR_CONTACT = 3
    VENDOR_PROFILE = 4
    VENDOR_DIRECTOR = 5
    VENDOR_BRANCH = 6
    VENDOR_CLIENT = 7
    VENDOR_CONTRACT = 8
    VENDOR_PRODUCT = 9
    VENDOR_DOCUMENT = 10
    VENDOR_SUPPLIERTAX = 11
    VENDOR_PAYMENT = 12
    VENDOR_ACTIVITY = 13
    VENDOR_ACTIVITYDETAIL = 14
    VENDOR_CATELOG = 15
    VENDOR_REL_ADDRESS = 16
    VENDOR_REL_CONTACT = 17
    VENDOR_SUPPLIERSUBTAX = 18
    VENDOR_RISK = 19
    VENDOR_KYC =20
    BCP_QUESION = 21
    DUE_DELIGENCE = 22

    VENDOR_VAL = 'VENDOR'
    VENDOR_ADDRESS_VAL = 'VENDOR_ADDRESS' #
    VENDOR_CONTACT_VAL = 'VENDOR_CONTACT' #
    VENDOR_PROFILE_VAL = 'VENDOR_PROFILE' #
    VENDOR_DIRECTOR_VAL = 'VENDOR_DIRECTOR' #
    VENDOR_BRANCH_VAL = 'BRANCH DETAILS'
    VENDOR_CLIENT_VAL = 'CLIENT'
    VENDOR_CONTRACT_VAL = 'CONTRACTOR'
    VENDOR_PRODUCT_VAL = 'PRODUCT'
    VENDOR_DOCUMENT_VAL = 'DOCUMENT'
    VENDOR_SUPPLIERTAX_VAL = 'SUPPLIERTAX'
    VENDOR_PAYMENT_VAL = 'PAYMENT'
    VENDOR_ACTIVITY_VAL = 'ACTIVITY'
    VENDOR_ACTIVITYDETAIL_VAL = 'ACTIVITYDETAIL'
    VENDOR_CATELOG_VAL = 'CATALOG'
    VENDOR_REL_ADDRESS_VAL = 'VENDOR_REL_ADDRESS' #
    VENDOR_REL_CONTACT_VAL = 'VENDOR_REL_CONTACT' #
    VENDOR_SUPPLIERSUBTAX_VAL = 'VENDOR_SUPPLIERSUBTAX' #
    VENDOR_RISK_VAL = 'RISK'
    VENDOR_KYC_VAL = 'KYC'
    BCP_QUESION_VAL = 'BCP QUESTIONAIRE'
    DUE_DELIGENCE_VAL = 'DUE DILIGENCE'

    ref_id_list = [VENDOR, VENDOR_ADDRESS, VENDOR_CONTACT, VENDOR_PROFILE, VENDOR_DIRECTOR, VENDOR_BRANCH,
                   VENDOR_CLIENT, VENDOR_CONTRACT, VENDOR_PRODUCT, VENDOR_DOCUMENT, VENDOR_SUPPLIERTAX,
                   VENDOR_PAYMENT, VENDOR_ACTIVITY, VENDOR_ACTIVITYDETAIL, VENDOR_CATELOG, VENDOR_REL_ADDRESS,
                   VENDOR_REL_CONTACT, VENDOR_SUPPLIERSUBTAX, VENDOR_RISK, VENDOR_KYC, BCP_QUESION, DUE_DELIGENCE]
    ref_val_list = [VENDOR_VAL, VENDOR_ADDRESS_VAL, VENDOR_CONTACT_VAL, VENDOR_PROFILE_VAL, VENDOR_DIRECTOR_VAL,
                    VENDOR_BRANCH_VAL, VENDOR_CLIENT_VAL, VENDOR_CONTRACT_VAL, VENDOR_PRODUCT_VAL, VENDOR_DOCUMENT_VAL,
                    VENDOR_SUPPLIERTAX_VAL, VENDOR_PAYMENT_VAL, VENDOR_ACTIVITY_VAL, VENDOR_ACTIVITYDETAIL_VAL,
                    VENDOR_CATELOG_VAL, VENDOR_REL_ADDRESS_VAL, VENDOR_REL_CONTACT_VAL, VENDOR_SUPPLIERSUBTAX_VAL,
                    VENDOR_RISK_VAL, VENDOR_KYC_VAL, BCP_QUESION_VAL, DUE_DELIGENCE_VAL]

    def get_ref_data(self,type_id):
        id_list = self.ref_id_list
        name_list = self.ref_val_list
        length = len(id_list)
        for x in range(length):
            if id_list[x] == type_id:
                data = {
                    "tab_name": name_list[x], "tab_id": id_list[x]
                }
                return data


def getVendorMainStatus(number):
    if (number == MainStatusUtil.DRAFT):
        return MainStatusUtil.DRAFT_VAL
    elif (number == MainStatusUtil.APPROVED):
        return MainStatusUtil.APPROVED_VAL
    elif (number == MainStatusUtil.DEACTIVATED):
        return MainStatusUtil.DEACTIVATED_VAL
    elif (number == MainStatusUtil.TERMINATED):
        return MainStatusUtil.TERMINATED_VAL


def getVendorActiveStatus(number):
    if (number == StatusUtil.ACTIVITY):
        return StatusUtil.ACTIVITY_VAL
    elif (number == StatusUtil.INACTIVITY):
        return StatusUtil.INACTIVITY_VAL


def getVendorRequestStatus(number):
    if (number == RequestStatusUtil.ONBOARD):
        return RequestStatusUtil.ONBOARD_VAL
    if (number == RequestStatusUtil.MODIFICATION):
        return RequestStatusUtil.MODIFICATION_VAL
    if (number == RequestStatusUtil.ACTIVATION):
        return RequestStatusUtil.ACTIVATION_VAL
    if (number == RequestStatusUtil.DEACTIVATION):
        return RequestStatusUtil.DEACTIVATION_VAL
    if (number == RequestStatusUtil.RENEWAL):
        return RequestStatusUtil.RENEWAL_VAL
    if (number == RequestStatusUtil.TERMINATION):
        return RequestStatusUtil.TERMINATION_VAL


class ModifyStatus:
    create = 1
    update = 2
    delete = 0
    active_in=3



class QueueStatus:
    maker = 1
    rm = 2
    checker = 3
    header = 4

    role_maker = "move to rm"
    role_rm = "move to checker"
    role_checker = "move to header"
    role_header = "approved"
def getroleStatus(type):
    if (type == QueueStatus.role_maker):
        return QueueStatus.maker
    elif (type == QueueStatus.role_rm):
        return QueueStatus.rm
    elif (type == QueueStatus.role_checker):
        return QueueStatus.checker
    elif (type == QueueStatus.role_header):
        return QueueStatus.header
    else:
        return -1


class Role:
    maker = 'Maker'
    rm = 'rm'
    checker = 'Checker'
    header = 'Header'


class Code_Gen_Type:
    vendor = 1
    supplier = 2

class Validation_vendor_doc:
    outsourcing_dict = {"due_deligence":'Due diligence',"bcp_quest":'BCP questionnaire'}
    # Third_party_intermediary_dict = {"intermediary":'INTERMEDIARY DUE DILIGENCE'}

    OUTSOURCING ='Outsourced services'
    # THIRD_PARTY_INTERMEDIARY = 'THIRD PARTY INTERMEDIARY'
    CANCEL_CHEQUE='Canceled cheque'
    PAN = 'PAN'
    GST = 'GST'
    BOARD_RESOLUTION = 'Board Resolution'
    CONTRACT = 'Contract/Email/Letter of engagement'

    MANDATORY_FIELD_REG = [CANCEL_CHEQUE, PAN, GST, BOARD_RESOLUTION, CONTRACT]
    MANDATORY_FIELD_UNREG = [CANCEL_CHEQUE, PAN, BOARD_RESOLUTION, CONTRACT]

class Vendor_Risk_Type:
    Information_security_risk = 1
    Reputational_risk = 2
    Operational_risk = 3
    Counterparty_Risk = 4
    Service_risk = 5
    Service_disruption_risk = 6
    Termination = 7
    discontinuation_risk = 8
    Concentration_risk = 9
    Non_compliance_risk = 10

    Information_security_risk_val = 'Information security risk'
    Reputational_risk_val = 'Reputational risk'
    Operational_risk_val = 'Operational risk'
    Counterparty_Risk_val = 'Counterparty Risk'
    Service_risk_val = 'Service risk'
    Service_disruption_risk_val = 'Service disruption risk'
    Termination_val = 'Termination'
    discontinuation_risk_val = 'discontinuation risk'
    Concentration_risk_val = 'Concentration risk'
    Non_compliance_risk_val = 'Non-compliance risk'

def get_risk_type_list():
    idarr = [Vendor_Risk_Type.Information_security_risk, Vendor_Risk_Type.Reputational_risk, Vendor_Risk_Type.Operational_risk,
             Vendor_Risk_Type.Counterparty_Risk, Vendor_Risk_Type.Service_risk, Vendor_Risk_Type.Service_disruption_risk,Vendor_Risk_Type.Termination,
             Vendor_Risk_Type.discontinuation_risk, Vendor_Risk_Type.Concentration_risk,Vendor_Risk_Type.Non_compliance_risk]
    typearr =[Vendor_Risk_Type.Information_security_risk_val, Vendor_Risk_Type.Reputational_risk_val, Vendor_Risk_Type.Operational_risk_val,
             Vendor_Risk_Type.Counterparty_Risk_val, Vendor_Risk_Type.Service_risk_val, Vendor_Risk_Type.Service_disruption_risk_val,Vendor_Risk_Type.Termination_val,
             Vendor_Risk_Type.discontinuation_risk_val, Vendor_Risk_Type.Concentration_risk_val,Vendor_Risk_Type.Non_compliance_risk_val]

    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist

def get_risk_type(type_id):
    if (type_id == Vendor_Risk_Type.Information_security_risk):
        data = {'id':Vendor_Risk_Type.Information_security_risk,
                'text':Vendor_Risk_Type.Information_security_risk_val}

    elif (type_id == Vendor_Risk_Type.Reputational_risk):
        data = {'id':Vendor_Risk_Type.Reputational_risk,
                'text':Vendor_Risk_Type.Reputational_risk_val}

    elif (type_id == Vendor_Risk_Type.Operational_risk):
        data = {'id':Vendor_Risk_Type.Operational_risk,
                'text':Vendor_Risk_Type.Operational_risk_val}

    elif (type_id == Vendor_Risk_Type.Counterparty_Risk):
        data = {'id':Vendor_Risk_Type.Counterparty_Risk,
                'text':Vendor_Risk_Type.Counterparty_Risk_val}

    elif (type_id == Vendor_Risk_Type.Service_risk):
        data = {'id':Vendor_Risk_Type.Service_risk,
                'text':Vendor_Risk_Type.Service_risk_val}

    elif (type_id == Vendor_Risk_Type.Service_disruption_risk):
        data = {'id':Vendor_Risk_Type.Service_disruption_risk,
                'text':Vendor_Risk_Type.Service_disruption_risk_val}

    elif (type_id == Vendor_Risk_Type.Termination):
        data = {'id':Vendor_Risk_Type.Termination,
                'text':Vendor_Risk_Type.Termination_val}

    elif (type_id == Vendor_Risk_Type.discontinuation_risk):
        data = {'id':Vendor_Risk_Type.discontinuation_risk,
                'text':Vendor_Risk_Type.discontinuation_risk_val}

    elif (type_id == Vendor_Risk_Type.Concentration_risk):
        data = {'id':Vendor_Risk_Type.Concentration_risk,
                'text':Vendor_Risk_Type.Concentration_risk_val}

    elif (type_id == Vendor_Risk_Type.Non_compliance_risk):
        data = {'id':Vendor_Risk_Type.Non_compliance_risk,
                'text':Vendor_Risk_Type.Non_compliance_risk_val}

    return data


class Questionnaire:
    BCP_QUESTIONNAIRE = 1
    DUE_DILIGENCE = 2


class VendorDefaults:
    EMAIL_DAYS = 30
    COM_REG_NO = ''
    WEBSITE = ''
    ACTIVE_CONTACT = ''
    NO_CONTACT_REASON = ''
    APPROX_SPEND = 0
    ACTUAL_SPEND = 0
    REMARKS = ''
    DESCRIPTION = ''
    PORTAL_FLAG = True
    GROUP = VendorGroupUtil.OUTSOURCING
    CUSTOMER_CATEGORY = 6 # other service
    CLASSIFIACTION = VendorClassificationUtil.ONE_TIME
    TYPE = VendorTypeUtil.MEDIUM
    ORGTYPE = VendorOrgtypeUtil.PRIVATE_LIMITED
    # PROFILE
    BRANCH = 1
    # CONTACT
    LAND_LINE = ''
    LAND_LINE_2 = ''
    MOBILE_1 = ''
    MOBILE_2 = ''
    EMAIL = ''
    # BRANCH
    CREDIT_TERMS = ''
    # activity
    FIDELITY = ''
    BIDDING = ''
    ACTIVE_STATUS = 'Active'
    # catelog
    NAME = ''
    SPECIFICATION = ''
    SIZE = ''
    CAPACITY = ''
    DIRECT_TO = False

    def get_composite(self, gst):
        if gst is None or gst == '':
            composite = VendorCompositeUtil.UNREGISTER
        else:
            composite = VendorCompositeUtil.REGISTER_COMPOSITE
        return composite


class Approving_level:
    LEVEL1 = 1
    LEVEL2 = 2
    LEVEL3 = 3

    LEVEL1_VAL = 'LEVEL1'
    LEVEL2_VAL = 'LEVEL2'
    LEVEL3_VAL = 'LEVEL3'


def get_approving_level(type):
    if(type == Approving_level.LEVEL1):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Approving_level.LEVEL1_VAL
        return vys_list
    elif(type == Approving_level.LEVEL2):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Approving_level.LEVEL2_VAL
        return vys_list
    elif(type == Approving_level.LEVEL3):
        vys_list = NWisefinLiteList()
        vys_list.id = type
        vys_list.name = Approving_level.LEVEL3_VAL
        return vys_list


def get_approval_type_val():
    idarr = [Approving_level.LEVEL1, Approving_level.LEVEL2, Approving_level.LEVEL3]
    typearr = [Approving_level.LEVEL1_VAL, Approving_level.LEVEL2_VAL, Approving_level.LEVEL3_VAL]

    length = len(idarr)
    list_data = NWisefinList()
    for x in range(length):
        vys_list = NWisefinLiteList()
        vys_list.id = idarr[x]
        vys_list.name = typearr[x]
        list_data.append(vys_list)
    return list_data

class Type_status:
    draft = 1
    approve = 2

    draft_val = 'Draft'
    approve_val = 'Approve'

def get_type_status(number):
    if (number == Type_status.draft):
        d = {"id": Type_status.draft, "text": Type_status.draft_val}
    elif (number == Type_status.approve):
        d = {"id": Type_status.approve, "text": Type_status.approve_val}
    else:
        d = {"id": None, "text": None}
    return d

class Period:
    half_yearly = 1
    quarterly = 2

    half_yearly_val = 'Half-Yearly'
    quarterly_val = 'Quarterly'

def get_period(number):
    if (number == Period.half_yearly):
        d = {"id": Period.half_yearly, "text": Period.half_yearly_val}
    elif (number == Period.quarterly):
        d = {"id": Period.quarterly, "text": Period.quarterly_val}
    else:
        d = {"id": None, "text": None}
    return d

class periodicity:
    jtoj = 1
    jtod = 2
    jtom = 3
    atoj = 4
    jtos = 5
    otod = 6

    jtoj_val = "Jan to Jun"
    jtod_val = "Jul to Dec"
    jtom_val = "Jan to Mar"
    atoj_val = "Apr to Jun"
    jtos_val = "Jul to Sep"
    otod_val = "Oct to Dec"


def get_periodicity(number):
    if (number == periodicity.jtoj):
        d = {"id": periodicity.jtoj, "text": periodicity.jtoj_val}
    elif (number == periodicity.jtod):
        d = {"id": periodicity.jtod, "text": periodicity.jtod_val}
    elif (number == periodicity.jtom):
        d = {"id": periodicity.jtom, "text": periodicity.jtom_val}
    elif (number == periodicity.atoj):
        d = {"id": periodicity.atoj, "text": periodicity.atoj_val}
    elif (number == periodicity.jtos):
        d = {"id": periodicity.jtos, "text": periodicity.jtos_val}
    elif (number == periodicity.otod):
        d = {"id": periodicity.otod, "text": periodicity.otod_val}
    else:
        d = {"id": None, "text": None}
    return d

def get_periodo(number):
    if (number == periodicity.jtoj):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Jan to Jun"
        return vyslite

    elif (number == periodicity.jtod):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Jul to Dec"
        return vyslite
    elif (number == periodicity.jtom):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Jan to Mar"
        return vyslite
    elif (number == periodicity.atoj):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Apr to Jun"
        return vyslite
    elif (number == periodicity.jtos):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Jul to Sep"
        return vyslite
    elif (number == periodicity.otod):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = "Oct to Dec"
        return vyslite


def get_periodicity_list():
    idarr = [periodicity.jtoj, periodicity.jtod, periodicity.jtom, periodicity.atoj,
             periodicity.jtos, periodicity.otod]
    statusarr = [periodicity.jtoj_val, periodicity.jtod_val, periodicity.jtom_val, periodicity.atoj_val,
             periodicity.jtos_val, periodicity.otod_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = statusarr[x]
        vyslist.append(vyslite)
    return vyslist

def get_fileextension_atma(extension):
    if extension in ['txt','doc','pdf','ppt','pot','pps','pptx','odt','odg','odp','ods','docx','docm','dotx','dotm','docb',
                     'xlsx','xls','xlt','xlm','xlsm','xltx','xltm','jpg', 'jpeg','tiff', 'tif','png','TXT','DOC','PDF','PPT',
                     'POT','PPS','PPTX','ODT','ODG','ODP','ODS','DOCX','DOCM','DOTX','DOTM','DOCB','XLSX','XLS','XLT','XLM',
                     'XLSM','XLTX','XLTM','JPG', 'JPEG','TIFF', 'TIF','PNG']:
        return True
    else:
        return False

class VendorOrActivityQueue:
    vendor = 1
    activity = 2