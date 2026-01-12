# 1. FETCH SUGGESTION
_ai_autosuggest_fetch() {
    # limit check: minimal buffer length
    if [[ ${#BUFFER} -ge 2 ]]; then
        
        # JSON Safe construction
        # We use a subshell for jq to ensure we don't break if jq is missing
        if ! command -v jq &> /dev/null; then return; fi
        
        local JSON_PAYLOAD=$(jq -n -c \
            --arg buf "$BUFFER" \
            --arg cwd "$PWD" \
            '{buffer: $buf, cwd: $cwd}')

        # 1. Capture response
        # --max-time is vital here. 
        local RESPONSE=$(curl -s --max-time 0.1 -X POST \
            -H "Content-Type: application/json" \
            -d "$JSON_PAYLOAD" \
            http://127.0.0.1:5005/predict 2>/dev/null)

        # 2. Extract suggestion
        local SUGGESTION=""
        if [[ -n "$RESPONSE" ]]; then
             SUGGESTION=$(echo "$RESPONSE" | jq -r '.suggestion // empty' 2>/dev/null)
        fi

        if [[ -n "$SUGGESTION" ]]; then
            # Display ghost text (Zsh syntax highlighting usually handles the gray color)
            POSTDISPLAY="$SUGGESTION"
        else
            POSTDISPLAY=""
        fi
    else
        POSTDISPLAY=""
    fi
}

# 2. SAVE HISTORY (On Enter)
_ai_save_history() {
    # Sanitize inputs for history saving too
    local CMD="$1"
    local JSON_PAYLOAD=$(jq -n -c \
            --arg cmd "$CMD" \
            --arg cwd "$PWD" \
            '{cmd: $cmd, cwd: $cwd}')

    curl -s -o /dev/null -X POST \
        -H "Content-Type: application/json" \
        -d "$JSON_PAYLOAD" \
        http://127.0.0.1:5005/train &!
}

# 3. ACCEPT SUGGESTION
_ai_accept_suggestion() {
    if [[ -n "$POSTDISPLAY" ]]; then
        BUFFER="$BUFFER$POSTDISPLAY"
        POSTDISPLAY=""
        CURSOR=${#BUFFER}
    else
        # Fallback to standard movement if no suggestion
        zle forward-char
    fi
}

# --- BINDINGS ---

zle -N _ai_autosuggest_fetch
zle -N _ai_accept_suggestion

_ai_self_insert() {
    zle .self-insert
    _ai_autosuggest_fetch
}
zle -N self-insert _ai_self_insert

autoload -Uz add-zsh-hook
add-zsh-hook preexec _ai_save_history

# Bind Right Arrow to accept (standard behavior for autosuggest)
bindkey '^[[C' _ai_accept_suggestion