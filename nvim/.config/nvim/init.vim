" vim: foldmethod=marker:foldlevel=0

" ==================================================
" Source the files ~/.config/nvim/settings/
" ==================================================
if empty(glob('~/.config/nvim/plugged'))
 !curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
 autocmd VimEnter * PlugInstall --sync | source $NEOVIMRC
endif
for f in split(glob('~/.config/nvim/settings/*.vim'), '\n')
    exe 'source' f
endfor

" Spac es & Tabs {{{
set tabstop=4                            " number of visual spaces per TAB
set softtabstop=4                        " number of spaces in tab when editing
set shiftwidth=4                         " key < has 4 spaces
set expandtab                            " tabs are spaces
" }}}

" General Config {{{
" vim clipboard are sync with the system clipboard
set clipboard=unnamedplus
" Don't automatically autocomplete when tabbing in the command line
set wildmode=list:longest
" Ignore when tabbing to autocomplete in command line
" Vim ignore case (i.e. when opening file :e filename)
set wildignorecase
" Keep at least 3 before/after cursor when moving screen
set scrolloff=3
" highlight matching [{()}]
set showmatch

" persistent undo
set undolevels=100 "maximum number of changes that can be undone
set undoreload=10000 "maximum number lines to save for undo on a buffer reload
" }}}
" }}}
