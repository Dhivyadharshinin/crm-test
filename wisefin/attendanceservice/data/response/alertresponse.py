import json


class AlertResponse:
    id = ''
    leave_data_id = ''
    status = ''
    message = ''
    created_date = ''
    alert_to = ''
    alert_from = ''
    seen = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_leave_data_id(self, leave_data_id):
        self.leave_data_id = ''
        if leave_data_id is not None:
            self.leave_data_id = leave_data_id

    def set_status(self, status):
        self.status = ''
        if status is not None:
            self.status = status

    def set_message(self, message):
        self.message = ''
        if message is not None:
            self.message = message

    def set_created_date(self, created_date):
        self.created_date = ''
        if created_date is not None:
            self.created_date = created_date

    def set_alert_to(self, alert_to):
        self.alert_to = ''
        if alert_to is not None:
            self.alert_to = alert_to

    def set_alert_from(self, alert_from):
        self.alert_from = ''
        if alert_from is not None:
            self.alert_from = alert_from

    def set_seen(self, seen):
        self.seen = ''
        if self is not None:
            self.seen = seen
