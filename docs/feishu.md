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

## Documents the bot can read (verified 2026-11-10)

| Document | Token | Bot access |
|---|---|---|
| 黄金三秒参考 1109 转存 (your copy; tables 黄金三秒参考 115 rows, 剪辑素材库 400, 黄金三秒方法论 8) | `U3FcbS0mOacHaOsbGDVcPdWGnwe` | ✅ |
| 黄金三秒参考 (wiki, owner Sky盖哥, 设计日记 org) | wiki `BrTbwcgsvixPOwkYMCSc6btZnzf` | ❌ only the owner can add the bot |
| AI 自动剪辑流程 (wiki, owner Sky盖哥, 设计日记 org) | wiki `Sy2HwbxG9iDlmZk2CqqcJ0H4nRc` | ❌ only the owner can add the bot |

Bases in your own space are readable by the bot directly. For shared docs you
only view, either ask the owner to add the app, or save a copy (转存) to your space.

```bash
node scripts/feishu-base-dump.mjs U3FcbS0mOacHaOsbGDVcPdWGnwe > golden3s.txt
```
