import { TIDClient } from '@trimblecloud/react-tid';
const tidClient = new TIDClient({
  config: {
            configurationEndpoint: "https://stage.id.trimblecloud.com/.well-known/openid-configuration",
            clientId: "e48e5118-8960-4f2a-a56e-d0db3e0c8cd6",
            redirectUrl: "http://todo.ai.trimblecloud.com:8080/",
            logoutRedirectUrl: "http://todo.ai.trimblecloud.com:8080/",
            scopes: ['core-ai-stg']
        },
  persistentOptions: {
    persistentStore: "localStorage"
  }
})

export default tidClient