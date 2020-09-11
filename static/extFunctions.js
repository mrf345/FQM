/* global $ */

var watchIt = function watchIt (id, imgId, links, callback) {
    callback = callback || Function
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

var reloadIf = function (toGo, duration) {
    toGo = toGo || window.location.href
    duration = duration || 1000

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

var flashMsg = function (cate) {
    $('.postFlash').removeClass('hide')
    $('.postFlash > .alert-' + cate).removeClass('hide')
}

var announce = function () {
    // to $.post for repeating announcement and displaying flash message for success or failure
    $.get('/set_repeat_announcement/1', function (resp) {
        resp.status ? flashMsg('info') : flashMsg('danger')
    })
}


var copyToClipboard = function (text) {
    // copy `text` to clipboard
    var tempInput = document.createElement('input')

    tempInput.display = 'none;'
    tempInput.value = text

    document.body.appendChild(tempInput)
    tempInput.select()
    tempInput.setSelectionRange(0, 99999)
    document.execCommand('copy')
    document.body.removeChild(tempInput)
}
