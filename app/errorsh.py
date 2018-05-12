# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from flask import url_for, flash, redirect, render_template, Blueprint
from flask import request, Markup, session
from flask_login import current_user

errorsh_app = Blueprint('errorsh_app', __name__)


@errorsh_app.route('/nojs/<int:ino>')
def nojs(ino):
    if ino == 1:
        s = session.get('next_url', '/')
        if s != '/':
            return redirect(s)
        return redirect(url_for('core.root'))
    return render_template('nojs.html',
                           ptitle='Javascript is disabled')
