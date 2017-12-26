/**
 * gak.js
 */

if (!gak_SerName){
	var gak_SerName = "gak.webtoons.com";
}

function gak_do(serviceZone) {
	if(getCookie("wtu") == null) {
		var gak_Addr = "http://" + gak_SerName + "/v1/web/cookie";
		try {
			var obj = (new Image());
			obj.src = gak_Addr;
			obj.onload = function() { gak_log(serviceZone); obj.onload = null; return; };
		} catch(e) {	
		}
	}
	else {
		gak_log(serviceZone);
	}
}

function gak_log(serviceZone) {
	var doc = document;
	var wlt = window.location;

	var gak_Addr = "http://" + gak_SerName + "/v1/web/pc?";
	
	try {
		rs = gak_Addr + "u=" + encodeURIComponent(wlt.href) 
			+ "&e=" + (doc.referrer ? encodeURIComponent(doc.referrer) : "");
		
		if(serviceZone) {
			rs = rs + "&s=" + serviceZone;
		}
		
	} catch(e) {
	}
	
	try {
		var obj = (new Image());
		obj.src = rs;
		obj.onload = function() { obj.onload = null; return; };
	} catch(e) {	
	}
}

function gak_do_email_push(platform, json, callback) {
	if(getCookie("wtu") == null) {
		var gak_Addr = "http://" + gak_SerName + "/v1/web/cookie";
		try {
			var obj = (new Image());
			obj.src = gak_Addr;
			var fAfterLoad = function() { gak_log_email_push(platform, json, callback); obj.onload = null; return; };
			obj.onload = fAfterLoad;
			obj.onerror = fAfterLoad;
		} catch(e) {	
		}
	}
	else {
		gak_log_email_push(platform, json, callback);
	}
}

function gak_log_email_push(platform, json, callback) {
	var doc = document;

	var gak_Addr = "http://" + gak_SerName + "/v1/email/statistics?";
	
	try {
		rs = gak_Addr + "&j=" + encodeURIComponent(json)
			+ "&e=" + (doc.referrer ? encodeURIComponent(doc.referrer) : "")	
			+ "&platform=" + platform;
	} catch(e) {
	}
	
	try {
		var obj = (new Image());
		obj.src = rs;
		var fAfterLoad = function() { obj.onload = null; callback && callback();	return; };
		obj.onload = fAfterLoad;
		obj.onerror = fAfterLoad;
	} catch(e) {	
	}
}


function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}