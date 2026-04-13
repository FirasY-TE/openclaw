#!/usr/bin/env bash
set -euo pipefail

topic_route_env_var_for() {
  local logical_route="$1"
  case "${logical_route}" in
    triage_digest) echo "ROUTE_TRIAGE_DIGEST_TARGET" ;;
    system_auth) echo "ROUTE_SYSTEM_AUTH_TARGET" ;;
    urgent) echo "ROUTE_URGENT_TARGET" ;;
    beeper) echo "ROUTE_BEEPER_TARGET" ;;
    hospitable) echo "ROUTE_HOSPITABLE_TARGET" ;;
    *)
      echo "Unknown logical route: ${logical_route}. Expected one of: triage_digest, system_auth, urgent, beeper, hospitable" >&2
      return 1
      ;;
  esac
}

is_topic_target() {
  local target="$1"
  [[ "$target" =~ ^-?[0-9]+:topic:[0-9]+$ ]]
}

resolve_telegram_route_target() {
  local logical_route="$1"
  local env_var_name
  env_var_name="$(topic_route_env_var_for "${logical_route}")"

  local target="${!env_var_name:-}"
  if [[ -z "${target}" ]]; then
    echo "Missing required route target env var: ${env_var_name}" >&2
    return 1
  fi

  if ! is_topic_target "${target}"; then
    echo "Invalid ${env_var_name} format '${target}'. Expected '<chatId>:topic:<topicId>'." >&2
    return 1
  fi

  printf "%s\n" "${target}"
}

send_telegram_target_message() {
  local target="$1"
  local message="$2"
  openclaw message send --channel telegram --target "${target}" --message "${message}"
}

send_with_topic_fallback() {
  local logical_route="$1"
  local message="$2"

  local primary_target
  primary_target="$(resolve_telegram_route_target "${logical_route}")"

  if send_telegram_target_message "${primary_target}" "${message}"; then
    return 0
  fi

  if send_telegram_target_message "${primary_target}" "${message}"; then
    return 0
  fi

  local fallback_target="telegram:1460581318"
  local fallback_message="[FALLBACK from ${logical_route}] ${message}"
  send_telegram_target_message "${fallback_target}" "${fallback_message}"
}
