#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_tests.sh [load|stress|spike|soak] [--headless] [extra locust args...]
#
# Examples:
#   ./run_tests.sh load --headless
#   ./run_tests.sh stress --headless --stop-timeout 60
#   ./run_tests.sh spike --headless --loglevel INFO
#   ./run_tests.sh soak --headless --html reports/soak.html
#
# Notes:
# - By default uses StudentUser only. To mix scenarios, set CLASS_PICKER or
#   update locustfiles/course_registration_tests.py to import and expose
#   scenario classes, then set CLASS_PICKER accordingly.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TEST_TYPE="${1:-load}"
shift || true

CONFIG_FILE="$ROOT_DIR/configs/${TEST_TYPE}_test.py"
if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Unknown test type: $TEST_TYPE"
  echo "Usage: $0 [load|stress|spike|soak] [--headless] [extra locust args]"
  exit 1
fi

# Import CONFIG dict from the selected config file
CONFIG_JSON=$(python - <<'PYCODE'
import importlib.util, json, sys, pathlib, os
config_path = pathlib.Path(os.environ["CONFIG_FILE"])
spec = importlib.util.spec_from_file_location("cfg", config_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps(module.CONFIG))
PYCODE
)

USERS=$(python - <<'PYCODE'
import json, os, sys
cfg = json.loads(os.environ["CONFIG_JSON"])
print(cfg["users"])
PYCODE
)
SPAWN_RATE=$(python - <<'PYCODE'
import json, os, sys
cfg = json.loads(os.environ["CONFIG_JSON"])
print(cfg["spawn_rate"])
PYCODE
)
RUN_TIME=$(python - <<'PYCODE'
import json, os, sys
cfg = json.loads(os.environ["CONFIG_JSON"])
print(cfg["run_time"])
PYCODE
)
HOST=$(python - <<'PYCODE'
import json, os, sys
cfg = json.loads(os.environ["CONFIG_JSON"])
print(cfg["host"])
PYCODE
)
CLASS_PICKER=$(python - <<'PYCODE'
import json, os, sys
cfg = json.loads(os.environ["CONFIG_JSON"])
print(cfg.get("class_picker", "StudentUser:1"))
PYCODE
)

echo "Running ${TEST_TYPE} test"
echo "  users:        $USERS"
echo "  spawn_rate:   $SPAWN_RATE"
echo "  run_time:     $RUN_TIME"
echo "  host:         $HOST"
echo "  class_picker: $CLASS_PICKER"

export CONFIG_FILE
export CONFIG_JSON

locust -f "$ROOT_DIR/course_registration_tests.py" \
  --users "$USERS" \
  --spawn-rate "$SPAWN_RATE" \
  --run-time "$RUN_TIME" \
  --host "$HOST" \
  --class-picker "$CLASS_PICKER" \
  "$@"

