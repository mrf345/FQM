/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/* global $, FormData */
 $(document).ready(function () {
   $('form').on('submit', function (event) {
     event.preventDefault()
     var formData = new FormData($('form')[0])
     $.ajax({
       xhr: function () {
         var xhr = new window.XMLHttpRequest()
         xhr.upload.addEventListener('progress', function (e) {
           if (e.lengthComputable) {
             var percent = Math.round((e.loaded / e.total) * 100)
             $('#pgbarc').attr('aria-valuenow', percent).css('width', percent + '%').text(percent + '%  Completed')
           }
         })
         $('#cancel').on('click', function () {
           xhr.abort()
         })
         return xhr
       },
       type: 'POST',
       url: "{{ url_for('multimedia') }}",
       data: formData,
       processData: false,
       contentType: false
     })
   })
 })
