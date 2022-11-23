from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList

class ActiveStatus:
    Active = 1
    Delete = 0

class DayUtil:
    SUNDAY = 1
    MONDAY = 2
    TUESDAY = 3
    WEDNESDAY = 4
    THURSDAY = 5
    FRIDAY = 6
    SATURDAY = 7

    SUNDAY_VAL = 'SUNDAY'
    MONDAY_VAL = 'MONDAY'
    TUESDAY_VAL = 'TUESDAY'
    WEDNESDAY_VAL = 'WEDNESDAY'
    THURSDAY_VAL = 'THURSDAY'
    FRIDAY_VAL = 'FRIDAY'
    SATURDAY_VAL = 'SATURDAY'

    ID_ARR = [SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY]
    TEXT_ARR = [SUNDAY_VAL, MONDAY_VAL, TUESDAY_VAL, WEDNESDAY_VAL, THURSDAY_VAL, FRIDAY_VAL, SATURDAY_VAL]
    ID_LENGTH = len(ID_ARR)


def days_summary():
    day = DayUtil()
    list_data = NWisefinList()
    for i in range(day.ID_LENGTH):
        data = NWisefinLiteList()
        data.set_id(day.ID_ARR[i])
        data.set_text(day.TEXT_ARR[i])
        list_data.append(data)
    return list_data


def day_get(type_id):
    day = DayUtil()
    type_id = int(type_id)
    data = NWisefinLiteList()
    id_val = ''
    text_val = ''
    if type_id == day.SUNDAY:
        id_val = day.SUNDAY
        text_val = day.SUNDAY_VAL
    elif type_id == day.MONDAY:
        id_val = day.MONDAY
        text_val = day.MONDAY_VAL
    elif type_id == day.TUESDAY:
        id_val = day.TUESDAY
        text_val = day.TUESDAY_VAL
    elif type_id == day.WEDNESDAY:
        id_val = day.WEDNESDAY
        text_val = day.WEDNESDAY_VAL
    elif type_id == day.THURSDAY:
        id_val = day.THURSDAY
        text_val = day.THURSDAY_VAL
    elif type_id == day.FRIDAY:
        id_val = day.FRIDAY
        text_val = day.FRIDAY_VAL
    elif type_id == day.SATURDAY:
        id_val = day.SATURDAY
        text_val = day.SATURDAY_VAL
    data.set_id(id_val)
    data.set_text(text_val)
    return data

def time_to_m_sec(time_data):
    time_data = int(time_data.timestamp() * 1000)
    return time_data

class Relationship:
    Father={"id":1,"text":"father"}
    Mother={"id":2,"text":"mother"}
    Spouse={"id":3,"text":"spouse"}
    var = [Father,Mother,Spouse]

    def get_relationship_util(self,number):
        relationship = None
        if (number ==Relationship.Father['id']):
            relationship = Relationship.Father

        elif(number ==Relationship.Mother['id']):
            relationship = Relationship.Mother

        elif(number == Relationship.Spouse['id']):
            relationship = Relationship.Spouse
        return relationship
def relationship_summary():
    relationship = Relationship()
    list_data = NWisefinList()
    for i in relationship.var:
        list_data.append(i)
    return list_data

class TemplateUtil:
    CallLetter = 1
    RelievingLetter = 2
    AddressConfirmation = 3

    CALLLETTER_VAR = 'CALLLETTER'
    RELIEVINGLETTER = 'RELIEVINGLETTER'
    ADDRESSCONFIRMATION = 'ADDRESSCONFIRMATION'

def templateutil_summary():
    idarr = [TemplateUtil.CallLetter, TemplateUtil.RelievingLetter, TemplateUtil.AddressConfirmation]
    typearr = [TemplateUtil.CALLLETTER_VAR, TemplateUtil.RELIEVINGLETTER, TemplateUtil.ADDRESSCONFIRMATION]
    length = len(idarr)
    vyslistt = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslistt.append(vyslite)
    return vyslistt
class EmployeeDocUtil:
    employee_document =1

class ApprovalStatus:
    DRAFT = 1
    PENDING = 2
    APPROVED = 3
    REJECTED = 4
    REVIEW = 5

    DRAFT_VAL = "DRAFT"
    PENDING_VAL = "PENDING"
    APPROVED_VAL = "APPROVED"
    REJECTED_VAL = "REJECTED"
    REVIEW_VAL = "REVIEW"

class RequestUtil:
    leave =1
    advance=2
    address_verification =3
