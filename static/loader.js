/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

 var pa,pv,qv,nv,fv,h
 function something(sc, ts, dv){
     $(pv).removeClass('active');
     $(pa).removeClass('active');
     $(qv).removeClass('active');
     $(nv).removeClass('active');
     $(fv).removeClass('active');
     $(h).addClass('hide');
     $(sc).addClass('active');
     $(sc).collapse('show');
     $(ts).addClass('active');
     $(dv).addClass('active');
     if (parseInt(dv.substr(-1)) == 2) {
	 $("#p"+ts.substr(-1)).removeClass("hide")
	 $("#ts"+ts.substr(-1)).addClass('active');
	 h = "#p"+ts.substr(-1)
	 qv = "#ts"+ts.substr(-1)
     }
     if (parseInt(dv.substr(-1)) == 3) {
	 $("#pa"+ts.substr(-1)).removeClass("hide")
	 $("#ds"+ts.substr(-1)).addClass('active');
	 h = "#pa"+ts.substr(-1)
	 tb = parseInt(ts.substr(-1))+6
	 nv = "#ds"+ts.substr(-1)
     }
     if (parseInt(dv.substr(-1)) == 4) {
	 $("#pb"+ts.substr(-1)).removeClass("hide")
	 $("#ss"+ts.substr(-1)).addClass('active');
	 h = "#pb"+ts.substr(-1)
	 fv = "#ss"+ts.substr(-1)
     }
     if (! $("#waiting").hasClass("hide")) $("#waiting").addClass("hide");
     pa = ts
     pv = dv
 }
