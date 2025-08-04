#!/bin/bash

# Fonction pour envoyer la notification
send_notification() {
    volume=$(pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\d+%' | head -n1 | sed 's/%//')
    mute_status=$(pactl get-sink-mute @DEFAULT_SINK@ | grep -o 'yes')

    if [[ "$mute_status" == "yes" ]]; then
        icon="audio-volume-muted-symbolic"
    elif [[ "$volume" -eq 0 ]]; then
        icon="audio-volume-muted-symbolic"
    elif [[ "$volume" -lt 36 ]]; then
        icon="audio-volume-low-symbolic"
    elif [[ "$volume" -lt 66 ]]; then
        icon="audio-volume-medium-symbolic"
    else
        icon="audio-volume-high-symbolic"
    fi

    dunstify -a "changeVolume" -u low -i "$icon" -h string:x-dunst-stack-tag:volume "Volume: ${volume}%"
}

# Gérer les arguments
case "$1" in
    inc)
        pactl set-sink-volume @DEFAULT_SINK@ +5%
        # Si le volume a dépassé 100% après l'augmentation, le ramener à 100%
        volume=$(pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\d+%' | head -n1 | sed 's/%//')
        if [ "$volume" -gt 153 ]; then
            pactl set-sink-volume @DEFAULT_SINK@ 153%
        fi
        send_notification
        ;;
    dec)
        pactl set-sink-volume @DEFAULT_SINK@ -5%
        send_notification
        ;;
    toggle)
        pactl set-sink-mute @DEFAULT_SINK@ toggle
        mute_status=$(pactl get-sink-mute @DEFAULT_SINK@ | grep -o 'yes')
        if [[ "$mute_status" == "yes" ]]; then
            dunstify -a "changeVolume" -u low -i "audio-volume-muted-symbolic" -h string:x-dunst-stack-tag:volume "Volume: mute"
        else
            volume=$(pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\d+%' | head -n1 | sed 's/%//')
			if [[ "$volume" -eq 0 ]]; then
				icon="audio-volume-muted-symbolic"
			elif [[ "$volume" -lt 36 ]]; then
				icon="audio-volume-low-symbolic"
			elif [[ "$volume" -lt 66 ]]; then
				icon="audio-volume-medium-symbolic"
			else
				icon="audio-volume-high-symbolic"
			fi
            dunstify -a "changeVolume" -u low -i "$icon" -h string:x-dunst-stack-tag:volume "Volume: unmute"
        fi
        ;;
esac
