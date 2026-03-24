# dotfiles

`GNU Stow` 前提の最小構成です。`zsh/` パッケージをホームディレクトリへ展開し、macOS と Ubuntu でできるだけ同じ操作感を維持します。

## Structure

- `zsh/.zshrc`
  共通設定、OS 別設定、ローカル差分を順に読み込むエントリポイントです。
- `zsh/.config/zsh/common.zsh`
  補完、alias、`upm()`、Starship 初期化などの共通設定です。
- `zsh/.config/zsh/macos.zsh`
  Homebrew や Antigravity など macOS 固有の PATH 設定です。
- `zsh/.config/zsh/linux.zsh`
  `~/.local/bin` など Linux 側の PATH 設定です。
- `~/.zshrc.local`
  Git 管理しないローカル差分です。`notify()` のようなローカル専用関数はここに置きます。

## macOS

### Initial setup

前提として Homebrew が入っていることを想定しています。

```sh
brew install zsh starship eza uv zsh-autosuggestions stow
git clone <your-dotfiles-repo> ~/dotfiles
cd ~/dotfiles
stow zsh
```

`zsh` をログインシェルにする場合は次を実行します。

```sh
chsh -s "$(which zsh)"
```

反映後は新しいシェルを開くか、現在のシェルで次を実行します。

```sh
exec zsh
```

### Update

```sh
cd ~/dotfiles
git pull
stow zsh
exec zsh
```

## Ubuntu

### Initial setup

`starship`、`eza`、`uv` は環境によって導入方法が複数ありますが、ここでは `apt` で入るものは `apt`、それ以外は公式インストーラを使う想定です。

```sh
sudo apt update
sudo apt install -y zsh stow git curl unzip zsh-autosuggestions
```

`starship` をインストールします。

```sh
curl -sS https://starship.rs/install.sh | sh
```

`uv` をインストールします。

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`eza` をインストールします。
- `gpg` コマンドが必要です．ない場合はインストールします．
```sh
sudo apt install -y gpg
```

- 続けてこれらを実行します
```sh
sudo mkdir -p /etc/apt/keyrings
wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list
sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
sudo apt update
sudo apt install -y eza
```

その後、このリポジトリを配置して設定を反映します。

```sh
git clone git@github.com:kanalsop/dotfiles.git ~/dotfiles
cd ~/dotfiles
stow zsh
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
cd ~/dotfiles
git pull
stow zsh
exec zsh
```

## Local-only settings

`notify()` など共有しない設定は各マシンで `~/.zshrc.local` に定義します。

```zsh
notify() {
  "$@"
  local exit_code=$?

  osascript -e 'display notification "処理が終了しました" with title "DONE"'
  return $exit_code
}
```
