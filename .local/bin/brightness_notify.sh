#!/bin/bash

# Script pour ajuster la luminosité et afficher une notification.

# Utilise le même périphérique que dans la config qtile
DEVICE="amdgpu_bl1"

send_notification() {
    # Récupère le pourcentage de luminosité actuel
    percentage=$(brightnessctl -d "$DEVICE" | grep -o "[0-9]*%" | sed 's/%//')

    # Envoie la notification avec une barre de progression et une icône
    dunstify "Brightness: ${percentage}%" \
        -a "changeBrightness" \
        -u low \
        -i "display-brightness-symbolic" \
        -h "int:value:$percentage" \
        -h "string:x-dunst-stack-tag:brightness"
}

# Change la luminosité en fonction de l'argument
case $1 in
    inc)
        brightnessctl -d "$DEVICE" set +5%
        send_notification
        ;;
    dec)
        brightnessctl -d "$DEVICE" set 5%-
        send_notification
        ;;
    *)
        echo "Usage: $0 {inc|dec}"
        exit 1
        ;;
esac
