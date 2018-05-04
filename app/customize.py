# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import url_for, flash, request, render_template, redirect, Markup
from flask import Blueprint, session
from flask_login import current_user, login_required
from werkzeug import secure_filename
import os
import imghdr
import sndhdr
import ex_functions
import forms
import data
from database import db, files
from printer import listp
from ex_functions import r_path
from ex_functions import get_lang

cust_app = Blueprint('cust_app', __name__)

# Midia files allowed used by forms and customize
mdal = [['jpg', 'JPG', 'png', 'PNG'], ['wav', 'WAV'], [
    'mp4', 'MP4', 'AVI', 'avi', 'webm', 'WEBM']]


@cust_app.route('/customize')
@login_required
def customize():
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    return render_template("customize.html",
                           ptitle="Customization",
                           snb="#snb2",
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/ticket', methods=['GET', 'POST'])
@login_required
def ticket():
    if os.name == 'nt':
        from win_printer import listpp
        lll = listpp()
    else:
        lll = listp()
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              'danger')
        return redirect(url_for('core.root'))
    form = forms.Printer_f(lll)
    if session.get('lang') == "AR":
        form = forms.Printer_f_ar(lll)
    tc = data.Touch_store.query.first()
    pr = data.Printer.query.first()
    if form.validate_on_submit():
        if form.kind.data == 1:
            tc.n = True
            pr.value = form.value.data
            pr.active = False
            db.session.add(tc)
            db.session.add(pr)
        else:
            if form.printers.data == "00":
                flash(get_lang(19),
                      'danger')
                return redirect(url_for('cust_app.ticket'))
            f = form.printers.data
            pr.product = f
            if os.name != 'nt':
                f = f.split('_')
                pr.vendor = f[0]
                pr.product = f[1]
                pr.in_ep = int(f[2])
                pr.out_ep = int(f[3])
            tc.n = False
            pr.active = True
            pr.langu = form.langu.data
            pr.value = form.value.data
            db.session.add(tc)
            db.session.add(pr)
        db.session.commit()
        flash(get_lang(27),
              'info')
        return redirect(url_for('cust_app.ticket'))
    if tc.n:
        form.kind.data = 1
    else:
        form.kind.data = 2
    form.printers.data = pr.vendor + '_' + pr.product
    form.printers.data += '_' + str(pr.in_ep) + '_' + str(pr.out_ep)
    form.langu.data = pr.langu
    form.value.data = pr.value
    return render_template('ticket.html', snb='#snb2',
                           ptitle='Tickets',
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status,
                           form=form, snb2='#da7')


@cust_app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              'danger')
        return redirect(url_for('core.root'))
    if data.Slides_c.query.first().status == 1:
        flash(get_lang(28),
              'danger')
        return redirect(url_for('cust_app.slide_c'))
    form = forms.Video()
    if session.get('lang') == "AR":
        form = forms.Video_ar()
    vdb = data.Vid.query.first()
    if form.validate_on_submit():
        if form.video.data == 00:
            vdb.enable = 2
            vdb.vkey = 00
        else:
            vdb.vkey = form.video.data
            vdb.enable = form.enable.data
            mname = data.Media.query.filter_by(id=form.video.data).first()
            vdb.vname = mname.name
            data.Display_store.query.first().vkey = form.video.data
            data.Media.query.filter_by(
                id=form.video.data).first().used = True
        vdb.ar = form.ar.data
        vdb.controls = form.controls.data
        vdb.mute = form.mute.data
        db.session.add(vdb)
        db.session.commit()
        flash(get_lang(29),
              'info')
        return redirect(url_for('cust_app.video'))
    if vdb is not None:
        form.video.data = vdb.vkey
        form.enable.data = vdb.enable
        form.ar.data = vdb.ar
        form.controls.data = vdb.controls
        form.mute.data = vdb.mute
    return render_template('video.html',
                           ptitle='Video settings',
                           snb='#snb2',
                           snb2='#da5',
                           form=form,
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/slideshow', methods=['GET', 'POST'])
@login_required
def slideshow():
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    if data.Vid.query.first().enable == 1:
        flash(get_lang(31),
              'danger')
        return redirect(url_for('cust_app.video'))
    page = request.args.get('page', 1, type=int)
    if page > int(data.Slides.query.count() / 10) + 1:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('cust_app.slideshow'))
    pagination = data.Slides.query.paginate(page, per_page=10,
                                            error_out=False)
    return render_template("slideshow.html",
                           len=len,
                           snb="#snb2", sli=data.Slides_c.query.first(),
                           mmm=data.Slides.query,
                           slides=pagination.items,
                           pagination=pagination,
                           sm=data.Slides.query.filter(data.Slides.
                                                       ikey != 0).count(),
                           ptitle="All slides",
                           slist=["#dropdown-lvl3", ".da4", "#ss1"],
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/slide_a', methods=['GET', 'POST'])
@login_required
def slide_a():
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    if data.Vid.query.first().enable == 1:
        flash(get_lang(31),
              'danger')
        return redirect(url_for('cust_app.video'))
    form = forms.Slide_a()
    if session.get('lang') == 'AR':
        form = forms.Slide_a_ar()
    if form.validate_on_submit():
        if form.background.data == 00:
            bb = form.bgcolor.data
        else:
            bb = data.Media.query.filter_by(id=form.background.data).first()
            if bb is None:
                flash(get_lang(4), "danger")
                return redirect(url_for("cust_app.slide_a"))
            bb = bb.name
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
        ss.bname = bb
        ss.ikey = form.background.data
        db.session.add(ss)
        db.session.commit()
        flash(get_lang(32), "info")
        return redirect(url_for("cust_app.slideshow"))
    return render_template("slide_add.html",
                           ptitle="Add Slide ",
                           form=form, snb="#snb2",
                           slist=["#dropdown-lvl3", ".da4", "#ss3"],
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/slide_c', methods=['GET', 'POST'])
@login_required
def slide_c():
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    if data.Vid.query.first().enable == 1:
        flash(get_lang(31),
              'danger')
        return redirect(url_for('cust_app.video'))
    form = forms.Slide_c()
    if session.get('lang') == 'AR':
        form = forms.Slide_c_ar()
    sc = data.Slides_c.query.first()
    if form.validate_on_submit():
        sc.rotation = form.rotation.data
        sc.navigation = form.navigation.data
        sc.effect = form.effect.data
        sc.status = form.status.data
        db.session.add(sc)
        db.session.commit()
        flash(get_lang(33), "info")
        return redirect(url_for("cust_app.slide_c"))
    form.rotation.data = sc.rotation
    form.navigation.data = sc.navigation
    form.effect.data = sc.effect
    form.status.data = sc.status
    return render_template("slide_settings.html",
                           form=form, snb="#snb2",
                           slist=["#dropdown-lvl3", ".da4", "#ss2"],
                           ptitle="Slideshow settings",
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/slide_r/<int:f_id>')
@login_required
def slide_r(f_id):
    ex_functions.mse()
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    if data.Slides.query.count() <= 0:
        flash(get_lang(34), "danger")
        return redirect(url_for('cust_app.slideshow'))
    if data.Vid.query.first().enable == 1:
        flash(get_lang(31),
              'danger')
        return redirect(url_for('cust_app.video'))
    if f_id == 00:
        for a in data.Slides.query:
            if a is not None:
                db.session.delete(a)
        db.session.commit()
        flash(get_lang(35), "info")
        return redirect(url_for('cust_app.slideshow'))
    mf = data.Slides.query.filter_by(id=f_id).first()
    if mf is not None:
        db.session.delete(mf)
        db.session.commit()
        flash(get_lang(35), "info")
        return redirect(url_for('cust_app.slideshow'))
    else:
        flash(get_lang(34), "danger")
        return redirect(url_for('core.root'))


@cust_app.route('/multimedia/<int:aa>', methods=['POST', 'GET'])
@login_required
def multimedia(aa):
    # Number of files limit
    nofl = 300
    # size folder limit in MB
    sfl = 2000 # Fix limited upload folder size
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    ex_functions.mse()
    dire = r_path('static/multimedia/')
    pf = data.Media.query.order_by(data.Media.id.desc()).first()
    if pf is not None:
        pf = pf.name
    if aa == 0:
        # Fix limited upload folder size
        # if int(ex_functions.getFolderSize(dire)) >= sfl:
        #     flash(get_lang(36) + str(sfl) + "MB",
        #           "danger")
        #     return redirect(url_for('cust_app.multimedia', aa=1))
        if data.Media.query.count() >= nofl:
            flash(get_lang(37) + str(nofl),
                  "danger")
            return redirect(url_for('cust_app.multimedia', aa=1))
        else:
            flash(get_lang(38),
                  "success")
    elif aa != 1:
        flash(get_lang(4),
              "danger")
        return redirect(url_for("core.root"))
    mmm = data.Media.query
    page = request.args.get('page', 1, type=int)
    if page > int(data.Media.query.count() / 10) + 1:
        flash(get_lang(4),
              'danger')
        return redirect(url_for('cust_app.multimedia', aa=1))
    pagination = data.Media.query.paginate(page, per_page=10,
                                           error_out=False)
    form = forms.Multimedia()
    if session.get('lang') == "AR":
        form = forms.Multimedia_ar()
    if mmm.count() >= 1:
        from sqlalchemy.sql import or_
        for me in mmm:
            if os.path.isfile(dire + me.name):
                dl = [data.Display_store.query.filter(or_(
                    data.Display_store.ikey == me.id,
                    data.Display_store.akey == me.id)).first(),
                    data.Touch_store.query.filter(or_(
                        data.Touch_store.ikey == me.id,
                        data.Touch_store.akey == me.id)).first(),
                    data.Slides.query.filter_by(ikey=me.id).first(),
                    data.Vid.query.filter_by(vkey=me.id).first()]
                me.used = False
                for d in dl:
                    if d is not None:
                        me.used = True
                        break
                db.session.add(me)
                db.session.commit()
            else:
                if me.img or me.audio or me.vid:
                    for t in [data.Touch_store,
                              data.Display_store, data.Slides]:
                        t = t.query.filter_by(or_(
                            data.Display_store.ikey == me.id,
                            data.Display_store.vkey == me.id)).first()
                        if me.img or me.vid and t is not None:
                            if me.img:
                                t.ikey = None
                            if me.vid:
                                t.vid = None
                            if t != data.Slides:
                                t.bgcolor = "bg-danger"
                            else:
                                t.bgname = "bg-danger"
                            db.session.add(t)
                        ttt = t.query.filter_by(akey=me.id).first()
                        if me.audio and ttt is not None:
                            if t != data.Slides:
                                t.akey = None
                                t.audio = "false"
                                db.session.add(t)
                db.session.delete(me)
        db.session.commit()
    if form.validate_on_submit():
        ff = form.mf.data
        ffn = secure_filename(ff.filename)
        dc = data.Media.query.count()
        # FIX ISUUE Remove folder size limitation
        # if int(ex_functions.getFolderSize(dire)) >= sfl or dc >= nofl:
        #     return redirect(url_for('cust_app.multimedia', aa=1))
        e = ffn[-3:len(ffn)]
        if e in mdal[0]:
            files.save(request.files['mf'], name=ffn)
            if imghdr.what(dire + ffn) is None:
                os.remove(dire + ffn)
                return redirect(url_for("cust_app.multimedia", aa=1))
            db.session.add(data.Media(False, False, True, False, ffn))
            db.session.commit()
            return redirect(url_for("cust_app.multimedia", aa=1))
        elif e in mdal[1]:
            files.save(request.files['mf'], name=ffn)
            if sndhdr.what(dire + ffn) is None:
                os.remove(dire + ffn)
                return redirect(url_for("cust_app.multimedia", aa=1))
            db.session.add(data.Media(False, True, False, False, ffn))
            db.session.commit()
            return redirect(url_for("cust_app.multimedia", aa=1))
        elif e in mdal[2]:
            files.save(request.files['mf'], name=ffn)
            db.session.add(data.Media(True, False, False, False, ffn))
            db.session.commit()
            return redirect(url_for("cust_app.multimedia", aa=1))
        else:
            flash(get_lang(4), "danger")
            return redirect(url_for("cust_app.multimedia", aa=1))
    return render_template("multimedia.html",
                           ptitle="Multimedia",
                           snb="#snb2",
                           form=form,
                           snb2="#da1",
                           mmm=mmm,
                           len=len,
                           ml=mdal,
                           mmmp=pagination.items,
                           pagination=pagination,
                           tc=data.Touch_store.query,
                           sl=data.Slides.query,
                           dc=data.Display_store.query,
                           fs=int(ex_functions.getFolderSize(dire)),
                           nofl=nofl, sfl=sfl,
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/multi_del/<int:f_id>')
@login_required
def multi_del(f_id):
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    dire = r_path('static/multimedia/')
    if data.Media.query.filter_by(used=False).count() <= 0:
        flash(get_lang(39),
              "danger")
        return redirect(url_for('cust_app.multimedia', aa=1))
    if f_id == 00:
        for a in data.Media.query:
            if not a.used:
                if os.path.exists(dire + a.name):
                    os.remove(dire + a.name)
                db.session.delete(a)
        db.session.commit()
        flash(get_lang(40), "info")
        return redirect(url_for('cust_app.multimedia', aa=1))
    mf = data.Media.query.filter_by(id=f_id).first()
    if mf is not None:
        if mf.used:
            flash(get_lang(39),
                  "danger")
            return redirect(url_for('cust_app.multimedia', aa=1))
        if os.path.exists(dire + mf.name):
            os.remove(dire + mf.name)
        db.session.delete(mf)
        db.session.commit()
        flash(get_lang(40), "info")
        return redirect(url_for('cust_app.multimedia', aa=1))
    else:
        flash(get_lang(39), "danger")
        return redirect(url_for('core.root'))


@cust_app.route('/displayscreen_c/<int:stab>', methods=['POST', 'GET'])
@login_required
def displayscreen_c(stab):
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    ex_functions.mse()
    form = forms.Display_c()
    if session.get('lang') == 'AR':
        form = forms.Display_c_ar()
    if stab not in range(1, 9):
        flash(get_lang(4), "danger")
        return redirect(url_for('core.root'))
    touch_s = data.Display_store.query.filter_by(id=0).first()
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
        touch_s.announce = form.announce.data
        touch_s.anr = form.anr.data
        touch_s.anrt = form.anrt.data
        touch_s.effect = form.effect.data
        touch_s.repeats = form.repeats.data
        bg = form.background.data
        if bg == 00:
            touch_s.bgcolor = form.bgcolor.data
            touch_s.ikey = None
        else:
            touch_s.bgcolor = data.Media.query.filter_by(id=form.background
                                                         .data).first().name
            data.Media.query.filter_by(id=form.background
                                       .data).first().used = True
            db.session.commit()
            touch_s.ikey = form.background.data
        au = form.naudio.data
        if au == 00:
            touch_s.audio = "false"
            touch_s.akey = None
        else:
            touch_s.audio = data.Media.query.filter_by(id=form.naudio
                                                       .data).first().name
            data.Media.query.filter_by(id=form.naudio
                                       .data).first().used = True
            db.session.commit()
            touch_s.akey = form.naudio.data
        db.session.add(touch_s)
        db.session.commit()
        flash(get_lang(41),
              "info")
        # Adding autoreload to display screen
        session['autoref'] = 1
        return redirect(url_for("cust_app.displayscreen_c", stab=1))
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
    form.announce.data = touch_s.announce
    form.anr.data = touch_s.anr
    form.anrt.data = touch_s.anrt
    form.effect.data = touch_s.effect
    form.repeats.data = touch_s.repeats
    if touch_s.bgcolor[:3] == "rgb":
        form.bgcolor.data = touch_s.bgcolor
        form.background.data = 00
    else:
        form.background.data = touch_s.ikey
    if touch_s.audio == "false":
        form.naudio.data = 00
    else:
        form.naudio.data = touch_s.akey
    return render_template("display_screen.html",
                           form=form,
                           ptitle="Display Screen customize",
                           snb="#snb2",
                           hash=stab,
                           slist=["#dropdown-lvl2",
                                  ".da3",
                                  stab],
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)


@cust_app.route('/touchscreen_c/<int:stab>', methods=['POST', 'GET'])
@login_required
def touchscreen_c(stab):
    if current_user.role_id != 1:
        flash(get_lang(0),
              "danger")
        return redirect(url_for('core.root'))
    form = forms.Touch_c()
    if session.get('lang') == 'AR':
        form = forms.Touch_c_ar()
    ex_functions.mse()
    if stab not in range(0, 6):
        flash(get_lang(4), "danger")
        return redirect(url_for('core.root'))
    touch_s = data.Touch_store.query.first()
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
        bg = form.background.data
        if bg == 00:
            touch_s.bgcolor = form.bcolor.data
            touch_s.ikey = None
        else:
            touch_s.bgcolor = data.Media.query.filter_by(id=form.background
                                                         .data).first().name
            data.Media.query.filter_by(id=form.background
                                       .data).first().used = True
            touch_s.ikey = form.background.data
        au = form.naudio.data
        if au == 00:
            touch_s.audio = "false"
            touch_s.akey = None
        else:
            touch_s.audio = data.Media.query.filter_by(id=form.naudio
                                                       .data).first().name
            data.Media.query.filter_by(id=form.naudio
                                       .data).first().used = True
            touch_s.akey = form.naudio.data
        db.session.add(touch_s)
        db.session.commit()
        flash(get_lang(42),
              "info")
        return redirect(url_for("cust_app.touchscreen_c", stab=0))
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
    if touch_s.bgcolor[:3] == "rgb":
        form.bcolor.data = touch_s.bgcolor
        form.background.data = 00
    else:
        form.background.data = touch_s.ikey
    if touch_s.audio == "false":
        form.naudio.data = 00
    else:
        form.naudio.data = touch_s.akey
    return render_template("touch_screen.html",
                           ptitle="Touch Screen customize",
                           snb="#snb2",
                           form=form,
                           slist=["#dropdown-lvl1",
                                  ".da2",
                                  stab],
                           vtrue=data.Vid.query.first().enable,
                           strue=data.Slides_c.query.first().status)
