from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
#from ftplib import FTP
# import paramiko
from environs import Env
from nwisefin.settings import logger
from datetime import datetime
from utilityservice.permissions.util.dbutil import SFTP_ModuleList
from django.conf import settings
import os
import pathlib

env = Env()
env.read_env()
SFTP_HOST_IP = env.str('SFTP_HOST_IP')
SFTP_USER_NAME = env.str('SFTP_USER_NAME')
SFTP_PASSWORD = env.str('SFTP_PASSWORD')
SERVER_ENVIRONMENT = env.str('SERVER_ENVIRONMENT')
SFTP_PORT = int(env.str('SFTP_PORT'))


class SFTPCommonService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def sftp_common_upload_api(self, module,local_filepath, emp_id):
        try:
            arr=[]
            import time
            sftp_list=SFTP_ModuleList()
            final_module=sftp_list.get_val(module)
            if(final_module==None or final_module==""):
                return {"Message": "Invalid module name, pls add module name to util "}
            now_today_date = datetime.now()
            today_data = now_today_date.strftime("%d-%m-%Y")
            today_date = now_today_date.strftime("%Y-%m-%d")
            Month = now_today_date.strftime("%B")
            Day = now_today_date.strftime("%d")
            Year = now_today_date.strftime("%Y")

            file_name=local_filepath.split("/")[-1]
            #extension = os.path.splitext(filename)[1]
            #filename = ''.join(e for e in filename if e.isalnum())
            #filename = filename + extension
            #millis = int(round(time.time() * 1000))
            #Emp_gid = emp_id
            #concat_filename = str(Emp_gid) + "_" + str(millis) + "_" + file_name

            remote_filepath=SERVER_ENVIRONMENT+"/"+str(Year)+"/"+str(Month)+"/"+final_module+"/"+str(today_data)+"/"
            send_remote_file_path = remote_filepath + str(file_name)

            # print(SFTP_USER_NAME, SFTP_HOST_IP, SFTP_PASSWORD, SERVER_ENVIRONMENT)
            # ftp = FTP(SFTP_HOST_IP)
            # ftp.login(SFTP_USER_NAME, SFTP_PASSWORD)
            # print("SFTP Login Success")
            # data = []
            # ftp.dir(data.append)
            # data_log = [{"SFTP_ALL_DATA": data}]
            # logger.info(data_log)
            # for line in data:
            #     data_log = [{"SFTP_SINGLE_DATA": line}]
            #     logger.info(data_log)
            # remote_filepath = ftp.mkd(remote_filepath)
            # ftp.cwd(remote_filepath)
            # ftp.put(local_filepath, remote_filepath)
            # ftp.quit()

            t = paramiko.Transport((SFTP_HOST_IP, SFTP_PORT))
            # set connection timeout number.
            #t.banner_timeout = timeout
            # connect to remote sftp server
            t.connect(username=SFTP_USER_NAME, password=SFTP_PASSWORD)
            log_data = {"Message": "SFTP LOGIN SUCCESS","File_path":remote_filepath}
            logger.info(log_data)
            # get the SFTP client object.
            sftp = paramiko.SFTPClient.from_transport(t)
            # upload local file to remote server path.
            try:
                sftp.chdir(remote_filepath)  # Test if remote_path exists
            except IOError:
                sftp.mkdir(remote_filepath)  # Create remote_path
                sftp.chdir(remote_filepath)
            sftp.put(local_filepath, send_remote_file_path)
            # close the connection.
            t.close()
            return {"Message": "SUCCESS","File_path":send_remote_file_path}
        except Exception as e:
            log_data={"Message": "ERROR_OCCURED_ON_SFTP_CONTROLLER_", "Data": str(e)}
            logger.info(log_data)
            return log_data



# import ftplib
# session = ftplib.FTP('server.address.com','USERNAME','PASSWORD')
# file = open('kitten.jpg','rb')                  # file to send
# session.storbinary('STOR kitten.jpg', file)     # send the file
# file.close()                                    # close file and FTP
# session.quit()


#img_path = settings.MEDIA_ROOT
#final_file_path=img_path+file_path
#os.mkdir(final_file_path)
#pathlib.Path(final_file_path).mkdir(parents=True, exist_ok=True)
#print("Directory '% s' created" % final_file_path)