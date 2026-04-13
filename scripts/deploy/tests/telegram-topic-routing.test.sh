#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
LIB_PATH="${REPO_ROOT}/scripts/deploy/lib/telegram-topic-routing.sh"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT
LOG_FILE="${TMP_DIR}/openclaw-calls.log"
BEHAVIOR_FILE="${TMP_DIR}/behavior.txt"

cat > "${TMP_DIR}/openclaw" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="${OPENCLAW_STUB_LOG:?missing OPENCLAW_STUB_LOG}"
BEHAVIOR_FILE="${OPENCLAW_STUB_BEHAVIOR:?missing OPENCLAW_STUB_BEHAVIOR}"

printf '%s\n' "$*" >> "${LOG_FILE}"

if [[ "$*" == message\ send* ]]; then
  if [[ ! -s "${BEHAVIOR_FILE}" ]]; then
    exit 0
  fi
  result="$(head -n 1 "${BEHAVIOR_FILE}")"
  tail -n +2 "${BEHAVIOR_FILE}" > "${BEHAVIOR_FILE}.tmp"
  mv "${BEHAVIOR_FILE}.tmp" "${BEHAVIOR_FILE}"
  if [[ "${result}" == "ok" ]]; then
    exit 0
  fi
  exit 1
fi

exit 0
EOF
chmod +x "${TMP_DIR}/openclaw"

assert_eq() {
  local expected="$1"
  local actual="$2"
  local message="$3"
  if [[ "${expected}" != "${actual}" ]]; then
    echo "ASSERT FAILED: ${message}" >&2
    echo "Expected: ${expected}" >&2
    echo "Actual:   ${actual}" >&2
    exit 1
  fi
}

assert_file_lines() {
  local expected="$1"
  local actual
  actual="$(wc -l < "${LOG_FILE}" | tr -d ' ')"
  assert_eq "${expected}" "${actual}" "call count mismatch"
}

setup_route_env() {
  export ROUTE_TRIAGE_DIGEST_TARGET="-100111:topic:201"
  export ROUTE_SYSTEM_AUTH_TARGET="-100111:topic:202"
  export ROUTE_URGENT_TARGET="-100111:topic:203"
  export ROUTE_BEEPER_TARGET="-100111:topic:204"
  export ROUTE_HOSPITABLE_TARGET="-100111:topic:205"
}

run_case() {
  local case_name="$1"
  local behavior_lines="$2"
  local route="$3"
  local message="$4"
  local expected_calls="$5"
  local expected_last_target="$6"
  local expected_last_message="$7"

  : > "${LOG_FILE}"
  printf '%s\n' "${behavior_lines}" > "${BEHAVIOR_FILE}"

  if ! send_with_topic_fallback "${route}" "${message}"; then
    echo "Case '${case_name}' failed unexpectedly" >&2
    exit 1
  fi

  assert_file_lines "${expected_calls}"
  local last_line
  last_line="$(awk 'NF {line=$0} END {print line}' "${LOG_FILE}")"
  [[ -n "${last_line}" ]] || {
    echo "No openclaw calls captured for ${case_name}" >&2
    exit 1
  }
  [[ "${last_line}" == *"--target ${expected_last_target}"* ]] || {
    echo "Wrong target for ${case_name}" >&2
    echo "Last call: ${last_line}" >&2
    exit 1
  }
  [[ "${last_line}" == *"--message ${expected_last_message}"* ]] || {
    echo "Wrong message for ${case_name}" >&2
    echo "Last call: ${last_line}" >&2
    exit 1
  }
}

export OPENCLAW_STUB_LOG="${LOG_FILE}"
export OPENCLAW_STUB_BEHAVIOR="${BEHAVIOR_FILE}"
export PATH="${TMP_DIR}:${PATH}"
setup_route_env
source "${LIB_PATH}"

run_case \
  "success path" \
  "ok" \
  "triage_digest" \
  "digest-ready" \
  "1" \
  "-100111:topic:201" \
  "digest-ready"

run_case \
  "retry success path" \
  $'fail\nok' \
  "system_auth" \
  "auth-issue" \
  "2" \
  "-100111:topic:202" \
  "auth-issue"

run_case \
  "retry then fallback path" \
  $'fail\nfail\nok' \
  "urgent" \
  "urgent-alert" \
  "3" \
  "telegram:1460581318" \
  "[FALLBACK from urgent] urgent-alert"

echo "telegram-topic-routing tests passed"
