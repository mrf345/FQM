/* global $ */ // to avoid false linter
/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.

*/

var uniqueness = function Unique (options, callback=function (data) {}) {
  var checkType = function checkType (type, args) {
    // checking the type of each variable in the passed array
    for (var a in args) {
      if (typeof args[a] !== type) return false
    }
    return true
  }
  var randint = function randint (digits) {
  // to generate a random int of certain range, it takes the length of
  // the randint as an argument
    if (!checkType('number')) throw new TypeError('randint() requires numbers')
    return Math.floor(Math.random() * (10 ** digits))
  }
  var choice = function choice (list) {
  // to chose randomly from an Array
    if (!(list instanceof Array)) throw new TypeError('choice() takes only Arrays')
    if (list.length <= 0) throw new Error('choice() requires populated Array')
    var powerOfLength = Math.floor(list.length / 10)
    if (powerOfLength <= 0) powerOfLength = 1
    return list[Math.floor(Math.random() * (10 * powerOfLength))]
  }
  var effects = [
    // jquery ui effects
    'blind', 'bounce', 'clip',
    'drop', 'explode', 'fade',
    'fold', 'highlight', 'puff',
    'pulsate', 'scale', 'shake',
    'size', 'slide']

  // main class that contains all functions
  if (!window.jQuery) throw new Error('This script depends fully on jquery, go get it') // check for jquery
  if (typeof options !== 'object') options = {}
  this.options = {
    // options to be passed by you, and its default replacement
    identifier: options.identifier || '.uniqueness', // class or id to identify elements by
    start_with: options.start_with || 0, // element index number to start from
    use_effects: options.use_effects || 'true', // to use transitional jquery UI effects
    effect: options.effect || choice(effects), // to get or set a random effect
    effect_duration: options.effect_duration * 1000 || randint(3), // effect duration in seconds. default random
    local_url: options.local_url || 'false', // to goto() via parsing index variable from url
    always_hash: options.always_hash || 'false' // to always display the current element id in hash url
  }
  this.turn = 0 // currently shown element
  this.preTurn = false // to store the previous turn
  this.s_length = $(this.options.identifier).length // length of the selected elements
  this.m_length = this.s_length - 1 // length deducted for ease of use
  this.onIt = false // to indicate if any effects is on

  this.__init__ = function __init__ () {
    // initial function to check the options and selection validity.
    // check for jquery ui and its effects, if use effects
    if (this.options.use_effects === 'true' && !$.ui) throw new Error('Effects depends on Jquery ui, go get it. or do not use effects !')
    // check types
    var bol; for (var b in bol = [
      this.options.use_effects,
      this.options.always_hash,
      this.options.local_url]) {
      if (bol[b] !== 'true' && bol[b] !== 'false') throw new TypeError("unique(options) require 'true' or 'false'")
    }
    if (!checkType('string', [
      this.options.identifier,
      this.options.effect])) throw new TypeError('unique(options) require string')
    if (!checkType('number', [
      this.options.effect_duration,
      this.options.start_with])) throw new TypeError('unique(options=effect_duration,start_with) requires number')
    if (this.options.start_with > this.m_length || this.options.start_with < 0) throw new Error('unique(start_with) requires a valid index number')
    // hide the selected elements according to options
    var tempSelected = $(this.options.identifier)
    tempSelected = tempSelected.not($(this.options.identifier + ':eq(' + this.options.start_with + ')'))
    tempSelected.toggle()
    // lunching url parser if allowed and settling the first element
    if (this.options.local_url === 'true') this.turn = this.localUrl() || this.options.start_with
    else this.turn = this.options.start_with
    callback(this.turn)
    return true
  }

  this.effect = function effect (effect, duration, index, doe = true) {
    // to apply the effect and toggle the element
    if (effects.indexOf(effect) === -1) {
      throw new Error('effect(effect) takes a valid jquery ui effect')
    } else {
      if (this.options.use_effects === 'true' && doe) {
        $(this.options.identifier + ':eq(' + index + ')').stop().toggle(effect, {}, duration)
      } else $(this.options.identifier + ':eq(' + index + ')').stop().toggle()
    }
  }

  this.checkLength = function checkLength () {
    // check length of selection for validity
    if (this.s_length <= 0) {
      throw new Error('unique(options=identifier) not enough elements to iterate')
    }
  }

  this.goto = function goto (index) {
    // to validate the index value and send it to the effect function
    this.checkLength()
    if (!checkType('number', index)) throw new TypeError('goto() requires number')
    if (index > this.m_length || index < 0) throw new Error('goto() requires a valid index number')
    // check if the element to be unbidden is actually hidden
    if (!this.onIt) { // to prevent over lapping
      if ($(this.identifier + ':eq(' + this.turn + ')').css('display') !== 'none') {
        this.effect(this.options.effect, this.options.effect_duration, this.turn, false)
      } // to avoid first and last hide issues
      this.effect(this.options.effect, this.options.effect_duration, index)
      this.preTurn = this.turn
      this.turn = index
      this.timeIt() // timeout indicator of end of effect
      callback(this.turn) // execute passed callback function 
    }
  }

  this.next = function next () {
    // to toggle the next element in selection
    this.checkLength()
    if (!this.onIt) {
      this.effect(this.options.effect, this.options.effect_duration, this.turn, false)
      if (this.turn >= this.m_length) this.turn = parseInt(-1) // weird behavior without parseInt
      this.preTurn = this.turn
      this.turn += 1
      this.effect(this.options.effect, this.options.effect_duration, this.turn)
      this.timeIt()
      callback('next') // execute passed callback function 
    }
  }

  this.back = function back () {
    // to toggle the previous element in selection
    if (!this.onIt) {
      this.checkLength()
      this.effect(this.options.effect, this.options.effect_duration, this.turn, false)
      if (this.turn < 0) this.turn = this.m_length
      this.preTurn = this.turn
      this.turn -= 1
      this.effect(this.options.effect, this.options.effect_duration, this.turn)
      this.timeIt()
      callback('back') // execute passed callback function 
    }
  }

  this.localUrl = function localUrl () {
    // splitting the href looking for our index and magic word unique
    var url = window.location.href.split('#')
    if (url.length < 2) {
      return false
    } else { // it contains #
      url = url[url.length - 1]
      if (url.slice(0, 6) === 'unique') { // found magic word
        url = url.slice(6)
        url = parseInt(url)
        this.goto(url)
        return url
      } else return false // return false so the || sets start_with option instead
    }
  }

  this.hashIt = function hashIt () {
    // to add the hashed element ID to the url
    var url = window.location.href.split('#')
    var nextUrl = url[0] + '#unique' + (this.turn === -1 ? this.m_length : this.turn)
    window.history.pushState(nextUrl.slice(1), nextUrl.slice(1), nextUrl)
  }

  this.timeIt = function timeIt () {
    // setting a timer out to prevent any overlapping
    this.onIt = true // timeout indicator of end of effect
    setTimeout(function () {
      this.onIt = false
      if (this.options.always_hash === 'true') this.hashIt() // adding hash to url after effect's done
    }, this.options.effect_duration)
  }

  this.list = function (param) {
    // logging selected elements with their index number or returning object of them
    if (!param) {
      $(this.options.identifier).each(function (k, v) {
        console.log('Index : ' + k)
        console.log('HTML : ' + v.innerHTML)
        console.log('------------------')
      })
    } else {
      param = {}
      $(this.options.identifier).each(function (k, v) {
        param[k] = v
      })
      return param
    }
  }

  this.current = function () { return this.turn } // returning he currently displayed element index
  this.length = function () { return this.s_length } // returning the number of existing elements

  // run initiating function to make sure of selection validity and lack of errors
  this.__init__()
  return this // returning the class
}
