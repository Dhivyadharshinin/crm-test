
class ActiveStatus:
    Active = 1
    Delete = 0

def time_to_m_sec(time_data):
    time_data = int(time_data.timestamp() * 1000)
    return time_data

def common_util_fetch(arr,id):
    for  i in arr :
        if i['id'] == id:
            return i
    return

class Relationship:
    Father={"id":1,"text":"father"}
    Mother={"id":2,"text":"mother"}
    Spouse={"id":3,"text":"spouse"}
    var = [Father,Mother,Spouse]

class AdressUtil:
    current ={"id":1,"text":"CURRENT"}
    permanent ={"id":2,"text":"PERMANENT"}
    var = [current,permanent]

class AgentValueUtil:
    state = {"id": 1, "text": "State"}
    district = {"id": 2, "text": "District"}
    city = {"id": 3, "text": "City"}
    pincode = {"id": 4, "text": "Pincode"}
    var = [state, district, city,pincode]

class SourceUtil:
    online ={"id":1,"text":"Online"}
    offline ={"id":2,"text":"Offine"}
    var = [online,offline]

class ContactUtil:
    phone_no ={"id":1,"text":"Phone No"}
    mailid ={"id":2,"text":"Mail id"}
    var = [phone_no,mailid]

class CodePrefix:
    product = 1
    lead = 2
    source = 3

    product_VAL = "PROD"
    source_VAL = "SR"
    lead_VAL = "LD"

class TaskStatusUtil:
    open = {"id": 1, "text": "Open"}
    pending = {"id": 2, "text": "Pending"}
    hold = {"id": 3, "text": "Hold"}
    closed = {"id": 4, "text": "Closed"}
    var = [open, pending, hold, closed]


