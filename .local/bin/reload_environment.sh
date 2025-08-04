#!/bin/bash

# D'abord, recharger la config Qtile pour que le fichier d'état soit à jour
$HOME/.local/bin/qtile cmd-obj -o cmd -f reload_config
sleep 0.2 # Laisser le temps à Qtile de recharger et d'écrire le fichier

FAILED_SERVICES=""
STATE_FILE="/tmp/qtile_bar_state"

# --- Gérer la barre (Polybar ou Qtile) ---
if [ -f "$STATE_FILE" ]; then
    DESIRED_BAR=$(cat "$STATE_FILE")
    if [ "$DESIRED_BAR" = "polybar" ]; then
        # Si Polybar doit être utilisé
        if pgrep -x "polybar" > /dev/null; then
            # S'il est déjà lancé, on le redémarre
            polybar-msg cmd restart
        else
            # Sinon, on le lance
            "$HOME/.config/polybar/launch.sh"
        fi
    else
        # Si la barre Qtile doit être utilisée, on s'assure que Polybar est arrêté
        polybar-msg cmd quit
    fi
fi

# --- Recharger Picom ---
killall -q picom
sleep 0.2 # Laisser le temps au processus de se terminer
/usr/local/bin/picom &
sleep 0.5 # Laisser le temps au nouveau processus de démarrer
if ! pgrep -x "picom" > /dev/null; then
    FAILED_SERVICES="$FAILED_SERVICES Picom"
fi

# --- Recharger xsettingsd ---
killall -q xsettingsd
xsettingsd -c ~/.config/xsettingsd/xsettingsd.conf &
sleep 0.2 # Laisser le temps au nouveau processus de démarrer
if ! pgrep -x "xsettingsd" > /dev/null; then
    FAILED_SERVICES="$FAILED_SERVICES xsettingsd"
fi

# --- Recharger Dunst ---
if ! dunstctl reload >/dev/null 2>&1; then
    FAILED_SERVICES="$FAILED_SERVICES Dunst"
fi

# --- Recharger eww ---
if ! eww reload -c ~/.config/eww >/dev/null 2>&1; then
    FAILED_SERVICES="$FAILED_SERVICES eww"
fi

# Donner à Dunst un instant pour se recharger avant de notifier
sleep 0.5

# --- Notification finale ---
if [ -z "$FAILED_SERVICES" ]; then
    dunstify -a "Qtile" -u low "Environment reloaded!"
else
    # Formater la liste des services en échec
    FAILED_SERVICES=$(echo "$FAILED_SERVICES" | sed -e 's/^ *//' -e 's/ /, /g')
    dunstify -a "Qtile" -u critical "Échec du rechargement : $FAILED_SERVICES"
fi
