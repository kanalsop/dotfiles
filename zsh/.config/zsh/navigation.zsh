# Initialize after OS-specific PATH setup and before local overrides.
if command -v fzf >/dev/null 2>&1; then
  # Shared find expression: prune excluded directories and omit Finder metadata.
  _fzf_find_filter='\( -type d \( -name .git -o -name node_modules -o -name .venv \) -prune \) -o \( ! -name .DS_Store'
  export FZF_DEFAULT_COMMAND="find -L . $_fzf_find_filter -type f -print \\) 2>/dev/null | sed 's|^./||'"
  export FZF_CTRL_T_COMMAND="find -L . $_fzf_find_filter \\( -type f -o -type d \\) ! -path . -print \\) 2>/dev/null | sed 's|^./||'"
  export FZF_ALT_C_COMMAND="find -L . $_fzf_find_filter -type d ! -path . -print \\) 2>/dev/null | sed 's|^./||'"
  unset _fzf_find_filter

  if _fzf_init="$(fzf --zsh 2>/dev/null)"; then
    eval "$_fzf_init"
  else
    # Ubuntu packages with fzf < 0.48.0 ship separate shell scripts.
    [[ -r /usr/share/doc/fzf/examples/completion.zsh ]] && source /usr/share/doc/fzf/examples/completion.zsh
    [[ -r /usr/share/doc/fzf/examples/key-bindings.zsh ]] && source /usr/share/doc/fzf/examples/key-bindings.zsh
  fi
  unset _fzf_init

  # Apply the same exclusions to ** completion, including roots with spaces.
  _fzf_compgen_path() {
    ( builtin cd -q -- "$1" && eval "$FZF_CTRL_T_COMMAND" ) |
      while IFS= read -r item; do print -r -- "${1%/}/$item"; done
  }
  _fzf_compgen_dir() {
    ( builtin cd -q -- "$1" && eval "$FZF_ALT_C_COMMAND" ) |
      while IFS= read -r item; do print -r -- "${1%/}/$item"; done
  }
fi

if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi
