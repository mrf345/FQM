from sqlalchemy import event


def setup_events(db):
    from app.views.core import feed, touch, display, repeat_announcement
    from app.helpers import (
        get_all_offices_cached, get_settings_cached,
        get_number_of_active_tickets_cached,
        get_number_of_active_tickets_office_cached,
        get_number_of_active_tickets_task_cached,
    )
    from app.database import (
        Serial, Display_store, Settings, Aliases, Touch_store, Task,
        Slides_c, Slides, Vid, Office, Settings,
    )

    serial_funcs = [
        feed,
        get_number_of_active_tickets_cached,
        get_number_of_active_tickets_office_cached,
        get_number_of_active_tickets_task_cached,
    ]

    model_action_func_map = {
        (Office, 'insert'): [repeat_announcement, get_all_offices_cached],
        (Office, 'delete'): [repeat_announcement, get_all_offices_cached],
        (Serial, 'update'): serial_funcs,
        (Serial, 'insert'): serial_funcs,
        (Serial, 'delete'): serial_funcs,
        (Display_store, 'update'): [touch, display],
        (Aliases, 'update'): [touch, display],
        (Settings, 'update'): [touch],
        (Touch_store, 'update'): [touch],
        (Task, 'update'): [touch],
        (Task, 'insert'): [touch],
        (Task, 'delete'): [touch],
        (Slides_c, 'update'): [display],
        (Vid, 'update'): [display],
        (Slides, 'update'): [display],
        (Slides, 'insert'): [display],
        (Slides, 'delete'): [display],
        (Settings, 'update'): [get_settings_cached],
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
