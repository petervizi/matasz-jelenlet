# INSTALLATION

#   i) Place this TCL into your eggdrop/scripts directory,
#  ii) make the usual 'source scripts/jelenlet.tcl'
#      entry at the end of eggdrop.conf,
# iii) and rehash the bot as normal.

# CONFIGURATION

# There are three variables you should configure, that are
# self-explanatory: login_url, logout_url and ch_name

set login_url "http://localhost:8080/login"
set logout_url "http://localhost:8080/logout"
set ch_name "#nomnom"

package require http

bind join - "$ch_name *!*@*" join:report_login

bind part - "$ch_name *!*@*" part:report_logout
bind sign - "$ch_name *!*@*" part:report_logout

proc join:report_login { nick host hand chan } {
    global login_url
    set query [http::formatQuery "user" $nick]
    http::geturl $login_url -query $query
    return 0
}

proc part:report_logout { nick host hand chan msg } {
    global logout_url
    set query [http::formatQuery "user" $nick]
    http::geturl $logout_url -query $query
    return 0
}

