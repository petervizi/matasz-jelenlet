
set url "http://erepstats.com/hu/napiparancs/index"

package require http

bind pub * "!napiparancs" pub:napiparancs

proc pub:napiparancs { nick host hand chan text } {
    global url
    set token [http::geturl $url]
    set result [http::data $token ]
    set code [http::ncode $token]
    if {$code == 200} {
	set result [split $result "|"]
	set parancs [lindex $result 0]
	set regio [lindex $result 1]
	set link [lindex $result 2]
	set ido [lindex $result 3]
	puthelp "NOTICE $chan :\002\[Parancs\]\002 $parancs"
	puthelp "NOTICE $chan :\002\[Csata  \]\002 $regio $link"
	puthelp "NOTICE $chan :\002\[Kiadva \]\002 $ido"
    } else {
	set code [http::code $token]
	puthelp "NOTICE $chan :\002\[Parancs\]\002 nem erheto el ($code)"
    }
}
