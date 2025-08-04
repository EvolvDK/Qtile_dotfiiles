# Qtile dotfiles

These are my dotfiles for Qtile, installed on Debian 12.

My Linux stack is composed of:
+ WM: Qtile
+ Display protocol: X11
+ Display manager: lightdm
+ Compositor: picom
+ Lock manager: betterlockscreen

+ Launcher: rofi
+ Notifications: dunst
+ Bar: polybar
+ Widgets: eww
+ Night mode app: gammastep

+ Clipboard manager: clipcat
+ GUI File manager: Thunar
+ Music controller: playerctl
+ Terminal: Tilix/Terminator
+ Screenshots: Flameshot
+ Browser: brave
+ Documents: geany/obsidian

The user can choose between Qtile's built-in bar and Polybar bar.
Polybar launches six bars that display:
 1. workspaces
 2. current window
 3. system tray
 4. date/clock + notification + pomodoro
 5. music controller
 6. system modules
 
It is less memory efficient than launching a single Polybar bar, but it renders well like that.

You might need to change the WiFi/Ethernet interface, as well as the battery supply connection in Qtile/Polybar configs.

Check ~/.config/qtile/config.py for keybindings.
