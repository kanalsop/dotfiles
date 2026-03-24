# =========================
# Completion
# =========================

[[ -d "$XDG_CONFIG_HOME/zsh/completions" ]] && fpath=("$XDG_CONFIG_HOME/zsh/completions" $fpath)

# Homebrew completions
if command -v brew >/dev/null 2>&1; then
  fpath=("$(brew --prefix)/share/zsh-completions" $fpath)
  fpath=("$(brew --prefix)/share/zsh/site-functions" $fpath)
fi

# Docker CLI completions
[[ -d "$HOME/.docker/completions" ]] && fpath=("$HOME/.docker/completions" $fpath)

autoload -Uz compinit
mkdir -p "${XDG_CACHE_HOME:-$HOME/.cache}/zsh"
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/.zcompdump"

# Accept both DEL and Ctrl-H as backspace.
bindkey '^?' backward-delete-char
bindkey '^H' backward-delete-char

# =========================
# Plugins
# =========================

# zsh-autosuggestions
for file in \
  "$HOME/.zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" \
  "/usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh" \
  "/usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh" \
  "/opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
do
  if [[ -f "$file" ]]; then
    source "$file"
    break
  fi
done

# =========================
# Aliases
# =========================

# uv alias
if command -v uv >/dev/null 2>&1; then
  alias upy='uv run'
  alias upa='uv run --active'
fi

# eza settings
if command -v eza >/dev/null 2>&1; then
  alias ls="eza --icons --git --no-user"
  alias ll="eza -l --icons --git --no-user"
  alias la="eza -la --icons --git --no-user"
  alias tree="eza --tree --icons"
fi

# python venv activation alias
alias srv='source .venv/bin/activate'

# =========================
# Functions
# =========================

upm() {
  if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    cat <<'EOF'
upm — run Python module by specifying file path with tab completion.

Usage:
  upm path/to/module.py [args...]
  upm --help       Show this help

Example:
  upm src/analyzer/analyze_results.py -h
EOF
    return 0
  fi

  local target="$1"
  if [[ -z "$target" ]]; then
    echo "upm: no module path given" >&2
    return 2
  fi

  shift

  if [[ "$target" == *.py ]]; then
    target="${target%.py}"
    target="${target#./}"
    target="${target//\//.}"
  fi

  uv run -m "$target" "$@"
}

# =========================
# Prompt
# =========================

if command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi
