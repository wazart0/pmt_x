../db/run_db.ps1

# python ..\db\startup_wait.py http://localhost:8080/admin check what's going on
Start-Sleep -Seconds 30

python ../initialize/initialize_db_schema.py http://localhost:8080/admin/schema

