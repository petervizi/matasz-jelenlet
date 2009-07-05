##
# Requires json (tcllib) and dict (http://pascal.scheffers.net/software/tclDict-8.5.2.tar.gz)

set log_url(#hunyadi) "http://hunyadiszazad.appspot.com"
set log_url(#nomnom) "http://hunyadiszazad.appspot.com"
#set log_url(#nomnom) "http://localhost:8080"

package require http
package require json

bind pub * "!utottem" pub:utottem
bind pub * "!mennyit" pub:mennyit
set regions { "Cuyo" "Pacifica" "Tyrol" "Victoria" "Northeast Region" "Zona Central" "Northern Territory" "British Columbia" "East Srpska Republic" "Norte Grande" "Henan" "Guizhou" "Varna" "Mesopotamia" "South Australia" "Western Australia" "Hunan" "Pando" "Liaoning" "Vidin" "Alberta" "Amazonica" "Vorarlberg" "Jiangsu" "Hainan" "Upper Austria" "Newfoundland and Labrador" "Saskatchewan" "Hubei" "Zhejiang" "Norte Chico" "Heilongjiang" "Tasmania" "Nunavut" "Xinjiang" "Shaanxi" "Salzburg" "Ruse" "Fujian" "Guangxi" "Ningxia" "North East Chaco" "Southeast Region" "Quebec" "Nova Scotia" "Burgenland" "Guangdong" "New South Wales" "Ontario" "Anhui" "Burgas" "Andina" "Walloon Region" "Inner Mongolia" "Bolivian Altiplano" "Gansu" "Yunnan" "Prince Edward Island" "Queensland" "Jiangxi" "Brussels-Capital Region" "North West Chaco" "North Region" "Argentine Northwest" "New Brunswick" "Beijing" "South Region" "Caribe e Insular" "Cundiboyacense" "Jilin" "Center-West Region" "Slavonia" "Gran Chaco" "Shanghai" "Zona Sur" "Central West Chaco" "Orinoquia" "Tibet" "Carinthia" "Federation of Bosnia and Herze" "Patagonia" "Northwest Territories" "Chongqing" "Flemish Region" "Zona Austral" "Lower Austria" "West Srpska Republic" "Central Croatia" "Styria" "Plovdiv" "Shandong" "Far South" "Pampas" "Sofia" "Qinghai" "Sichuan" "Manitoba" "Yukon" "Shanxi" "Dnipro" "North Caucasus Region" "West Serbia" "East Serbia" "Belgrade" "Limpopo"}

proc pub:utottem { nick host hand chan text } {
    global log_url regions
    if {[info exists log_url($chan)]} {
	set text [split $text ","]
	set where [lindex $text 0]
	set dmg [lindex $text 1]
	if {($where != "") && ($dmg != "")} {
	    if { [lsearch -exact $regions $where] == -1} {
		puthelp "NOTICE $nick :Ilyen region nincs: $where"
		return 0
	    }
	    set query [http::formatQuery "user" $nick "where" $where "dmg" $dmg]
	    set token [http::geturl "$log_url($chan)/hit" -query $query]
	    set code [http::ncode $token]
	    if {$code == 200} {
		set result [http::data $token]
		puthelp "NOTICE $nick :$result"
	    } else {
		puthelp "NOTICE $nick :Baj van a szerverrel, probald meg kesobb! ($code)"
	    }
	} else {
	    puthelp "NOTICE $nick :\002Nem jol jelentetted az utesed!\002"
	    puthelp "NOTICE $nick :Igy kell utest jelenteni: !utottem <hol>, <mennyit>"
	    puthelp "NOTICE $nick :A <hol>-hoz irdd ki rendesen a csatater nevet."
	    puthelp "NOTICE $nick :A <mennyit>-hez pedig egy darab szamot."
	    puthelp "NOTICE $nick :Peldaul: !utottem Cuyo, 100"
	}
    }
    return 0
}

##
# Returns {ido help}
proc get_time_and_place {a b} {
    set hely ""
    set ido ""
    if [regexp -nocase {(tegnap|ma|[1-9]+)} $a match1] then {
	set ido $match1
    } elseif [regexp -nocase {([a-zA-Z]+)(ban|ben|ba|be|en)} $a match1 match2] then {
 	set hely $match2
    }
    if [regexp -nocase {(tegnap|ma|[1-9]+)} $b match1] then {
	set ido $match1
    } elseif [regexp -nocase {([a-zA-Z]+)(ban|ben|ba|be|en)} $b match1 match2] then {
 	set hely $match2
    }
    return [list $ido $hely]
}

proc pub:mennyit { nick host hand chan text } {
    global log_url
    putlog $text
    if [regexp -nocase {(utottunk|utottem|utott)[ ]{0,1}([A-Za-z]*) ([a-zA-Z]+(?:ban|ben|ba|be|en)|tegnap|ma|[1-9]+)[ ]{0,1}(([a-zA-Z]+)(ban|ben|ba|be|en)|tegnap|ma|[1-9]+){0,1}\?} $text matchresult group1 group2 group3 group4] then {
	if {$group1 == "utott"} then {
	    set ki $group2
	    set idohely [get_time_and_place $group3 $group4]
	} elseif {$group1 == "utottem"} then {
	    set ki "en"
	    set idohely [get_time_and_place $group2 $group3]
	} elseif {$group1 == "utottunk"} then {
	    set ki ""
	    set idohely [get_time_and_place $group2 $group3]
	}
	set ido [lindex $idohely 0]
	set hely [lindex $idohely 1]
	set now [clock seconds]
	if {$ido == "tegnap"} then {
	    set dat [expr $now - 86400]
	    set ido [clock format $dat -format "%Y-%m-%d"]
	} elseif {$ido == "ma"} then {
	    set ido [clock format $now -format "%Y-%m-%d"]
	}
	if {$ki == "en"} {
	    set ki $nick
	}
	set query [http::formatQuery "name" $ki "where" $hely "time" $ido "format" "txt"]
	set token [http::geturl "$log_url($chan)/hits/" -query $query]
	set code [http::ncode $token]
	if {$code == 200} {
	    set result [http::data $token]
	    set result [split $result "\n"]
	    if {$ki == ""} {
		set ki "Az egyseg"
	    }
	    puthelp "NOTICE $chan :$nick: $ki utese"
	    foreach line $result {
		puthelp "NOTICE $chan :$nick: $line"
	    }
	} else {
	    puthelp "NOTICE $nick :A szerver nem erheto el ($code)"
	}
    } else {
	puthelp "NOTICE $nick :Nem ertem mit mondol!"
    }
    return 0
}
