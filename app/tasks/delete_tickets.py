from app.tasks.base import TaskBase
from app.tasks.celery import CeleryTaskBase, CeleryTasks
from app.database import Serial
from app.middleware import db


class DeleteTicketsMixin:
    def delete_tickets(self):
        tickets = Serial.all_clean()
        number_of_tickets = tickets.count()

        if number_of_tickets:
            tickets.delete()
            db.session.commit()

        return number_of_tickets


class DeleteTickets(DeleteTicketsMixin, TaskBase):
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
            number_of_tickets = self.delete_tickets()

            if number_of_tickets:
                self.log(f'DeleteTickets(Task): {number_of_tickets} deleted.')


@CeleryTasks.add
class DeleteTicketsCelery(DeleteTicketsMixin, CeleryTaskBase):
    proxy = 'DeleteTickets'

    def run(self, *args, **kwargs):
        self.delete_tickets()
