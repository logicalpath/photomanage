#!/bin/bash

# Pull the SQLite databases from the Mac Studio (the source of truth) to this machine.
#
# For each database:
# - Take a consistent snapshot on the Studio with sqlite3 ".backup" (safe while datasette has it open)
# - Seed a temp file with an APFS clone of the local copy, so rsync only sends changed blocks
# - rsync the snapshot over the temp file, sanity-check it, then atomically swap it into place
#
# Configuration (environment variables):
#   STUDIO_HOST    SSH host for the Studio (default: eddies-mac-studio.local)
#   STUDIO_DB_DIR  database directory on the Studio (default: same path as this repo's database/)

set -euo pipefail

usage() {
    echo "Usage: $0 [<database.db> ...]"
    echo ""
    echo "Arguments:"
    echo "  database.db   : Optional. Databases to sync. Default: mediameta.db embeddings-vlm2.db"
    echo ""
    echo "Example:"
    echo "  $0                        # sync all"
    echo "  $0 embeddings-vlm2.db     # sync one"
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
local_db_dir="$repo_dir/database"
studio_host="${STUDIO_HOST:-eddies-mac-studio.local}"
studio_db_dir="${STUDIO_DB_DIR:-$local_db_dir}"

if [ $# -gt 0 ]; then
    databases=("$@")
else
    databases=(mediameta.db embeddings-vlm2.db)
fi

remote_snapshot=""
local_tmp=""
cleanup() {
    if [ -n "$remote_snapshot" ]; then
        ssh "$studio_host" "rm -f '$remote_snapshot'" || true
    fi
    if [ -n "$local_tmp" ]; then
        rm -f "$local_tmp"
    fi
}
trap cleanup EXIT

for db in "${databases[@]}"; do
    local_db="$local_db_dir/$db"
    echo "==> $db"

    if lsof "$local_db" >/dev/null 2>&1; then
        echo "    Warning: $local_db is open (local datasette?). Restart it after the sync to see new data."
    fi

    remote_snapshot="/tmp/photomanage-sync-$db"
    echo "    Snapshotting on $studio_host..."
    ssh "$studio_host" "test -f '$studio_db_dir/$db' && sqlite3 '$studio_db_dir/$db' \".backup '$remote_snapshot'\""

    local_tmp="$local_db.sync-tmp"
    if [ -f "$local_db" ]; then
        # APFS clone: instant, no extra disk space, gives rsync a basis for delta transfer
        cp -c "$local_db" "$local_tmp"
    fi

    echo "    Transferring..."
    rsync -t --progress "$studio_host:$remote_snapshot" "$local_tmp"

    if ! sqlite3 "$local_tmp" "select count(*) from sqlite_master" >/dev/null; then
        echo "    Error: synced copy of $db did not open as a SQLite database; local copy left unchanged."
        exit 1
    fi

    mv "$local_tmp" "$local_db"
    local_tmp=""
    ssh "$studio_host" "rm -f '$remote_snapshot'"
    remote_snapshot=""
    echo "    Done: $local_db"
done
