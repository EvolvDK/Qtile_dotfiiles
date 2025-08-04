#!/bin/bash

# Basculer l'état muet de la source par défaut
pactl set-source-mute @DEFAULT_SOURCE@ toggle

# Vérifier le nouvel état et envoyer une notification
if pactl get-source-mute @DEFAULT_SOURCE@ | grep -q 'yes'; then
    # Le micro est coupé
    dunstify -a "mic-toggle" -u low "   Microphone : Coupé" -h string:x-dunst-stack-tag:mic_status
else
    # Le micro est activé
    dunstify -a "mic-toggle" -u low "   Microphone : Activé" -h string:x-dunst-stack-tag:mic_status
fi
