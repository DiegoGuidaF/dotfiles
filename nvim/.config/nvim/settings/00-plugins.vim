" ==================================================
" vim-plug  setup
" ==================================================
"
" Make sure you use single quotes
call plug#begin('~/.config/nvim/plugged')
" Color scheme and appearance
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'gruvbox-community/gruvbox'

" Plugin to add commonly used fzf tools
Plug 'junegunn/fzf', { 'do': './install --all' }
Plug 'junegunn/fzf.vim'
"
" General Utilities
" Show git commit message in a popup window
" Plug 'rhysd/git-messenger.vim', { 'on': 'GitMessenger' }
Plug 'tpope/vim-fugitive'
" Add Git signs to the sign column also provedides staging and diff moving
Plug 'airblade/vim-gitgutter'
" Source of snippets to use with coc-ultisnips
Plug 'honza/vim-snippets'
"
" Plugins to enable completitions with LanguageServerProtocol
" Load from source, since tags only happen upon release.
Plug 'neoclide/coc.nvim', {'branch': 'release'}
" If installing from source
"Plug 'neoclide/coc.nvim', {'do': 'yarn install --frozen-lockfile'}
"
" Install coc extensions. This won't keep updating them or install an specific
" version
let g:coc_global_extensions = ['coc-json', 'coc-python', 'coc-snippets', 'coc-phpls']
" Extra info:
" Installed watchman with yay to theoretically inform coc when files changes.
" This should fix behaviour

" On-demand loading
Plug 'scrooloose/nerdtree', { 'on':  'NERDTreeToggle' }

" Tool to generate tags async
" Tags shouldn't be needed when LSP server works as expected (Remove them in
" the future)
Plug 'jsfaint/gen_tags.vim', { 'on':  'GenCtags' }
" Plugin to have an async, lsp compatible TAGBAR
Plug 'liuchengxu/vista.vim'

Plug 'tpope/vim-surround'

" Plugin to work with Csv files
Plug 'mechatroner/rainbow_csv'

" Plugin to show init screen with useful info.
Plug 'mhinz/vim-startify'

" Plugin to add markdown md support
Plug 'iamcco/markdown-preview.nvim', { 'do': 'cd app & yarn install'  }

" Alpha state utility to seach through many different things in a popup window
"Plug 'liuchengxu/vim-clap'
Plug 'liuchengxu/vim-clap', { 'do': ':Clap install-binary!' }

Plug 'aouelete/sway-vim-syntax'

" Enable writing writing/reading files with privileges by running sudo
Plug 'lambdalisue/suda.vim'

" Initialize plugin system
call plug#end()
