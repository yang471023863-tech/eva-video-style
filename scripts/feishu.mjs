#!/usr/bin/env node
// Minimal Feishu (Lark) Open API client. No dependencies (Node 18+ fetch).
//
// Credentials come from the environment, never from the repo:
//   FEISHU_APP_ID       self-built app ID (cli_xxx)
//   FEISHU_APP_SECRET   self-built app secret
//   FEISHU_BASE_URL     optional, default https://open.feishu.cn (use https://open.larksuite.com for Lark)
//
// Usage:
//   node scripts/feishu.mjs check                     verify credentials, show bot info
//   node scripts/feishu.mjs chats                     list group chats the bot has joined
//   node scripts/feishu.mjs send <chat_id> <text...>  send a text message to a chat
//   node scripts/feishu.mjs api <METHOD> <path> [json] raw call, e.g. api GET /open-apis/im/v1/chats

const BASE = (process.env.FEISHU_BASE_URL || 'https://open.feishu.cn').replace(/\/$/, '');

let cachedToken = null;

export async function getTenantToken() {
  if (cachedToken && cachedToken.expires > Date.now() + 60_000) return cachedToken.value;
  const app_id = process.env.FEISHU_APP_ID;
  const app_secret = process.env.FEISHU_APP_SECRET;
  if (!app_id || !app_secret) {
    throw new Error('FEISHU_APP_ID / FEISHU_APP_SECRET are not set in the environment.');
  }
  const res = await fetch(`${BASE}/open-apis/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ app_id, app_secret }),
  });
  const data = await res.json();
  if (data.code !== 0) throw new Error(`Token request failed: code=${data.code} msg=${data.msg}`);
  cachedToken = { value: data.tenant_access_token, expires: Date.now() + data.expire * 1000 };
  return cachedToken.value;
}

export async function api(method, path, body) {
  const token = await getTenantToken();
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json; charset=utf-8',
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let data;
  try { data = JSON.parse(text); } catch { throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`); }
  if (data.code !== 0) {
    const err = new Error(`Feishu API ${method} ${path} failed: code=${data.code} msg=${data.msg}`);
    err.data = data;
    throw err;
  }
  return data.data ?? data;
}

export async function sendText(chatId, text) {
  return api('POST', '/open-apis/im/v1/messages?receive_id_type=chat_id', {
    receive_id: chatId,
    msg_type: 'text',
    content: JSON.stringify({ text }),
  });
}

async function main() {
  const [cmd, ...args] = process.argv.slice(2);
  switch (cmd) {
    case 'check': {
      await getTenantToken();
      console.log(`OK: tenant_access_token obtained from ${BASE}`);
      try {
        const bot = await api('GET', '/open-apis/bot/v3/info');
        const info = bot.bot || bot;
        console.log(`Bot: ${info.app_name ?? '(unnamed)'}  open_id=${info.open_id ?? '-'}`);
      } catch (e) {
        console.log(`Token works, but bot info unavailable (enable the Bot capability?): ${e.message}`);
      }
      break;
    }
    case 'chats': {
      const data = await api('GET', '/open-apis/im/v1/chats?page_size=50');
      const items = data.items || [];
      if (!items.length) console.log('No chats. Add the bot to a group first.');
      for (const c of items) console.log(`${c.chat_id}\t${c.name}`);
      break;
    }
    case 'send': {
      const [chatId, ...words] = args;
      if (!chatId || !words.length) throw new Error('usage: send <chat_id> <text...>');
      const msg = await sendText(chatId, words.join(' '));
      console.log(`Sent: message_id=${msg.message_id}`);
      break;
    }
    case 'api': {
      const [method, path, json] = args;
      if (!method || !path) throw new Error('usage: api <METHOD> <path> [json]');
      const out = await api(method.toUpperCase(), path, json ? JSON.parse(json) : undefined);
      console.log(JSON.stringify(out, null, 2));
      break;
    }
    default:
      console.log('usage: node scripts/feishu.mjs check | chats | send <chat_id> <text> | api <METHOD> <path> [json]');
      process.exitCode = cmd ? 1 : 0;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((e) => { console.error(e.message); process.exit(1); });
}
