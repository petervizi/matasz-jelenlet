bind pub * "!org" pub:org
bind pub * "!level" pub:level
bind pub * "!avatar" pub:avatar
bind pub * "!honlap" pub:honlap

bind msg * "parancsok" msg:parancsok

proc pub:org { nick host hand chan text } {
    puthelp "NOTICE $chan :\002\[Org\]\002 http://tinyurl.com/mq8e6u"
    return 0
}

proc pub:level { nick host hand chan text } {
    puthelp "NOTICE $chan :\002\[Email\]\002 ehunyadiszazad@gmail.com"
    return 0
}

proc pub:avatar { nick host hand chan text } {
    puthelp "NOTICE $chan :\002\[Avatar\]\002 http://tinyurl.com/npqvnq"
    return 0
}

proc msg:parancsok { nick user handle text } {
    puthelp "NOTICE $nick :Ezeket a parancsokat hasznalhatod:"
    puthelp "NOTICE $nick :!avatar"
    puthelp "NOTICE $nick :!honlap"
    puthelp "NOTICE $nick :!level"
    puthelp "NOTICE $nick :!napiparancs"
    puthelp "NOTICE $nick :!org"
    puthelp "NOTICE $nick :!seen <nick>"
    puthelp "NOTICE $nick :!utottem <hol>, <mennyit>"
    return 0
}

proc pub:honlap { nick host hand chan text } {
    puthelp "NOTICE $chan :\002\[Honlap\]\002 http://hunyadiszazad.appspot.com"
    return 0

}
