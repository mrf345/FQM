/* global document, window, $, localStorage */
/*
  Dependencies: Bootstrap ver. * > 3, jQuery
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */

 // TODO: add option to disable if went to another website reminder

var disciple = function (options) {    
    options = options || {}

    var checkType = function checkType (type, args) {
       // checking the type of each variable in the passed array
      for (var a in args) {
        if (typeof args[a] !== type) return false
      }
      return true
    }
		var escapeReady = function (todo) {
			// to add function to document ready event with escape
			if (document.readyState === 'complete') todo()
			else $(document).ready(todo)
		}

    options = {
      identifier: options.identifier || '.disciple', // ID to identifiy the form to watch
      // confirm message displayed when form is dirty
      msg_text: options.msg_text || 'You made changes on the previous form without submiting. Do you wish to restore it ?',
      restore_text: options.restore_text || 'Now', // restore now button text
      later_text: options.later_text || 'Later', // restore later button text
      forget_text: options.forget_text || 'Forget it', // do not store it, button text
      restoring_text: options.restoring_text || 'Restoring your saved form ..', // msg displayed while restoring
      msg_classes: options.msg_classes || [], // confirm message classes to be added to the element
      restore_classes: options.restore_classes || ['btn', 'btn-large btn-default'], // classes to be added to restore now button
      later_classes: options.later_classes || ['btn', 'btn-large btn-default'], // classes to be added to restore later button
      forget_classes: options.forget_classes || ['btn', 'btn-large btn-danger'], // classes to be added to don't store button
      restoring_classes: options.restoring_classes || [], // classes to be added to message while restoring
      msg_css: options.msg_css || {'font-family': 'serif', 'color': '#fff'}, // CSS to be added to confirm message
      restore_css: options.restore_css || { // CSS to be added to restore now button
        'font-size': '130%',
        'font-weight': 'bold',
        'background-color': 'rgb(70, 180, 173)',
        'font-family': 'serif'},
      later_css: options.later_css || { // CSS to be added to restore later button
        'font-family': 'serif',
        'font-size': '130%',
        'font-weight': '200',
        'font-streatch': 'extra-extended',
        'background-color': 'rgb(70, 180, 173)',
        'font-style': 'italic'},
      forget_css: options.forget_css || { // CSS to be added to don't store button
        'font-family': 'serif',
        'font-size': '130%',
        'font-weight': 'bold',
        'font-streatch': 'ultra-extended'},
      restoring_css: options.restoring_css || { // CSS to be added to while restoring message
        'font-family': 'serif', 'color': '#fff'},
      msgbox_background: options.msgbox_background || 'rgba(0,0,0,0.8)' // Background color for messages div
    }
  
    defaultsDis = {
      elements: ['input', 'select', 'textarea', 'fieldset', 'datalist'], // form elements that gets checked
      separator: '~%^disciple^%~', // special string to separate form values when stored
      storeForm: [], // to store the form upon loading
      leaveForm: [], // to store the form after unload event
      cleared: false, // indicator that messenger is done
      cLoop: false, // interval to delay execution until messenger is done
      submitted: false, // to indelicate if form submitted
      transparent: { // transparent over-lay css properties
        'background': options.msgbox_background,
        'opacity': '1',
        'width': '100%',
        'height': '100%',
        'z-index': '10',
        'top': '0',
        'left': '0',
        'position': 'fixed',
        'min-height': '100%',
        'min-height': '100vh',
        'display': 'flex',
        'align-items': 'center',
        '-webkit-transition': 'opacity 1s ease-in',
        '-moz-transition': 'opacity 1s ease-in',
        '-o-transition': 'opacity 1s ease-in',
        '-ms-transition': 'opacity 1s ease-in',
        'transition': 'opacity 1s ease-in'
      }
    }
  
    this.__init__ = function __init__ () {
      // check options type correct values
      if (!checkType('string', [
        options.msg_text,
        options.restore_text,
        options.later_text,
        options.forget_text,
        options.restoring_text,
        options.msgbox_background
      ])) throw new TypeError('disciple(options) _text takes a string')
      if (!checkType('object', [
        options.msg_css,
        options.restore_css,
        options.later_css,
        options.forget_css,
        options.restoring_css
      ])) throw new TypeError('disciple(options) _css takes a CSS object')
      var ds; for (var d in ds = [
        options.msg_classes,
        options.restore_classes,
        options.later_classes,
        options.forget_classes,
        options.restoring_classes
      ]) {
        if (!(ds[d] instanceof Array)) throw new Error('disciple(options) _classes takes an Array of strings')
      }
			// initial setup
			escapeReady(function () {
				if (localStorage.stopped !== 'yes') {
						if (localStorage.hasOwnProperty(window.location.href) && localStorage.disciple === 'yes') {
								if (window.location.href !== localStorage.togo) messenger(true)
								else defaultsDis.cleared = true
								defaultsDis.cLoop = setInterval(function () {
										// in case of messenger and reincarnate to restore we will wait for messenger to be done first
										if (defaultsDis.cleared) {
												reincarnate()
												defaultsDis.cleared = false
												witness() // to start storing form values
												clearInterval(defaultsDis.cLoop)
										}
								}, 200)
						} else {
								witness()
								if (localStorage.hasOwnProperty(window.location.href)) reincarnate() // if page is set for later
								else if (localStorage.disciple === 'yes') messenger() // if form is dirty changed
						}
				}
			})
    }
  
    var witness = function witness () {
			// watch over and store identified form, if exists
      if ($(options.identifier).length >= 1) {
				escapeReady(function () {
					for (var e in defaultsDis.elements) {
						$(options.identifier).find(defaultsDis.elements[e]).each(function () {
							defaultsDis.storeForm.push($(this).val())
						})
					}
					$(options.identifier).submit(function () {
						defaultsDis.submitted = true
					})
				})
        $(window).on('unload', function () {
          if (!defaultsDis.submitted) {
            for (var e in defaultsDis.elements) {
              $(options.identifier).find(defaultsDis.elements[e]).each(function () {
                defaultsDis.leaveForm.push($(this).val())
              })
            }
            if (defaultsDis.storeForm.join() !== defaultsDis.leaveForm.join()) {
              localStorage.disciple = 'yes'
              localStorage.togo = window.location.href
              localStorage[window.location.href] = defaultsDis.leaveForm.join(defaultsDis.separator)
            } else localStorage.disciple = 'no'
          }
        })
      }
    }
  
    var messenger = function messenger (clearing) {
      clearing = clearing || false

      // display confirm message, with options and click events
      $('body').append(
        $('<div>').attr('id', 'messenger').css(defaultsDis.transparent
        ).append($('<div>').addClass('col-xs-12 text-center').append(
          $('<h2>').addClass(options.msg_classes.join(' ')).css(options.msg_css).text(options.msg_text)
        ).append(
          $('<button>').css({'margin-top': '5%', 'margin-right': '5%'}).addClass(
            options.restore_classes.join(' ')).css(options.restore_css).text(options.restore_text
            ).click(
            function (event) {
              event.preventDefault()
              localStorage.disciple = 'no'
              window.location.href = localStorage.togo
            })
        ).append(
          $('<button>').css({'margin-top': '5%', 'margin-right': '5%'}).addClass(
            options.later_classes.join(' ')).css(options.later_css).text(options.later_text
            ).click(
            function (event) {
              event.preventDefault()
              if (clearing) postpone(true)
              else postpone()
            })
        ).append(
          $('<button>').css({'margin-top': '5%'}).addClass(options.forget_classes.join(' ')).css(
            options.forget_css).text(options.forget_text
          ).click(
            function (event) {
              event.preventDefault()
              if (clearing) forgive(true)
              else forgive()
            })
          )
        )
      )
    }
  
    this.judgement = function judgement () {
      // display message while restoring old form data
      $('body').append(
        $('<div>').attr('id', 'judgement').css(defaultsDis.transparent
        ).append($('<div>').addClass('col-xs-12 text-center').append(
          $('<h1>').addClass(options.restoring_classes.join(' ')).css(
            options.restoring_css).text(options.restoring_text)
        )
      ))
      setTimeout(function () {
        $('#judgement').css('opacity', '0')
        setTimeout(function () {
          $('#judgement').remove()
        }, 1200)
      }, 1000)
    }
  
    var reincarnate = function reincarnate () {
      // to restore the values of saved form
      localStorage.disciple = 'no'
      this.judgement() // load the while restoring message
      var data = localStorage[window.location.href].split(defaultsDis.separator)
      for (var e in defaultsDis.elements) {
        $(options.identifier).find(defaultsDis.elements[e]).each(function (index, value) {
          $(this).val(data.shift())
        })
      }
      // careful, clean up
      localStorage.removeItem(window.location.href)
      localStorage.togo = false
    }
  
    var postpone = function postpone (clearing) {
      clearing = clearing || false
      // to store for later. Just by removing the confirm message
      // and upon loading the stored later page automatically will be restored
      localStorage.disciple = 'no'
      localStorage.togo = false
      $('#messenger').css({'opacity': '0'})
      setTimeout(function () {
        $('#messenger').remove()
        if (clearing) defaultsDis.cleared = true
      }, 1200)
    }
  
    var forgive = function forgive (clearing) {
      clearing = clearing || false
      // to don't store with localStorage cleanup
      localStorage.removeItem(localStorage.togo) // removing the stored form with its href
      localStorage.disciple = 'no'
      localStorage.togo = false
      $('#messenger').css({'opacity': '0'})
      setTimeout(function () {
        $('#messenger').remove()
        if (clearing) defaultsDis.cleared = true
      }, 1200)
    }
  
    this.pause = function pause () {
      // to pause disciple
      localStorage.stopped = 'yes'
    }
  
    this.resume = function resume () {
      // to resume from where paused
      localStorage.stopped = 'no'
    }
  
    this.exit = function exit () {
      // to clean up memory and stop
      localStorage.clear()
      this.pause()
      console.log('disciple has exited, later then !')
    }
  
    this.__init__()
    this.defaultsDis = defaultsDis
    return this
  }
  