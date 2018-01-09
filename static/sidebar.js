/* global $ */
$(function () {
  $('.navbar-toggle-sidebar').click(function () {
    $('.navbar-nav').toggleClass('slide-in')
    $('.side-body').toggleClass('body-slide-in')
    $('#search').removeClass('in').addClass('collapse').slideUp(200)
  })
})

function sidetoggle () {
  $('.navbar-nav').toggleClass('slide-in')
  $('.side-body').toggleClass('body-slide-in')
  $('#search').removeClass('in').addClass('collapse').slideUp(200)
}
