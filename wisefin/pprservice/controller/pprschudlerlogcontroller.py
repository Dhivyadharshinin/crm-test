# from nwisefin import settings
# import requests
# import datetime
# import json
# from apscheduler.schedulers.background import BackgroundScheduler
# from datetime import timedelta
# val_url = settings.VYSFIN_URL
#
#
# def ppr_log():
#     from userservice.controller.authcontroller import get_authtoken
#     from pprservice.data.request.pprinsertrequest import PPRlogrequest
#     from pprservice.service.ppr_reportservice import Pprservice
#     from nwisefin.settings import logger
#     # from pprservice.service.ppr_reportservice import Pprservice as PPRService
#
#     try:
#         from_date_time = Pprservice().pprlog_fromdate()
#         Current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         updated_time = datetime.datetime.now() + timedelta(hours=6)
#         log_id = []
#         i = 0
#         while True:
#             payload_ = {
#                 "Params": {
#                     "pageno": i,
#                     "tran_fromdate": str(from_date_time),
#                     "tran_todate": str(updated_time.strftime("%Y-%m-%d %H:%M:%S"))
#                 },
#                 "Classification": {
#                             "Entity_Gid": "1",
#                             "Create_By": "0ADMIN"
#                         }
#             }
#             print("log payload",payload_)
#             token_ = "Bearer  " + get_authtoken()
#             headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
#             resp_ = requests.post("" + val_url + "pprMonoMicro_split?Group=Mono_Get&Action=pprlog_out",
#                                   data=json.dumps(payload_),
#                                   headers=headers_,
#                                   verify=False).json()
#             print("mono response",resp_)
#             if resp_["MESSAGE"] == "NOT FOUND" or len(resp_["DATA"]) <=0:
#                 break
#             elif resp_["MESSAGE"] == "FOUND" and len(resp_["DATA"]) > 0:
#                 pprrequest_obj = PPRlogrequest(resp_, i, (i + 1), str(Current_date_time))
#                 ppr_service = Pprservice()
#                 pprdata = ppr_service.create_pprlog(pprrequest_obj)
#                 log_id.append(json.loads(pprdata.get()))
#                 logger.info(str({"PPR_Log": pprdata.get()}))
#             elif resp_["MESSAGE"] == "FOUND" or len(resp_["DATA"]) <= 0:
#                 break
#             i += 1
#         return {"data":log_id}
#     except Exception as e:
#         logger.info(str(e))
#         return {"error":str(e)}
#
# def ppr_monolog():
#     from userservice.controller.authcontroller import get_authtoken
#     from pprservice.data.request.pprinsertrequest import PPRlogrequest
#     from pprservice.service.ppr_reportservice import Pprservice
#     from nwisefin.settings import logger
#     from pprservice.service.ppr_reportservice import Pprservice as PPRService
#     from_date_time = Pprservice().pprlog_fromdate()
#     Current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     print("from date",from_date_time)
#     payload_ = {
#         "Params": {
#             "pageno": 0,
#             "tran_fromdate": str(from_date_time),
#             "tran_todate": str(Current_date_time)
#         },
#         "Classification": {
#             "Entity_Gid": "1",
#             "Create_By": "0ADMIN"
#         }
#     }
#     token_ = "Bearer  " + get_authtoken()
#     headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
#     resp_ = requests.post("" + val_url + "pprMonoMicro_split?Group=Mono_Get&Action=Insert",
#                           data=json.dumps(payload_),
#                           headers=headers_,
#                           verify=False).json()
#     return resp_
#
# def ppr_log_main():
#     from userservice.controller.authcontroller import get_authtoken
#     from pprservice.data.request.pprinsertrequest import PPRlogrequest
#     from pprservice.service.ppr_reportservice import Pprservice
#     from nwisefin.settings import logger
#     from pprservice.service.ppr_reportservice import Pprservice as PPRService
#     pprservice = PPRService()
#     pprserv_arr = []
#     i = 0
#     while True:
#         arr = pprservice.pprlog_main(i,i+10)
#         if len(arr) <=0:
#             break
#         pprserv = pprservice.create_ppr(arr)
#         pprserv_arr.append(pprserv.get())
#         i=i+10
#     return pprserv_arr
#
# def run_ppr_log_main():
#     from userservice.controller.authcontroller import get_authtoken
#     from pprservice.data.request.pprinsertrequest import PPRlogrequest
#     from pprservice.service.ppr_reportservice import Pprservice
#     from nwisefin.settings import logger
#     from pprservice.service.ppr_reportservice import Pprservice as PPRService
#     logger.info(f'PPR_LOG_START {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#     service = PPRService()
#     service.pprlog_check_currentdata_status()
#     log_main = {}
#     microLog = ppr_log()
#     print(f'micro api Time {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#     logger.info(str({'PPR_MICRO_API': microLog,"Time":str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#     if 'data' in microLog:
#         logger.info(str({'BEFORE_PPR_LOG_MAIN_START': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#         if len(microLog['data']) > 0:
#             logger.info(str({'PPR_LOG_MAIN_START': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#             log_main = ppr_log_main()
#             print(f'main to log len{len(microLog["data"])} Time {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#             logger.info(str({'PPR_LOG_MAIN': log_main,"Time":str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#         logger.info(str({'PPR_LOG_MAIN_END': str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#     else:
#         print(f'micro api failed Time {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#         logger.info(str({'PPR_LOG_MAIN': log_main,"Time":str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}))
#     logger.info(f'PPR_LOG_END {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
#
#
#
#
# def run_ppr_scheduler():
#     current_time = datetime.datetime.now() + timedelta(minutes=5)
#     sched = BackgroundScheduler()
#     h=current_time.hour
#     m=current_time.minute
#     s=current_time.second
#     sched.add_job(run_ppr_log_main, 'cron', hour=h,minute=m,second =s)
#     sched.start()
#
# def run_monolog_nac():
#     from userservice.controller.authcontroller import get_authtoken
#     from pprservice.data.request.pprinsertrequest import PPRlogrequest
#     from pprservice.service.ppr_reportservice import Pprservice
#     from nwisefin.settings import logger
#     from pprservice.service.ppr_reportservice import Pprservice as PPRService
#     from_date_time = Pprservice().pprlog_fromdate()
#     Current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     payload_ = {
#         "Params": {
#             "tran_fromdate": str(from_date_time),
#             "tran_todate": str(Current_date_time)
#         },
#         "Classification": {
#             "Entity_Gid": "1",
#             "Create_By": "0ADMIN"
#         }
#     }
#     token_ = "Bearer  " + get_authtoken()
#     headers_ = {"content-type": "application/json", "Authorization": "" + token_ + ""}
#     resp_ = requests.post("" + val_url + "pprMonoMicro_split?Group=Mono_Get&Action=ppr_insert_nac",
#                           data=json.dumps(payload_),
#                           headers=headers_,
#                           verify=False).json()
#     return resp_
