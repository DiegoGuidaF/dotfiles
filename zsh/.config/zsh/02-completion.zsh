### vim: ft=zsh:fdm=marker:fml=1:fdl=0:fmr=<,>:smc&:cc&:
#
### zstyle :completion:<function>:<completer>:<command>:<argument>:<tag> _settings_

#< LS_COLORS
zstyle ':completion:*:default'               list-colors ${(s.:.)LS_COLORS}
zstyle '*' single-ignored show
#>
#< basics
zstyle ':completion:*'                          file-sort date reverse
zstyle ':completion:*'                          accept-exact      '*(N)'
zstyle ':completion:*'                          list-dirs-first   true
zstyle ':completion:*'                          matcher-list      'm:{a-z}={A-Z}'
zstyle ':completion:*'                          menu select       auto
zstyle ':completion:*'                          separate-sections yes
zstyle ':completion:*'                          squeeze-slashes   false
zstyle ':completion:*'                          use-perl          1
zstyle ':completion:*:(all-|)files'             ignored-patterns  '*.un~'
zstyle ':completion:*:functions'                ignored-patterns  '_*'
zstyle ':completion::complete:*'                cache-path        ${XDG_CONFIG_HOME}/cache/$HOST
zstyle ':completion::complete:*'                use-cache         on
zstyle ':completion:most-accessed-file:*'       completer         _files
zstyle ':completion:most-accessed-file:*'       file-patterns     '*:all\ files'
zstyle ':completion:most-accessed-file:*'       file-sort         access
zstyle ':completion:most-accessed-file:*'       hidden            all
zstyle ':completion:most-accessed-file:*'       match-original    both
zstyle ':completion:*:*:*:users'                ignored-patterns \
  avahi bin daemon dbus ftp http mail nobody

zstyle ':completion:*:cd:*'                     ignored-patterns '(*/)#lost+found'
zstyle ':completion:*:(mv|cp|file|m|mplayer):*' ignored-patterns '(#i)*.(url|mht)'

#zstyle ':completion:*'                       menu select      7 
#zstyle ':completion:*' group-name            ''
#>

###                                                                             ###
## -C will inhibit the check for new completion files, meaning you'll have to    ##
## manually delete .zcompdump or run compinit without -C. The -i flag will skip  ##
## the security check but still check for new completion files. It will ignore   ##
## the insecure files without asking, while -u will use them without asking.     ##
###                                                                             ###

#< processes
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:processes'          command 'ps -axw'
zstyle ':completion:*:processes-names' command 'ps -awxho command'
