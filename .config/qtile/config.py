import os
import re
import subprocess
from libqtile import hook, layout, qtile, bar, widget
from libqtile.config import Click, Drag, Group, Key, Match, Screen, Rule, ScratchPad, DropDown
from libqtile.lazy import lazy

from widgets.toggle_clock import ToggleClock
from widgets.pulse_volume import PulseVolumeCustom
from widgets.network_status import NetworkStatus


# --- Barre à utiliser ---
# Mettre à True pour utiliser Polybar, False pour la barre Qtile
use_polybar = True

# --- Variables ---
mod = "mod4"  # Touche Super
terminal = "terminator"
browser = "brave-browser"
editor = "geany"
file_manager = "thunar"
font_name = "FiraCode Nerd Font"
home = os.path.expanduser('~')
network_interfaces = {
    "wifi": "wlo1",
    "ethernet": "enp2s0",
}

# --- Couleurs (extraites de Polybar) ---
colors = {
    "background": "#2d353b",
    "background-alt": "#373B41",
    "foreground": "#d3c6aa",
    "foreground-alt": "#555555",
    "pink": "#FF0677",
    "blue": "#7fbbb3",
    "indigo": "#6C77BB",
    "red": "#e67e80",
    "amber": "#FBC02D",
    "slate": "#b3b1a3",
    "blue-gray": "#2d353b",
    "green": "#a7c080",
    "yellow": "#dbbc7f",
    "brown": "#AC8476",
    "lgrey": "#778185",
}


# --- Raccourcis Clavier (AZERTY) ---
keys = [
    # --- Gestion des fenêtres ---
    Key([mod], "Left", lazy.layout.left(), desc="Focus à gauche"),
    Key([mod], "Right", lazy.layout.right(), desc="Focus à droite"),
    Key([mod], "Down", lazy.layout.down(), desc="Focus en bas"),
    Key([mod], "Up", lazy.layout.up(), desc="Focus en haut"),
    Key([mod, "shift"], "Left", lazy.layout.shuffle_left(), desc="Déplacer à gauche"),
    Key([mod, "shift"], "Right", lazy.layout.shuffle_right(), desc="Déplacer à droite"),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down(), desc="Déplacer en bas"),
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up(), desc="Déplacer en haut"),
    Key([mod, "control"], "Left", lazy.layout.grow_left(), desc="Agrandir vers la gauche"),
    Key([mod, "control"], "Right", lazy.layout.grow_right(), desc="Agrandir vers la droite"),
    Key([mod, "control"], "Down", lazy.layout.grow_down(), desc="Agrandir vers le bas"),
    Key([mod, "control"], "Up", lazy.layout.grow_up(), desc="Agrandir vers le haut"),
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="Plein écran"),
    Key([mod, "shift"], "f", lazy.window.bring_to_front(), desc="Amener au premier plan"),
    Key([mod, "shift"], "space", lazy.window.toggle_floating(), desc="Basculer flottant"),
    Key([mod], "q", lazy.window.kill(), desc="Tuer la fenêtre"),

    # --- Gestion des layouts ---
    Key([mod], "Tab", lazy.next_layout(), desc="Changer de layout"),
    Key([mod], "r", lazy.layout.normalize(), desc="Réinitialiser la taille des fenêtres"),
    Key([mod], "s", lazy.layout.toggle_split(), desc="Basculer split/unsplit"),

    # --- Lanceurs d'applications ---
    Key([mod], "Return", lazy.spawn(terminal), desc="Lancer le terminal"),
    Key([mod], "space", lazy.spawn("rofi -show drun -modi drun,run,window,filebrowser -theme ~/.config/rofi/themes/config.rasi"), desc="Lancer Rofi"),
    Key([mod], "b", lazy.spawn(browser), desc="Lancer Brave"),
    Key([mod], "d", lazy.spawn("discord"), desc="Lancer Discord"),
    Key([mod], "g", lazy.spawn(editor), desc="Lancer Geany"),
    Key([mod], "t", lazy.spawn(file_manager), desc="Lancer Thunar"),
    Key([mod], "o", lazy.spawn("obsidian"), desc="Lancer Obsidian"),
    Key([mod], "v", lazy.spawn("code"), desc="Lancer VS Code"),
    Key([mod], "c", lazy.spawn(f"{home}/.cargo/bin/clipcat-menu"), desc="Afficher l'historique du presse-papiers"),
    Key([mod], "k", lazy.group["scratchpad"].dropdown_toggle("keepass"), desc="Afficher/masquer KeePass"),

    # --- Contrôles système ---
    Key([mod], "F1", lazy.spawn([f"{home}/.local/bin/volume_notify.sh", "toggle"]), desc="Muet"),
    Key([mod], "F2", lazy.spawn([f"{home}/.local/bin/volume_notify.sh", "dec"]), desc="Baisser le volume"),
    Key([mod], "F3", lazy.spawn([f"{home}/.local/bin/volume_notify.sh", "inc"]), desc="Augmenter le volume"),
    Key([mod], "F4", lazy.spawn(f"{home}/.local/bin/mic-toggle.sh"), desc="Activer/Désactiver le micro"),
    Key([mod], "F5", lazy.spawn([f"{home}/.local/bin/brightness_notify.sh", "dec"]), desc="Baisser la luminosité"),
    Key([mod], "F6", lazy.spawn([f"{home}/.local/bin/brightness_notify.sh", "inc"]), desc="Augmenter la luminosité"),
    Key([], "Print", lazy.spawn("flameshot gui"), desc="Capture d'écran"),
    Key([mod], "n", lazy.spawn(f"{home}/.local/bin/gammastep-toggle.sh"), desc="Basculer le mode nuit"),

    # --- Contrôles Qtile ---
    Key([mod, "shift"], "r", lazy.spawn(f"{home}/.local/bin/reload_environment.sh"), desc="Recharger l'environnement"),
    Key([mod, "shift"], "q", lazy.shutdown(), desc="Quitter Qtile"),
    Key([mod, "shift"], "c", lazy.spawn(f"{editor} {home}/.config/qtile/config.py")),
    Key([mod, "shift"], "p", lazy.spawn(f"{home}/.config/rofi/scripts/rofi-power-menu"), desc="Menu d'alimentation"),
]

# --- Espaces de travail (Workspaces) ---
workspace_definitions = [
    {"name": "web", "icon": " "},
    {"name": "dev", "icon": ""},
    {"name": "ros", "icon": "󰭆 "},
    {"name": "dir", "icon": " "},
    {"name": "txt", "icon": " "},
    {"name": "mus", "icon": " "},
    {"name": "dis", "icon": " "},
    {"name": "gen", "icon": " "},
]

# Table de correspondance pour les notifications Dunst (icône -> nom textuel)
icon_to_name_map = {ws["icon"]: ws["name"] for ws in workspace_definitions}

groups = [Group(name=ws["icon"], label=ws["icon"]) for ws in workspace_definitions]
groups.append(ScratchPad("scratchpad", [
    DropDown("keepass", "flatpak run --command=bottles-cli com.usebottles.bottles run -b KeePass2 -p KeePass",
             width=0.6, height=0.7, x=0.3, y=0.15, opacity=0.95, on_focus_lost_hide=False),
]))

azerty_keys = ["ampersand", "eacute", "quotedbl", "apostrophe", "parenleft", "minus", "egrave", "underscore"]
for i, ws in enumerate(workspace_definitions):
    key_name = azerty_keys[i]
    icon_name = ws["icon"]
    keys.extend([
        Key([mod], key_name, lazy.group[icon_name].toscreen(), desc=f"Aller à l'espace {ws['name']}"),
        Key([mod, "shift"], key_name, lazy.window.togroup(icon_name), desc=f"Déplacer la fenêtre vers {ws['name']}"),
    ])

# --- Layouts ---
layout_theme = {
    "border_width": 2, "margin": [5, 10, 5, 10],
    "border_focus": colors["blue"], "border_normal": "#163a48"
}
layouts = [layout.Columns(**layout_theme), layout.Max(margin=0, border_width=0)]

# --- Réglages par défaut pour les widgets ---
widget_defaults = dict(font=font_name, fontsize=12, padding=3, background=colors["background"])
extension_defaults = widget_defaults.copy()

# --- Barre Qtile ---
def init_widget_list():
    return [
        widget.GroupBox(
            font=font_name, fontsize=16, margin_y=3, margin_x=0, padding_y=5, padding_x=3,
            borderwidth=3, active=colors["foreground"], inactive=colors["foreground-alt"],
            rounded=False, highlight_method="block",
            this_current_screen_border=colors["pink"],
            this_screen_border=colors["pink"],
            other_current_screen_border=colors["background"],
            other_screen_border=colors["background"],
            background=colors["background-alt"],
        ),
        widget.Sep(linewidth=0, padding=10),
        widget.WindowName(foreground=colors["foreground"], max_chars=50),
        widget.Spacer(),
        ToggleClock(
            foreground=colors["background"], background=colors["indigo"],
            format="󰥔 %I:%M:%S %p",
            long_format="󰃭 %A, %d %B %Y",
            padding=5,
            mouse_callbacks={'Button3': lazy.spawn(f'/usr/local/bin/eww -c {home}/.config/eww open --toggle date')}
        ),
        widget.TextBox(
            text="", foreground=colors["foreground"], padding=10,
            mouse_callbacks={'Button1': lazy.spawn('dunstctl history-pop')}
        ),
        widget.Sep(linewidth=0, padding=5),
        widget.Pomodoro(
            color_active=colors["green"], color_break=colors["yellow"], color_inactive=colors["red"],
            prefix_inactive='󱎫', length_pomodori=25, length_short_break=5, length_long_break=15,
            num_pomodori=4, padding=5
        ),
        widget.Spacer(),
        NetworkStatus(
            interface=network_interfaces["wifi"],
            interface_type='wireless',
            home=home,
            foreground=colors["blue-gray"],
            background_connected=colors["green"],
            background_disconnected=colors["lgrey"],
        ),
        NetworkStatus(
            interface=network_interfaces["ethernet"],
            interface_type='wired',
            home=home,
            foreground=colors["blue-gray"],
            background_connected=colors["green"],
            background_disconnected=colors["lgrey"],
        ),
        PulseVolumeCustom(
            max_volume=153,
            step=5,
            foreground=colors["blue-gray"],
            background_unmuted=colors["amber"],
            background_muted=colors["brown"],
        ),
        widget.ThermalSensor(
            foreground=colors["blue-gray"], background=colors["blue"],
            tag_sensor="Tctl", fmt=' {}', padding=5
        ),
        widget.CPU(
            format=' {load_percent}%', foreground=colors["blue-gray"],
            background=colors["slate"], padding=5
        ),
        widget.Memory(
            fmt='▓▓▓ {}', format='{MemPercent}%', foreground=colors["blue-gray"],
            background=colors["slate"], padding=5
        ),
        widget.Battery(
            battery="BAT1",
            charge_char='',
            discharge_char='',
            format='{char} {percent:2.0%}',
            show_short_text=True,
            full_short_text='Charged ',
            foreground=colors["blue-gray"],
            background=colors["blue"],
            charging_background=colors["yellow"],
            padding=5,
            low_foreground=colors["red"]
        ),
        widget.Sep(linewidth=0, padding=10),
        widget.Systray(icon_size=20, padding=5),
        widget.Sep(linewidth=0, padding=10),
    ]

# --- Écrans ---
def _write_bar_state_to_file():
    """Écrit l'état de la barre choisie dans un fichier temporaire."""
    state_file = "/tmp/qtile_bar_state"
    bar_to_use = "polybar" if use_polybar else "qtile"
    with open(state_file, "w") as f:
        f.write(bar_to_use)

if use_polybar:
    # La barre est gérée par Polybar, on laisse juste un espace vide.
    # La taille du gap (30px) doit correspondre à la hauteur de votre Polybar.
    screens = [Screen(top=bar.Gap(40))]
else:
    # Utilise la barre intégrée de Qtile
    screens = [Screen(top=bar.Bar(init_widget_list(), 30, opacity=0.95, margin=[5, 15, 0, 15]))]

# Écrire l'état actuel de la barre pour que le script de rechargement puisse le lire
_write_bar_state_to_file()

# --- Souris ---
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

# --- Hooks ---
@hook.subscribe.setgroup
def show_workspace_notification():
    """Affiche une notification avec le nom textuel de l'espace de travail."""
    if qtile.current_group:
        icon_name = qtile.current_group.name
        # Utilise la table de correspondance pour trouver le nom textuel
        text_name = icon_to_name_map.get(icon_name, icon_name)
        subprocess.run(["dunstify", "-t", "500", "-r", "9991", text_name])

# --- Démarrage automatique (Autostart) ---
@hook.subscribe.startup_once
def autostart():
    """Lancement des applications au démarrage de Qtile."""
    if use_polybar:
        subprocess.Popen([f"{home}/.config/polybar/launch.sh"])
    subprocess.Popen(['picom'])
    subprocess.Popen(['xsettingsd', '-c', f'{home}/.config/xsettingsd/xsettingsd.conf'])
    subprocess.Popen([f'{home}/.cargo/bin/clipcatd'])
    subprocess.Popen(['dunst'])
    subprocess.Popen(['eww', 'daemon', '-c', f'{home}/.config/eww'])
    subprocess.Popen(['caffeine-indicator'])

# --- Autres réglages ---
dgroups_key_binder = None
# Pré-compiler les expressions régulières pour une meilleure performance
app_rules_definitions = {
    "web": (re.compile(r"^(Brave-browser)$"), workspace_definitions[0]["icon"]),
    "dev": (re.compile(r"^(Code)$"), workspace_definitions[1]["icon"]),
    "dir": (re.compile(r"^(Thunar)$"), workspace_definitions[3]["icon"]),
    "txt": (re.compile(r"^(Geany|obsidian)$"), workspace_definitions[4]["icon"]),
    "mus": (re.compile(r"^(Spotube)$"), workspace_definitions[5]["icon"]),
    "dis": (re.compile(r"^(discord)$"), workspace_definitions[6]["icon"]),
    "gen": (re.compile(r"^(steamwebhelper|Lutris|heroic)$"), workspace_definitions[7]["icon"]),
}
dgroups_app_rules = [
    Rule(Match(wm_class=rule), group=icon) for rule, icon in app_rules_definitions.values()
]
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"), Match(wm_class="makebranch"),
        Match(wm_class="maketag"), Match(wm_class="ssh-askpass"),
        Match(title="branchdialog"), Match(title="pinentry"),
    ],
    **layout_theme
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wmname = "LG3D"
