# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi
# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:/usr/local/bin:$PATH

# Path to your oh-my-zsh installation.
ZSH=/usr/share/oh-my-zsh/
DEFAULT_USER=`whoami`
# Set name of the theme to load. Optionally, if you set this to "random"
# it'll load a random theme each time that oh-my-zsh is loaded.
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="powerlevel10k/powerlevel10k"
#ZSH_THEME="agnoster"

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion. Case
# sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment the following line to disable bi-weekly auto-update checks.
# DISABLE_AUTO_UPDATE="true"

# Do not warn on oh-my-zsh update
DISABLE_UPDATE_PROMPT=true

# Uncomment the following line to change how often to auto-update (in days).
# export UPDATE_ZSH_DAYS=13

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# The optional three formats: "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
HIST_STAMPS="mm/dd/yyyy"
# History file location (oh-my-zsh default)
HISTFILE="$HOME/.zsh_history"
# Max stored history of a session
HISTSIZE=50000
# History saved in the history file
SAVEHIST=20000

# Would you like to use another custom folder than $ZSH/custom?
ZSH_CUSTOM=$HOME/.config/zsh

# Which plugins would you like to load? (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
    git
    docker
    docker-compose
    colored-man-pages
    colorize
    bgnotify
)


# User configuration

# Disable terminal pausing (XON/XOFF flow control)
stty -ixon

if [ -n "$DESKTOP_SESSION" ];then
# Init keyring
    gnome-keyring-daemon --start --components=gpg,pkcs11,secrets,ssh
    dbus-update-activation-environment --systemd $DISPLAY
    export SSH_AUTH_SOCK
fi
# export MANPATH="/usr/local/man:$MANPATH"

# Set language environment
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"

export EDITOR="nvim"
export VISUAL="nvim"

export TERM="xterm-256color"

# Set env variables for wayland if running it
if [ -n $WAYLAND_DISPLAY ]; then
    export XDG_SESSION_TYPE="wayland"
    export XDG_CURRENT_DESKTOP="sway"

    # Enable usage of wayland for QT
    export QT_QPA_PLATFORM="wayland-egl"
    export QT_WAYLAND_DISABLE_WINDOWDECORATION="1"
    # To use your monitor's DPI instead of the default of 96 DPI:
    export QT_WAYLAND_FORCE_DPI=physical

    export _JAVA_AWT_WM_NONREPARENTING=1

    # Force firefox to enable firefox
    export MOZ_ENABLE_WAYLAND=1

fi

# Skip compresion of makepkg for AUR packages, this saves
# A LOT of time but cache will be bigger.
export PKGEXT='.pkg.tar'

export PIP

#Init the ssh-keys manager keychain and export the variables
#eval $(keychain --eval --quiet ws_bitbucket ws_loadsensing --confhost)

ZSH_CACHE_DIR=$HOME/.oh-my-zsh-cache
if [[ ! -d $ZSH_CACHE_DIR ]]; then
  mkdir $ZSH_CACHE_DIR
fi

source $ZSH/oh-my-zsh.sh
# Add custom completions
fpath=(~/.config/zsh/completions/ $fpath)

# Ccache compilation folder
export PATH="/usr/lib/ccache/bin/:$PATH"
# Add pip utilities installed only to user. i.e: pip install --user <package>
export PATH="/home/diego/.local/bin/:$PATH"

export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh
