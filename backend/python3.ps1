$working_dir = '/app'

$args[0] = $args[0] -replace "\\", "/"

$pmt_x = Split-Path -Parent -Path $PSScriptRoot
 
docker run -it -v ${pmt_x}:$working_dir -w $working_dir --network pmtx_network dev_pmtx_be python3 $args
