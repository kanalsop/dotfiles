# gemini cli
[[ -d "/opt/homebrew/opt/node@22/bin" ]] && export PATH="/opt/homebrew/opt/node@22/bin:$PATH"

# Homebrew user binaries
[[ -d "/opt/homebrew/bin" ]] && export PATH="/opt/homebrew/bin:$PATH"

# User-local binaries
[[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"


# nvm
export NVM_DIR="$HOME/.config/nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# openjdk
export PATH="/opt/homebrew/opt/openjdk/bin:$PATH"
