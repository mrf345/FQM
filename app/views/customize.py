import os
from flask import url_for, flash, request, render_template, redirect, Blueprint
from flask_login import login_required
from werkzeug.utils import secure_filename


import app.database as data
from app.middleware import db, files
from app.forms.constents import EVERY_TIME_OPTIONS
from app.forms.customize import (DisplayScreenForm, TouchScreenForm, TicketForm,
                                 AliasForm, VideoForm, MultimediaForm, SlideAddForm,
                                 SlideSettingsForm, BackgroundTasksForms)
from app.printer import get_printers_cli, get_printers_usb
from app.tasks.celery import CeleryTasks
from app.utils import absolute_path, getFolderSize, convert_to_int_or_hex
from app.constants import SUPPORTED_MEDIA_FILES
from app.helpers import (reject_not_admin, reject_slides_enabled, reject_videos_enabled,
                         get_tts_safely)
from app.tasks import start_tasks, stop_tasks


cust_app = Blueprint('cust_app', __name__)


@cust_app.route('/customize')
@login_required
@reject_not_admin
def customize():
    ''' view of main customize screen '''
    return render_template('customize.html',
                           page_title='Customization',
                           navbar='#snb2',
                           vtrue=data.Vid.get().enable,
                           strue=data.Slides_c.get().status)


@cust_app.route('/ticket', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def ticket():
    ''' view of ticket customization '''
    windows = os.name == 'nt'
    settings = data.Settings.get()
    printer = data.Printer.get()
    touch_screen_settings = data.Touch_store.get()
    printers = get_printers_cli(windows=windows, unix=not windows)\
        if windows or settings.lp_printing else get_printers_usb()
    form = TicketForm(printers, settings.lp_printing)

    if form.validate_on_submit():
        printer = data.Printer.get()  # NOTE: sessions's lost

        if form.kind.data == 1:  # Rigestered
            printer.value = form.value.data
            printer.active = False
            touch_screen_settings = data.Touch_store.get()  # NOTE: sessions's lost
            touch_screen_settings.n = True
        else:  # Printed
            printer_id = form.printers.data

            if printer_id == '00':  # Not found
                flash('Error: you must have available printer, to use printed',
                      'danger')
                return redirect(url_for('cust_app.ticket'))

            printer.header = form.header.data
            printer.sub = form.sub.data

            if windows or settings.lp_printing:
                printer.name = printer_id
            else:
                id_chunks = printer_id.split('_')
                printer.vendor = convert_to_int_or_hex(id_chunks[0])
                printer.product = convert_to_int_or_hex(id_chunks[1])

                if len(id_chunks) == 4:
                    printer.in_ep = convert_to_int_or_hex(id_chunks[2])
                    printer.out_ep = convert_to_int_or_hex(id_chunks[3])
                else:
                    printer.in_ep = None
                    printer.out_ep = None

            printer.active = True
            printer.langu = form.langu.data
            printer.value = form.value.data
            printer.scale = form.scale.data
            touch_screen_settings = data.Touch_store.get()  # NOTE: sessions's lost
            touch_screen_settings.n = False

        db.session.commit()
        flash('Notice: settings have been updated .', 'info')
        return redirect(url_for('cust_app.ticket'))

    if not form.errors:
        form.kind.data = 1 if touch_screen_settings.n else 2
        form.langu.data = printer.langu
        form.value.data = printer.value
        form.scale.data = printer.scale
        form.header.data = printer.header
        form.sub.data = printer.sub

        if windows or settings.lp_printing:
            form.printers.data = printer.name or ''
        else:
            form.printers.data = f'{printer.vendor}_{printer.product}'

            if printer.in_ep and printer.out_ep:
                form.printers.data += f'_{printer.in_ep}_{printer.out_ep}'

    return render_template('ticket.html', navbar='#snb2',
                           page_title='Tickets',
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status,
                           form=form, hash='#da7')


@cust_app.route('/video', methods=['GET', 'POST'])
@login_required
@reject_not_admin
@reject_slides_enabled
def video():
    ''' view of video customization for display '''
    form = VideoForm()
    display_screen_settings = data.Display_store.query.first()
    video = data.Vid.get()

    if form.validate_on_submit():
        if not form.video.data:
            video.enable = 2
            video.vkey = None
            video.vname = ''
        else:
            media_record = data.Media.get(form.video.data)
            video.vkey = form.video.data
            video.enable = form.enable.data
            video.vname = media_record.name
            media_record.used = True
            display_screen_settings.vkey = form.video.data

        video.ar = form.ar.data
        video.controls = form.controls.data
        video.mute = form.mute.data

        db.session.commit()
        flash('Notice: new video has been set.', 'info')
        return redirect(url_for('cust_app.video'))

    if video and not form.errors:
        form.video.data = video.vkey
        form.enable.data = video.enable
        form.ar.data = video.ar
        form.controls.data = video.controls
        form.mute.data = video.mute

    return render_template('video.html',
                           page_title='Video settings',
                           navbar='#snb2',
                           hash='#da5',
                           form=form,
                           vtrue=video.enable,
                           strue=data.Slides_c.get().status)


@cust_app.route('/slideshow', methods=['GET', 'POST'])
@login_required
@reject_not_admin
@reject_videos_enabled
def slideshow():
    ''' view of slide-show customization for display '''
    slides = data.Slides_c.get()
    page = request.args.get('page', 1, type=int)
    pagination = data.Slides.query.paginate(page, per_page=10,
                                            error_out=False)

    return render_template('slideshow.html',
                           len=len,
                           navbar='#snb2',
                           sli=slides,
                           mmm=data.Slides.query,
                           slides=pagination.items,
                           pagination=pagination,
                           sm=data.Slides.query.filter(data.Slides.
                                                       ikey != 0).count(),
                           page_title='All slides',
                           hash='#ss1',
                           dropdown='#dropdown-lvl3',
                           vtrue=data.Vid.get().enable,
                           strue=slides.status)


@cust_app.route('/slide_a', methods=['GET', 'POST'])
@login_required
@reject_not_admin
@reject_videos_enabled
def slide_a():
    ''' adding a slide '''
    form = SlideAddForm()

    if form.validate_on_submit():
        background = form.background.data

        if background:
            image = data.Media.get(background)

            if not image:
                flash('Error: wrong entry, something went wrong', 'danger')
                return redirect(url_for('cust_app.slide_a'))

            background = image.name
        else:
            background = form.bgcolor.data

        ss = data.Slides()
        ss.title = form.title.data
        ss.hsize = form.hsize.data
        ss.hcolor = form.hcolor.data
        ss.hfont = form.hfont.data
        ss.hbg = form.hbg.data
        ss.subti = form.subti.data
        ss.tsize = form.tsize.data
        ss.tcolor = form.tcolor.data
        ss.tfont = form.tfont.data
        ss.tbg = form.tbg.data
        ss.bname = background
        ss.ikey = form.background.data

        db.session.add(ss)
        db.session.commit()
        flash('Notice: templates been updated.', 'info')
        return redirect(url_for('cust_app.slideshow'))

    return render_template('slide_add.html',
                           page_title='Add Slide ',
                           form=form, navbar='#snb2',
                           hash=1,
                           dropdown='#dropdown-lvl3',
                           vtrue=data.Vid.get().enable,
                           strue=data.Slides_c.get().status)


@cust_app.route('/slide_c', methods=['GET', 'POST'])
@login_required
@reject_not_admin
@reject_videos_enabled
def slide_c():
    ''' updating a slide '''
    form = SlideSettingsForm()
    sc = data.Slides_c.get()

    if form.validate_on_submit():
        sc.rotation = form.rotation.data
        sc.navigation = form.navigation.data
        sc.effect = form.effect.data
        sc.status = form.status.data

        db.session.add(sc)
        db.session.commit()
        flash('Notice: slide settings is done.', 'info')
        return redirect(url_for('cust_app.slide_c'))

    if not form.errors:
        form.rotation.data = sc.rotation
        form.navigation.data = sc.navigation
        form.effect.data = sc.effect
        form.status.data = sc.status

    return render_template('slide_settings.html',
                           form=form, navbar='#snb2',
                           hash='#ss2',
                           page_title='Slideshow settings',
                           dropdown='#dropdown-lvl3',
                           vtrue=data.Vid.get().enable,
                           strue=sc.status)


@cust_app.route('/slide_r/<int:f_id>')
@login_required
@reject_not_admin
@reject_videos_enabled
def slide_r(f_id):
    ''' removing a slide '''
    if not data.Slides.query.count():
        flash('Error: there is no slides to be removed ', 'danger')
        return redirect(url_for('cust_app.slideshow'))

    slide = data.Slides.get(f_id)

    if slide:
        db.session.delete(slide)
    else:
        if not f_id:
            for a in data.Slides.query:
                db.session.delete(a)

    db.session.commit()
    flash('Notice: All slides removed.', 'info')
    return redirect(url_for('cust_app.slideshow'))


@cust_app.route('/multimedia/<int:aa>', methods=['POST', 'GET'])
@login_required
@reject_not_admin
def multimedia(aa):
    ''' uploading multimedia files '''
    if aa == 0:
        flash('Notice: if you followed the rules, it should be uploaded ..',
              'success')

    files_limit_indicator = 300
    folder_size_limit_indicator = 2000
    media_path = absolute_path('static/multimedia')
    form = MultimediaForm()
    medias = data.Media.query
    page = request.args.get('page', 1, type=int)
    pagination = data.Media.query.paginate(page,
                                           per_page=10,
                                           error_out=False)
    supported_images = SUPPORTED_MEDIA_FILES[0]
    supported_audios = SUPPORTED_MEDIA_FILES[1]
    supported_videos = SUPPORTED_MEDIA_FILES[2]
    supported_all = supported_images + supported_audios + supported_videos

    if medias.count():  # cleanup unused media files
        for media in medias:
            if os.path.isfile(os.path.join(media_path, media.name)):
                media.used = media.is_used()
            else:
                db.session.delete(media)

        db.session.commit()

    if form.validate_on_submit():
        name = secure_filename(form.mf.data.filename)
        extension = name[-3:]

        if extension in supported_all:
            files.save(request.files['mf'], name=name)
            db.session.add(data.Media(extension in supported_videos or name[-4:] in supported_videos,
                                      extension in supported_audios, extension in supported_images,
                                      False, name))
        else:
            flash('Error: wrong entry, something went wrong', 'danger')
            return redirect(url_for('cust_app.multimedia', aa=1))

        db.session.commit()
        return redirect(url_for('cust_app.multimedia', aa=0))

    return render_template('multimedia.html',
                           page_title='Multimedia',
                           navbar='#snb2',
                           form=form,
                           hash='#da1',
                           mmm=medias,
                           len=len,
                           ml=SUPPORTED_MEDIA_FILES,
                           mmmp=pagination.items,
                           pagination=pagination,
                           tc=data.Touch_store.query,
                           sl=data.Slides.query,
                           dc=data.Display_store.query,
                           fs=int(getFolderSize(media_path, True)),
                           nofl=files_limit_indicator,
                           sfl=folder_size_limit_indicator,
                           vtrue=data.Vid.get().enable,
                           strue=data.Slides_c.get().status)


@cust_app.route('/multi_del/<int:f_id>')
@login_required
@reject_not_admin
def multi_del(f_id):
    ''' to delete multimedia file '''
    media_path = absolute_path('static/multimedia/')
    medias = data.Media.query.filter_by(used=False)
    media = medias.filter_by(id=f_id).first()

    if not medias.count():
        flash('Error: there is no unused multimedia file to be removed !',
              'danger')
        return redirect(url_for('cust_app.multimedia', aa=1))

    def delete_media(m):
        file_path = os.path.join(media_path, m.name)

        if os.path.isfile(file_path):
            os.remove(file_path)

        db.session.delete(m)

    if media:
        delete_media(media)
    elif not f_id:
        for media in medias:
            delete_media(media)
    else:
        flash('Error: there is no unused multimedia file to be removed !',
              'danger')
        return redirect(url_for('cust_app.multimedia', aa=1))

    db.session.commit()
    flash('Notice: multimedia file been removed.', 'info')
    return redirect(url_for('cust_app.multimedia', aa=1))


@cust_app.route('/displayscreen_c/<int:stab>', methods=['POST', 'GET'])
@login_required
@reject_not_admin
def displayscreen_c(stab):
    ''' view for display screen customization '''
    form = DisplayScreenForm()
    text_to_speech = get_tts_safely()

    if stab not in range(1, 9):
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('core.root'))

    touch_s = data.Display_store.get()

    if form.validate_on_submit():
        touch_s.tmp = form.display.data
        touch_s.title = form.title.data
        touch_s.hsize = form.hsize.data
        touch_s.hcolor = form.hcolor.data
        touch_s.hbg = form.hbg.data
        touch_s.tsize = form.tsize.data
        touch_s.tcolor = form.tcolor.data
        touch_s.h2size = form.h2size.data
        touch_s.h2color = form.h2color.data
        touch_s.ssize = form.ssize.data
        touch_s.scolor = form.scolor.data
        touch_s.mduration = form.mduration.data
        touch_s.hfont = form.hfont.data
        touch_s.tfont = form.tfont.data
        touch_s.h2font = form.h2font.data
        touch_s.sfont = form.sfont.data
        touch_s.mduration = form.mduration.data
        touch_s.rrate = form.rrate.data
        touch_s.anr = form.anr.data
        touch_s.anrt = form.anrt.data
        touch_s.effect = form.effect.data
        touch_s.repeats = form.repeats.data
        touch_s.prefix = form.prefix.data
        touch_s.always_show_ticket_number = form.always_show_ticket_number.data
        touch_s.wait_for_announcement = form.wait_for_announcement.data
        touch_s.hide_ticket_index = form.hide_ticket_index.data

        if not form.background.data:
            touch_s.bgcolor = form.bgcolor.data
            touch_s.ikey = None
        else:
            touch_s.bgcolor = data.Media.query.filter_by(id=form.background
                                                         .data).first().name
            data.Media.query.filter_by(id=form.background
                                       .data).first().used = True
            db.session.commit()
            touch_s.ikey = form.background.data

        if not form.naudio.data:
            touch_s.audio = 'false'
            touch_s.akey = None
        else:
            touch_s.audio = data.Media.query.filter_by(id=form.naudio
                                                       .data).first().name
            data.Media.query.filter_by(id=form.naudio
                                       .data).first().used = True
            db.session.commit()
            touch_s.akey = form.naudio.data

        enabled_tts = [s for s in text_to_speech.keys() if form[f'check{s}'].data]
        touch_s.announce = ','.join(enabled_tts) if enabled_tts else 'false'

        db.session.add(touch_s)
        db.session.commit()
        flash('Notice: Display customization has been updated. ..', 'info')
        return redirect(url_for('cust_app.displayscreen_c', stab=1))

    if not form.errors:
        form.display.data = touch_s.tmp
        form.title.data = touch_s.title
        form.hsize.data = touch_s.hsize
        form.hcolor.data = touch_s.hcolor
        form.hbg.data = touch_s.hbg
        form.tsize.data = touch_s.tsize
        form.tcolor.data = touch_s.tcolor
        form.h2size.data = touch_s.h2size
        form.h2color.data = touch_s.h2color
        form.ssize.data = touch_s.ssize
        form.scolor.data = touch_s.scolor
        form.mduration.data = touch_s.mduration
        form.hfont.data = touch_s.hfont
        form.tfont.data = touch_s.tfont
        form.h2font.data = touch_s.h2font
        form.sfont.data = touch_s.sfont
        form.mduration.data = touch_s.mduration
        form.rrate.data = touch_s.rrate
        form.anr.data = touch_s.anr
        form.anrt.data = touch_s.anrt
        form.effect.data = touch_s.effect
        form.repeats.data = touch_s.repeats
        form.prefix.data = touch_s.prefix
        form.always_show_ticket_number.data = touch_s.always_show_ticket_number
        form.wait_for_announcement.data = touch_s.wait_for_announcement
        form.hide_ticket_index.data = touch_s.hide_ticket_index

        if touch_s.bgcolor[:3] == 'rgb':
            form.bgcolor.data = touch_s.bgcolor
            form.background.data = 0
        else:
            form.background.data = touch_s.ikey

        if touch_s.audio == 'false':
            form.naudio.data = 0
        else:
            form.naudio.data = touch_s.akey

        for short in touch_s.announce.split(','):
            field = getattr(form, f'check{short}', None)

            if field:
                field.data = short in touch_s.announce

    return render_template('display_screen.html',
                           form=form,
                           page_title='Display Screen customize',
                           navbar='#snb2',
                           hash=stab,
                           dropdown='#dropdown-lvl2',
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status,
                           tts=text_to_speech)


@cust_app.route('/touchscreen_c/<int:stab>', methods=['POST', 'GET'])
@reject_not_admin
def touchscreen_c(stab):
    ''' view for touch screen customization '''
    form = TouchScreenForm()

    if stab not in range(0, 6):
        flash('Error: wrong entry, something went wrong', 'danger')
        return redirect(url_for('core.root'))

    touch_s = data.Touch_store.get()

    if form.validate_on_submit():
        touch_s.tmp = form.touch.data
        touch_s.title = form.title.data
        touch_s.hsize = form.hsize.data
        touch_s.hcolor = form.hcolor.data
        touch_s.hbg = form.hbg.data
        touch_s.mbg = form.mbg.data
        touch_s.tsize = form.tsize.data
        touch_s.tcolor = form.tcolor.data
        touch_s.msize = form.msize.data
        touch_s.mcolor = form.mcolor.data
        touch_s.mduration = form.mduration.data
        touch_s.hfont = form.hfont.data
        touch_s.tfont = form.tfont.data
        touch_s.mfont = form.mfont.data
        touch_s.message = form.message.data

        if not form.background.data:
            touch_s.bgcolor = form.bcolor.data
            touch_s.ikey = None
        else:
            touch_s.bgcolor = data.Media.query.filter_by(id=form.background
                                                         .data).first().name
            data.Media.query.filter_by(id=form.background
                                       .data).first().used = True
            touch_s.ikey = form.background.data

        if not form.naudio.data:
            touch_s.audio = 'false'
            touch_s.akey = None
        else:
            touch_s.audio = data.Media.query.filter_by(id=form.naudio
                                                       .data).first().name
            data.Media.query.filter_by(id=form.naudio
                                       .data).first().used = True
            touch_s.akey = form.naudio.data

        db.session.add(touch_s)
        db.session.commit()
        flash('Notice: Touchscreen customization has been updated. ..', 'info')
        return redirect(url_for('cust_app.touchscreen_c', stab=0))

    if not form.errors:
        form.touch.data = touch_s.tmp
        form.title.data = touch_s.title
        form.hsize.data = touch_s.hsize
        form.hcolor.data = touch_s.hcolor
        form.hbg.data = touch_s.hbg
        form.mbg.data = touch_s.mbg
        form.tsize.data = touch_s.tsize
        form.tcolor.data = touch_s.tcolor
        form.msize.data = touch_s.msize
        form.mcolor.data = touch_s.mcolor
        form.mduration.data = touch_s.mduration
        form.hfont.data = touch_s.hfont
        form.tfont.data = touch_s.tfont
        form.mfont.data = touch_s.mfont
        form.message.data = touch_s.message

        if (touch_s.bgcolor or '')[:3] == 'rgb':
            form.bcolor.data = touch_s.bgcolor
            form.background.data = 00
        else:
            form.background.data = touch_s.ikey

        if touch_s.audio == 'false':
            form.naudio.data = 00
        else:
            form.naudio.data = touch_s.akey

    return render_template('touch_screen.html',
                           page_title='Touch Screen customize',
                           navbar='#snb2',
                           form=form,
                           dropdown='#dropdown-lvl1',
                           hash=stab,
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/alias', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def alias():
    ''' view for aliases customization '''
    form = AliasForm()
    aliases = data.Aliases.get()

    if form.validate_on_submit():
        aliases.office = form.office.data
        aliases.task = form.task.data
        aliases.ticket = form.ticket.data
        aliases.name = form.name.data
        aliases.number = form.number.data

        db.session.add(aliases)
        db.session.commit()
        flash('Notice: aliases got updated successfully.', 'info')
        return redirect(url_for('cust_app.alias'))

    if not form.errors:
        form.office.data = aliases.office
        form.task.data = aliases.task
        form.ticket.data = aliases.ticket
        form.name.data = aliases.name
        form.number.data = aliases.number

    return render_template('alias.html',
                           page_title='Aliases',
                           navbar='#snb2',
                           form=form,
                           hash='#da8',
                           vtrue=data.Vid.get().enable,
                           strue=data.Slides_c.get().status)


@cust_app.route('/background_tasks', methods=['GET', 'POST'])
@login_required
@reject_not_admin
def background_tasks():
    ''' view for background tasks customization '''
    form = BackgroundTasksForms()
    cache_tts = data.BackgroundTask.get(name='CacheTicketsAnnouncements')
    delete_tickets = data.BackgroundTask.get(name='DeleteTickets')

    def _resolve_time(every, time):
        return time if every in EVERY_TIME_OPTIONS else None

    if form.validate_on_submit():
        cache_tts.enabled = form.cache_tts_enabled.data
        cache_tts.every = form.cache_tts_every.data
        delete_tickets.enabled = form.delete_tickets_enabled.data
        delete_tickets.every = form.delete_tickets_every.data
        delete_tickets.time = _resolve_time(delete_tickets.every,
                                            form.delete_tickets_time.data)

        db.session.commit()

        if os.environ.get('DOCKER'):
            CeleryTasks._runner.stop()
            CeleryTasks._runner.apply_async()            
        else:
            stop_tasks()
            start_tasks()

        flash('Notice: background tasks got updated successfully.', 'info')
        return redirect(url_for('cust_app.background_tasks'))

    if not form.errors:
        form.cache_tts_enabled.data = cache_tts.enabled
        form.cache_tts_every.data = cache_tts.every
        form.delete_tickets_enabled.data = delete_tickets.enabled
        form.delete_tickets_every.data = delete_tickets.every
        form.delete_tickets_time.data = delete_tickets.time

    return render_template('background_tasks.html',
                           page_title='Background Tasks',
                           navbar='#snb2',
                           form=form,
                           hash='#da9',
                           vtrue=data.Vid.get().enable,
                           strue=data.Slides_c.get().status,
                           time_options=','.join(EVERY_TIME_OPTIONS))
