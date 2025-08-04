#!/bin/bash

# Bascule gammastep et envoie une notification

if pgrep -x "gammastep" > /dev/null
then
    # Si gammastep est en cours, on l'arrête
    killall gammastep
    dunstify -a "gammastep" -u low -i "display-brightness-symbolic" "Gammastep : Désactivé"
else
    # Sinon, on le démarre en arrière-plan
    gammastep &
    dunstify -a "gammastep" -u low -i "display-brightness-symbolic" "Gammastep : Activé"
fi
