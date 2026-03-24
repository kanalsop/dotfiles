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

## Deploy

```sh
git clone <your-dotfiles-repo> ~/dotfiles
cd ~/dotfiles
stow zsh
```

更新時は pull 後に `stow zsh` を再実行します。

```sh
cd ~/dotfiles
git pull
stow zsh
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
