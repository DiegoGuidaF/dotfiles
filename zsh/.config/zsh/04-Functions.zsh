# All bash functions declared should be here

# Check if a command exists
command_exists () {
    command -v $1 &> /dev/null
}

# Extract stuff from any filetype
extract() {
  if [ -z ${1} ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Usage: extract <archive> [directory]"
    echo "Example: extract presentation.zip."
    echo "Valid archive types are:"
    echo "tar.bz2, tar.gz, tar.xz, tar, bz2, gz, tbz2,"
    echo "tbz, tgz, lzo, rar, zip, 7z, xz, txz, lzma and tlz"
  else
    case "$1" in
      *.tar.bz2|*.tbz2|*.tbz)         tar xvjf "$1" ;;
      *.tgz)                          tar zxvf "$1" ;;
      *.tar.gz)                       tar xvzf "$1" ;;
      *.tar.xz)                       tar xvJf "$1" ;;
      *.tar)                          tar xvf "$1" ;;
      *.rar)                          7z x "$1" ;;
      *.zip)                          unzip "$1" ;;
      *.7z)                           7z x "$1" ;;
      *.lzo)                          lzop -d  "$1" ;;
      *.gz)                           gunzip "$1" ;;
      *.bz2)                          bunzip2 "$1" ;;
      *.Z)                            uncompress "$1" ;;
      *.xz|*.txz|*.lzma|*.tlz)        xz -d "$1" ;;
      *) echo "Sorry, '$1' could not be decompressed." ;;
    esac
  fi
}
