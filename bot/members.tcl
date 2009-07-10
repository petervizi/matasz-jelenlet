set log_url(#nomnom) "http://localhost:8080"
set admins(#nomnom) {"Pitir"}

package require http

bind pub "*" "!tag" pub:member

proc pub:member { nick host hand chan text } {
    global log_url admins
    if { [lsearch -exact $admins($chan) $nick] == -1 } {
	puthelp "NOTICE $nick :Ehhez nincs jogosultsagod."
	return 0
    }
    if {[info exists log_url($chan)]} {
	set text [split $text " "]
	set command [lindex $text 0]
	set name [lindex $text 1]
	set id [lindex $text 2]
	if {$command == "hozzaad"} {
	    set query [http::formatQuery "name" $name "id" $id]
	    set token [http::geturl "$log_url($chan)/member/add/" -query $query]
	} elseif {$command == "elvesz"} {
	    set query [http::formatQuery "name" $name]
	    set token [http::geturl "$log_url($chan)/member/remove/" -query $query]
	} else {
	    puthelp "NOTICE $nick :Nincs ilyen parancs."
	    return 0
	}
	set code [http::ncode $token]
	if {$code == 200} {
	    set result [http::data $token]
	    puthelp "NOTICE $chan :$result"
	} else {
	    puthelp "NOTICE $nick :Hiba a szerveren ($code)."
	}
    } else {
	puthelp "NOTICE $nick :Ez a parancs itt nem hasznalhato."
    }
    return 0
}
