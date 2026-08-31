#!/usr/bin/env bash
# Gate 219 scope fixture. A hook cannot detect a challenge widget without
# matching the widget's own class name in its own source, and a shell line can
# never be a markdown link. This file must therefore never be read by the
# **/*.md sweep. If it ever is, the scope has rotted.
grep -q 'cf-turnstile' "$1" && echo "widget present"
