#
# Based on Ernst's chanstats2.01
#

# INSTALLATION

#   i) Place this TCL into your eggdrop/scripts directory,
#  ii) make the usual 'source scripts/jelenlet.tcl'
#      entry at the end of eggdrop.conf,
# iii) and rehash the bot as normal.

# CONFIGURATION

set log_url(#hunyadi) "http://hunyadiszazad.appspot.com"
set log_url(#matasz) "http://localhost:8080"

package require http

bind join - * stats_join
bind part - * stats_part
bind kick - * stats_kick
bind nick - * stats_nick
bind splt - * stats_splt
bind rejn - * stats_rejn
bind sign - * stats_sign

proc stats_join {nick uhost hand chan} {
    global log_url botnick
    set chan [string tolower $chan]
    if {[info exists log_url($chan)]} {
	set query [http::formatQuery "user" $nick]
	http::geturl "$log_url($chan)/login" -query $query
    }
    return 0
}

proc stats_part { nick uhost hand chan msg } {
    global log_url botnick
    set chan [string tolower $chan]
    if {[info exists log_url($chan)]} {
	set query [http::formatQuery "user" $nick]
	http::geturl "$log_url($chan)/logout" -query $query
    }
}

proc stats_sign {nick uhost hand chan reason} {
    return [stats_part $nick $uhost $hand $chan $reason]
}

proc stats_kick {nick uhost hand chan kicked reason} {
    return [stats_part $nick $uhost $hand $chan ""]
}

proc stats_nick {nick uhost hand chan newnick} {
    global log_url
    set chan [string tolower $chan]
    if {[info exists log_url($chan)]} {
	set query [http::formatQuery "old" $nick "new" $newnick]
	http::geturl "$log_url($chan)/nickchange" -query $query
    }
    return 0
}

proc stats_splt {nick uhost hand chan} {
    return [stats_part $nick $uhost $hand $chan ""]
}

proc stats_rejn {nick uhost hand chan} {
    return [stats_join $nick $uhost $hand $chan]
}
