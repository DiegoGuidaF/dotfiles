" ==================================================
" Basic Settings
" ==================================================

let nvimDir = '$HOME/.config/nvim'  " Set a variable for working dir
let mapleader = ","     " Remap leader key to a closer key with current keymapping for ES

" Colors
set termguicolors
set background=dark
syntax enable

" General
set clipboard=unnamedplus   " Clipboard synced with system one
set number               " show line numbers
set cursorline           " have a line indicate the cursor location

set pyxversion=3         " Set the preferred python version to use when both work
set autoindent           " always set autoindenting on
set nobackup             " do not keep a backup file
set nowritebackup        " Needed by CoC Pluggin
set hidden               " Hides buffers instead of closing them
set modeline             " last lines in document sets vim mode
set shortmess=atI        " Abbreviate messages
set shortmess+=c         " Don't give completion messages like 'match 1 of 2' or 'The only match'
set showmatch            " Briefly display any matching bracket if available.
set matchtime=3          " Time the match above is displayed
set noshowmode           " Hide the default mode text (e.g. -- INSERT -- below the statusline)
set history=1000         " larger history
set splitright           " Splits to the right
set updatetime=200       " Smaller updatetime for CursorHold & CursorHoldI
set signcolumn=yes       " always show signcolumns
set noshowcmd            " Don't show last command

filetype plugin on
filetype indent plugin on
autocmd VimResized * wincmd =   " Automatically equalize splits when Vim is resized
" Enable using mouse for all modes
" This also allows resizing splits with the mouse
set mouse=a
set scrolloff=3  " Keep at least 3 before/after cursor when moving screen
if has('linebreak')      " Break indent wrapped lines
	set breakindent
	let &showbreak = '↳ '
	set cpo+=n
end

" Completion
set wildmenu                    " show list instead of just completing
set wildmode=list:longest,full  " command <Tab> completion, list matches, then longest common part, then all.
set wildignore+=*.so,*.swp,*.bak,*.pyc,*.cache,*.o,*.d,tags,cscope.*,*.pyo
set wildignorecase 		" Vim ignore case (i.e. when opening file :e filename)
set completeopt=menu            " Just show the menu upon completion (faster)<Paste>

" ==================================================
" Search settings
" ==================================================
set hlsearch             " highlight searches
set infercase            " smarter completions that will be case aware when ignorecase is on
set smartcase            " if searching and search contains upper case, make case sensitive search
set incsearch            " search as characters are entered
set ignorecase           " search are not case sensitive


" ==================================================
" Tab expanded to 4 spaces
" ==================================================
set tabstop=4            " numbers of spaces of tab character
set shiftwidth=4         " numbers of spaces to (auto)indent
set expandtab		     " Tab to spaces by default
set softtabstop=4        " number of spaces in tab when editing

" ==================================================
" Trailing whitespace handling
" ==================================================

" Highlight end of line whitespace.
"highlight WhitespaceEOL ctermbg=red guibg=red
"match WhitespaceEOL /\s\+$/

" ==================================================
" Undofile
" ==================================================
if has('persistent_undo')
    let myUndoDir = expand(nvimDir . '/undodir')
    " Create dirs
    call system('mkdir ' . nvimDir)
    call system('mkdir ' . myUndoDir)
    let &undodir = myUndoDir
    set undofile
endif

" ==================================================
" Terminal
" ==================================================

" Enter insert mode whenever we're in a terminal
" autocmd TermOpen,BufWinEnter,BufEnter term://* startinsert

" ==================================================
" Neovim-remote improvements
" ==================================================
" Set editor to current neovim session
if has('nvim')
  let $GIT_EDITOR = 'nvr -cc split --remote-wait'
endif
" Below fix automatically delets buffeer when its commit type
" else nvr would wait for it to be deleted
autocmd FileType gitcommit,gitrebase,gitconfig set bufhidden=delete
