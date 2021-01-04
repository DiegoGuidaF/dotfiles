# vim:ft=zsh ts=2 sw=2 sts=2
#
# Custom aliases for ZSH
#

# Use android's SDK ADB
alias adb=~/Android/Sdk/platform-tools/adb

### Makefile
alias mk="make"
alias mc="make clean"
alias md="make download"
alias mut="make debug_x86"
alias mg="make gcov"
alias ml="make lcov"

# Tldr, help by examples
alias help="tldr"

# Make cd and ls in one command
cd() {
  builtin cd "$@" && l
}

