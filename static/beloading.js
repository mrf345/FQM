/* global $ */ // to avoid linter false alarm
/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 */


var beloading = function beload (options, callback) {
  callback = callback || Function
  var checkType = function checkType (type, args) {
    // checking the type of each variable in the passed array
    for (var a in args) {
      if (typeof args[a] !== type) return false
    }
    return true
  }
  var beloadingReturn = {} // unique object to return

  // main class with all functions
  if (typeof options !== 'object') options = {} // assigning empty object if options is not passed
  if (!window.jQuery) throw new Error('This script is based on jQuery, go get it') // checking for jQuery
  if (typeof $.ui === 'undefined') throw new Error('This script uses jQuery UI effects, go get it') // checking for jQuery UI
  options = {
    // options that will be passed and replacements in case not
    background: options.background || 'rgba(0, 0, 0, 0.9)', // background color
    icon: options.icon || 'fa fa-refresh fa-spin', // takes font awesome icon
    text: options.text || 'Behold the Beloading ahead ...', /// text to be displayed while waiting
    text_color: options.text_color || 'rgb(255, 255, 255)', // text and icon color
    text_font: options.text_font || 'Georgia, Times, serif', // text font
    text_shadow: options.text_shadow || '0 0 30px rgba(255,255,255,0.5)', // text and icon shadow
    text_size: options.text_size || '300%', // text and icon size
    effect_duration: options.effect_duration * 1000 || 3000, // fade effect duration in seconds
    trail: options.trail || 'false', // to add escape button, and cancel on load event
  }

  beloadingReturn.defaults = {
    loops: false, // to store the fade effect interval
    effect_duration: options.effect_duration // to get the effect duration from outside
  }

  beloadingReturn.__init__ = function __init__ () {
    // validating types
    if (!checkType('string', [
      options.background,
      options.icon,
      options.text,
      options.text_color,
      options.text_shadow,
      options.text_size,
      options.text_font
    ])) throw new TypeError('beloading(options) background, icon, text, color, shadow, size, font take string')
    if (typeof options.effect_duration !== 'number') throw new TypeError('beloading(options) effect_duration takes number of seconds')
    if (options.trail !== 'true' && options.trail !== 'false') throw new TypeError('beloading(options) trail requires "true" or "false"')
    beloadingReturn.loading()
    beloadingReturn.effectit()
    if (options.trail === 'false') {
      function toCall () {
        beloadingReturn.stop()
        callback()
      }
      if (document.readyState === "complete") toCall()
      else $(window).on('load', toCall)
    }
  }

  beloadingReturn.loading = function loading () {
    // here elements and css styles will be created and loaded
    var gets = Math.round((options.effect_duration / 2) / 1000)
    var div = $('<div>').css({
      'background-color': options.background,
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
      '-webkit-transition': 'opacity ' + gets + 's ease-in',
      '-moz-transition': 'opacity ' + gets + 's ease-in',
      '-o-transition': 'opacity ' + gets + 's ease-in',
      '-ms-transition': 'opacity ' + gets + 's ease-in',
      'transition': 'opacity ' + gets + 's ease-in'
    }).addClass('beloader')
    var div2 = $('<div>').css({
      'width': '70%',
      'margin-left': '30%',
      'margin-right': '30%'
    }).addClass('col-xs-12 text-center').append(
        $('<h1>').addClass('beloaderc').append(
          $('<span>').addClass(options.icon).css({
            'font-size': options.text_size,
            'color': options.text_color,
            'text-shadow': options.text_shadow
          }))).append(
            $('<h1>').addClass('beloadert').css({
              'font-size': options.text_size,
              'color': options.text_color,
              'text-shadow': options.text_shadow,
              'margin-top': '10%',
              'font-family': options.text_font}).text(options.text))
    if (options.trail === 'true') { // to add escape button
      div2.append($('<div>').addClass('col-xs-12 text-center').attr('style', 'margin-top: 15%;').append(
        $('<button>').addClass('btn btn-danger').text('Escape').attr('onclick', 'stop()')))
    }
    $('body').prepend(div.append(div2))
  }

  beloadingReturn.effectit = function effectit () {
    // here loop fade effect is created
    var def = options.effect_duration / 4
    var ofc = options.effect_duration - def
    $('.beloadert').toggle('fade', {}, def).toggle('fade', {}, ofc)
    beloadingReturn.defaults.loops = setInterval(function () {
      $('.beloadert').toggle('fade', {}, def).toggle('fade', {}, ofc)
    }, 2000)
  }

  beloadingReturn.stop = function stop () {
    // here where elements get removed and loops cleared
    $('.beloader').css('opacity', '0')
    if (beloadingReturn.defaults.loops) {
      clearInterval(beloadingReturn.defaults.loops)
      beloadingReturn.defaults.loops = false
    }
    $('.beloaderc').fadeOut()
    $('.beloadert').stop().fadeOut()
    setTimeout(function () {
      $('.beloader').remove()
    }, Math.round(options.effect_duration / 2) + 500)
  }

  beloadingReturn.__init__()
  return beloadingReturn
}
