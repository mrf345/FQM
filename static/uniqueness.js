/* global $ */ // to avoid false linter
/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.

*/

var uniqueness = function Unique (options, callback) {
  callback = callback || Function
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
    return Math.floor(Math.random() * Math.pow(10, digits))
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
  uniquenessReturn = {} // unique object to wrap this

  uniquenessReturn.options = {
    // options to be passed by you, and its default replacement
    identifier: options.identifier || '.uniqueness', // class or id to identify elements by
    start_with: options.start_with || 0, // element index number to start from
    use_effects: options.use_effects || 'true', // to use transitional jquery UI effects
    effect: options.effect || choice(effects), // to get or set a random effect
    effect_duration: options.effect_duration * 1000 || randint(3), // effect duration in seconds. default random
    local_url: options.local_url || 'false', // to goto() via parsing index variable from url
    always_hash: options.always_hash || 'false', // to always display the current element id in hash url
    special_url: options.special_url || function () {} // handler executed right before adding url hash
  }
  uniquenessReturn.turn = 0 // currently shown element
  uniquenessReturn.preTurn = false // to store the previous turn
  uniquenessReturn.s_length = $(uniquenessReturn.options.identifier).length // length of the selected elements
  uniquenessReturn.m_length = uniquenessReturn.s_length - 1 // length deducted for ease of use
  uniquenessReturn.onIt = false // to indicate if any effects is on

  uniquenessReturn.__init__ = function __init__ () {
    // initial function to check the options and selection validity.
    // check for jquery ui and its effects, if use effects
    if (uniquenessReturn.options.use_effects === 'true' && !$.ui) throw new Error('Effects depends on Jquery ui, go get it. or do not use effects !')
    // check types
    var bol; for (var b in bol = [
      uniquenessReturn.options.use_effects,
      uniquenessReturn.options.always_hash,
      uniquenessReturn.options.local_url]) {
      if (bol[b] !== 'true' && bol[b] !== 'false') throw new TypeError("unique(options) require 'true' or 'false'")
    }
    if (!checkType('string', [
      uniquenessReturn.options.identifier,
      uniquenessReturn.options.effect])) throw new TypeError('unique(options) require string')
    if (!checkType('number', [
      uniquenessReturn.options.effect_duration,
      uniquenessReturn.options.start_with])) throw new TypeError('unique(options=effect_duration,start_with) requires number')
    if (uniquenessReturn.options.start_with > uniquenessReturn.m_length || uniquenessReturn.options.start_with < 0) throw new Error('unique(start_with) requires a valid index number')
    // hide the selected elements according to options
    var tempSelected = $(uniquenessReturn.options.identifier)
    tempSelected = tempSelected.not($(uniquenessReturn.options.identifier + ':eq(' + uniquenessReturn.options.start_with + ')'))
    tempSelected.toggle()
    // lunching url parser if allowed and settling the first element
    if (uniquenessReturn.options.local_url === 'true') uniquenessReturn.turn = uniquenessReturn.localUrl() || uniquenessReturn.options.start_with
    else uniquenessReturn.turn = uniquenessReturn.options.start_with
    callback(uniquenessReturn.turn)
    return true
  }

  uniquenessReturn.effect = function effect (effect, duration, index, doe) {
    doe = doe || true
    // to apply the effect and toggle the element
    if (effects.indexOf(effect) === -1) {
      throw new Error('effect(effect) takes a valid jquery ui effect')
    } else {
      if (uniquenessReturn.options.use_effects === 'true' && doe) {
        $(uniquenessReturn.options.identifier + ':eq(' + index + ')').stop().toggle(effect, {}, duration)
      } else $(uniquenessReturn.options.identifier + ':eq(' + index + ')').stop().toggle()
    }
  }

  uniquenessReturn.checkLength = function checkLength () {
    // check length of selection for validity
    if (uniquenessReturn.s_length <= 0) {
      throw new Error('unique(options=identifier) not enough elements to iterate')
    }
  }

  uniquenessReturn.goto = function goto (index) {
    // to validate the index value and send it to the effect function
    uniquenessReturn.checkLength()
    if (!checkType('number', index)) throw new TypeError('goto() requires number')
    if (index > uniquenessReturn.m_length || index < 0) throw new Error('goto() requires a valid index number')
    // check if the element to be unbidden is actually hidden
    if (!uniquenessReturn.onIt) { // to prevent over lapping
      if ($(uniquenessReturn.identifier + ':eq(' + uniquenessReturn.turn + ')').css('display') !== 'none') {
        uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, uniquenessReturn.turn, false)
      } // to avoid first and last hide issues
      uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, index)
      uniquenessReturn.preTurn = uniquenessReturn.turn
      uniquenessReturn.turn = index
      uniquenessReturn.timeIt() // timeout indicator of end of effect
      callback(uniquenessReturn.turn) // execute passed callback function 
    }
  }

  uniquenessReturn.next = function next () {
    // to toggle the next element in selection
    uniquenessReturn.checkLength()
    if (!uniquenessReturn.onIt) {
      uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, uniquenessReturn.turn, false)
      if (uniquenessReturn.turn >= uniquenessReturn.m_length) uniquenessReturn.turn = parseInt(-1) // weird behavior without parseInt
      uniquenessReturn.preTurn = uniquenessReturn.turn
      uniquenessReturn.turn += 1
      uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, uniquenessReturn.turn)
      uniquenessReturn.timeIt()
      callback('next') // execute passed callback function 
    }
  }

  uniquenessReturn.back = function back () {
    // to toggle the previous element in selection
    if (!uniquenessReturn.onIt) {
      uniquenessReturn.checkLength()
      uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, uniquenessReturn.turn, false)
      if (uniquenessReturn.turn < 0) uniquenessReturn.turn = uniquenessReturn.m_length
      uniquenessReturn.preTurn = uniquenessReturn.turn
      uniquenessReturn.turn -= 1
      uniquenessReturn.effect(uniquenessReturn.options.effect, uniquenessReturn.options.effect_duration, uniquenessReturn.turn)
      uniquenessReturn.timeIt()
      callback('back') // execute passed callback function 
    }
  }

  uniquenessReturn.localUrl = function localUrl () {
    // splitting the href looking for our index and magic word unique
    var url = window.location.href.split('#')
    if (url.length < 2) {
      return false
    } else { // it contains #
      url = url[url.length - 1]
      if (url.slice(0, 6) === 'unique') { // found magic word
        url = url.slice(6)
        url = parseInt(url)
        uniquenessReturn.goto(url)
        return url
      } else return false // return false so the || sets start_with option instead
    }
  }

  uniquenessReturn.hashIt = function hashIt () {
    // to add the hashed element ID to the url
    var url = window.location.href.split('#')
    var nextUrl = url[0] + '#unique' + (uniquenessReturn.turn === -1 ? uniquenessReturn.m_length : uniquenessReturn.turn)
    window.history.pushState(nextUrl.slice(1), nextUrl.slice(1), nextUrl)
  }

  uniquenessReturn.timeIt = function timeIt () {
    // setting a timer out to prevent any overlapping
    uniquenessReturn.onIt = true // timeout indicator of end of effect
    setTimeout(function () {
      uniquenessReturn.onIt = false
      uniquenessReturn.options.special_url()
      if (uniquenessReturn.options.always_hash === 'true') uniquenessReturn.hashIt() // adding hash to url after effect's done
    }, uniquenessReturn.options.effect_duration)
  }

  uniquenessReturn.list = function (param) {
    // logging selected elements with their index number or returning object of them
    if (!param) {
      $(uniquenessReturn.options.identifier).each(function (k, v) {
        console.log('Index : ' + k)
        console.log('HTML : ' + v.innerHTML)
        console.log('------------------')
      })
    } else {
      param = {}
      $(uniquenessReturn.options.identifier).each(function (k, v) {
        param[k] = v
      })
      return param
    }
  }

  uniquenessReturn.current = function () { return uniquenessReturn.turn } // returning he currently displayed element index
  uniquenessReturn.length = function () { return uniquenessReturn.s_length } // returning the number of existing elements

  // run initiating function to make sure of selection validity and lack of errors
  uniquenessReturn.__init__()
  return uniquenessReturn // returning the class
}
