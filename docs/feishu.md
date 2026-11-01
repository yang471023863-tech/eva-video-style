# Feishu (Lark) integration

## Current setup

| Item | Value |
|---|---|
| App | 企业自建应用, App ID `cli_aa6c506457f85bf6` |
| Bot name | 和 cc 对话 |
| Console | https://open.feishu.cn/app/cli_aa6c506457f85bf6/baseinfo |
| Credentials | Cloud environment → Edit → **环境变量** (not 网络密钥) |

Environment variables (set once on the environment; every new session gets them):

```
FEISHU_APP_ID=cli_aa6c506457f85bf6
FEISHU_APP_SECRET=<App Secret from the console>
```

Network secrets (网络密钥) do not work for Feishu: the secret must go in the JSON
body of the token request, which the proxy cannot inject. If the secret leaks,
reset it in the console (重置 App Secret) and update the environment variable.

## Bot identity — `scripts/feishu.mjs`

Zero-dependency client, reads the env vars above.

```bash
node scripts/feishu.mjs check            # verify credentials + bot info
node scripts/feishu.mjs chats            # groups the bot is in
node scripts/feishu.mjs send oc_xxx 你好  # send text to a group
node scripts/feishu.mjs api GET /open-apis/im/v1/chats
```

To post into a group, first add the bot 「和 cc 对话」 to that group.

## User identity (act as yourself) — official `@larksuite/cli`

User tokens are stored inside the session container, so each new cloud
session needs one browser confirmation:

```bash
npm i @larksuite/cli
npx lark-cli config init --app-id "$FEISHU_APP_ID" --app-secret-stdin <<< "$FEISHU_APP_SECRET"
npx lark-cli auth login --recommend   # prints a link; the user opens it and confirms
npx lark-cli auth status
```

Then e.g. `lark-cli calendar +agenda`, `lark-cli im +messages-send --as user ...`.
Access tokens last ~2h and refresh automatically for 7 days within a session.
