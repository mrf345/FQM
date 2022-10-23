import pytest

from . import TEST_REPEATS
from app.database import Task, Settings, Serial, Office
from app.settings import single_row


@pytest.mark.usefixtures('c')
def test_single_row_restrictions_enabled(c):
    task = Task.get()
    office = task.offices[0]

    if not Settings.get().single_row:
        c.get('/settings/single_row', follow_redirects=True)

    assert Settings.get().single_row is True

    message = f'flag setting single_row must be disabled'
    contains_message = lambda p: message in c\
        .get(p, follow_redirects=True)\
        .data.decode('utf-8')

    assert contains_message(f'/serial/{task.id}') is True
    assert contains_message('/serial_ra') is True
    assert contains_message(f'/serial_rt/{task.id}') is True
    assert contains_message(f'/pull_unordered/1/test') is True
    assert contains_message(f'/on_hold/1/test') is True
    assert contains_message(f'/touch/1') is True
    assert contains_message(f'/offices/{office.id}') is True
    assert contains_message(f'/office_a') is True
    assert contains_message(f'/office_d/{office.id}') is True
    assert contains_message(f'/office_da') is True
    assert contains_message(f'/task/{task.id}') is True
    assert contains_message(f'/task_d/{task.id}') is True
    assert contains_message(f'/common_task_a') is True
    assert contains_message(f'/task_a/{office.id}') is True


@pytest.mark.usefixtures('c')
def test_single_row_restrictions_disabled(c):
    task = Task.get()
    office = task.offices[0]

    if Settings.get().single_row:
        c.get('/settings/single_row', follow_redirects=True)

    assert Settings.get().single_row is False

    message = f'flag setting single_row must be disabled'
    contains_message = lambda p: message in c\
        .get(p, follow_redirects=True)\
        .data.decode('utf-8')

    assert contains_message(f'/serial/{task.id}') is False
    assert contains_message('/serial_ra') is False
    assert contains_message(f'/serial_rt/{task.id}') is False
    assert contains_message(f'/touch/1') is False
    assert contains_message(f'/offices/{office.id}') is False
    assert contains_message(f'/office_a') is False
    assert contains_message(f'/office_d/{office.id}') is False
    assert contains_message(f'/office_da') is False
    assert contains_message(f'/task/{task.id}') is False
    assert contains_message(f'/task_d/{task.id}') is False
    assert contains_message(f'/common_task_a') is False
    assert contains_message(f'/task_a/{office.id}') is False


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_single_row_pulling(_, c):
    c.get('/settings/single_row', follow_redirects=True)

    office = Office.get(0)
    tickets_length = office.tickets.count()
    last_number = getattr(office.tickets.order_by(Serial.timestamp.desc()).first(),
                          'number',
                          100)

    response = c.get(f'/pull', follow_redirects=False)
    pulled_ticket = Office.get(0).tickets.order_by(Serial.timestamp.desc()).first()

    # assert response.status == '200 OK'
    assert Office.get(0).tickets.count() - 1 == tickets_length
    assert pulled_ticket.number - 1 == last_number
    assert pulled_ticket.p is True

    c.get('/settings/single_row', follow_redirects=True)


@pytest.mark.usefixtures('c')
def test_single_row_switch_handler(c):
    single_row(True)

    assert Office.get(0) is not None
    assert [Task.get(0)] == Office.get(0).tasks

    single_row(False)

    assert Office.get(0) is None


@pytest.mark.parametrize('_', range(TEST_REPEATS))
@pytest.mark.usefixtures('c')
def test_single_row_feed(_, c):
    c.get('/settings/single_row', follow_redirects=True)
    c.get(f'/pull', follow_redirects=False)

    current_ticket = Serial.get_last_pulled_ticket(0)
    expected_parameters = {
        f'w{_index + 1}': f'{_index + 1}. {number}'
        for _index, number in enumerate(range(current_ticket.number + 1,
                                              current_ticket.number + 9))}

    response = c.get('/feed')

    for key, value in expected_parameters.items():
        assert response.json.get(key) == value

    c.get('/settings/single_row', follow_redirects=True)
