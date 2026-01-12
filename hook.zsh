# 1. FETCH SUGGESTION
_ai_autosuggest_fetch() {
    # Only fetch if buffer is longer than 1 char to save resources
    if [[ ${#BUFFER} -ge 1 ]]; then
        # Send Buffer + CWD to Python
        # Timeout 50ms to prevent lag
        local SUGGESTION=$(curl -s --max-time 0.05 -X POST \
            -H "Content-Type: application/json" \
            -d "{\"buffer\": \"$BUFFER\", \"cwd\": \"$PWD\"}" \
            http://127.0.0.1:5005/predict | jq -r '.suggestion')

        if [[ "$SUGGESTION" != "null" && -n "$SUGGESTION" ]]; then
            # Display ghost text (Gray color)
            POSTDISPLAY=$SUGGESTION
        else
            POSTDISPLAY=""
        fi
    else
        POSTDISPLAY=""
    fi
}

# 2. SAVE HISTORY (On Enter)
_ai_save_history() {
    # Send executed command to Python to save/train
    # Runs in background (&!) so it doesn't slow down the terminal
    curl -s -o /dev/null -X POST \
        -H "Content-Type: application/json" \
        -d "{\"cmd\": \"$1\"}" \
        http://127.0.0.1:5005/train &!
}

# 3. ACCEPT SUGGESTION (On Tab)
_ai_accept_suggestion() {
    if [[ -n "$POSTDISPLAY" ]]; then
        BUFFER="$BUFFER$POSTDISPLAY"
        POSTDISPLAY=""
        # Move cursor to end of line
        CURSOR=${#BUFFER}
    else
        # If no suggestion, perform normal tab completion
        zle expand-or-complete
    fi
}

# --- BINDINGS ---

# Define widgets
zle -N _ai_autosuggest_fetch
zle -N _ai_accept_suggestion

# Hook 'fetch' to every key press (Self Insert)
# Note: We wrap self-insert to trigger fetch afterwards
_ai_self_insert() {
    zle .self-insert
    _ai_autosuggest_fetch
}
zle -N self-insert _ai_self_insert

# Hook 'save' to command execution
autoload -Uz add-zsh-hook
add-zsh-hook preexec _ai_save_history

# Bind Tab key to accept suggestion
bindkey '^I' _ai_accept_suggestion