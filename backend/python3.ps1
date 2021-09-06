$working_dir = '/app'

$args[0] = $args[0] -replace "\\", "/"

$script_root = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$pmt_x = Split-Path -Parent -Path $script_root
 
docker run -it -v ${pmt_x}:$working_dir -w $working_dir --network pmtx_network dev_pmtx_be python3 $args
