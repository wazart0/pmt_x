import { Configuration } from "@components/api";
import { Token, DefaultApi } from "@components/api";


export const openapiconfig = new Configuration()
openapiconfig.basePath = 'http://localhost:11001'

export const defaultApi = new DefaultApi(openapiconfig)


