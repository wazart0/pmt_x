
docker stop dev_pmtx_be
docker rm dev_pmtx_be

docker run -d -v $PSScriptRoot\..:/app  --network pmtx_network --name dev_env_pmtx dev_pmtx_be sleep infinity
