from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
class ModifyStatus:
    create = 1
    update = 2
    delete = 0

class rems_premission_type:
    branch ='branch'
    do = 'do'
    emc = 'emc'
    estate_cell ='estate_cell'

class employeelog_status:
    employee =1
    branch =2

class employee_team_ta:
    ceo ="ceo"
    hr ="hr"
    admin ="admin"
    ceo_admin ="CEO Office - Admin"

class GroupRole:
    admin=1
    moderator=2
    user=3

    admin_val="Admin"
    moderator_val="Moderator"
    user_val="User"

class GroupType:
    group =1
    employee =2

class ActiveStatus:
    Active=1
    Delete=2

def get_grouprole(number):
    if (number == GroupRole.admin):
        d = {"id":GroupRole.admin,"text":GroupRole.admin_val}
    elif (number == GroupRole.moderator):
        d = {"id":GroupRole.moderator,"text":GroupRole.moderator_val}
    elif (number == GroupRole.user):
        d = {"id":GroupRole.user,"text":GroupRole.user_val}
    else:
        d={"id":None,"text":None}
    return d


def get_group_list():
    idarr = [GroupRole.admin, GroupRole.moderator,GroupRole.user]
    typearr = [GroupRole.admin_val, GroupRole.moderator_val,GroupRole.user_val]
    length = len(idarr)
    vyslist = NWisefinList()
    for x in range(length):
        vyslite = NWisefinLiteList()
        vyslite.id = idarr[x]
        vyslite.text = typearr[x]
        vyslist.append(vyslite)

    return vyslist