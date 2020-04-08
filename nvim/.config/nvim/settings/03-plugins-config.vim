" ==================================================
" Airline
" ==================================================
" Naming regex for things to ignore on upper buffer list. Since new update
" terminal was listed. Return to the previous default where terminal IS
" listed.
let g:airline#extensions#tabline#ignore_bufadd_pat = '!|defx|gundo|nerd_tree|startify|tagbar|undotree|vimfiler'

" ==================================================
" CoC
" ==================================================

" don't give |ins-completion-menu| messages.
"set shortmess+=c
function! s:check_back_space() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~ '\s'
endfunction

" Use tab for trigger completion with characters ahead and navigate.
" Use command ':verbose imap <tab>' to make sure tab is not mapped by other plugin.
inoremap <silent><expr> <TAB>
      \ pumvisible() ? "\<C-n>" :
      \ <SID>check_back_space() ? "\<TAB>" :
      \ coc#refresh()

inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"

"Close preview window when completion is done.
autocmd! CompleteDone * if pumvisible() == 0 | pclose | endif


" ==================================================
" Airline
" ==================================================
let g:airline_theme = 'hybrid'
" use patchet fonts that can use >
let g:airline_powerline_fonts = 1
"Enable airline tabline
let g:airline#extensions#tabline#enabled = 1
" Customize tabline (Showing buffers on top)
let g:airline#extensions#tabline#buffer_nr_show = 1
" Just show the filename (no path) in the tab
let g:airline#extensions#tabline#fnamemod = ':t'


" ==================================================
" Gruvbox
" ==================================================
let g:gruvbox_italic = 1
let g:gruvbox_bold = 1
let g:gruvbox_underline = 1
let g:gruvbox_undercurl = 1
let g:gruvbox_contrast_dark = 'medium'
colorscheme gruvbox

" ==================================================
" Vista - Tagbar with lsp support and async
" ==================================================
"" Ensure you have installed some decent font to show these pretty symbols, then you can enable icon for the kind.
let g:vista#renderer#enable_icon = 1

" ==================================================
" Startify - Init screen with MRU and random cowsay
" ==================================================
let g:startify_change_to_dir = 0
let g:startify_change_to_vsc_root = 1


" ==================================================
" Suda - Write/Read to files with privileges
" ==================================================
" Suda automatically switch a buffer name when the target file is not readable or writable.
let g:suda_smart_edit = 1

" ==================================================
" Clap - Async search through many sources
" ==================================================
" Set clap to grep in hidden files too but ignoring .git subfolder
let g:clap_provider_grep_opts = '-H --no-heading --vimgrep --smart-case --hidden -g "!.git/"'
