function dload_hits(arg1, arg2) {
    var myA = new Ajax.Request(
			       '/hits/',
			       {
				   method: 'post',
				   parameters: {name: arg1, page: arg2},
				   onSuccess: display_hits
			       }
			       );
    
}

function display_hits(transport) {
    $('hitstable').update( transport.responseText);
}

function dload_sessions(arg1, arg2) {
    var myA = new Ajax.Request(
			       '/list/',
			       {
				   method: 'post',
				   parameters: {name: arg1, page: arg2},
				   onSuccess: display_sessions
			       }
			       );
    
}

function display_sessions(transport) {
    $('sessionstable').update( transport.responseText);
}

function display_base_stats(transport) {
    var response = transport.responseText.evalJSON();
    $('online_peak').update(response.online_peak);
    $('online_users').update(response.online_users);
    $('metersm').setStyle({height: response.online_percent});
}

new Ajax.Request('/base_stats',
		 {
		     method:'get',
		     onSuccess: display_base_stats,
		 });

function dload_timestat1(arg1, arg2) {
    // $('dload_timestat1img').update('<img src="/images/parts/spinner_big.gif" />');
    $('dload_timestat1img').src = "/images/parts/spinner_big.gif";
    new Ajax.Request('/timestat/week/' + arg1 + '/' + arg2,
		     {
			 method: 'post',
			 onSuccess: function(response) {
			     $('timestat1').update(response.responseText);
			 }
		    });
}

function dload_timestat2(arg1, arg2) {
    $('dload_timestat2img').src = "/images/parts/spinner_big.gif";
    new Ajax.Request('/timestat/month/' + arg1 + '/' + arg2,
		     {
			 method: 'post',
			 onSuccess: function(response) {
			     $('timestat2').update(response.responseText);
			 }
		    });
}

