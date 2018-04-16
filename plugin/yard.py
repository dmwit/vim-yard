import hashlib
import io
import os.path
import vim

PLUGIN_DIR = vim.eval('fnamemodify(resolve(expand("<sfile>:p")), ":h")')
LINE_WHITELIST_NAME = os.path.join(PLUGIN_DIR, 'line_whitelist')
HASH_WHITELIST_NAME = os.path.join(PLUGIN_DIR, 'hash_whitelist')

def load_local_vimrc():
    # locate the rc-file, if any
    # There is a question here about what to do with symlinks. Here we opt for
    # the simplest thing, which also seems perfectly reasonable: don't chase
    # them down. This is even potentially useful: you could have two sets of
    # local variables for a single project by creating a suitable symlink
    # structure.
    here = vim.current.buffer.name
    up = os.path.dirname(here)
    while here != up:
        here = up
        up = os.path.dirname(here)
        try:
            rc_name = os.path.join(here, '.yard')
            rc = io.open(rc_name, encoding='utf-8')
            break
        except IOError: pass
    else:
        # no rc-file, nothing to do
        return

    rc_name_as_vim_string = "'%s'" % rc_name.replace("'","''")
    # escape wildcards like *, ?, and the like
    rc_name_as_vim_file = vim.eval('fnameescape(%s)' % rc_name_as_vim_string)
    vim.command('let b:yard_rc=' + rc_name_as_vim_string)

    # demand that vim's encoding be utf-8, so it sees the files we're loading
    # the same way we do
    if vim.options['encoding'] != 'utf-8':
        sys.stderr.write(
            "Found a local rc file to load, but vim's current encoding isn't utf-8.\n" +
            "To avoid mismatches between our security checks and vim's understanding\n" +
            "of the script, it will not be loaded."
            )
        return

    # This try block is used exclusively to add a finally block to close rc. It
    # doesn't catch any exceptions; all catches are matched with enclosed try
    # blocks.
    try:
        # read the line whitelist
        try:
            with io.open(LINE_WHITELIST_NAME, encoding='utf-8') as f:
                line_whitelist = set(f)
        except IOError:
            # The line whitelist doesn't exist or isn't readable. Having no
            # whitelisted lines is a perfectly safe default.
            line_whitelist = set()
        # We do not catch UnicodeErrors. If the whitelist exists but is corrupted,
        # the human should handle that before we do anything.

        # hash the file and check whether we should use the hash at all
        # We do not catch UnicodeErrors or IOErrors; letting them propagate up to
        # the user for human handling is exactly what's wanted.
        rc_hash = hashlib.sha256()
        lines_white = True
        for line in rc:
            rc_hash.update(line.encode('utf-8'))
            lines_white = lines_white and line in line_whitelist
            if line not in line_whitelist:
                pass
        rc_hash_hex = rc_hash.hexdigest()

        if lines_white: vim.command('source ' + rc_name_as_vim_file)
        else:
            # read the hashes whitelist
            try:
                with io.open(HASH_WHITELIST_NAME, encoding='utf-8') as f:
                    hash_white = any(rc_hash_hex == line.strip() for line in f)
            except IOError:
                # The hash whitelist doesn't exist or isn't readable. Declaring
                # the rc file non-whitelisted is a safe default.
                hash_white = False
            # We do not catch UnicodeErrors. If the whitelist exists but is
            # corrupted, the human should handle that before we do anything.

            if hash_white: vim.command('source ' + rc_name_as_vim_file)
            # Report the problem. But as a special case, we skip the error
            # reporting if g:yard_rc is alread set to the file currently being
            # edited, as this means the user probably just saw the error and is
            # currently in the process of addressing it.
            elif vim.eval('exists("g:yard_rc")') == '0' or \
                 vim.current.buffer.name != vim.eval('g:yard_rc'):
                vim.command("let g:yard_rc='%s'" % rc_name.replace("'","''"))
                vim.command("let g:yard_hash='%s'" % rc_hash_hex)
                vim.command("let g:yard_line_wl='%s'" % LINE_WHITELIST_NAME)
                vim.command("let g:yard_hash_wl='%s'" % HASH_WHITELIST_NAME)
                vim.command("let @\"='%s\n'" % rc_hash_hex)
                sys.stderr.write(
                    "Found a local rc file, but didn't load it. Some lines were not\n" +
                    'whitelisted, and its hash was not whitelisted. Review the file; if it\n' +
                    'looks safe, add its contents to the line whitelist or add its hash to\n' +
                    'the hash whitelist. These registers and variables may help:\n' +
                    ' \n' +
                    'register "       the hash of the local rc file\n' +
                    'g:yard_hash      the hash of the local rc file (in case the register\n' +
                    '                 gets clobbered during other editing actions)\n'
                    'g:yard_rc        the name of the local rc file\n' +
                    'g:yard_line_wl   the name of the line whitelist file\n' +
                    'g:yard_hash_wl   the name of the hash whitelist file\n' +
                    ' \n' +
                    'For example, these commands may be useful:\n' +
                    ':sp <CTRL-R>=g:yard_rc to get started viewing the local rc file (similar\n' +
                    '                       commands work to edit the whitelists)\n' +
                    ':r <CTRL-R>=g:yard_rc  to add the entire contents of the local rc file\n' +
                    '                       after the cursor\n' +
                    'p                      to insert the hash of the local rc file after\n' +
                    '                       the cursor\n'
                    '"=g:yard_hash<CR>p     to insert the hash of the local rc file after\n' +
                    '                       the cursor, even if other edits have modified\n' +
                    '                       the unnamed register\n'
                    )

    finally: rc.close()
