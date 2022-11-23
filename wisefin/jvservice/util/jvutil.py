import json

from django.db.models import QuerySet

from utilityservice.data.response.nwisefinlist import NWisefinList
#test

class JournalType:
    NEW_ENTRY = 1
    RECTIFICATION_ENTRY = 2
    TA_ENTRY = 3
    PROVISION_ENTRY = 4

    NEW_ENTRY_TYPE = "New-Entry"
    RECTIFICATION_ENTRY_TYPE = "Rectification Entry"
    TA_ENTRY_TYPE = "TA-Entry"
    PROVISION_ENTRY_TYPE = "Provision-Entry"

def get_Journaltype(string):
    if (string == JournalType.NEW_ENTRY):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "New-Entry"
        return vyslite

    elif (string == JournalType.RECTIFICATION_ENTRY):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "Rectification Entry"
        return vyslite

    elif (string == JournalType.TA_ENTRY):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "TA-Entry"
        return vyslite

    elif (string == JournalType.PROVISION_ENTRY):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "Provision-Entry"
        return vyslite


def get_Journaltype_list():
    idarr = [JournalType.NEW_ENTRY, JournalType.RECTIFICATION_ENTRY, JournalType.TA_ENTRY, JournalType.PROVISION_ENTRY]
    jearr = [JournalType.NEW_ENTRY_TYPE, JournalType.RECTIFICATION_ENTRY_TYPE, JournalType.TA_ENTRY_TYPE,
              JournalType.PROVISION_ENTRY_TYPE]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = jearr[x]
        vyslist.append(vyslite)
    return vyslist


class JournalDetailType:
    DEBIT = 1
    CREDIT = 2

    DEBIT_TYPE = "Debit"
    CREDIT_TYPE = "Credit"

def get_JournalDetail(string):
    if (string == JournalDetailType.DEBIT):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "Debit"
        return vyslite

    elif (string == JournalDetailType.CREDIT):
        vyslite = NWisefinList()
        vyslite.id = string
        vyslite.text = "Credit"
        return vyslite

def get_JournalDetail_list():
    idarr = [JournalDetailType.DEBIT, JournalDetailType.CREDIT]
    jearr = [JournalDetailType.DEBIT_TYPE, JournalDetailType.CREDIT_TYPE]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = jearr[x]
        vyslist.append(vyslite)
    return vyslist

class JVRefType:
    JournalEntry = 1
    JournalDetailEntry = 2
    JVFiles = 3

class JVModifyStatus:
    DELETE = 0
    CREATE = 1
    UPDATE = 2

class JournalStatus:
    PENDING_FOR_APPROVAL = 1
    APPROVED = 2
    REJECTED = 3
    DELETED = 4

    PENDING_FOR_APPROVAL_TYPE = "Pending For Approval"
    APPROVED_TYPE = "Approved"
    REJECTED_TYPE = "Rejected"
    DELETED_TYPE = "Deleted"

def get_journalstatus(number):
    if (number == JournalStatus.PENDING_FOR_APPROVAL):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Pending For Approval'
        return vyslite

    elif (number == JournalStatus.APPROVED):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Approved'
        return vyslite
    elif (number == JournalStatus.REJECTED):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Rejected'
        return vyslite
    elif (number == JournalStatus.DELETED):
        vyslite = NWisefinList()
        vyslite.id = number
        vyslite.text = 'Deleted'
        return vyslite

def get_journalstatus_list():
    idarr = [JournalStatus.PENDING_FOR_APPROVAL, JournalStatus.APPROVED, JournalStatus.REJECTED, JournalStatus.DELETED]
    statusarr = [JournalStatus.PENDING_FOR_APPROVAL_TYPE, JournalStatus.APPROVED_TYPE, JournalStatus.REJECTED_TYPE,
                 JournalStatus.DELETED_TYPE]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinList()
        vyslite.id = idarr[x]
        vyslite.text = statusarr[x]
        vyslist.append(vyslite)
    return vyslist


class DictObj:
    queryset_data=[]
    result_set=[]
    def get(self,dict1):
        if isinstance(dict1,str):
            dict1=json.loads(dict1)
        self.__dict__.update(dict1)
        return self.__dict__
    def get_obj(self,dict1):
        if isinstance(dict1,QuerySet):

            for data in dict1:
                self.__dict__.update(data)
                self.queryset_data.append(self)
            return self.queryset_data
        else:
            self.__dict__.update(dict1)
            return self

    def values_list(self, field):
        for data in self.queryset_data:
            for key, value in data.items():
                if key == field:
                    self.result_set.append(value)
        return self.result_set