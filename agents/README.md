# agents

Claude Code と Codex で共有する、最小構成のエージェントハーネスです。
[furedea/dotfiles](https://github.com/furedea/dotfiles) の `agents/`（コミット `3cdb49c` 時点）を元に、Nix・hooks・Herdr などへの依存を外して汎用化しています。

## 構成

```text
agents/
├── AGENTS.md                      # 言語非依存の開発方針（共通の指示）
├── install.sh                     # 各エージェントへのリンクと設定のマージ
├── merge_config.py                # settings.json / config.toml のマージ（install.sh から使用）
├── claude/
│   ├── settings.json              # Claude Code の共通設定（~/.claude/settings.json にマージ）
│   └── statusline/statusline.py   # Claude Code のステータスライン
├── codex/
│   └── config.toml                # Codex の共通設定（~/.codex/config.toml にマージ）
├── tests/                         # merge_config.py と skills の設定のテスト
└── skills/
    ├── tsdd/              # テスト仕様駆動開発（TDD の進め方・テストの質）
    ├── git-workflow/      # ブランチ/コミット/PR の作法と「どこまでやってよいか」
    ├── issue-workflow/    # Issue と実装計画コメントの管理
    ├── source-of-truth/   # 情報の正典の置き場所・重複の解消
    ├── adr/               # ADR（設計判断記録）の要否判定と書き方
    ├── domain-modeling/   # 用語・概念境界・不変条件の整理
    ├── grilling/          # 計画を質問攻めで詰める（明示的に呼んだ時だけ）
    ├── explain-visually/  # 長い文書や PR を HTML で図解（明示的に呼んだ時だけ）
    └── python-style/      # Python の規約（uv / pytest / ty / ruff）
```

## インストール

Python 3.11 以上の `python3` が必要です（設定のマージに標準ライブラリの `tomllib` を使います）。

```sh
bash ~/dotfiles/agents/install.sh --dry-run   # 何が起きるか確認
bash ~/dotfiles/agents/install.sh
```

指示ファイル、Skills、ステータスラインは次の場所にシンボリックリンクを張ります。リンクなので、このフォルダのファイルを編集すればすぐに反映されます。

| 対象        | 指示ファイル          | Skills                    | その他                                |
| ----------- | --------------------- | ------------------------- | ------------------------------------- |
| Claude Code | `~/.claude/CLAUDE.md` | `~/.claude/skills/<name>` | `~/.claude/statusline/statusline.py`  |
| Codex       | `~/.codex/AGENTS.md`  | `~/.agents/skills/<name>` |                                       |

既存のファイルがある場合は `<name>.bak.<日時>` に退避してからリンクします。

### 設定ファイルのマージ

`~/.claude/settings.json` と `~/.codex/config.toml` は、各エージェント自身もテーマ・信頼済みプロジェクト・hook の承認状態などを書き込むため、リンクではなくマージします。

- `claude/settings.json` と `codex/config.toml` に書いたキーで上書きします。テーブル（オブジェクト）は再帰的にマージし、配列などの値は置き換えます。
- repo に書いていないキー（モデル選択、プロジェクトの信頼設定、プラグインの有効化など）はそのまま残ります。
- 内容が変わるときだけ `<name>.bak.<日時>` に退避してから書き込みます。`config.toml` は書き直すときにコメントと書式が失われます。
- repo からキーを削除しても、反映済みの設定からは消えません。不要になったキーは各エージェントの設定から手動で削除してください。

設定を変えたいときは repo 側のファイルを編集して `install.sh` を再実行します。

### アンインストール

`bash install.sh --uninstall` はこのフォルダを指すリンクだけを削除します。マージ済みの設定は残るので、戻す場合は `.bak` を戻してください。

## 元のハーネスから変えた点

- **削除**: Nix / flake、hooks（コマンドガード・自動検証・監査ログ）、Herdr 連携、`project-setup` と `nix-dotfiles` などの個人環境向け skill、Rust/Bash/GitHub Actions の style skill
- **AGENTS.md**: 「，．」の句読点ルールと、ディレクトリ名・ファイル名の命名ルールを外し、skill の使い分けを追記
- **tsdd / git-workflow**: 独自の `verification_session.py` を前提にした検証手順を、「リポジトリで定められた検証コマンド（Makefile、pre-commit、CI 相当のスクリプトなど）を使う」に置き換え
- **grilling / explain-visually**: 元の `skill_rendering.json` による生成をやめ、明示呼び出し専用の設定を各スキルに直接置く（Claude Code は SKILL.md の `disable-model-invocation: true` と `argument-hint`、Codex は `agents/openai.yaml` の `allow_implicit_invocation: false`）。同じフォルダを両方にリンクしており、それぞれ相手のキーやファイルを無視するため
- **explain-visually**: 検証スクリプトを `uv` 経由ではなく `python3` で直接実行する形に変更（Python 3.10 以上、標準ライブラリのみ。スクリーンショットの確認には Chrome か Chromium が必要）
- **python-style**: 個人テンプレート前提の記述を「プロジェクトの dependency group」に変更
- **claude/settings.json**: モデル・推論強度・サブエージェントのモデル、vim モード、プラグインとマーケットプレイス、Nix や Herdr 向けの sandbox 設定、`core.fsmonitor` の上書き、通知用ドメインを外す
- **codex/config.toml**: モデル・推論強度・承認レビュアー、`sandbox_mode = "read-only"`、vim モード、プラグインの有効化、生成スクリプト向けのコメントを外す
- **statusline.py**: Python 3.14 専用の `except` 構文を括弧付きにして、古い Python でも動くように変更

## テスト

```sh
python3 -m unittest discover -s ~/dotfiles/agents/tests
```

## カスタマイズのヒント

- 回答言語やコミット規約は `AGENTS.md` の `# General` で変更できます。
- `git-workflow` の stacked PR 手順は `gh stack` コマンドを前提にしています。使わない場合は `skills/git-workflow/references/stacked_prs.md` と SKILL.md の該当行を消して構いません。
- プロジェクト固有のルールは、各リポジトリの `AGENTS.md` や `CLAUDE.md` に書けばグローバル設定と併用できます。
