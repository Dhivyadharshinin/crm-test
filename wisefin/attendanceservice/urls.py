from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from attendanceservice.controller import leavecontroller, attendancecontroller, utilcontroller, alertmessagecontroller

urlpatterns = [
                 path('leave_request', leavecontroller.leave_request, name='Leave Request'),
                 path('leave_request/<leave_id>', leavecontroller.fetch_leave, name='Get Leave Request'),
                 path('leave_approve', leavecontroller.leave_approver_status, name='Leave Approve'),
                 path('leave_approve/<leave_id>', leavecontroller.fetch_leave_approve, name='Get Leave Approve'),
                 path('leave_summary', leavecontroller.leave_summary, name='Get Leave Approve'),
                 path('check_in', attendancecontroller.check_in, name='Check In'),
                 path('check_in/<log_id>', attendancecontroller.fetch_check_in_log, name='Get Check In'),
                 path('holiday_type', utilcontroller.holiday_type, name='Holiday Type'),
                 path('attendance_type_summary', utilcontroller.attendance_type_summary,
                      name='Attendance Type Summary'),
                 path('update_alert_message/<alert_id>', alertmessagecontroller.update_alert_message,
                      name='Update alert message'),
                 path('get_alert', alertmessagecontroller.alert, name='Alert Summary'),
                 path('alert/<alert_id>', alertmessagecontroller.get_alert, name='Get Alert'),
                 path('get_ip', alertmessagecontroller.get_ip, name='Get IP'),
                 # attendance , attendance report
                 path('attendance', attendancecontroller.attendance_summary, name='Attendance Summary'),
                 path('attendanceexcel',attendancecontroller.attendanceexcel, name='attendanceexcel'),
                 path('attendance/<attendance_id>', attendancecontroller.fetch_attendance, name='Get Attendance'),
                 #  attendance scheduler
                 path('attendance_scheduler', attendancecontroller.per_day_attendance, name='per_day_attendance'),
                 path('per_day_log', attendancecontroller.per_day_log, name='per_day_attendance'),
                 path('per_day_log/<emp_id>', attendancecontroller.per_day_log_employee, name='per_day_log_employee'),
                 path('atd_download/<file_id>', attendancecontroller.attendance_download_file, name='Attendance Download'),
                #  check in log
                path('day_log_summary',attendancecontroller.day_log_summary,name='day_log_summary'),
                # employee leave count
                path('employee_leave_count', leavecontroller.get_leave_count, name='get_leave_count'),
                path('payrollattendance',attendancecontroller.payroll_attendance,name='payrollatendance')

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
