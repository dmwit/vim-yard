# vim-yard

It is frequently convenient to have project-specific settings when editing
files in vim. For example, whitespace and line wrapping settings frequently
vary from project to project. In more complex settings, one may want to load
project-specific plugins, set up project-specific compiler flags, or add
project-specific autocommands.

On a file-by-file basis, vim natively supports modelines, which let you embed a
short vimscript snippet into your file and have it run when you open the file.
To avoid security problems, the script is run in a sandbox which disables most
scripting commands. This feature has two drawbacks: it requires significant
redundancy if many files share settings, and the sandbox greatly restricts what
can be done.

This plugin, **yard**, is a sandbox for adults. You can do anything you want in
the yard -- provided you get approval that your plan is safe to carry out.
Unlike modelines, they are per-project; you can write a single `.yard` file in
the top-level project directory, and its contents will be executed every time
you edit a file in any subdirectory.

There are other plugins that offer this feature, but with an unfortunate
security story about when vimscripts are executed; typically chosen from one of
"always executed", "requires user interaction every time a file is edited", or
"matches on file name to decide what to do". By contrast, **yard** uses file
*contents* to decide what to do; you need not worry about a local rc file from
a git repository you cloned changing out from under you after you marked it as
trusted, you need not repeatedly confirm the same rc file over and over as safe
(even if it migrates to another project), and even an attacker who knows your
whitelists cannot run unapproved code.

## Usage

Install with one of the many excellent vim package managers. If you haven't
looked into them yet and just want to get started without evaluating them all,
I use [vundle](https://github.com/VundleVim/Vundle.vim) and don't hate it. If
you can't be bothered to use a package manager, copy the contents of the
`plugin` directory into `~/.vim/plugin/`.

Every time you start editing a new file, **yard** will search up the directory
tree for a file named `.yard`. The first one it finds will have its name placed
in the `b:yard_rc` variable (to aid in viewing and modifying the file) and be
subjected to a security check. If the check passes, the file will be
`:source`d. If the check does not pass, an error explaining how to review and
whitelist the file will be printed.

## Security

There are two whitelists, a line-by-line whitelist and a whole-file hash
whitelist. A script must be valid utf-8 text to pass the security check. Under
the assumption that it is, a file passes the security check if every line in it
is in the line-by-line whitelist or if the sha256sum of the entire file is in
the whole-file hash whitelist. These whitelists are stored (again in utf-8) in
the `plugin` directory next to `yard.vim` and `yard.py`; they are named
`line_whitelist` and `hash_whitelist`, respectively.

An attacker might be able to make your editor run out of memory by writing a
valid utf-8 encoded file with a single line that is very long. This is fixable
in principle, but the fix is not yet implemented.

The **yard** plugin is intentionally feature-poor to increase its auditability.
It is designed and written to be read in its entirety in one sitting without
much strain:

| Language | Lines |
| -------- | ----- |
| vimscript | 11 |
| python | 59 |
| comments | 33 |
| error strings | 25 |
