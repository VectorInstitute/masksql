#!/bin/bash

set -euo pipefail

DATA_DIR=$1
DATA_ZIP="$DATA_DIR.zip"
DROPBOX_ROOT="/masksql"

echo "Zipping directory $DATA_DIR"
zip -rq "$DATA_ZIP" "$DATA_DIR"

echo "Uploading to Dropbox $DROPBOX_ROOT"
rclone copy "$DATA_ZIP" "dropbox:$DROPBOX_ROOT"
DATA_PUBLIC_URL=$(rclone link dropbox:"$DROPBOX_ROOT/$DATA_ZIP")

echo "Downloading from public URL: $DATA_PUBLIC_URL"
TMP_ROOT="/tmp/masksql"
TMP_DATA_ZIP="$TMP_ROOT/$DATA_ZIP"
wget -q --show-progress "$DATA_PUBLIC_URL" -O "$TMP_DATA_ZIP"


echo "Unzipping downloaded file: $TMP_DATA_ZIP"
unzip -oq -d "$TMP_ROOT" "$TMP_DATA_ZIP"

echo "Checking diff"
diff -r "$DATA_DIR" "$TMP_ROOT/$DATA_DIR"

echo "Data uploaded successfully!"
