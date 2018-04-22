/* global $ */

var watchIt = function watchIt (id, imgId, links, callback) {
    // To control change of select field and update image src whenever
    var toDo = function () {
        var idIndex = $(id + ' option:selected').val()
        $(imgId).attr('src', links[idIndex])
        callback(idIndex)
    }
    $(id).change(function () {
        toDo()
    })
    toDo()
}

var reloadIf = function (toGo=window.location.href, duration=1000) {
    // To auto-reload the page if its served content has changed
    var storePage
    var location = window.location.href
    $.get(location, function(data) {
        storePage = data
    })
    setInterval(function () {
        $.get(location, function (data) {
           if (data !== storePage) window.location = toGo
        })
    }, duration)
}