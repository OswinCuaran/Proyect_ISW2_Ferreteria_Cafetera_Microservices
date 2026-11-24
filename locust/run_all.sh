#!/bin/bash
# Uso: ADMIN_PASSWORD=... INTERNAL_TOKEN=... ./run_all.sh
mkdir -p results

run() {  # $1 = ID, $2 = etiqueta de la tarea, $3 = forma (load, stress, spike)
  echo "=== $1 ($3) ==="
  SHAPE=$3 locust -f locustfileSantiago.py --headless --host http://localhost:8000 \
    --tags "$2" --csv "results/$1" --csv-full-history --only-summary
}

run P01 sup_list      load
run P02 sup_create    load
run P03 sup_list      stress
run P04 sup_list      spike
run C01 cat_list      load
run C02 cat_detail    load
run C03 cat_list      stress
run C04 cat_list      spike
run C05 cat_direct    load
run R01 rep_dashboard load
run R02 rep_stock     load
run R03 rep_dashboard stress
run R04 rep_stock     spike
run N01 not_alert     load
run N02 not_alert     spike
