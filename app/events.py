from sqlalchemy import event


def setup_events(db):
    from app.views.core import touch, display, repeat_announcement
    from app.helpers import (
        get_all_offices_cached,
        get_settings_cached,
        is_user_office_operator,
    )
    from app.database import (
        Serial, Display_store, Settings, Aliases, Touch_store, Task,
        Slides_c, Slides, Vid, Office, Settings, User,
    )

    serial_funcs = get_cached_serial_funcs()
    task_funcs = get_cached_task_funcs()

    model_action_func_map = {
        (Serial, 'update'): serial_funcs,
        (Serial, 'insert'): serial_funcs,
        (Serial, 'delete'): serial_funcs,
        (Display_store, 'update'): [touch, display],
        (Aliases, 'update'): [touch, display],
        (Settings, 'update'): [touch],
        (Touch_store, 'update'): [touch],
        (Task, 'update'): task_funcs,
        (Task, 'insert'): task_funcs,
        (Task, 'delete'): task_funcs,
        (Slides_c, 'update'): [display],
        (Vid, 'update'): [display],
        (Slides, 'update'): [display],
        (Slides, 'insert'): [display],
        (Slides, 'delete'): [display],
        (Settings, 'update'): [get_settings_cached],
        (User, 'update'): [is_user_office_operator],
        (User, 'insert'): [is_user_office_operator],
        (User, 'delete'): [is_user_office_operator],
        (Office, 'insert'): [repeat_announcement, get_all_offices_cached],
        (Office, 'update'):  serial_funcs,
        (Office, 'delete'):  [
            repeat_announcement,
            get_all_offices_cached,
            is_user_office_operator,
            *serial_funcs,
        ],
    }

    def clear_cache(session):
        modal_changes = getattr(session, '_model_changes', {})

        for instance, action in modal_changes.values():
            endpoints = model_action_func_map.get(
                (instance.__class__, action), []
            )

            for endpoint in endpoints:
                endpoint.cache_clear()

    event.listen(db.session, 'after_commit', clear_cache)


def get_cached_serial_funcs():
    from app.views.core import feed
    from app.helpers import (
        get_number_of_active_tickets_cached,
        get_number_of_active_tickets_office_cached,
        get_number_of_active_tickets_task_cached,
    )

    return [
        feed,
        get_number_of_active_tickets_cached,
        get_number_of_active_tickets_office_cached,
        get_number_of_active_tickets_task_cached,
    ]


def get_cached_task_funcs():
    from app.views.core import touch
    return [touch, *get_cached_serial_funcs()]
