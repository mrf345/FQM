/* global $ */ // to avoid linter false alarm

/*

Script : beloading 0.1 beta
Author : Mohamed Feddad
Date : 2017/12/16
Source : https://github.com/mrf345/beloading
License: MPL 2.0
Dependancies: Bootstrap ver. * > 3, jQuery UI
Today's lesson: CSS necessary evil.

 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.

 */


const beloading = function beload (options,callback=() => {}) {
  const checkType = function checkType (type, args) {
    // checking the type of each varible in the passed array
    for (let a in args) {
      if (typeof args[a] !== type) return false
    }
    return true
  }

  // main class with all functions
  if (typeof options !== 'object') options = {} // assigning empty object if options is not passed
  if (!window.jQuery) throw new Error('Thsi script is based on jQuery, go get it') // checking for jQuery
  if (typeof $.ui === 'undefined') throw new Error('This script uses jQuery UI effects, go get it') // checking for jQuery UI
  options = {
    // options that will be passed and replacements in case not
    background: options.background || 'rgba(0, 0, 0, 0.9)', // background color
    icon: options.icon || 'fa fa-refresh fa-spin', // takes font awsome icon
    text: options.text || 'Behold the Beloading ahead ...', /// text to be displayed while waiting
    text_color: options.text_color || 'rgb(255, 255, 255)', // text and icon color
    text_font: options.text_font || 'Georgia, Times, serif', // text font
    text_shadow: options.text_shadow || '0 0 30px rgba(255,255,255,0.5)', // text and icon shadow
    text_size: options.text_size || '300%', // text and icon size
    effect_duration: options.effect_duration * 1000 || 3000, // fade effect duration in seconds
    trail: options.trail || 'false' // to add escape button, and cancel on load event
  }

  this.defaults = {
    loops: false, // to store the fade effect interval
    effect_duration: options.effect_duration // to get the effect duration from outside
  }

  this.__init__ = function __init__ () {
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
    this.loading()
    this.effectit()
    if (options.trail === 'false') {
      function toCall () {
        this.stop()
        callback()
      }
      if (document.readyState === "complete") toCall()
      else $(window).on('load', toCall)
    }
  }

  this.loading = function loading () {
    // here elements and css styles will be created and loaded
    const gets = Math.round((options.effect_duration / 2) / 1000)
    const div = $('<div>').css({
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
    const div2 = $('<div>').css({
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

  this.effectit = function effectit () {
    // here loop fade effect is created
    const def = options.effect_duration / 4
    const ofc = options.effect_duration - def
    $('.beloadert').toggle('fade', {}, def).toggle('fade', {}, ofc)
    this.defaults.loops = setInterval(function () {
      $('.beloadert').toggle('fade', {}, def).toggle('fade', {}, ofc)
    }, 2000)
  }

  this.stop = function stop () {
    // here where elements get removed and loops cleared
    $('.beloader').css('opacity', '0')
    if (this.defaults.loops) {
      clearInterval(this.defaults.loops)
      this.defaults.loops = false
    }
    $('.beloaderc').fadeOut()
    $('.beloadert').stop().fadeOut()
    setTimeout(function () {
      $('.beloader').remove()
    }, Math.round(options.effect_duration / 2) + 500)
  }

  this.__init__()
  return this
}
