# Keep PATH entries unique while adding Linux-specific executables.
typeset -U path PATH

# apt installs bubblewrap as /usr/bin/bwrap. Codex resolves bwrap from PATH.
path=(/usr/bin $path)

# Codex CLI and other user-local commands.
[[ -d "$HOME/.local/bin" ]] && path=("$HOME/.local/bin" $path)
