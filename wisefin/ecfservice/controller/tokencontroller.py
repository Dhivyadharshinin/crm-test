import base64
import requests
from nwisefin.settings import SERVER_IP, logger
import boto3
from botocore.exceptions import ClientError
from django.http import HttpResponse
from nwisefin import settings
import json
from datetime import datetime

def get_authtoken_micro():
    ip_address=SERVER_IP+'/usrserv/auth_token'
    username = 'apuser'
    password = b'vsolv123'
    password = base64.b64encode(password)
    password=password.decode("utf-8")
    datas = json.dumps({"username": username, "password": password})
    resp = requests.post(ip_address,  data=datas,verify=False)
    token_data = json.loads(resp.content.decode("utf-8"))
    ### Validations
    if resp.status_code == 200:
        return token_data["token"]


# def send_mail(request):
def send_mail(data,template):
    print("data", data)
    recipient_check = settings.SAN_DESK
    sender_mailid = settings.SENDER_MAILID
    subject = data.get('subject')
    to = data.get('to')
    cc = data.get('cc')
    referenceno = data.get('referenceno')
    raiseddate = data.get('raiseddate')
    amount = data.get('amount')
    ecftype = data.get('ecftype')
    SENDER = "KVB <"+sender_mailid+">"
    # SENDER = 'emc-noreply@kvbmail.com'
    print("sender", SENDER)

    if recipient_check == True:
        RECIPIENT = to
    else:
        RECIPIENT = ["vsolvstab@gmail.com"]

    settings.logger.info([{"RECIPIENT": RECIPIENT}])
    CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"
    SUBJECT = subject
    # BODY_HTML = template
    today = datetime.now().date()
    BODY_HTML = "Dear Approver, <br></br><br> Please note the Claim raised by you dated:"     "  "+ "<b>"+str(raiseddate)+"</b>" + "   with Reference Num:"     "   "+ "<b>"+referenceno+"</b>" + "    has been successfully approved.</br>  \n<br></br><br></br><br></br> ECF Amount : " + "<b>"+str(amount)+"<b>" + "\n<br></br><br>Regards,</br>  <br>KVB EMC Center.</br>"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses':
                    RECIPIENT
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info("ECF mail Source:" + str(SENDER))
        logger.info("ECF mail response:" + str(response))
    except ClientError as e:
        settings.logger.info(str(e.response['Error']['Message']))
        return HttpResponse(e.response['Error']['Message'], content_type='application/json')
    else:
        settings.logger.info("Email sent! Message ID:"),
        settings.logger.info(str(response['MessageId']))
        return HttpResponse(response['MessageId'], content_type='application/json')


def send_mailraiser(data,template):
    print("data", data)
    recipient_check = settings.SAN_DESK
    sender_mailid = settings.SENDER_MAILID
    subject = data.get('subject')
    to = data.get('to')
    cc = data.get('cc')
    referenceno = data.get('referenceno')
    raiseddate = data.get('raiseddate')
    amount = data.get('amount')
    ecftype = data.get('ecftype')
    SENDER = "KVB <"+sender_mailid+">"
    # SENDER = 'emc-noreply@kvbmail.com'
    print("sender", SENDER)

    if recipient_check == True:
        RECIPIENT = to
    else:
        RECIPIENT = ["vsolvstab@gmail.com"]

    settings.logger.info([{"RECIPIENT": RECIPIENT}])
    CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"
    SUBJECT = subject
    # BODY_HTML = template
    today = datetime.now().date()
    BODY_HTML = "Dear Raiser, <br></br><br> Please note the Claim raised by you dated:"     "  "+ "<b>"+str(raiseddate)+"</b>" + "   with Reference Num:"     "   "+ "<b>"+str(referenceno)+"</b>" + "    has been successfully raised.</br>  \n<br></br><br></br><br></br> ECF Amount : " + "<b>"+str(amount)+"<b>" + "\n<br></br><br>Regards,</br>  <br>KVB EMC Center.</br>"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses':
                    RECIPIENT
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info("ECF mail Source:" + str(SENDER))
        logger.info("ECF mail response:" + str(response))
    except ClientError as e:
        settings.logger.info(str(e.response['Error']['Message']))
        return HttpResponse(e.response['Error']['Message'], content_type='application/json')
    else:
        settings.logger.info("Email sent! Message ID:"),
        settings.logger.info(str(response['MessageId']))
        return HttpResponse(response['MessageId'], content_type='application/json')


def send_mailreject(data,template):
    print("data", data)
    recipient_check = settings.SAN_DESK
    sender_mailid = settings.SENDER_MAILID
    subject = data.get('subject')
    to = data.get('to')
    cc = data.get('cc')
    referenceno = data.get('referenceno')
    raiseddate = data.get('raiseddate')
    amount = data.get('amount')
    ecftype = data.get('ecftype')
    SENDER = "KVB <"+sender_mailid+">"
    # SENDER = 'emc-noreply@kvbmail.com'
    print("sender", SENDER)

    if recipient_check == True:
        RECIPIENT = to
    else:
        RECIPIENT = ["vsolvstab@gmail.com"]

    settings.logger.info([{"RECIPIENT": RECIPIENT}])
    CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "ap-south-1"
    SUBJECT = subject
    # BODY_HTML = template
    today = datetime.now().date()
    BODY_HTML = "Dear Approver, <br></br><br> Please note the Claim raised by you dated:"     "  "+ "<b>"+str(raiseddate)+"</b>" + "   with Reference Num:"     "   "+ "<b>"+str(referenceno)+"</b>" + "    has been rejected successfully.</br>  \n<br></br><br></br><br></br> ECF Amount : " + "<b>"+str(amount)+"<b>" + "\n<br></br><br>Regards,</br>  <br>KVB EMC Center.</br>"
    CHARSET = "UTF-8"
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses':
                    RECIPIENT
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    # 'Text': {
                    #     'Charset': CHARSET,
                    #     'Data': BODY_TEXT,
                    # },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
        logger.info("ECF mail Source:" + str(SENDER))
        logger.info("ECF mail response:" + str(response))
    except ClientError as e:
        settings.logger.info(str(e.response['Error']['Message']))
        return HttpResponse(e.response['Error']['Message'], content_type='application/json')
    else:
        settings.logger.info("Email sent! Message ID:"),
        settings.logger.info(str(response['MessageId']))
        return HttpResponse(response['MessageId'], content_type='application/json')
