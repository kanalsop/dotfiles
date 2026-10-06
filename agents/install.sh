#!/usr/bin/env bash
set -euCo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_DIR
readonly AGENTS_FILE="$REPO_DIR/AGENTS.md"
readonly SKILLS_DIR="$REPO_DIR/skills"
readonly INSTRUCTION_TARGETS=(
  "$HOME/.claude/CLAUDE.md"
  "$HOME/.codex/AGENTS.md"
)
readonly SKILL_TARGET_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.agents/skills"
)
readonly STATUSLINE_SOURCE="$REPO_DIR/claude/statusline/statusline.py"
readonly STATUSLINE_TARGET="$HOME/.claude/statusline/statusline.py"
readonly MERGE_SCRIPT="$REPO_DIR/merge_config.py"
readonly CONFIG_SOURCES=(
  "$REPO_DIR/claude/settings.json"
  "$REPO_DIR/codex/config.toml"
)
readonly CONFIG_TARGETS=(
  "$HOME/.claude/settings.json"
  "$HOME/.codex/config.toml"
)

function usage() {
  cat <<EOF
Description:
    Link AGENTS.md, skills, and the status line from this directory into Claude Code and Codex,
    and merge the managed keys of claude/settings.json and codex/config.toml into the agents' own
    config files. Existing files that are replaced or changed are kept as <name>.bak.<timestamp>.

Usage:
    $0 [--dry-run] [--uninstall]

Options:
    --dry-run: print the actions without changing anything
    --uninstall: remove only the links that point into this directory (merged config keys stay)
    --help, -h: print this
EOF
}

dry_run=false
uninstall=false

function run() {
  if "$dry_run"; then
    echo "[dry-run] $*"
  else
    "$@"
  fi
}

function points_into_repo() {
  local _target="$1"
  [[ -L "$_target" ]] && [[ "$(readlink "$_target")" == "$REPO_DIR"/* ]]
}

function link_path() {
  local _source="$1"
  local _target="$2"
  if points_into_repo "$_target"; then
    run ln -sfn "$_source" "$_target"
    return
  fi
  run mkdir -p "$(dirname "$_target")"
  if [[ -e "$_target" || -L "$_target" ]]; then
    local _backup
    _backup="$_target.bak.$(date +%Y%m%d%H%M%S)"
    echo "backup: $_target -> $_backup"
    run mv "$_target" "$_backup"
  fi
  run ln -s "$_source" "$_target"
  echo "linked: $_target -> $_source"
}

function unlink_path() {
  local _target="$1"
  if points_into_repo "$_target"; then
    run rm "$_target"
    echo "removed: $_target"
  fi
}

function merge_config() {
  local _source="$1"
  local _target="$2"
  if "$dry_run"; then
    python3 "$MERGE_SCRIPT" --dry-run "$_source" "$_target"
  else
    python3 "$MERGE_SCRIPT" "$_source" "$_target"
  fi
}

function skill_dirs() {
  find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d | sort
}

function install_all() {
  local _target _target_dir _skill
  for _target in "${INSTRUCTION_TARGETS[@]}"; do
    link_path "$AGENTS_FILE" "$_target"
  done
  for _target_dir in "${SKILL_TARGET_DIRS[@]}"; do
    while IFS= read -r _skill; do
      link_path "$_skill" "$_target_dir/$(basename "$_skill")"
    done < <(skill_dirs)
  done
  link_path "$STATUSLINE_SOURCE" "$STATUSLINE_TARGET"
  local _i
  for _i in "${!CONFIG_SOURCES[@]}"; do
    merge_config "${CONFIG_SOURCES[$_i]}" "${CONFIG_TARGETS[$_i]}"
  done
}

function uninstall_all() {
  local _target _target_dir _skill
  for _target in "${INSTRUCTION_TARGETS[@]}"; do
    unlink_path "$_target"
  done
  for _target_dir in "${SKILL_TARGET_DIRS[@]}"; do
    while IFS= read -r _skill; do
      unlink_path "$_target_dir/$(basename "$_skill")"
    done < <(skill_dirs)
  done
  unlink_path "$STATUSLINE_TARGET"
  echo "kept: merged keys in ${CONFIG_TARGETS[*]} (restore a .bak file to revert them)"
}

function main() {
  while (($# > 0)); do
    case "$1" in
      --dry-run) dry_run=true ;;
      --uninstall) uninstall=true ;;
      --help | -h)
        usage
        exit 0
        ;;
      *)
        usage >&2
        exit 1
        ;;
    esac
    shift
  done

  if "$uninstall"; then
    uninstall_all
  else
    install_all
  fi
}

main "$@"
