" ==================================================
" Basic Mappings
" ==================================================
" control + vim direction key to navigate windows
noremap <C-J> <C-W>j
noremap <C-K> <C-W>k
noremap <C-H> <C-W>h
noremap <C-L> <C-W>l

" control + arrow key to navigate windows
noremap <C-Down> <C-W>j
noremap <C-Up> <C-W>k
noremap <C-Left> <C-W>h
noremap <C-Right> <C-W>l

" - and + to resize horizontal splits
map - <C-W>-
map + <C-W>+

" alt-< or alt-> for vertical splits
map <m-,> <C-W>>
map <m-.> <C-W><

" Map Esc to exit terminal mode
tnoremap <leader><Esc> <C-\><C-n>

" consistent window movement commands
tnoremap <c-h> <c-\><c-n><c-w>h
tnoremap <c-j> <c-\><c-n><c-w>j
tnoremap <c-k> <c-\><c-n><c-w>k
tnoremap <c-l> <c-\><c-n><c-w>l

" stop highlighting searched terms
nnoremap <silent> <leader><space> :nohlsearch<cr>
" ==================================================
" Setup grep shortcuts and use ripgrep if available
" ==================================================
"nmap g/ :grep!<space>
"nmap g* :grep! -w <C-R><C-W><space>
"nmap ga :grepadd!<space>

if executable("rg")
    set grepprg=rg\ --vimgrep\ --no-heading
    set grepformat=%f:%l:%c:%m,%f:%l:%m
endif

" Auto open grep quickfix window
"autocmd QuickFixCmdPost *grep* cwindow<Paste>

" ==================================================
" CoC
" ==================================================
" Use K to show documentation in preview window
nnoremap <silent> K :call <SID>show_documentation()<CR>
function! s:show_documentation()
  if (index(['vim','help'], &filetype) >= 0)
    execute 'h '.expand('<cword>')
  else
    call CocAction('doHover')
  endif
endfunction

" Remap for rename current word
nmap <leader>crn <Plug>(coc-rename)
nmap <silent> <leader>cd <Plug>(coc-definition)
nmap <silent> <leader>ct <Plug>(coc-type-definition)
nmap <silent> <leader>ci <Plug>(coc-implementation)
nmap <silent> <leader>cr <Plug>(coc-references)

" Remap for format selected region
xmap <leader>cf  <Plug>(coc-format-selected)
nmap <leader>cf  <Plug>(coc-format-selected)

    " ========================
    " Shortcuts for Coc cls
    " =======================
"    " bases
"    nn <silent> xb :call CocLocations('ccls','$ccls/inheritance')<cr>
"    " bases of up to 3 levels
"    nn <silent> xb :call CocLocations('ccls','$ccls/inheritance',{'levels':3})<cr>
"    " derived
"    nn <silent> xd :call CocLocations('ccls','$ccls/inheritance',{'derived':v:true})<cr>
"    " derived of up to 3 levels
"    nn <silent> xD :call CocLocations('ccls','$ccls/inheritance',{'derived':v:true,'levels':3})<cr>
"
"    " caller
"    nn <silent> xc :call CocLocations('ccls','$ccls/call')<cr>
"    " callee
"    nn <silent> xC :call CocLocations('ccls','$ccls/call',{'callee':v:true})<cr>
"
"    " $ccls/member
"    " member variables / variables in a namespace
"    nn <silent> xm :call CocLocations('ccls','$ccls/member')<cr>
"    " member functions / functions in a namespace
"    nn <silent> xf :call CocLocations('ccls','$ccls/member',{'kind':3})<cr>
"    " nested classes / types in a namespace
"    nn <silent> xs :call CocLocations('ccls','$ccls/member',{'kind':2})<cr>
"
"    nmap <silent> xt <Plug>(coc-type-definition)<cr>
"    nn <silent> xv :call CocLocations('ccls','$ccls/vars')<cr>
"    nn <silent> xV :call CocLocations('ccls','$ccls/vars',{'kind':1})<cr>
"
"    nn xx x

" ==================================================
" Denite
" ==================================================

"   ;         - Browser currently open buffers
"   <leader>t - Browse list of files in current directory
"   <leader>g - Search current directory for occurences of given term and
"   close window if no results
"   <leader>j - Search current directory for occurences of word under cursor
nmap ; :Denite buffer -split=floating -winrow=1<CR>
nmap <leader>t :Denite file/rec -split=floating -winrow=1<CR>
nnoremap <leader>g :<C-u>Denite grep:. -no-empty<CR>
nnoremap <leader>j :<C-u>DeniteCursorWord grep:.<CR>

" ==================================================
" Vista - Tagbar with async and lsp support
" ==================================================
map <F3> :Vista!!<CR>

" ==================================================
" NerdTree - File browser
" ==================================================
map <F2> :NERDTreeToggle<CR>

" ==================================================
" Clap - Async search through many sources
" ==================================================
map <leader>ff :Clap files --hidden<CR>

" Add no-messages option to ignore files with no permission to read
" Find words
map <leader>fl :Clap grep ++opt=--no-messages<CR>
map <leader>fw :Clap grep2 ++opt=--no-messages ++query=<cword><CR>

" Search in dotfiles
map <leader>fd :Clap files --hidden ~/Personal/dotfiles<CR>

" Search list of open buffers
map <leader>fb :Clap buffers<CR>

" Search list of open buffers
map <leader>fh :Clap history<CR>
