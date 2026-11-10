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

## User identity (act as yourself) — one click per new session

Anything the user can open in Feishu, the user identity can read — including
docs shared from other organizations (e.g. Sky盖哥's tables). The token lives in
the session container (refreshes for up to 7 days), so **each new cloud session
needs one 授权 click**:

```bash
bash scripts/feishu-login.sh        # prints a link -> user opens it, clicks 授权
bash scripts/feishu-login.sh wait   # run right after; prints userName + valid
npx -y @larksuite/cli@1.0.98 base +table-list --as user --base-token <token>
```

Wiki URLs (`/wiki/<node>`) map to a base token via
`npx -y @larksuite/cli@1.0.98 api GET /open-apis/wiki/v2/spaces/get_node --as user --params '{"token":"<node>"}'` (field `node.obj_token`).

## Documents the bot can read (verified 2026-11-10)

| Document | Token | Bot access |
|---|---|---|
| 黄金三秒参考 1109 转存 (your copy; tables 黄金三秒参考 115 rows, 剪辑素材库 400, 黄金三秒方法论 8) | `U3FcbS0mOacHaOsbGDVcPdWGnwe` | ✅ |
| 黄金三秒参考 (wiki, owner Sky盖哥, 设计日记 org; base `Le2gb4MMqanLIHsPN1mcKWTPndf`) | wiki `BrTbwcgsvixPOwkYMCSc6btZnzf` | ❌ bot · ✅ user identity |
| AI 自动剪辑流程 (wiki, owner Sky盖哥, 设计日记 org; base `V6kKbcrC5aGY2Dsup6UctTHnnLg`; tables 风格总览/开头库/怎么选/结尾库) | wiki `Sy2HwbxG9iDlmZk2CqqcJ0H4nRc` | ❌ bot · ✅ user identity |

Bases in your own space are readable by the bot directly. For shared docs you
only view, either ask the owner to add the app, or save a copy (转存) to your space.

```bash
node scripts/feishu-base-dump.mjs U3FcbS0mOacHaOsbGDVcPdWGnwe > golden3s.txt
```
