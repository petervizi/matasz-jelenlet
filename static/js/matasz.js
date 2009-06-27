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

var Duration = Class.create();
Duration.setup = function(params) {
    function param_default(name, def) {
	if (!params[name]) params[name] = def;
    }
    param_default('durationField', null);
    param_default('triggerElement', null);
    var triggerElement = $(params.triggerElement);
    triggerElement.onclick = function() {
	var duration = new Duration();
	duration.showAtElmenet(triggerElement);
	return duration;
    };    
}
// Duration.HOURS = new Array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 
// 			   14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24);
// Duration.handleMouseDownEvent = function(event) {
//     Event.observe(document, 'mouseup', Durationalendar.handleMouseUpEvent);
//     Event.stop(event);
// }
// Duration.handleMouseUpEvent = function(event) {
//     alert('ok');
//     return Event.stop(event);
// }
Duration.prototype = {
    container: null,
    initialize: function(parent) {
	if (parent) {
	    this.create($(parent));
	} else {
	    this.create();
	}
    },
    // Constructor
    create: function(parent) {
	if (!parent) {
	    parent = document.getElementsByTagName('body')[0]
	}
	this.container = new Element('div');
	this.container.update('hello');
	parent.appendChild(this.container);
    },
    show: function() {
	this.container.show();
    },
    showAt: function(x, y) {
	this.container.setStyle({left: x + 'px', top: y + 'px'});
	this.show();
    },
    showAtElmenet: function(element) {
	var pos = Position.cumulativeOffset(element);
	this.showAt(pos[0], pos[1]);
    },
}

function submit_session_search() {
    dload_sessions($('searchname').value, 1);
}
function submit_hits_search() {
    dload_hits($('searchname').value, 1);
}
function getCookie(c_name)
{
    if (document.cookie.length>0)
	{
	    c_start=document.cookie.indexOf(c_name + "=");
	    if (c_start!=-1)
		{
		    c_start=c_start + c_name.length+1;
		    c_end=document.cookie.indexOf(";",c_start);
		    if (c_end==-1) c_end=document.cookie.length;
		    return unescape(document.cookie.substring(c_start,c_end));
		}
	}
    return "";
}
function setCookie(c_name,value,expiredays)
{
    var exdate=new Date();
    exdate.setDate(exdate.getDate()+expiredays);
    document.cookie=c_name+ "=" +escape(value)+
	((expiredays==null) ? "" : ";expires="+exdate.toGMTString()) + "; path=/";
}
function increase_page(type) {
    var oldvalue = getCookie(type);
    var newvalue = 10;
    if (!oldvalue) {
	oldvalue = 10;
    }
    if (oldvalue < 90) {
	newvalue = parseInt(oldvalue) + 10;
    }
    setCookie(type, newvalue, 365);
}
function decrease_page(type) {
    var oldvalue = getCookie(type);
    var newvalue = 10;
    if (!oldvalue) {
	oldvalue = 10;
    }
    if (oldvalue > 10) {
	newvalue = parseInt(oldvalue) - 10;
    }
    setCookie(type, newvalue, 365);
}
