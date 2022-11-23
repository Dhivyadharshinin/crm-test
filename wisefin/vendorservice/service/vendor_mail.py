import smtplib
from nwisefin import settings
from django.db import transaction
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template import loader
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.service.userservice import Vendor_user_service
from vendorservice.models.vendormodels import VendorMail, Vendor
from environs import Env
from vendorservice.util.vendorutil import VendorStatusUtil, RequestStatusUtil, VendorGroupUtil

env = Env()
env.read_env()
BASE_URL = env.str("WISEFIN_URL")
is_send = env.str("MAIL_FEATURE_ENABLE")
email_id = env.str("SMTP_USER_NAME")
password = env.str("SMTP_KEY")
flag = False


def automate_mail_generator(data):
    emp_mail = data['emp_mail']
    raisername = data['raiser_name']
    rmname = data['rm_name']
    vendor_id = data['vendor_id']
    template = data['template']
    subject = data['subject']
    vendor_code = data['vendor_code']
    msg = MIMEMultipart()
    msg['from'] = 'Nwisefin@NorthernARC.com'
    msg['to'] = emp_mail
    msg['Subject'] = subject
    msg['Cc'] = ''
    template = template
    url = "https://www.northernarc.com/"
    data = {"raisername": raisername, "rmname": rmname, "Vendor_id": vendor_id,
            "url": url, 'vendor_code': vendor_code}
    body_html = template.render(data)
    msg.attach(MIMEText(body_html, 'html'))
    server = smtplib.SMTP("smtp-mail.outlook.com", 587)
    server.starttls()
    server.ehlo()
    server.login("Nwisefin@NorthernARC.com", "Today@123")
    server.send_message(msg)
    server.quit()
    return vendor_id


@transaction.atomic
class VendorEmail(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def vendor_mail(self, vendor_id):
        if flag:
            pass
        else:
            return
        vendor_list = Vendor.objects.using(self._current_app_schema()).filter(id=vendor_id, entity_id=self._entity_id())
        if len(vendor_list) != 0:
            vendor = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
            if vendor.requeststatus in (RequestStatusUtil.MODIFICATION, RequestStatusUtil.RENEWAL):
                mod_status = True
            else:
                mod_status = False

            if mod_status:
                vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=vendor_id)
                new_vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     id=vendor[
                                                                                         0].modify_ref_id).order_by(
                    'created_date')
                if len(new_vendor) != 0:
                    response = new_vendor[0]
                else:
                    response = vendor[0]
            else:
                vendor = Vendor.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=vendor_id,
                                                                                 modify_status=-1)
                response = vendor[0]
            mail_send = self.sending_mail(response, vendor_list[0])
            return mail_send
        else:
            logger.info('mail for vendor id '+str(vendor_id)+' is not send')
            return

    def sending_mail(self, mod_vendor, old_vendor):
        group = mod_vendor.group
        if group == VendorGroupUtil.OUTSOURCING:
            compliance = True
        else:
            compliance = False
        maker_id = mod_vendor.created_by
        rm_id = mod_vendor.rm_id
        vendor_status = old_vendor.vendor_status
        request_status = old_vendor.requeststatus
        status = [RequestStatusUtil.ACTIVATION, RequestStatusUtil.DEACTIVATION, RequestStatusUtil.TERMINATION,
                  RequestStatusUtil.RENEWAL]
        if request_status in status:
            return
        old_mail = VendorMail.objects.using(self._current_app_schema()).filter(vendor_id=old_vendor.id,
                                                                               entity_id=self._entity_id(),
                                                                               mail_type=request_status,
                                                                               rejected_by=-1, returned_by=-1,
                                                                               is_approved=0,
                                                                               compliance_type=compliance)
        if len(old_mail) == 0:
            vendor_mail = VendorMail.objects.using(self._current_app_schema()).create(
                vendor_id=old_vendor.id, maker_id=maker_id, rm_id=rm_id, mail_type=request_status,
                vendor_code=old_vendor.code, entity_id=self._entity_id(),compliance_type=compliance
            )
            self.get_detaild_vendor(vendor_mail, vendor_status, compliance)
        else:
            self.get_detaild_vendor(old_mail[0], vendor_status, compliance)
        return True

    def get_detaild_vendor(self, vendor_mail, vendor_status, compliance):
        mail_update = None
        mail_type = vendor_mail.mail_type
        return_type = vendor_mail.is_header
        employee_service = Vendor_user_service(self._scope())
        # raiser
        raiser = employee_service.get_employee(vendor_mail.maker_id)
        # rm
        rm = employee_service.get_employee(vendor_mail.rm_id)
        if (raiser is None) and (rm is None):
            return
        else:
            pass
        raisername = raiser.full_name
        rmname = rm.full_name
        vendor_id = vendor_mail.vendor_id
        vendor_code = vendor_mail.vendor_code
        mail_id = vendor_mail.id
        data = {'raiser_name': raisername, 'rm_name': rmname, 'vendor_id': vendor_id, 'vendor_code': vendor_code}
        subject = None
        template = None
        emp_mail = None
        if mail_type == RequestStatusUtil.ONBOARD:
            if vendor_status == VendorStatusUtil.PENDING_RM:
                subject = 'Vendor #' + str(vendor_code) + ' :: Onboard request raised by Raiser'
                template = loader.get_template("01_Onboard_submit_to_rm.html")
                emp_mail = rm.email_id
                mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                    id=mail_id, entity_id=self._entity_id()).update(is_rm=True)
            elif vendor_status in [VendorStatusUtil.PENDING_HEADER, VendorStatusUtil.PENDING_COMPLIANCE]:
                subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Approved by RM'
                template = loader.get_template("02_Onboard_submit_to_header.html")
                emp_mail = raiser.email_id
                mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                    id=mail_id, entity_id=self._entity_id()).update(is_header=True)
            elif vendor_status == VendorStatusUtil.APPROVED:
                if compliance:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Approved by Compliance'
                    template = loader.get_template("15_Onboard_Compliance_approved.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(is_approved=True)
                else:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Approved by Header'
                    template = loader.get_template("03_Onboard_header_approved.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(is_approved=True)
            elif vendor_status == VendorStatusUtil.REJECTED:
                if return_type is False:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Rejected by RM'
                    template = loader.get_template("04_Onboard_rm_rejected.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(rejected_by=1)
                else:
                    if compliance:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Rejected by Compliance'
                        template = loader.get_template("16_Onboard_Compliance_rejected.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(rejected_by=3)
                    else:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Rejected by Header'
                        template = loader.get_template("05_Onboard_header_rejected.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(rejected_by=2)
            elif vendor_status == VendorStatusUtil.RETURN:
                if return_type is False:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Returned by RM'
                    template = loader.get_template("06_Onboard_rm_returned.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(returned_by=1)
                else:
                    if compliance:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Returned by Compliance'
                        template = loader.get_template("17_Onboard_Compliance_returned.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(returned_by=3)
                    else:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Onboard Returned by Header'
                        template = loader.get_template("07_Onboard_header_returned.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(returned_by=2)
        elif mail_type == RequestStatusUtil.MODIFICATION:
            if vendor_status == VendorStatusUtil.PENDING_RM:
                subject = 'Vendor #' + str(vendor_code) + ' :: Modification request raised by Raiser'
                template = loader.get_template("08_Modification_submit_to_rm.html")
                emp_mail = rm.email_id
                mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                    id=mail_id, entity_id=self._entity_id()).update(is_rm=True)
            elif vendor_status in [VendorStatusUtil.PENDING_HEADER, VendorStatusUtil.PENDING_COMPLIANCE]:
                subject = 'Vendor #' + str(vendor_code) + ' :: Modification Approved by RM'
                template = loader.get_template("09_Modification_submit_to_header.html")
                emp_mail = raiser.email_id
                mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                    id=mail_id, entity_id=self._entity_id()).update(is_header=True)
            elif vendor_status == VendorStatusUtil.APPROVED:
                if compliance:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Modification Approved by Compliance'
                    template = loader.get_template("18_Modification_Compliance_approved.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(is_approved=True)
                else:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Modification Approved by Header'
                    template = loader.get_template("10_Modification_header_approved.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(is_approved=True)
            elif vendor_status == VendorStatusUtil.REJECTED:
                if return_type is False:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Modification Rejected by RM'
                    template = loader.get_template("11_Modification_rm_rejected.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(rejected_by=1)
                else:
                    if compliance:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Modification Rejected by Compliance'
                        template = loader.get_template("19_Modification_Compliance_rejected.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(rejected_by=3)
                    else:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Modification Rejected by Header'
                        template = loader.get_template("12_Modification_header_rejected.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(rejected_by=2)
            elif vendor_status == VendorStatusUtil.RETURN:
                if return_type is False:
                    subject = 'Vendor #' + str(vendor_code) + ' :: Modification Returned by RM'
                    template = loader.get_template("13_Modification_rm_returned.html")
                    emp_mail = raiser.email_id
                    mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                        id=mail_id, entity_id=self._entity_id()).update(returned_by=1)
                else:
                    if compliance:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Modification Returned by Compliance'
                        template = loader.get_template("20_Modification_Compliance_returned.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(returned_by=3)
                    else:
                        subject = 'Vendor #' + str(vendor_code) + ' :: Modification Returned by Header'
                        template = loader.get_template("14_Modification_header_returned.html")
                        emp_mail = raiser.email_id
                        mail_update = VendorMail.objects.using(self._current_app_schema()).filter(
                            id=mail_id, entity_id=self._entity_id()).update(returned_by=2)
        elif mail_type == RequestStatusUtil.ACTIVATION:
            pass
        elif mail_type == RequestStatusUtil.DEACTIVATION:
            pass
        elif mail_type == RequestStatusUtil.TERMINATION:
            pass
        elif mail_type == RequestStatusUtil.RENEWAL:
            pass
        data['subject'] = subject
        data['template'] = template
        data['emp_mail'] = emp_mail
        logger.info(str(subject))
        automate_mail_generator(data)
        return mail_update

# types
# returned_by (1-rm, 2-header, 3-compliance)
# rejected)by (1-rm, 2-header, 3-compliance)
# compliance_type (1-outsourcing, 0-others)
