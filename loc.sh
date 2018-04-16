#!/bin/zsh

echo vimscript
grep -v '^ *"' **/*.vim | grep -v '^ *$' | wc -l

echo python
grep -v '^ *[#"'"']" **/*.py | grep -v '^ *$' | wc -l

echo comments
{ grep '^ *#' **/*.py; grep '^ *"' **/*.vim } | wc -l

echo error strings
{ grep '^ *["'"']" **/*.py } | wc -l
