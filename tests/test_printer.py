import pytest
from random import randint
from datetime import datetime
from escpos.printer import Dummy

from app.printer import get_font_height_width, printit
from app.constants import PRINTED_TICKET_DIMENSIONS, PRINTED_TICKET_SCALES, PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH


def test_printer_height_and_width_random_scaling():
    dimensions = PRINTED_TICKET_DIMENSIONS
    random_scale = randint(1, 20)

    for font, (height, width) in dimensions.items():
        expected_height = height * random_scale
        expected_width = width * random_scale
        returned_dimension = get_font_height_width(font=font,
                                                   scale=random_scale)

        assert returned_dimension.get('height') == (PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                                                    if expected_height > PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                                                    else expected_height)
        assert returned_dimension.get('width') == (PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                                                   if expected_width > PRINTED_TICKET_MAXIMUM_HEIGH_OR_WIDTH
                                                   else expected_width)


@pytest.mark.parametrize('scale', PRINTED_TICKET_SCALES)
def test_printit_random_scales_sanity_check(scale):
    printer = Dummy()
    ticket = 'TESTING100'
    office = 'TESTING_OFFICE'
    tickets_ahead = 'TESTING300'
    task = 'TESTING_TASK_NAME'
    current_ticket = 'TESTING200'
    site = 'www.testing.com'
    language = 'en'
    number_of_saperators = 2

    ticket_content = printit(printer, ticket, office, tickets_ahead, task,
                             current_ticket, site, language, scale
                             ).output.decode('utf-8')

    assert 'FQM\n' in ticket_content
    assert f'\n{site}\n' in ticket_content
    assert f'\n{ticket}\n' in ticket_content
    assert f'\nOffice : {office}\n' in ticket_content
    assert f'\nCurrent ticket : {current_ticket}\n' in ticket_content
    assert f'\nTickets ahead : {tickets_ahead}\n' in ticket_content
    assert f'\nTask : {task}\n' in ticket_content
    assert f'\nTime : {datetime.now().__str__()[:-7]}\n' in ticket_content
    assert ticket_content.count(f'\n{"-" * 15}\n') == number_of_saperators
