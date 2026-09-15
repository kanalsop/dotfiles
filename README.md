# dotfiles

このリポジトリは、macOS のローカル端末環境と SSH 接続先の Ubuntu 環境で、できるだけ同じシェル操作感を再現するための dotfiles を管理するものです。

主に `zsh`、`starship`、`eza`、`uv`、補完設定、alias / function 類を Git で一元管理し、OS 依存の差分は分離したまま共通化します。

展開には `GNU Stow` を使い、必要な設定だけをホームディレクトリへ安全に反映する方針です。

`GNU Stow` 前提の最小構成です。`zsh/` パッケージをホームディレクトリへ展開し、macOS と Ubuntu でできるだけ同じ操作感を維持します。

## Structure

- `.stowrc`
  macOS が生成する `.DS_Store` を Stow の対象から除外します。Stow はリポジトリのルートで実行してください。
- `ghostty/.config/ghostty/config`
  macOS ローカルで使う Ghostty の設定です。
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
- `zsh/.config/zsh/navigation.zsh`
  OS 別の PATH 設定後に fzf と zoxide を初期化します。
- `zsh/.config/zsh/macos.zsh`
  Homebrew、`~/.local/bin`、nvm、OpenJDK など macOS 固有の PATH 設定です。
- `zsh/.config/zsh/linux.zsh`
  `~/.local/bin` と、Codex CLI が `bwrap` を検出するための `/usr/bin` など、Linux 側の PATH 設定です。
- `zsh/.local/bin/linux-setup`
  Ubuntu 上で Codex CLI、`bubblewrap`、AppArmor profile をセットアップし、Linux sandbox の動作を検証する補助コマンドです。
- `~/.zshrc.local`
  Git 管理しないローカル差分です。

## macOS

### Initial setup

前提として Homebrew、VS Code、VS Code CLI の `code` コマンドが入っていることを想定しています。

```sh
brew install ghostty starship eza uv zsh-autosuggestions fzf zoxide stow bat && \
brew install --cask font-moralerspace-hw font-udev-gothic-nf font-cica && \
git clone git@github.com:kanalsop/dotfiles.git ~/dotfiles && \
cd ~/dotfiles && \
stow zsh ghostty code && \
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

### Fonts

Ghostty と VS Code の設定で指定しているフォントは次のとおりです。すべて Homebrew の cask からインストールできます。

| フォント | 使用箇所 | Homebrew cask |
| --- | --- | --- |
| Moralerspace Neon HW | Ghostty、VS Code 共通設定のエディター・ターミナル、Python profile のエディター・ターミナル、Web Manager profile のターミナル | [font-moralerspace-hw](https://formulae.brew.sh/cask/font-moralerspace-hw) |
| UDEV Gothic NF | Ghostty、VS Code 共通設定のエディター・ターミナル、Python / Web Manager profile のターミナル | [font-udev-gothic-nf](https://formulae.brew.sh/cask/font-udev-gothic-nf) |
| Cica | Ghostty | [font-cica](https://formulae.brew.sh/cask/font-cica) |

`font-moralerspace-hw` には `Moralerspace Neon HW` が含まれます。VS Code の `monospace` は汎用フォント指定なので、個別のインストールは不要です。

インストール後は Ghostty と VS Code を再起動してください。

### Update

```sh
cd ~/dotfiles && \
git pull && \
stow zsh ghostty code && \
vscode-setup && \
exec zsh
```

## Ubuntu

Ghostty, VS Code はローカル端末側の責務なので、Ubuntu サーバー側では設定しません。

### Initial setup

`starship`、`eza`、`uv`、Codex CLI は環境によって導入方法が複数ありますが、ここでは `apt` で入るものは `apt`、それ以外は公式インストーラを使う想定です。

```sh
sudo apt update && \
sudo apt install -y zsh stow git curl unzip gpg zsh-autosuggestions fzf zoxide bat
```

このリポジトリを配置し、Codex CLI の Linux sandbox をセットアップします。

```sh
git clone git@github.com:kanalsop/dotfiles.git ~/dotfiles && \
cd ~/dotfiles && \
./zsh/.local/bin/linux-setup
```

`linux-setup` は [Codex の Linux sandbox prerequisites](https://developers.openai.com/codex/concepts/sandboxing#prerequisites) に沿って次を冪等に実行するため、既存のサーバーへの再適用や Codex CLI の更新にも使用できます。

- `bubblewrap`、`apparmor-profiles`、`apparmor-utils` のインストール
- unprivileged user namespace が制限されている場合の `bwrap` AppArmor profile の配置と読み込み
- Codex CLI 公式インストーラの実行
- `bwrap` 単体と `codex sandbox` の動作確認

その他の共通ツールは個別にインストールします。

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

その後、zsh の設定を反映します。

```sh
stow zsh
```

`linux.zsh` は Codex CLI などのユーザーコマンド用に `~/.local/bin` を、`apt` がインストールする `/usr/bin/bwrap` を Codex CLI が確実に検出できるように `/usr/bin` を PATH へ明示的に追加します。

`linux-setup` は、Linux sandbox と同じ条件で次の 2 段階の確認を行います。どちらも終了コードが `0` なら sandbox は利用可能です。

```sh
/usr/bin/bwrap \
  --unshare-user \
  --unshare-net \
  --ro-bind / / \
  /bin/true

codex sandbox -- /bin/true
```

Codex CLI v0.146.0 では、両方が成功していても起動時に `bwrap` の PATH または user namespace に関する警告が表示されることがあります（[PATH 警告の報告](https://github.com/openai/codex/issues/30691)、[sandbox が動作する場合の誤検知報告](https://github.com/openai/codex/issues/25404)）。この場合は sandbox の実動作に成功しているため、追加の sysctl 変更や警告を隠す alias は設定しません。

`bwrap` 単体の確認に失敗した場合は AppArmor profile の状態を確認します。

```sh
sudo aa-status | grep -i bwrap || true
sysctl \
  kernel.apparmor_restrict_unprivileged_userns \
  kernel.unprivileged_userns_clone \
  user.max_user_namespaces
sudo journalctl -k -n 100 --no-pager \
  | grep -Ei 'apparmor|denied|bwrap|userns' \
  | tail -30
```

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

## fzf / zoxide

セットアップ済みの環境には、macOS では `brew install fzf zoxide`、Ubuntu では `sudo apt install -y fzf zoxide` で追加し、`stow zsh` と `exec zsh` で設定を反映します。

インストール済みのツールは `navigation.zsh` が自動で初期化するため、手動で `.zshrc` に追記する必要はありません。

| 操作 | 機能 |
| --- | --- |
| `Ctrl-R` | fzf でコマンド履歴を検索 |
| `Ctrl-T` | fzf でファイル・ディレクトリを選択して入力欄に挿入 |
| `Alt-C` | fzf でディレクトリを選んで移動 |
| `z 名前の一部` | zoxide が記録した訪問履歴からディレクトリへ移動 |
| `zi` | 訪問済みディレクトリを fzf で選んで移動 |

zoxide は通常の `cd` で訪問したディレクトリも記録します。`zsh-autosuggestions` の入力中の提案も引き続き利用できます。

fzf 0.48.0 以降では `fzf --zsh` を使い、それ以前の Ubuntu パッケージでは同梱の補完・キーバインド設定を読み込みます。

公式ドキュメント: [fzf](https://github.com/junegunn/fzf#setting-up-shell-integration)、[zoxide](https://github.com/ajeetdsouza/zoxide#installation)

## Local-only settings

他のマシンと共有しない設定は各マシンで `~/.zshrc.local` に定義します。

## References

- [https://zenn.dev/108_twil3akine/articles/mac-setup-263](https://zenn.dev/108_twil3akine/articles/mac-setup-263)
