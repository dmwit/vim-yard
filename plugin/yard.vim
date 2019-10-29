if exists("s:did_yard_plugin")
    finish
endif
let s:did_yard_plugin = 1

execute("py3file " . fnamemodify(resolve(expand("<sfile>:p")), ":h") . "/yard.py")

augroup yard
    " The two autocmd!'s below aren't really needed; since the script should
    " run just once, there shouldn't be any autocmd's in the yard_plugin
    " augroup yet. Just defensive programming.
    autocmd! BufRead
    autocmd  BufRead * python3 load_local_vimrc()

    autocmd! BufNewFile
    autocmd  BufNewFile * python3 load_local_vimrc()
augroup END
