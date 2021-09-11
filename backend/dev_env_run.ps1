
docker stop dev_env_pmtx
docker rm dev_env_pmtx

docker run -d -v $PSScriptRoot\..:/app --name dev_env_pmtx dev_pmtx_be sleep infinity
