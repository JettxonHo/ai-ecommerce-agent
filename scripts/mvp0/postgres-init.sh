#!/usr/bin/env bash
set -Eeuo pipefail

: "${POSTGRES_USER:?POSTGRES_USER must be set by compose}"
: "${MVP0_BUSINESS_DB:?MVP0_BUSINESS_DB must be set by compose}"
: "${MVP0_BUSINESS_ROLE:?MVP0_BUSINESS_ROLE must be set by compose}"
: "${MVP0_BUSINESS_PASSWORD:?MVP0_BUSINESS_PASSWORD must be set by compose}"
: "${MVP0_CHECKPOINT_DB:?MVP0_CHECKPOINT_DB must be set by compose}"
: "${MVP0_CHECKPOINT_ROLE:?MVP0_CHECKPOINT_ROLE must be set by compose}"
: "${MVP0_CHECKPOINT_PASSWORD:?MVP0_CHECKPOINT_PASSWORD must be set by compose}"

validate_identifier() {
  local name="$1"
  local value="$2"
  [[ "$value" =~ ^[a-z_][a-z0-9_]*$ ]] || {
    printf 'ERROR: %s must match [a-z_][a-z0-9_]*; got %q\n' "$name" "$value" >&2
    exit 2
  }
}

validate_identifier MVP0_BUSINESS_DB "$MVP0_BUSINESS_DB"
validate_identifier MVP0_BUSINESS_ROLE "$MVP0_BUSINESS_ROLE"
validate_identifier MVP0_CHECKPOINT_DB "$MVP0_CHECKPOINT_DB"
validate_identifier MVP0_CHECKPOINT_ROLE "$MVP0_CHECKPOINT_ROLE"
validate_identifier POSTGRES_USER "$POSTGRES_USER"

[[ "$MVP0_BUSINESS_DB" != "$MVP0_CHECKPOINT_DB" ]] || {
  printf 'ERROR: Business and Checkpoint databases must be distinct\n' >&2
  exit 2
}
[[ "$MVP0_BUSINESS_ROLE" != "$MVP0_CHECKPOINT_ROLE" ]] || {
  printf 'ERROR: Business and Checkpoint roles must be distinct\n' >&2
  exit 2
}
[[ "$POSTGRES_USER" != "$MVP0_BUSINESS_ROLE" && "$POSTGRES_USER" != "$MVP0_CHECKPOINT_ROLE" ]] || {
  printf 'ERROR: admin role must be distinct from Business and Checkpoint roles\n' >&2
  exit 2
}
[[ -n "$MVP0_BUSINESS_PASSWORD" && -n "$MVP0_CHECKPOINT_PASSWORD" ]] || {
  printf 'ERROR: application role passwords must not be empty\n' >&2
  exit 2
}

PSQL=(psql --no-password --username "$POSTGRES_USER" --dbname postgres -v ON_ERROR_STOP=1)

ensure_resources() {
  # Every generated identifier/value is passed as a psql variable. PostgreSQL's
  # format(%I/%L) performs identifier/value quoting; no raw env text is put in
  # executable SQL. Existing roles keep their password so a normal `up` never
  # silently rotates credentials used by a running host process.
  "${PSQL[@]}" \
    --set=business_db="$MVP0_BUSINESS_DB" \
    --set=business_role="$MVP0_BUSINESS_ROLE" \
    --set=business_password="$MVP0_BUSINESS_PASSWORD" \
    --set=checkpoint_db="$MVP0_CHECKPOINT_DB" \
    --set=checkpoint_role="$MVP0_CHECKPOINT_ROLE" \
    --set=checkpoint_password="$MVP0_CHECKPOINT_PASSWORD" \
    --set=admin_role="$POSTGRES_USER" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'business_role', :'business_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'business_role')
\gexec

SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', :'checkpoint_role', :'checkpoint_password')
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'checkpoint_role')
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'business_db', :'business_role')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'business_db')
\gexec

SELECT format('CREATE DATABASE %I OWNER %I', :'checkpoint_db', :'checkpoint_role')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'checkpoint_db')
\gexec

SELECT format('ALTER DATABASE %I OWNER TO %I', :'business_db', :'business_role')
\gexec

SELECT format('ALTER DATABASE %I OWNER TO %I', :'checkpoint_db', :'checkpoint_role')
\gexec

SELECT format('REVOKE CONNECT ON DATABASE %I FROM PUBLIC', :'business_db')
\gexec

SELECT format('REVOKE CONNECT ON DATABASE %I FROM PUBLIC', :'checkpoint_db')
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', :'business_db', :'business_role')
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', :'checkpoint_db', :'checkpoint_role')
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', :'business_db', :'admin_role')
\gexec

SELECT format('GRANT CONNECT ON DATABASE %I TO %I', :'checkpoint_db', :'admin_role')
\gexec
SQL
}

query() {
  local statement="$1"
  # psql performs :variable interpolation for SQL read from stdin, but not
  # for the string supplied through `--command`; feed the short diagnostic
  # query through stdin so the same safe quoting path is used as ensure.
  "${PSQL[@]}" \
    --set=business_db="$MVP0_BUSINESS_DB" \
    --set=business_role="$MVP0_BUSINESS_ROLE" \
    --set=checkpoint_db="$MVP0_CHECKPOINT_DB" \
    --set=checkpoint_role="$MVP0_CHECKPOINT_ROLE" \
    --set=admin_role="$POSTGRES_USER" \
    --tuples-only --no-align <<< "$statement" | tr -d '\r\n'
}

verify_resources() {
  local failures=0
  local actual

  check() {
    local label="$1"
    local expected="$2"
    local statement="$3"
    actual="$(query "$statement")"
    if [[ "$actual" == "$expected" ]]; then
      printf '  PASS %-38s %s\n' "$label" "$actual"
    else
      printf '  FAIL %-38s expected=%s actual=%s\n' "$label" "$expected" "${actual:-<empty>}" >&2
      failures=$((failures + 1))
    fi
  }

  printf 'MVP-0 PostgreSQL resource verification\n'
  check 'Business database exists' yes \
    "SELECT CASE WHEN EXISTS (SELECT 1 FROM pg_database WHERE datname = :'business_db') THEN 'yes' ELSE 'no' END"
  check 'Checkpoint database exists' yes \
    "SELECT CASE WHEN EXISTS (SELECT 1 FROM pg_database WHERE datname = :'checkpoint_db') THEN 'yes' ELSE 'no' END"
  check 'Business role can login' yes \
    "SELECT CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'business_role' AND rolcanlogin) THEN 'yes' ELSE 'no' END"
  check 'Checkpoint role can login' yes \
    "SELECT CASE WHEN EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'checkpoint_role' AND rolcanlogin) THEN 'yes' ELSE 'no' END"
  check 'Business database owner' "$MVP0_BUSINESS_ROLE" \
    "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = :'business_db'"
  check 'Checkpoint database owner' "$MVP0_CHECKPOINT_ROLE" \
    "SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname = :'checkpoint_db'"
  check 'Business role CONNECT' yes \
    "SELECT CASE WHEN has_database_privilege(:'business_role', :'business_db', 'CONNECT') THEN 'yes' ELSE 'no' END"
  check 'Checkpoint role CONNECT' yes \
    "SELECT CASE WHEN has_database_privilege(:'checkpoint_role', :'checkpoint_db', 'CONNECT') THEN 'yes' ELSE 'no' END"
  check 'Business role blocked from Checkpoint DB' yes \
    "SELECT CASE WHEN has_database_privilege(:'business_role', :'checkpoint_db', 'CONNECT') THEN 'no' ELSE 'yes' END"
  check 'Checkpoint role blocked from Business DB' yes \
    "SELECT CASE WHEN has_database_privilege(:'checkpoint_role', :'business_db', 'CONNECT') THEN 'no' ELSE 'yes' END"

  if (( failures > 0 )); then
    printf 'Verification failed (%d check(s)); run scripts/mvp0/up after fixing configuration.\n' "$failures" >&2
    return 1
  fi
  printf '  Databases: %s (Business), %s (Checkpoint)\n' "$MVP0_BUSINESS_DB" "$MVP0_CHECKPOINT_DB"
  return 0
}

case "${1:-ensure}" in
  ensure)
    ensure_resources
    ;;
  verify)
    verify_resources
    ;;
  *)
    printf 'Usage: %s [ensure|verify]\n' "$0" >&2
    exit 2
    ;;
esac
