import json
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from django.db import transaction
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template import loader

from docservice.service.documentservice import DocumentsService
from taservice.models import TAScheduler, TourRequest, TravelHistory, ClaimRequest
from django.utils.timezone import now
from userservice.service.employeeservice import TA_employee_service
from environs import Env
from utilityservice.data.response.nwisefinlist  import NWisefinList
# from taservice.service.travelrequirement import Cab_requirement, Bus_requirement, Air_requirement, Train_requirement, \
#     AccomodationBooking_requirement, Booking_requirement
from nwisefin.settings import logger
from taservice.models.tamodels import BusBookingInfo, CabBookingInfo, AirBookingInfo, TrainBookingInfo, \
    AccomodationBookingInfo, CabBookingDetails, BusBookingDetails, AirBookingDetails, TrainBookingDetails, \
    AccomodationBookingDetails, TourRequest, TourDetail, TravelHistory, BookingHistory, CabMapping,TADocuments
from taservice.data.response.tourmaker import Doc_response
from taservice.util.ta_util import App_type, Filterstatus, Travel_requirements, Validation, Status, App_level, \
    Timecalculation, TADocUtil, DocModule, TourRequest_BookingStatus, Requirements_booking_status, Requirements_official
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
time_function=Timecalculation()
env = Env()
env.read_env()
BASE_URL = env.str("WISEFIN_URL")
is_send = env.str("MAIL_FEATURE_ENABLE")
email_id = env.str("SMTP_USER_NAME")
password = env.str("SMTP_KEY")

@transaction.atomic
class ta_email(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)

    def automate_mail_gen(self,emp_mail, raisername, rmname, tour_id, template, id, subject):
        msg = MIMEMultipart()
        msg['from'] = "Nwisefin@NorthernARC.com"
        msg['to'] = emp_mail
        msg['Subject'] = subject
        server_id = BASE_URL
        msg['Cc'] = ''
        template = template
        # emp_name = emp_name
        # emp_id = emp_id
        # email = "ss"  # request.to
        url = "https://www.northernarc.com/"
        # email_url = "http://159.89.168.245:8089/ta/tourmaker?tour_id="+tour_id
        data = {"raisername": raisername, "rmname": rmname, "tour_id": tour_id, "url": url, "server_id": server_id}
        body_html = template.render(data)
        msg.attach(MIMEText(body_html, 'html'))
        # from_email = "nimbus@northernarc.com"
        # recipient_list = ""
        # body = MIMEText(body_html, 'html')
        # msg.attach(MIMEText(body))

        # file_count = len(request.FILES.getlist('file'))
        # for i in range(0, file_count):
        #     file = request.FILES.getlist('file')[i]
        #     # for filename in attachments:
        #     #     SourcePathName='/home/raghul/Downloads/' + filename
        #     print("source: ", file)
        #     # x = open(file.name, 'rb')
        #     part = MIMEBase('application', "octet-stream")
        #     part.set_payload((file).read())
        #     encoders.encode_base64(part)
        #     part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file.name))
        #     msg.attach(part)
        # msg.attach(body_html)
        # msg.attach(MIMEText("body_html", 'html'))
        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        server.starttls()
        server.ehlo()
        server.login("Nwisefin@NorthernARC.com", "Today@123")
        server.send_message(msg)
        server.quit()
        try:
            list = TAScheduler.objects.using(self._current_app_schema()).filter(
                id=id).update(is_send=1)
        except:
            pass

    def cancellation_report(self, requirement_id, booking_type):
        # requirement_id = 450
        # booking_type = 2
        # maker_id = 1
        # travelno = 123
        try:
            if int(booking_type) == Travel_requirements.accomodation:
                try:
                    details = list(AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=2).values())
                    info = list(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=2).values())
                    tour = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=info[0]['travel_detail_id'])[0]
                    travelno = tour.tour_id
                    employee = TourRequest.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=travelno)[0]
                    maker_id = employee.empgid
                    template = loader.get_template("cancel_1.html")
                except:
                    pass

            elif int(booking_type) == Travel_requirements.bus:
                try:
                    details = list(BusBookingDetails.objects.using(self._current_app_schema()).filter(
                        requirement_id=requirement_id, entity_id=self._entity_id(), booking_status=2).values())
                    info = list(BusBookingInfo.objects.using(self._current_app_schema()).filter(id=requirement_id,
                                                                                                entity_id=self._entity_id(),
                                                                                                booking_status=2).values())
                    tour = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=info[0]['travel_detail_id'])[0]
                    travelno = tour.tour_id
                    employee = TourRequest.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=travelno)[0]
                    maker_id = employee.empgid
                    template = loader.get_template("cancel_3.html")
                except:
                    pass

            elif int(booking_type) == Travel_requirements.train:
                try:
                    details = list(TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=2).values())
                    info = list(TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=2).values())
                    tour = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=info[0]['travel_detail_id'])[0]
                    travelno = tour.tour_id
                    employee = TourRequest.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=travelno)[0]
                    maker_id = employee.empgid
                    template = loader.get_template("cancel_5.html")
                except:
                    pass

            elif int(booking_type) == Travel_requirements.air:
                try:
                    details = list(AirBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=2).values())
                    info = list(AirBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=2).values())
                    tour = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=info[0]['travel_detail_id'])[0]
                    travelno = tour.tour_id
                    employee = TourRequest.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=travelno)[0]
                    maker_id = employee.empgid
                    template = loader.get_template("cancel_2.html")
                except:
                    pass


            elif int(booking_type) == Travel_requirements.cab:
                try:
                    mapping = list(CabMapping.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=2).values())
                    info = list(CabBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=2).values())
                    details = list(CabBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=mapping[0]['BookingDetailId'], booking_status=2).values())
                    tour = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=info[0]['travel_detail_id'])[0]
                    travelno = tour.tour_id
                    employee = TourRequest.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=travelno)[0]
                    maker_id = employee.empgid
                    template = loader.get_template("cancel_4.html")
                except:
                    pass

            employeeService = TA_employee_service(self._scope())
            maker_details = employeeService.maker_details(maker_id)
            maker_fullname = maker_details.full_name
            maker_mail = maker_details.email_id
            try:
                admin_mails = employeeService.admin_details1()
                admin_mail_id1 = []
                for admin in admin_mails:
                    for each_admin in admin:
                        if each_admin['email_id'] == None:
                            continue
                        else:
                            admin_mail_id1.append(each_admin['email_id'])
                # admin_email_id = {admin_mail_id}
            # admin_mails[0][0]['email_id']
            except:
                pass

            try:
                admin_mails = employeeService.admin_details2()
                admin_mail_id2 = []
                for admin in admin_mails:
                    for each_admin in admin:
                        if each_admin['email_id'] == None:
                            continue
                        else:
                            admin_mail_id2.append(each_admin['email_id'])
                # admin_email_id = {admin_mail_id}
            # admin_mails[0][0]['email_id']
            except:
                pass

            emp_mail = set(admin_mail_id1 + admin_mail_id2)
            admin_email = ','.join(emp_mail)
        except:
            pass

        doc_table = list(
            TADocuments.objects.using(self._current_app_schema()).filter(requirement_type=int(booking_type),
                                                                         entity_id=self._entity_id(),
                                                                         requirement=int(info[0]['id']),
                                                                          ref_type=1, status=1).values())

        msg = MIMEMultipart()
        msg['from'] = email_id
        msg['to'] = admin_email
        msg['Subject'] = 'Travel No :: '+str(travelno)+' Requirement Cancellation'
        server_id = BASE_URL
        msg['Cc'] = ''
        template = template
        url = "https://www.northernarc.com/"
        if int(booking_type) == Travel_requirements.accomodation:
            data = {"raisername": maker_fullname, "url": url, "server_id": server_id, "tour_id": travelno,
                    "checkindate": info[0]['checkin_time'],
                    "checkoutdate": info[0]['checkout_time'], "placeofstay": info[0]['place_of_stay'],
                    "vendorname": details[0]['vendor_name'],
                    "remarks": details[0]["comments"], "paidbyadmin": details[0]['admin_paid'],
                    "pnr_no": details[0]['PNR'], "issuancetype": details[0]['issuance_type'],
                    "bookingsite": details[0]['website'],
                    "personal_amt": details[0]['ticket_amount'], "official_amt": details[0]['ticket_amount_personal']
                    }
        elif int(booking_type) == Travel_requirements.bus:
            data = {"raisername": maker_fullname, "url": url, "server_id": server_id, "tour_id": travelno,
                    "fromtime": info[0]['from_time'],
                    "fromplace": info[0]['from_place'], "toplace": info[0]['to_place'],
                    "remarks": details[0]["comments"],
                    "pnr_no": details[0]['PNR'], "vendorname": details[0]['vendor_name'],
                    "paidbyadmin": details[0]['admin_paid'],
                    "issuancetype": details[0]['issuance_type'], "ticket_no": details[0]['ticket_no'],
                    "bookingsite": details[0]['website'], "personal_amt": details[0]['ticket_amount'],
                    "official_amt": details[0]['ticket_amount_personal']}
        elif int(booking_type) == Travel_requirements.train:
            data = {"raisername": maker_fullname, "url": url, "server_id": server_id, "tour_id": travelno,
                    "fromtime": info[0]['from_time'],
                    "fromplace": info[0]['from_place'], "toplace": info[0]['to_place'],
                    "remarks": details[0]['comments'],
                    "pnr_no": details[0]['pnr_no'], "vendorname": details[0]['vendor_name'],
                    "paidbyadmin": details[0]['admin_paid'],
                    "issuancetype": details[0]['issuance_type'], "ticket_no": details[0]['ticket_no'],
                    "bookingsite": details[0]['ticket_no'],
                    "personal_amt": details[0]['ticket_amount'], "official_amt": details[0]['ticket_amount_personal']}
        elif int(booking_type) == Travel_requirements.air:
            data = {"raisername": maker_fullname, "url": url, "fromtime": info[0]['from_time'], "tour_id": travelno,
                    "fromplace": info[0]['from_place'], "toplace": info[0]['to_place'],
                    "remarks": details[0]["comments"],
                    "pnr_no": details[0]['PNR'], "vendorname": details[0]['vendor_name'],
                    "paidbyadmin": details[0]['vendor_name'],
                    "issuancetype": details[0]['issuance_type'], "ticket_no": details[0]['ticket_no'],
                    "bookingsite": details[0]['website'],
                    "personal_amt": details[0]['ticket_amount'], "official": details[0]['ticket_amount_personal']}
        elif int(booking_type) == Travel_requirements.cab:
            data = {"raisername": maker_fullname, "url": url, "server_id": server_id,
                    "fromtime": info[0]['from_time'], "tour_id": travelno,
                    "fromplace": info[0]['from_place'], "toplace": info[0]['to_place'],
                    "remarks": details[0]["comments"],
                    "cabnumber": details[0]['cab_number'],
                    "pnr_no": details[0]['PNR'], "vendorname": details[0]['vendor_name'],
                    "paidbyadmin": mapping[0]['admin_paid'],
                    "issuancetype": details[0]['issuance_type'], "ticket_no": details[0]['ticket_no'],
                    "bookingsite": details[0]['ticket_no'], "cabtype": details[0]['travel_type_cab'],
                    "personal_amt": mapping[0]['ticket_amount'], "official_amt": mapping[0]['ticket_amount_personal']}
        body_html = template.render(data)
        msg.attach(MIMEText(body_html, 'html'))
        try:
            files = []
            if len(doc_table) > 0:
                for i in doc_table:
                    employee_id = None
                    doc_service = DocumentsService(self._scope())
                    file_id = i['file_id']
                    file = doc_service.mail_doc_download(file_id, employee_id)
                    files.append(file)
                for i in files:
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload((i).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(i.name))
                    msg.attach(part)
        except:
            pass
        server = smtplib.SMTP("smtp-mail.outlook.com", 587)
        server.starttls()
        server.ehlo()
        server.login(email_id, password)
        server.send_message(msg)
        server.quit()

    def mail_data(self, tour_id ):
        # tour_id = 1114
        try:
            logger.info("mail_data")
            tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,
                                                                                       entity_id=self._entity_id())[0]
            maker_id = tourrequest.empgid
            flow_condition = tourrequest.international_travel

            try:
                claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
                                                                                      entity_id=self._entity_id())[0]
                claim_amt_check = claim.claimedamount
                if int(claim_amt_check) < 25000:
                    flow_condition = 0
                else:
                    flow_condition = 1
            except:
                pass

            entry_list = list(TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
                                                                                             entity_id=self._entity_id()).values(
                'id', 'approvedby', 'request_type', 'applevel', 'status'))
            first_idx = entry_list[0]
            last_idx = entry_list[-1]
            try:
                second_last_idx = entry_list[-2]
            except:
                pass

            # if last_idx['status'] == 2 and last_idx['request_type'] == 'TourCancel':
            #     status = 'SUBMIT'
            # elif last_idx['status'] == 3 and last_idx['request_type'] == 'TourCancel':
            #     status = 'RM_APPROVED'
            if last_idx['status'] == 2 and last_idx['applevel'] == 1:
                status = '1'
            elif last_idx['request_type'] == 'TOUR' \
                    and second_last_idx['status'] == 3 and second_last_idx['applevel'] == 1 \
                    and last_idx['applevel'] == 3 and last_idx['status'] == 3:
                status = '2'
            elif last_idx['request_type'] == 'CLAIM' and second_last_idx['status'] == 3 and second_last_idx[
                'applevel'] == 1 \
                    and last_idx['applevel'] == 3 and last_idx['status'] == 2:
                status = '2'
            elif last_idx['request_type'] == 'ADVANCE' \
                    and second_last_idx['status'] == 3 and second_last_idx['applevel'] == 1 \
                    and last_idx['applevel'] == 3 and last_idx['status'] == 3:
                status = '2'
            # elif second_last_idx['status'] == 3 and second_last_idx['applevel'] == 2 and last_idx['applevel'] == 3\
            #         and last_idx['status'] == 2 and second_last_idx['request_type'] == 'TOUR':
            #     status = 'CEO_APPROVED'
            # elif second_last_idx['status'] == 3 and second_last_idx['applevel'] == 2 and last_idx['applevel'] == 3\
            #         and last_idx['status'] == 2 and second_last_idx['request_type'] == 'CLAIM':
            #     status = 'FH_APPROVED'
            # elif last_idx['status'] == 4 and second_last_idx['applevel'] == 2:
            #     status = 'CEO_REJECTED'
            # elif last_idx['status'] == 4 and second_last_idx['applevel'] == 2:
            #     status = 'FH_REJECTED'
            # elif last_idx['status'] == 5 and second_last_idx['applevel'] == 2:
            #     status = 'CEO_RETURNED'
            # elif last_idx['status'] == 5 and second_last_idx['applevel'] == 2:
            #     status = 'FH_RETURNED'
            elif last_idx['status'] == 4 and last_idx['applevel'] == 1:
                status = '4'
            elif last_idx['status'] == 5 and last_idx['applevel'] == 1:
                status = '3'
            elif last_idx['status'] == 3 and last_idx['applevel'] == 3 and last_idx['request_type'] == 'CLAIM':
                status = '5'
            elif last_idx['status'] == 3 and last_idx['applevel'] == 3 and last_idx['request_type'] == 'ADVANCE':
                status = '5'
            elif last_idx['status'] == 4 and last_idx['applevel'] == 3:
                status = '7'
            elif last_idx['status'] == 5 and last_idx['applevel'] == 3:
                status = '6'

            if last_idx['approvedby'] == -1:
                trans_status = second_last_idx['approvedby']
            else:
                trans_status = last_idx['approvedby']

            ta = TAScheduler.objects.using(self._current_app_schema()).create(tour_id=tour_id,
                                                                              tran_id=maker_id,
                                                                              tran_status=trans_status,
                                                                              tran_type=last_idx['request_type'],
                                                                              mail_type=status,
                                                                              created_by=last_idx['applevel'],
                                                                              created_date=now(),
                                                                              flow_condition=flow_condition)
            mail_send = self.interval_mail_trigger_with_using(tour_id)
            return
        except:
            pass


    def interval_mail_trigger_with_using(self, tour_id):
        list = TAScheduler.objects.using(self._current_app_schema()).filter(tour_id = tour_id,
            is_send=0).last()

        maker_id = int(list.tran_id)
        checker_id = int(list.tran_status)
        tour_id = int(list.tour_id)
        mail_type = int(list.mail_type)
        tran_type = list.tran_type
        id = list.id
        flow_condition = list.flow_condition

        employeeService = TA_employee_service(self._scope())
        if checker_id == -1:
            checker_fullname = 'Admin'
        else:
            checker_details = employeeService.checker_details(checker_id)
            checker_fullname = checker_details.full_name
            checker_mail = checker_details.email_id
        maker_details = employeeService.maker_details(maker_id)
        maker_fullname = maker_details.full_name
        maker_mail = maker_details.email_id
        try:
            admin_mails = employeeService.admin_details1()
            admin_mail_id1 = []
            for admin in admin_mails:
                for each_admin in admin:
                    if each_admin['email_id'] == None:
                        continue
                    else:
                        admin_mail_id1.append(each_admin['email_id'])
            # admin_email_id = {admin_mail_id}
        # admin_mails[0][0]['email_id']
        except:
            pass

        try:
            admin_mails = employeeService.admin_details2()
            admin_mail_id2 = []
            for admin in admin_mails:
                for each_admin in admin:
                    if each_admin['email_id'] == None:
                        continue
                    else:
                        admin_mail_id2.append(each_admin['email_id'])
            # admin_email_id = {admin_mail_id}
        # admin_mails[0][0]['email_id']
        except:
            pass

        admin_email = set(admin_mail_id1 + admin_mail_id2)

        # tour_dtls = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,
        #                                                                          entity_id=self._entity_id()).values('id', 'request_date', 'empgrade', 'empbranchgid', 'start_date', 'end_date', 'reason',
        #     'air_status', 'train_status', 'bus_status',
        #     'cab_status', 'accomodation_status')
        #
        # claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
        #                                                                       entity_id=self._entity_id())
        # ttl_claim_amt = 0
        # for tour_id in claim.tour_id:
        #     claim_amt = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
        #                                                                               entity_id=self._entity_id())[
        #         0].claimedamount
        #     ttl_claim_amt = ttl_claim_amt + claim_amt
        #     claim_amt = ttl_claim_amt
        # tour_dtls.append(claim_amt)

        if mail_type == MailType.SUBMIT and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                emp_mail = checker_mail
                raisername = maker_fullname
                subject = 'Travel #' + str(tour_id) + ' :: Travel request raised by Raiser'
                template = loader.get_template("email_2.html")
                logger.info("email_2.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_REJECTED and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by RM'
                template = loader.get_template("email_11.html")
                logger.info("email_11.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_RETURNED and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by RM'
                template = loader.get_template("email_9.html")
                logger.info("email_9.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_APPROVED and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                template = loader.get_template("email_3.html")
                logger.info("email_3.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

            if bool(is_send) == True:
                # admin
                try:
                    rmname = checker_fullname
                    raisername = maker_fullname
                    emp_mail = ','.join(admin_email)
                    subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                    template = loader.get_template("email_5.html")
                    logger.info("email_5.html")
                    self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
                except:
                    pass

        if mail_type == MailType.SUBMIT and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = checker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Travel claim raised by Raiser'
                template = loader.get_template("email_18.html")
                logger.info("email_18.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_REJECTED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by RM'
                template = loader.get_template("email_30.html")
                logger.info("email_30.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_RETURNED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by RM'
                template = loader.get_template("email_25.html")
                logger.info("email_25.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_APPROVED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                template = loader.get_template("email_20.html")
                logger.info("email_20.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

            if bool(is_send) == True:
                #         ADMIN
                try:
                    rmname = checker_fullname
                    raisername = maker_fullname
                    emp_mail = ','.join(admin_email)
                    subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                    template = loader.get_template("email_22.html")
                    logger.info("email_22.html")
                    self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
                except:
                    pass

        if mail_type == MailType.ADMIN_APPROVED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Approved by ADMIN'
                template = loader.get_template("email_77.html")
                logger.info("email_77.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_RETURNED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by Admin'
                template = loader.get_template("email_79.html")
                logger.info("email_79.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_REJECTED and tran_type == MailTranType.CLAIM:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by Admin'
                template = loader.get_template("email_78.html")
                logger.info("email_78.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_RETURNED and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by Admin'
                template = loader.get_template("email_81.html")
                logger.info("email_81.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_REJECTED and tran_type == MailTranType.TRAVEL:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by Admin'
                template = loader.get_template("email_80.html")
                logger.info("email_80.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

'''
        Advance email trigger-----------------------------------------------------------------------------
        if mail_type == MailType.SUBMIT and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = checker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Travel claim raised by advance'
                template = loader.get_template("email_50.html")
                logger.info("email_50.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_APPROVED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                template = loader.get_template("email_51.html")
                logger.info("email_51.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

            if bool(is_send) == True:
                #         ADMIN
                try:
                    rmname = checker_fullname
                    raisername = maker_fullname
                    emp_mail = ','.join(admin_mail_id1)
                    subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                    template = loader.get_template("email_53.html")
                    logger.info("email_53.html")
                    self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
                except:
                    pass

                #         ADMIN
                try:
                    rmname = checker_fullname
                    raisername = maker_fullname
                    emp_mail = ','.join(admin_mail_id2)
                    subject = 'Travel #' + str(tour_id) + ' :: Approved by RM'
                    template = loader.get_template("email_53.html")
                    logger.info("email_53.html")
                    self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
                except:
                    pass

        if mail_type == MailType.RM_REJECTED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by RM'
                template = loader.get_template("email_54.html")
                logger.info("email_54.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.RM_RETURNED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by RM'
                template = loader.get_template("email_52.html")
                logger.info("email_52.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_APPROVED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Approved by ADMIN'
                template = loader.get_template("email_55.html")
                logger.info("email_55.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_REJECTED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Rejection by Admin'
                template = loader.get_template("email_57.html")
                logger.info("email_57.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass

        if mail_type == MailType.ADMIN_RETURNED and tran_type == MailTranType.ADVANCE:
            try:
                rmname = checker_fullname
                raisername = maker_fullname
                emp_mail = maker_mail
                subject = 'Travel #' + str(tour_id) + ' :: Return by Admin'
                template = loader.get_template("email_56.html")
                logger.info("email_56.html")
                self.automate_mail_gen(emp_mail, raisername, rmname, tour_id, template, id, subject)
            except:
                pass
        ------------------------------------------------------------------------------------------------------              
'''
#             if mail_type == MailType.SUBMIT and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         emp_mail = emp['email_id']
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_57.html")
#                         logger.info("email_57.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_58.html")
#                         logger.info("email_58.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         emp_mail = emp['email_id']
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_1.html")
#                         logger.info("email_1.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_2.html")
#                         logger.info("email_2.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.RM_APPROVE and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_59.html")
#                         logger.info("email_59.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_60.html")
#                         logger.info("email_60.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_3.html")
#                         logger.info("email_3.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_4.html")
#                         logger.info("email_4.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     # admin
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_5.html")
#                         logger.info("email_5.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.CEO_APPROVED and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_61.html")
#                         logger.info("email_61.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_62.html")
#                         logger.info("email_62.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     # admin
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_63.html")
#                         logger.info("email_63.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.CEO_RETURN and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_70.html")
#                         logger.info("email_70.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_71.html")
#                         logger.info("email_71.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.CEO_REJECT and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_72.html")
#                         logger.info("email_72.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_73.html")
#                         logger.info("email_73.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.ADMINBOOKS and tran_type == MailTranType.TRAVEL:
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     template = loader.get_template("email_6.html")
#                     logger.info("email_6.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_7.html")
#                     logger.info("email_7.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#             #         ADMIN
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_8.html")
#                     logger.info("email_8.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#             if mail_type == MailType.RM_RETURNED and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_9.html")
#                         logger.info("email_9.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_10.html")
#                         logger.info("email_10.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_68.html")
#                         logger.info("email_68.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_69.html")
#                         logger.info("email_69.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.RM_REJECTED and tran_type == MailTranType.TRAVEL:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_11.html")
#                         logger.info("email_11.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_12.html")
#                         logger.info("email_12.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_72.html")
#                         logger.info("email_72.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_73.html")
#                         logger.info("email_73.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#
#             if mail_type == MailType.MAKERCANCEL and tran_type == MailTranType.TRAVEL:
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     template = loader.get_template("email_13.html")
#                     logger.info("email_13.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_14.html")
#                     logger.info("email_14.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#             #         ADMIN
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_15.html")
#                     logger.info("email_15.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#             if mail_type == MailType.SUBMIT and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_17.html")
#                         logger.info("email_17.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_18.html")
#                         logger.info("email_18.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#                 #         EMAIL.HTML FILE 16,19,32 ARE DUPLICATE(NOT USED HERE)
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_35.html")
#                         logger.info("email_35.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_36.html")
#                         logger.info("email_36.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.RM_APPROVE and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_20.html")
#                         logger.info("email_20.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_21.html")
#                         logger.info("email_21.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_22.html")
#                         logger.info("email_22.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_37.html")
#                         logger.info("email_37.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_38.html")
#                         logger.info("email_38.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_39.html")
#                         logger.info("email_39.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.RM_RETURN and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_25.html")
#                         logger.info("email_25.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_26.html")
#                         logger.info("email_26.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_45.html")
#                         logger.info("email_45.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_46.html")
#                         logger.info("email_46.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.RM_REJECT and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_30.html")
#                         logger.info("email_30.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_31.html")
#                         logger.info("email_31.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_45.html")
#                         logger.info("email_45.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_46.html")
#                         logger.info("email_46.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.FH_APPROVE and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_40.html")
#                         logger.info("email_40.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_38.html")
#                         logger.info("email_41.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_42.html")
#                         logger.info("email_42.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.FH_RETURN and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_47.html")
#                         logger.info("email_47.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_48.html")
#                         logger.info("email_48.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.FH_REJECT and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_53.html")
#                         logger.info("email_53.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_54.html")
#                         logger.info("email_54.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.ADMIN_APPROVED and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_43.html")
#                         logger.info("email_43.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_44.html")
#                         logger.info("email_44.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.ADMIN_RETURNED and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_27.html")
#                         logger.info("email_27.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_28.html")
#                         logger.info("email_28.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_29.html")
#                         logger.info("email_29.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_49.html")
#                         logger.info("email_49.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_50.html")
#                         logger.info("email_50.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.ADMIN_REJECTED and tran_type == MailTranType.CLAIM:
#                 if flow_condition == 0:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_33.html")
#                         logger.info("email_33.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_34.html")
#                         logger.info("email_34.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                 if flow_condition == 1:
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         template = loader.get_template("email_55.html")
#                         logger.info("email_55.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#                     #         ADMIN
#                     try:
#                         emp_id = checker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         rmname = emp['full_name']
#                         emp_mail = emp['email_id']
#
#                         emp_id = maker_id
#                         api_ser = ApiService(self._scope())
#                         emp = api_ser.get_emp_id(request, emp_id)
#                         raisername = emp['full_name']
#
#                         template = loader.get_template("email_56.html")
#                         logger.info("email_56.html")
#                         self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                     except:
#                         continue
#
#             if mail_type == MailType.SUBMIT and tran_type == MailTranType.MAKERCANCEL:
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     template = loader.get_template("email_13.html")
#                     logger.info("email_13.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_14.html")
#                     logger.info("email_14.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#             if mail_type == MailType.APPROVED and tran_type == MailTranType.MAKERCANCEL:
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     template = loader.get_template("email_13.html")
#                     logger.info("email_13.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_14.html")
#                     logger.info("email_14.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue
#
#                 #         ADMIN
#                 try:
#                     emp_id = checker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     rmname = emp['full_name']
#                     emp_mail = emp['email_id']
#
#                     emp_id = maker_id
#                     api_ser = ApiService(self._scope())
#                     emp = api_ser.get_emp_id(request, emp_id)
#                     raisername = emp['full_name']
#
#                     template = loader.get_template("email_15.html")
#                     logger.info("email_15.html")
#                     self.automate_mail_gen(emp_mail, emp_id, raisername, rmname, tour_id, template, id)
#                 except:
#                     continue


class MailType:
    SUBMIT = 1
    RM_APPROVED = 2
    RM_RETURNED = 3
    RM_REJECTED = 4
    ADMIN_APPROVED = 5
    ADMIN_RETURNED = 6
    ADMIN_REJECTED = 7
    FORWARD = 'FORWARD'
    ADMINBOOKS = 'ADMINBOOKS'

class MailTranType :
    TRAVEL = "TOUR"
    CLAIM = "CLAIM"
    ADVANCE = "ADVANCE"
    MAKERCANCEL = 'TourCancel'

class MailTranStatus:
    approver = 'approver'
    receiver = 'receiver'
    sender = 'sender'
    recommender = 'recommender'

class Admin:
    Admin = 'Admin'

# def Server(self, BASE_URL):
#     if BASE_URL == 'http://143.110.244.51:8185':
#         server_id = WISEFIN_URL
#     elif BASE_URL == 'https://sitnwisefin.northernarc.com:8443/nwisefin':
#         server_id = 'https://sitnwisefin.northernarc.com'
#     else:
#         server_id = 'http://127.0.0.1:8000'
#     return server_id


