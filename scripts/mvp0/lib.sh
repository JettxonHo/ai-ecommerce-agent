#!/usr/bin/env bash
set -Eeuo pipefail

# All lifecycle commands use a repository-scoped Compose project and explicit
# volume name. The defaults are deliberately fixed for the persistent local
# demo; demo --ephemeral supplies a validated, unique pair for acceptance.
MVP0_ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MVP0_DEFAULT_COMPOSE_PROJECT="ai-ecommerce-agent-mvp0"
MVP0_DEFAULT_POSTGRES_VOLUME_NAME="ai-ecommerce-agent-mvp0-postgres-data"
MVP0_COMPOSE_PROJECT="${MVP0_COMPOSE_PROJECT:-$MVP0_DEFAULT_COMPOSE_PROJECT}"
MVP0_POSTGRES_VOLUME_NAME="${MVP0_POSTGRES_VOLUME_NAME:-$MVP0_DEFAULT_POSTGRES_VOLUME_NAME}"
export MVP0_COMPOSE_PROJECT MVP0_POSTGRES_VOLUME_NAME
MVP0_COMPOSE_FILE="$MVP0_ROOT_DIR/compose.yaml"
MVP0_ENV_FILE="$MVP0_ROOT_DIR/.env"
MVP0_POSTGRES_INIT="/docker-entrypoint-initdb.d/20-mvp0-databases.sh"

mvp0_die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

mvp0_compose() {
  mvp0_validate_resource_scope
  local -a args=(--project-name "$MVP0_COMPOSE_PROJECT" --file "$MVP0_COMPOSE_FILE")
  if [[ -f "$MVP0_ENV_FILE" ]]; then
    args+=(--env-file "$MVP0_ENV_FILE")
  fi
  docker compose "${args[@]}" "$@"
}

mvp0_validate_resource_scope() {
  if [[ "$MVP0_COMPOSE_PROJECT" == "$MVP0_DEFAULT_COMPOSE_PROJECT" ]]; then
    [[ "$MVP0_POSTGRES_VOLUME_NAME" == "$MVP0_DEFAULT_POSTGRES_VOLUME_NAME" ]] ||
      mvp0_die "default Compose project may use only $MVP0_DEFAULT_POSTGRES_VOLUME_NAME"
    return 0
  fi

  [[ "$MVP0_COMPOSE_PROJECT" =~ ^ai-ecommerce-agent-mvp0-ephemeral-[0-9]{12}-[0-9]{5}-[0-9]{5}$ ]] ||
    mvp0_die "refusing unscoped Compose project: $MVP0_COMPOSE_PROJECT"
  [[ "$MVP0_POSTGRES_VOLUME_NAME" == "${MVP0_COMPOSE_PROJECT}-pg" ]] ||
    mvp0_die "ephemeral Compose project must use its paired temporary volume"
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
