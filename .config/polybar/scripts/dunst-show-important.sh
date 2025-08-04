#!/bin/bash

# Script pour afficher la notification la plus importante de l'historique de dunst.
#
# Ce script utilise `jq` pour analyser la sortie JSON de `dunstctl history`.
#
# Logique de priorité :
# 1. La dernière notification avec une urgence CRITICAL.
# 2. Si aucune, la dernière notification d'une application importante.
# 3. En dernier recours, la toute dernière notification de l'historique.
#
# Une fois la notification trouvée, `dunstctl history-pop` est utilisé pour l'afficher.

# Vérifie si dunst est en pause. Si c'est le cas, ne rien faire.
if dunstctl is-paused | grep -q "true"; then
    exit 0
fi

# Récupérer l'historique des notifications
history=$(dunstctl history)

# Si l'historique est vide, ne rien faire.
# On vérifie s'il y a au moins un élément dans le tableau aplani.
if [ -z "$(echo "$history" | jq '.data | flatten | .[0]')" ]; then
    exit 0
fi

# --- Priorité 1: Dernière notification critique ---
# On sélectionne les notifications critiques, on prend la dernière et on extrait son ID.
# `// empty` assure une sortie vide si aucun résultat n'est trouvé (au lieu de "null").
target_id=$(echo "$history" | jq -r '
    .data | flatten | map(select(.urgency.data == "CRITICAL")) | last | .id.data // empty
')

# --- Priorité 2: Dernière notification d'une application importante ---
if [ -z "$target_id" ]; then
    # Définition de la regex pour les applications importantes (insensible à la casse)
    important_apps_regex="^(discord|brave|firefox|thunderbird|telegram|slack|teams)$"
    target_id=$(echo "$history" | jq -r --arg regex "$important_apps_regex" '
        .data | flatten | map(select(.appname.data | test($regex; "i"))) | last | .id.data // empty
    ')
fi

# --- Priorité 3: La toute dernière notification (fallback) ---
if [ -z "$target_id" ]; then
    target_id=$(echo "$history" | jq -r '
        .data | flatten | last | .id.data // empty
    ')
fi

# --- Action ---
# Si un ID a été identifié, on utilise `dunstctl history-pop` pour afficher la notification.
if [ -n "$target_id" ]; then
    dunstctl history-pop "$target_id"
fi
