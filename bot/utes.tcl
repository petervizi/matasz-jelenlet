set log_url(#matasz) "http://matasz-jelenlet.appspot.com"

package require http

bind pub * "!utottem" pub:utottem

proc pub:utottem { nick host hand chan text } {
    global log_url
    if {[info exists log_url($chan)]} {
	set text [split $text ","]
	set where [lindex $text 0]
	set dmg [lindex $text 1]
	if {($where != "") && ($dmg != "")} {
	    set query [http::formatQuery "user" $nick "where" $where "dmg" $dmg]
	    set token [http::geturl "$log_url($chan)/hit" -query $query]
	    set result [http::data $token]
	    puthelp "PRIVMSG $nick :$result"
	} else {
	    puthelp "PRIVMSG $nick :Igy kell utest jelenteni: !utottem <hol>, <mennyit>"
	    puthelp "PRIVMSG $nick :A <hol>-hoz irdd ki rendesen a csatater nevet."
	    puthelp "PRIVMSG $nick :A <mennyit>-hez pedig egy darab szamot."
	    puthelp "PRIVMSG $nick :Peldaul: !utottem Cuyo, 100"
	}
    }
    return 0
}
