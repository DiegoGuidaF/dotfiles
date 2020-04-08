# Personal Dotfiles
Repository with my dotfiles and configurations. This repo is used to:

* Easily setup my environment in new machines
* Keep track of changes
* Backup my configurations

### Usage
Intended to be used via [Stow](https://www.gnu.org/software/stow/manual/stow.html), hence why each package is autocontained in a folder of its own.
For example, installing only kitty (terminal) config:
```
$ stow -vRt $HOME bin
```

Also the python script __setup.py__ is provided which helps on installing and configuring the packages in a new ArchLinux install.
For example:
```
$ ./setup.py zsh kitty sway nvim
```
This will install the required packages (as indicated in the dependencies.yml file) and then place the corresponding configs.

# Current setup
Main utilities:

* Window manager: __Sway__ tiling window manager (replacement for i3 using wayland).
* IDE: __neovim__ as IDE with code completion using CoC (as well as a few other plugins).
* Status bar: __Waybar__, similar to polybar but for Sway.

Theme is centered around __Gruvbox__ template.
