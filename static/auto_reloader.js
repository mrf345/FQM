/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

 defaultDuration = 5000

var AutoReloader = function autoReloader (options) {
  var returning = {}
  // validating functions
  var checkBool = function checkBool (args) {
    // check if passed args are 'true' or 'false' type
    for (var a in args) {
      if (args[a] !== 'true' && args[a] !== 'false') return false
    }
    return true
  }
  var checkType = function checkType (type, args) {
    // checking the type of each variable in the passed array
    for (var a in args) {
      if (typeof args[a] !== type) return false
    }
    return true
  }

  // main class, contains all
  if (typeof options !== 'object') options = {}
  returning.options = { // inserted options, with defaults
    identifier: options.identifier || '.autoreloader', // class or id to identify the autoloading element with
    duration: options.duration * 1000 || defaultDuration, // duration number in seconds, in-which each reload is due
    add_classes: options.add_classes || ['btn-danger'], // css classes to add or remove with start or stop
    add_classes_span: options.add_classes_span || ['fa-spin'], // to add classes to span inside button
    add_style: options.add_style || ';font-size: 200%; color: green;', // css style to add or remove with start or stop
    remember_position: options.remember_position || 'true', // to remember the screen position after reload
    fix_rotation: options.screen_rotation || 'true', // to fix screen size rotation with reload
    auto_start: options.auto_start || 'false' // to start auto reloading without element click
  }

  returning.defaults = {
    sleeps: []  // to store timeouts
  }

  returning.__init__ = function __init__ () {
  // Validation
    // Type validation
    if (!checkType('string', [
      returning.options.add_classes]) && !(
        returning.options.add_classes instanceof Array)
      ) throw new TypeError('auto_reloader(options) add_classes requires array of strings')
    if (!checkType('string', [
      returning.options.add_classes_span]) && !(
        returning.options.add_classes_span instanceof Array)
      ) throw new TypeError('auto_reloader(options) add_classes_span requires array of strings')
    if (!checkType('string', [
      returning.options.identifier,
      returning.options.add_style
    ])) throw new TypeError('auto_reloader(options) identifier, add_style require strings')
    if (!checkBool([
      returning.options.remember_position,
      returning.options.fix_rotation
    ])) throw new TypeError('auto_reloader(options) remember_position, fix_rotation require "true" or "false"')
    if (typeof returning.options.duration !== 'number' || returning.options.duration < 0) throw new TypeError('auto_reloader(options) duration requires valid number')
    // Value validation
    if (!(returning.options.identifier.startsWith('.')) && !(returning.options.identifier.startsWith('#'))) throw new Error('auto_reloader(options) identifier should start with # or .')
    if ($(returning.options.identifier).length <= 0 && returning.options.auto_start === 'false') throw new Error('auto_reloader(options) can not find any elements with identifier')
  // Setup directions
    $(returning.options.identifier).click(function (event) {
      if (localStorage.active === undefined) start(); else stop() // start or stop if clicked
    })
    if (localStorage.active !== undefined || returning.options.auto_start === 'true') start() // start if not first time
  }

// Starter and Stopper

  // global name to access from events
  var start = function start () {
    // starting the auto reload, changing style
    if (localStorage.active !== undefined) {
      returning.set_style(false)
      if (returning.options.remember_position) $(window).scrollTop(localStorage.position) // to remember position
      if (returning.options.fix_rotation) returning.check_screen() // to watch out for screen size change
      returning.reload() // timeout to reload
    } else {
      returning.set_style()
      returning.reload(0)
    }
  }
  // global name to access from events
  var stop = function stop () {
    // stopping the auto reload clearing timeouts restoring style
    returning.restore_style()
    if (returning.defaults.sleeps.length > 0) {
      $.each(returning.defaults.sleeps, function (i, value) {
        clearTimeout(value)
      })
    }
    // clearing up the storage
    localStorage.clear()
  }

// When Started

  returning.reload = function reload (duration) {
    duration = duration || localStorage.duration || returning.options.duration
    // setting timeout to reload
    // clearing timeouts before loading
    returning.defaults.sleeps.push(
      setTimeout(function () {
        localStorage.position = $(window).scrollTop() // getting screen position
        localStorage.active = 'true' // to indeicate not a first time
        location.reload()
      }, duration)
    )
  }
  returning.check_screen = function checkScreen (
    // setting event watch for screen resize or rotation and reload if so
    height, width) {
    
    height = height || $(window).height()
    width = width || $(window).width()

    jQuery(function ($) {
      $(window).resize(function () {
        if (height !== $(window).height() || width !== $(window).width()) {
          location.reload()
        }
      })
    })
  }
  returning.set_style = function setStyle (notactive) {
    notactive = notactive || true

    // setting the button style with style and class
    for (var i = 0; returning.options.add_classes.length > i; i += 1) {
      $(returning.options.identifier).addClass(returning.options.add_classes[i])
    }
    for (var i = 0; returning.options.add_classes_span.length > i; i += 1) {
      $(returning.options.identifier + '> span').addClass(returning.options.add_classes_span[i])
    }
    if ($(returning.options.identifier).attr('style') !== undefined && notactive) {
      localStorage.style = $(returning.options.identifier).attr('style') // storing style
      $(returning.options.identifier).attr(
        'style', localStorage.style + ';' + returning.options.add_style
      ) // adding style to existing one
    } else {
      if (localStorage.style !== undefined) $(returning.options.identifier).attr('style', localStorage.style + ';' + returning.options.add_style)
      else $(returning.options.identifier).attr('style', returning.options.add_style)
    }
  }

// When Stopped

  returning.restore_style = function restoreStyle () {
    // restoring the button previous style
    for (var i = 0; returning.options.add_classes.length > i; i += 1) {
      if ($(returning.options.identifier).hasClass(returning.options.add_classes[i])) {
        $(returning.options.identifier).removeClass(returning.options.add_classes[i])
      }
    }
    for (var i = 0; returning.options.add_classes_span.length > i; i += 1) {
      if ($(returning.options.identifier + ' > span').hasClass(returning.options.add_classes_span[i])) {
        $(returning.options.identifier + ' > span').removeClass(returning.options.add_classes_span[i])
      }
    }
    if (localStorage.style !== undefined) {
      $(returning.options.identifier).attr('style', localStorage.style)
      localStorage.style = false
    } else { // if style not stored and equal to iserted style, will be emptied
      if ($(returning.options.identifier).attr('style') === returning.options.add_style) {
        $(returning.options.identifier).attr('style', '')
      }
    }
  }

// Initiate and return the class

  returning.__init__()
  return returning
}

var AskReloader = function ask (msg) {
  msg = msg || "Enter new auto-reload duration in seconds : "
  // to prompt user to set new duration
  var newDuration = window.prompt(
    msg,
    localStorage.duration / 1000 || defaultDuration / 1000
  )
  localStorage.duration = newDuration > 0 ? newDuration * 1000 : localStorage.duration ? localStorage.duration : defaultDuration
}