#!/bin/bash
# Restore the media Docker volume from a backup archive.
# Usage: bash scripts/restore_media.sh backups/media-YYYYMMDD-HHMMSS.tar.gz

ARCHIVE="$1"
if [ -z "$ARCHIVE" ] || [ ! -f "$ARCHIVE" ]; then
    echo 'Usage: bash scripts/restore_media.sh backups/media-<timestamp>.tar.gz'
    exit 1
fi

# Find the volume mounted at the app's media directory
VOLUME=$(docker inspect amra --format '{{range .Mounts}}{{if eq .Destination "/usr/src/app/media"}}{{.Name}}{{end}}{{end}}')
if [ -z "$VOLUME" ]; then
    echo '[ERROR] Could not find the media volume on container "amra"'
    exit 1
fi

BACKUP_DIR="$(cd "$(dirname "$ARCHIVE")" && pwd)"

docker stop amra
docker run --rm -v "$VOLUME":/data/media -v "$BACKUP_DIR":/backups:ro alpine:3.20 \
    sh -c "rm -rf /data/media/* && tar -xzf /backups/$(basename "$ARCHIVE") -C /data"
docker start amra
echo "[restore] media volume $VOLUME restored from $ARCHIVE"
