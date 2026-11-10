// Dump every table, field and record of a Feishu Bitable using the bot identity.
// Usage: node scripts/feishu-base-dump.mjs <base_token> > out.txt
import { api } from './feishu.mjs';
const B = process.argv[2];
const fmt = (v) => {
  if (v == null) return '';
  if (Array.isArray(v)) return v.map(fmt).join('、');
  if (typeof v === 'object') return v.text ?? v.name ?? v.link ?? (v.file_token ? `[附件:${v.name||v.file_token}]` : JSON.stringify(v));
  return String(v);
};
const tables = (await api('GET', `/open-apis/bitable/v1/apps/${B}/tables?page_size=100`)).items;
for (const t of tables) {
  const fields = (await api('GET', `/open-apis/bitable/v1/apps/${B}/tables/${t.table_id}/fields?page_size=100`)).items;
  let recs = [], pt = '';
  do {
    const d = await api('GET', `/open-apis/bitable/v1/apps/${B}/tables/${t.table_id}/records?page_size=500${pt?`&page_token=${pt}`:''}`);
    recs.push(...(d.items||[])); pt = d.has_more ? d.page_token : '';
  } while (pt);
  console.log(`\n### 表：${t.name}（${recs.length} 条记录，${fields.length} 个字段）`);
  console.log('字段：' + fields.map(f => `${f.field_name}(type ${f.type})`).join('，'));
  recs.forEach((r, i) => {
    console.log(`\n--- 记录 ${i+1}`);
    for (const f of fields) { const v = fmt(r.fields[f.field_name]); if (v) console.log(`【${f.field_name}】${v}`); }
  });
}
