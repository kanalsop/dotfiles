# dotfiles

このリポジトリは、macOS のローカル端末環境と SSH 接続先の Ubuntu 環境で、できるだけ同じシェル操作感を再現するための dotfiles を管理するものです。

主に `zsh`、`starship`、`eza`、`uv`、補完設定、alias / function 類を Git で一元管理し、OS 依存の差分は分離したまま共通化します。

展開には `GNU Stow` を使い、必要な設定だけをホームディレクトリへ安全に反映する方針です。

`GNU Stow` 前提の最小構成です。`zsh/` パッケージをホームディレクトリへ展開し、macOS と Ubuntu でできるだけ同じ操作感を維持します。

## Structure

- `ghostty/.config/ghostty/config`
  macOS ローカルで使う Ghostty の設定です。
- `zellij/.config/zellij/`
  macOS ローカルで使う zellij の設定です。
- `code/Library/Application Support/Code/User/`
  macOS ローカルで使う VS Code の共通 User 設定です。
- `code/.config/vscode/`
  VS Code profile ごとの設定テンプレートと拡張機能リストです。
- `code/.local/bin/vscode-setup`
  VS Code の拡張機能と profile 設定を再現する補助コマンドです。
- `zsh/.zshrc`
  共通設定、OS 別設定、ローカル差分を順に読み込むエントリポイントです。
- `zsh/.config/zsh/common.zsh`
  補完、alias、`upm()`、Starship 初期化などの共通設定です。
- `zsh/.config/zsh/macos.zsh`
  Homebrew、`~/.local/bin`、nvm、OpenJDK など macOS 固有の PATH 設定です。
- `zsh/.config/zsh/linux.zsh`
  `~/.local/bin` と、Codex CLI が `bwrap` を検出するための `/usr/bin` など、Linux 側の PATH 設定です。
- `~/.zshrc.local`
  Git 管理しないローカル差分です。

## macOS

### Initial setup

前提として Homebrew、VS Code、VS Code CLI の `code` コマンドが入っていることを想定しています。

```sh
brew install starship eza uv zsh-autosuggestions stow && \
git clone git@github.com:kanalsop/dotfiles.git ~/dotfiles && \
cd ~/dotfiles && \
stow zsh ghostty zellij code && \
~/.local/bin/vscode-setup
```

反映後は新しいシェルを開くか、現在のシェルで次を実行します。

```sh
exec zsh
```

Ghostty の設定は `stow ghostty` 実行後に Ghostty を再起動するか、Ghostty の設定リロードを実行して反映します。

VS Code は次の 2 段階で設定します。

1. `stow code`
   `~/Library/Application Support/Code/User/settings.json` などの VS Code 設定ファイルと、`~/.local/bin/vscode-setup` コマンドをホームディレクトリへリンクします。
2. `~/.local/bin/vscode-setup`
   VS Code CLI の `code` コマンドを使って、拡張機能をインストールします。あわせて `Python`、`Rust`、`Swift`、`Web Manager`、`tex editor`、`workflow runner` profile の設定ファイルも反映します。

初回セットアップ時点では、まだ新しいシェル設定が読み込まれていないため `~/.local/bin/vscode-setup` とフルパスで実行します。`exec zsh` 後や次回以降の新しいシェルでは、`~/.local/bin` に PATH が通るので `vscode-setup` だけで実行できます。

### Update

```sh
cd ~/dotfiles && \
git pull && \
stow zsh ghostty zellij code && \
vscode-setup && \
exec zsh
```

## Ubuntu

Ghostty, zellij, VS Code はローカル端末側の責務なので、Ubuntu サーバー側では設定しません。

### Initial setup

`starship`、`eza`、`uv`、Codex CLI は環境によって導入方法が複数ありますが、ここでは `apt` で入るものは `apt`、それ以外は公式インストーラを使う想定です。Codex CLI の Linux sandbox が使う `bwrap` は `bubblewrap` パッケージで導入します。

```sh
sudo apt update && \
sudo apt install -y zsh stow git curl unzip gpg zsh-autosuggestions bubblewrap
```

- `Codex CLI` のインストール

```sh
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

- `starship` のインストール

```sh
curl -sS https://starship.rs/install.sh | sh
```

- `uv` のインストール

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

- `eza` のインストール

```sh
sudo mkdir -p /etc/apt/keyrings && \
curl -fsSL https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor --yes -o /etc/apt/keyrings/gierens.gpg && \
echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list > /dev/null && \
sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list && \
sudo apt update && \
sudo apt install -y eza
```

その後、このリポジトリを配置して設定を反映します。

```sh
git clone git@github.com:kanalsop/dotfiles.git ~/dotfiles && \
cd ~/dotfiles && \
stow zsh
```

`linux.zsh` は Codex CLI などのユーザーコマンド用に `~/.local/bin` を、`apt` がインストールする `/usr/bin/bwrap` を Codex CLI が確実に検出できるように `/usr/bin` を PATH へ明示的に追加します。

`zsh` をログインシェルにする場合は次を実行します。

```sh
chsh -s "$(which zsh)"
```

反映後は再ログインするか、現在のシェルで次を実行します。

```sh
exec zsh
```

### Update

```sh
cd ~/dotfiles && \
git pull && \
stow zsh && \
exec zsh
```

## Local-only settings

他のマシンと共有しない設定は各マシンで `~/.zshrc.local` に定義します。

## References

- [https://zenn.dev/108_twil3akine/articles/mac-setup-263](https://zenn.dev/108_twil3akine/articles/mac-setup-263)
