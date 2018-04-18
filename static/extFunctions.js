var watchIt = function watchIt (id, imgId, links, callback) {
    // To control change of select field and update image src whenever
    $(id).change(function () {
        var idIndex = $(id + ' option:selected').val()
        $(imgId).attr('src', links[idIndex])
        callback(idIndex)
    })
}

