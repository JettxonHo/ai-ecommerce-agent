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
MVP0_LOCAL_WEB_PROFILE="local-web"
MVP0_READY_ATTEMPTS_MAX=600

mvp0_die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

mvp0_validate_ready_attempts() {
  local value="$1"
  [[ "$value" =~ ^[1-9][0-9]*$ ]] ||
    mvp0_die 'readiness attempt limits must be positive integers'
  (( value <= MVP0_READY_ATTEMPTS_MAX )) ||
    mvp0_die "readiness attempt limits must be <= ${MVP0_READY_ATTEMPTS_MAX}"
}

mvp0_compose() {
  mvp0_validate_resource_scope
  local -a args=(--project-name "$MVP0_COMPOSE_PROJECT" --file "$MVP0_COMPOSE_FILE")
  if [[ -f "$MVP0_ENV_FILE" ]]; then
    args+=(--env-file "$MVP0_ENV_FILE")
  fi
  docker compose "${args[@]}" "$@"
}

mvp0_local_web_compose() {
  mvp0_validate_resource_scope
  # Explicitly disable Compose's implicit project .env loading and activate
  # only the private API/Web profile.  The Postgres service remains the same
  # named service and volume used by the host-development path.  All
  # interpolation inputs other than the validated project/volume pair are
  # fixed local-demo values, so a caller's shell environment cannot alter the
  # Docker-only topology or credentials.
  local -a args=(
    --project-name "$MVP0_COMPOSE_PROJECT"
    --file "$MVP0_COMPOSE_FILE"
    --env-file /dev/null
    --profile "$MVP0_LOCAL_WEB_PROFILE"
  )
  MVP0_COMPOSE_PROJECT="$MVP0_COMPOSE_PROJECT" \
    MVP0_POSTGRES_VOLUME_NAME="$MVP0_POSTGRES_VOLUME_NAME" \
    MVP0_ADMIN_USER=mvp0_admin \
    MVP0_ADMIN_PASSWORD=mvp0_admin_local_only \
    MVP0_BUSINESS_DB=ecommerce_business \
    MVP0_BUSINESS_ROLE=mvp0_business \
    MVP0_BUSINESS_PASSWORD=mvp0_business_local_only \
    MVP0_CHECKPOINT_DB=ecommerce_checkpoint \
    MVP0_CHECKPOINT_ROLE=mvp0_checkpoint \
    MVP0_CHECKPOINT_PASSWORD=mvp0_checkpoint_local_only \
    MVP0_POSTGRES_PORT=55432 \
    docker compose "${args[@]}" "$@"
}

mvp0_set_ephemeral_scope() {
  command -v date >/dev/null 2>&1 ||
    mvp0_die 'required command date is missing; cannot create an ephemeral scope'
  local timestamp
  local process_id
  local random_part
  timestamp="$(date -u +%y%m%d%H%M%S)"
  process_id="$(printf '%05d' "$(( $$ % 100000 ))")"
  random_part="$(printf '%05d' "$RANDOM")"
  export MVP0_COMPOSE_PROJECT="ai-ecommerce-agent-mvp0-ephemeral-${timestamp}-${process_id}-${random_part}"
  export MVP0_POSTGRES_VOLUME_NAME="${MVP0_COMPOSE_PROJECT}-pg"
  mvp0_validate_resource_scope
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
