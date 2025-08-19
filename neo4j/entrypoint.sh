#!/usr/bin/env bash
set -euo pipefail
# If a dump is present at /var/lib/neo4j/import/seed/graph.dump, load it into /data if empty
if [ -d "/data/databases" ] && [ -z "$(ls -A /data/databases 2>/dev/null || true)" ]; then
  if [ -f "/var/lib/neo4j/import/seed/graph.dump" ]; then
    echo "Loading Neo4j dump into /data..."
    neo4j-admin database load --from=/var/lib/neo4j/import/seed/graph.dump neo4j --force
  fi
fi
# Start Neo4j
exec /sbin/tini -g -- /docker-entrypoint.sh neo4j
