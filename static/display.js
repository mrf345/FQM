var prevTicket, audioStore = undefined
function update_values(fr, lang) {
     $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
     $.getJSON($SCRIPT_ROOT+"/feed", function(data) {
	 if (data.refre === 1) location.reload()
	 if (prevTicket !== data.cot) {
	     prevTicket = data.cot
             if (lang === 'ar') {
		 $("#hm1").text("المكتب : " + data.con)
		 $("#hm2").text("التذكرة : " + data.cot)
  		 $("#hm3").text("المهمة : " + data.cott)
	     } else {
		 $("#hm1").text("Office : " + data.con)
		 $("#hm2").text("Ticket : " + data.cot)
  		 $("#hm3").text("Task : " + data.cott)
	     }
	     if (audioStore) AudioSequence.exit()
	     audioStore = AudioSequence({
		 files: [
		     "{{ url_for('static', filename='tts/') }}" + data.anf,
		     "{{ url_for('static', filename='tts/') }}" + "ar_" + data.anf
		 ],
		 repeats: fr,
		 repeat_each: 'true'
	     })
	     function toFade (item, fadeCounter = 0) {
		 if (fadeCounter >= 8) return undefined
		 else $(item).toggle(duration='slow', complete=toFade(fadeCounter + 1))
	     }
	     toFade('#hm1')
	     toFade('#hm2')
	     toFade('#hm3')
	 }
	 $("#hs1").text(data.w1)
	 $("#hs2").text(data.w2)
	 $("#hs3").text(data.w3)
	 $("#hs4").text(data.w4)
	 $("#hs5").text(data.w5)
	 $("#hs6").text(data.w6)
	 $("#hs7").text(data.w7)
	 $("#hs8").text(data.w8)
	 $('#hcounter').text(data.w9)
     })
}

function tom(tmm, fr, lang) {
    window.setInterval(function(){
	update_values(fr, lang)
    }, tmm)
}

window.onload = function(){
    tom({{ ts.rrate }},{{ ts.mduration }})
}
