#!/usr/bin/env bash
set -Eeuo pipefail

# All lifecycle commands use this fixed Compose project and explicit volume
# name. That keeps down/reset-demo scoped to this repository's local demo.
MVP0_ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MVP0_COMPOSE_PROJECT="ai-ecommerce-agent-mvp0"
MVP0_COMPOSE_FILE="$MVP0_ROOT_DIR/compose.yaml"
MVP0_ENV_FILE="$MVP0_ROOT_DIR/.env"
MVP0_POSTGRES_INIT="/docker-entrypoint-initdb.d/20-mvp0-databases.sh"

mvp0_die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

mvp0_compose() {
  local -a args=(--project-name "$MVP0_COMPOSE_PROJECT" --file "$MVP0_COMPOSE_FILE")
  if [[ -f "$MVP0_ENV_FILE" ]]; then
    args+=(--env-file "$MVP0_ENV_FILE")
  fi
  docker compose "${args[@]}" "$@"
}

mvp0_require_repo() {
  [[ -f "$MVP0_COMPOSE_FILE" ]] || mvp0_die "compose.yaml is missing from $MVP0_ROOT_DIR"
}

mvp0_service_container_id() {
  mvp0_compose ps -q postgres 2>/dev/null | sed -n '1p'
}

mvp0_run_init_script() {
  local mode="${1:-ensure}"
  mvp0_compose exec -T postgres "$MVP0_POSTGRES_INIT" "$mode"
}
