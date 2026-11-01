# Feishu (Lark) integration

`scripts/feishu.mjs` is a zero-dependency client for the Feishu Open API using a
self-built app (企业自建应用). Credentials are read from the environment only:

| Variable | Value |
|---|---|
| `FEISHU_APP_ID` | App ID (`cli_...`) |
| `FEISHU_APP_SECRET` | App Secret |
| `FEISHU_BASE_URL` | optional; `https://open.larksuite.com` for Lark international |

```bash
node scripts/feishu.mjs check            # verify credentials + bot info
node scripts/feishu.mjs chats            # groups the bot is in
node scripts/feishu.mjs send oc_xxx 你好  # send text to a group
node scripts/feishu.mjs api GET /open-apis/im/v1/chats
```

Never commit the secret; set it in the cloud environment's Network secrets /
environment variables.
