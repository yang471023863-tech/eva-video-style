#!/usr/bin/env python3
"""用机器人身份读取飞书多维表格（凭据取环境变量 FEISHU_APP_ID / FEISHU_APP_SECRET）。

用法：
  python3 feishu_base.py schema <base_token 或 wiki 链接里的 token>        只看每张表的字段名和条数（省 token）
  python3 feishu_base.py dump   <token> <输出目录>                        把每张表拉到本地 JSON，之后用脚本检索
  python3 feishu_base.py fetch  <file_token> <输出文件> [extra]           下载附件
wiki 链接（/wiki/xxx）会先解析成真正的 base token。
"""
import json, os, sys, urllib.parse, urllib.request

API = 'https://open.feishu.cn/open-apis'

def req(url, data=None, tok=None, raw=False):
    r = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                               headers={'Content-Type': 'application/json', **({'Authorization': 'Bearer ' + tok} if tok else {})})
    x = urllib.request.urlopen(r)
    return x if raw else json.load(x)

def token():
    return req(f'{API}/auth/v3/tenant_access_token/internal',
               {'app_id': os.environ['FEISHU_APP_ID'], 'app_secret': os.environ['FEISHU_APP_SECRET']})['tenant_access_token']

def base_of(t, tok):
    try:
        n = req(f'{API}/wiki/v2/spaces/get_node?token={t}', tok=tok)['data']['node']
        return n['obj_token'] if n['obj_type'] == 'bitable' else t
    except Exception:
        return t

def tables(base, tok):
    return req(f'{API}/bitable/v1/apps/{base}/tables?page_size=100', tok=tok)['data']['items']

def records(base, tid, tok):
    out, pt = [], ''
    while True:
        d = req(f'{API}/bitable/v1/apps/{base}/tables/{tid}/records?page_size=500' + (f'&page_token={pt}' if pt else ''), tok=tok)['data']
        out += d.get('items') or []
        if not d.get('has_more'): return out
        pt = d['page_token']

if __name__ == '__main__':
    cmd, tok = sys.argv[1], token()
    if cmd in ('schema', 'dump'):
        base = base_of(sys.argv[2], tok)
        for t in tables(base, tok):
            fields = req(f"{API}/bitable/v1/apps/{base}/tables/{t['table_id']}/fields?page_size=100", tok=tok)['data']['items']
            recs = records(base, t['table_id'], tok)
            print(f"{t['name']} | {len(recs)} 条 | " + ', '.join(f['field_name'] for f in fields))
            if cmd == 'dump':
                os.makedirs(sys.argv[3], exist_ok=True)
                json.dump({'fields': fields, 'records': recs}, open(f"{sys.argv[3]}/{t['name'].replace('/', '_')}.json", 'w'), ensure_ascii=False)
    elif cmd == 'fetch':
        url = f'{API}/drive/v1/medias/{sys.argv[2]}/download' + (('?extra=' + urllib.parse.quote(sys.argv[4])) if len(sys.argv) > 4 else '')
        with req(url, tok=tok, raw=True) as x, open(sys.argv[3], 'wb') as f:
            while (b := x.read(1 << 20)): f.write(b)
        print('ok', sys.argv[3])
