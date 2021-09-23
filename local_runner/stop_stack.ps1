
. $PSScriptRoot/../backend/stop_be.ps1

. $PSScriptRoot/../db/stop_db.ps1

docker network rm pmtx_network
