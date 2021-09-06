
docker network create pmtx_network

. $PSScriptRoot/../db/run_db.ps1
# . $PSScriptRoot/../backend/python3.ps1 .\db\startup_wait.py http://pmt_x_db:8080/admin # do not work, implemented in initialize_db_schema.py

. $PSScriptRoot/../backend/python3.ps1 ./initialize/initialize_db_schema.py http://pmt_x_db:8080/admin/schema
. $PSScriptRoot/../backend/python3.ps1 ./initialize/db_data/init_tui_schemas.py http://pmt_x_db:8080/graphql
