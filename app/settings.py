from app.middleware import db
from app.database import (Office, Task)


def single_row(status):
    ''' `single_row` flag setting switch handler.

    Parameters
    ----------
        status: bool
            setting switched to status.
    '''
    office = Office.get(id=0)
    task = Task.get(id=0)

    if status:  # NOTE: Enabled
        office = office or Office.create_generic(id=0)
        task = task or Task.create_generic(id=0)

        task.offices.append(office)
        db.session.commit()
    else:
        office and office.delete_all()
