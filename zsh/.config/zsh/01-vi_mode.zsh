### vim: ft=zsh:fdm=marker:fml=1:fdl=0:fmr=<,>:smc&:cc&:
vim_ins_mode="INSERT"
vim_cmd_mode="CMD"
vim_mode=$vim_ins_mode
function zle-keymap-select {
  vim_mode="${${KEYMAP/vicmd/${vim_cmd_mode}}/(main|viins)/${vim_ins_mode}}"
  zle reset-prompt
}
zle -N zle-keymap-select

function zle-line-finish {
  vim_mode=$vim_ins_mode
}
zle -N zle-line-finish

setopt transient_rprompt
PROMPT='${vim_mode}'
