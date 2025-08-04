#!/bin/bash

# Terminer les instances de barres déjà lancées
polybar-msg cmd quit

# Attendre que les processus soient terminés
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done

# Lancer Polybar sur chaque moniteur
if type "xrandr"; then
  for m in $(xrandr --query | grep " connected" | cut -d" " -f1); do
    echo "---" | tee -a "/tmp/polybar-$m-bar1.log" "/tmp/polybar-$m-bar2.log" "/tmp/polybar-$m-bar3.log" "/tmp/polybar-$m-bar4.log" "/tmp/polybar-$m-bar5.log" "/tmp/polybar-$m-systray.log"
    MONITOR=$m polybar --reload bar1 2>&1 | tee -a "/tmp/polybar-$m-bar1.log" & disown
    MONITOR=$m polybar --reload bar2 2>&1 | tee -a "/tmp/polybar-$m-bar2.log" & disown
    MONITOR=$m polybar --reload bar3 2>&1 | tee -a "/tmp/polybar-$m-bar3.log" & disown
    MONITOR=$m polybar --reload bar4 2>&1 | tee -a "/tmp/polybar-$m-bar4.log" & disown
    MONITOR=$m polybar --reload bar5 2>&1 | tee -a "/tmp/polybar-$m-bar5.log" & disown
    MONITOR=$m polybar --reload systray 2>&1 | tee -a "/tmp/polybar-$m-systray.log" & disown
  done
else
  echo "---" | tee -a "/tmp/polybar-bar1.log" "/tmp/polybar-bar2.log" "/tmp/polybar-bar3.log" "/tmp/polybar-bar4.log" "/tmp/polybar-bar5.log" "/tmp/polybar-systray.log"
  polybar --reload bar1 2>&1 | tee -a "/tmp/polybar-bar1.log" & disown
  polybar --reload bar2 2>&1 | tee -a "/tmp/polybar-bar2.log" & disown
  polybar --reload bar3 2>&1 | tee -a "/tmp/polybar-bar3.log" & disown
  polybar --reload bar4 2>&1 | tee -a "/tmp/polybar-bar4.log" & disown
  polybar --reload bar5 2>&1 | tee -a "/tmp/polybar-bar5.log" & disown
  polybar --reload systray 2>&1 | tee -a "/tmp/polybar-systray.log" & disown
fi

echo "Bars launched..."
