/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
 
jQuery(function($){
  var windowWidth = $(window).width();
  var windowHeight = $(window).height();

  $(window).resize(function() {
    if(windowWidth != $(window).width() || windowHeight != $(window).height()) {
      location.reload();
      return;
    }
  });
});
function areload (timeo=8000) {
    if (!Number.isInteger(timeo)) {
	     timeo = 8000
    }
    var timeout
    if (sessionStorage.autoReload) {
	timeout = setTimeout("document.location.reload(true);",timeo);
	if ($('#ar').is(':visible')) {
	    $('#ar').removeClass("btn-primary");
	    $('#ar').addClass("btn-danger");
	}
	if ($('#arb').is(':visible')) {
	    $('#arb').removeClass("btn-primary");
	    $('#arb').addClass("btn-danger");
	}
    }
    $(window).scroll(function() {
	     sessionStorage.scrollTop = $(this).scrollTop();
    });

    $(document).ready(function() {
	if (sessionStorage.scrollTop != "undefined") {
	    $(window).scrollTop(sessionStorage.scrollTop);
	}
    });

    document.getElementById('ar').onclick = function autorl() {
	if ($('#ar').hasClass("btn-primary") && $('#ar').is(':visible')) {
	    clearTimeout(timeout);
	    timeout = setTimeout("document.location.reload(true);",timeo);
	    sessionStorage.autoReload = true
	    $('#ar').removeClass("btn-primary");
	    $('#ar').addClass("btn-danger");
	} else {
	    clearTimeout(timeout);
	    sessionStorage.clear();
	    $('#ar').removeClass("btn-danger");
	    $('#ar').addClass("btn-primary");
	}
    }
    document.getElementById('arb').onclick = function autorl() {
	if ($('#arb').hasClass("btn-primary") && $('#arb').is(':visible')) {
	    clearTimeout(timeout);
	    timeout = setTimeout("document.location.reload(true);",timeo);
	    sessionStorage.autoReload = true
	    $('#arb').removeClass("btn-primary");
	    $('#arb').addClass("btn-danger");
	    document.location.reload(true);
	} else {
	    clearTimeout(timeout);
	    sessionStorage.clear();
	    $('#arb').removeClass("btn-danger");
	    $('#arb').addClass("btn-primary");
	}
    }
}
