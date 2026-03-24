export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"

# Some SSH targets do not ship Ghostty terminfo yet.
# Fall back so interactive redraw and backspace behave normally.
if [[ -n "${SSH_CONNECTION:-}" ]] && [[ -n "${TERM:-}" ]]; then
  if ! infocmp "$TERM" >/dev/null 2>&1; then
    export TERM="xterm-256color"
  fi
fi

case "$(uname -s)" in
  Darwin) ZSH_PLATFORM="macos" ;;
  Linux)  ZSH_PLATFORM="linux" ;;
  *)      ZSH_PLATFORM="other" ;;
esac

[[ -f "$XDG_CONFIG_HOME/zsh/common.zsh" ]] && source "$XDG_CONFIG_HOME/zsh/common.zsh"
[[ -f "$XDG_CONFIG_HOME/zsh/${ZSH_PLATFORM}.zsh" ]] && source "$XDG_CONFIG_HOME/zsh/${ZSH_PLATFORM}.zsh"

# Git 管理しないホスト固有差分
[[ -f "$HOME/.zshrc.local" ]] && source "$HOME/.zshrc.local"
