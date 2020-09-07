from app.tasks.base import TaskBase
from app.database import Serial
from app.middleware import db


class DeleteTickets(TaskBase):
    def __init__(self, app, interval=5):
        '''Task to reset tickets index number to 0.

        Parameters
        ----------
        app : Flask app
        interval : int, optional
            duration of sleep between iterations in seconds, by default 5
        '''
        super().__init__(app)
        self.app = app
        self.interval = interval

    def run(self):
        @self.execution_loop()
        def main():
            tickets = Serial.query.filter(Serial.number != 100)

            if tickets.count():
                tickets.delete()
                db.session.commit()
                self.log('DeleteTickets(Task): All tickets deleted.')
