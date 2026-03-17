"""데이터 관리 모듈 - Base64 인코딩 JSON 파일 기반 저장/로드"""
import json, base64, os, sys
from datetime import datetime, timedelta

DEFAULT_TAGS = ['식사', '취미', '쇼핑', '생필품', '공과금', '저축']

def _add_months(dt, months):
    y = dt.year + (dt.month + months - 1) // 12
    m = (dt.month + months - 1) % 12 + 1
    d = min(dt.day, [31, 29 if y%4==0 and not(y%100==0 and y%400!=0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
    return dt.replace(year=y, month=m, day=d)

class DataManager:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self._files = {k: os.path.join(self.base_dir, f'{k}.txt')
                       for k in ('contacts', 'ledger', 'events', 'diary', 'reminders', 'tags', 'settings')}
        if not self._load('tags'):
            self._save('tags', list(DEFAULT_TAGS))

    # ===== 설정 (PIN 포함) =====
    def get_settings(self):
        data = self._load('settings')
        if isinstance(data, dict): return data
        return {'language': 'en', 'theme': 'dark_purple', 'pin': '', 'use_pin': False}

    def save_settings(self, settings):
        self._save('settings', settings)

    def _load(self, key):
        fp = self._files[key]
        if not os.path.exists(fp): return []
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                enc = f.read().strip()
                return json.loads(base64.b64decode(enc).decode('utf-8')) if enc else []
        except Exception:
            return []

    def _save(self, key, data):
        fp = self._files[key]
        enc = base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        with open(fp, 'w', encoding='utf-8') as f: f.write(enc)

    def _nid(self, items):
        return max((i.get('id', 0) for i in items), default=0) + 1

    # ===== 연락처 =====
    def get_contacts(self): return self._load('contacts')

    def add_contact(self, name, phone='', nickname='', email='', address=''):
        items = self.get_contacts()
        c = {'id': self._nid(items), 'name': name, 'phone': phone,
             'nickname': nickname, 'email': email, 'address': address, 'created_at': datetime.now().isoformat()}
        items.append(c); self._save('contacts', items); return c

    def update_contact(self, cid, **kw):
        items = self.get_contacts()
        for c in items:
            if c['id'] == cid: c.update(kw); break
        self._save('contacts', items)

    def delete_contact(self, cid):
        self._save('contacts', [c for c in self.get_contacts() if c['id'] != cid])

    # ===== 가계부 =====
    def get_ledger(self, t=None):
        items = self._load('ledger')
        return [e for e in items if e.get('type') == t] if t else items

    def add_ledger(self, typ, amount, tag, desc='', date=None):
        items = self._load('ledger')
        e = {'id': self._nid(items), 'type': typ, 'amount': amount, 'tag': tag,
             'description': desc, 'date': date or datetime.now().strftime('%Y-%m-%d'), 'created_at': datetime.now().isoformat()}
        items.append(e); self._save('ledger', items); return e

    def update_ledger(self, eid, **kw):
        items = self._load('ledger')
        for e in items:
            if e['id'] == eid: e.update(kw); break
        self._save('ledger', items)

    def delete_ledger(self, eid):
        self._save('ledger', [e for e in self._load('ledger') if e['id'] != eid])

    # ===== 태그 =====
    def get_tags(self): return self._load('tags')

    def add_tag(self, tag):
        tags = self.get_tags()
        if tag not in tags: tags.append(tag); self._save('tags', tags)

    def delete_tag(self, tag):
        if tag in DEFAULT_TAGS: return False
        tags = self.get_tags()
        if tag in tags:
            tags.remove(tag); self._save('tags', tags); return True
        return False

    def is_default_tag(self, tag): return tag in DEFAULT_TAGS

    # ===== 일정 (달력) + 반복기능 =====
    def get_events(self): return self._load('events')

    def add_event(self, title, start, end, location='', people=None, desc='', repeat='none'):
        items = self._load('events')
        e = {'id': self._nid(items), 'title': title, 'start_date': start,
             'end_date': end, 'location': location, 'people': people or [],
             'description': desc, 'repeat': repeat, 'created_at': datetime.now().isoformat()}
        items.append(e); self._save('events', items); return e

    def update_event(self, eid, **kw):
        items = self._load('events')
        for e in items:
            if e['id'] == eid: e.update(kw); break
        self._save('events', items)

    def delete_event(self, eid):
        self._save('events', [e for e in self._load('events') if e['id'] != eid])

    def get_daily_events(self, ds_str):
        # 지정된 날짜(ds_str: 'YYYY-MM-DD')에 해당하는 모든 이벤트를 반복까지 적용하여 전개(Expand)
        events = self.get_events()
        ds = datetime.strptime(ds_str, '%Y-%m-%d')
        res = []
        for e in events:
            s_date_str = e['start_date'][:10]
            e_date_str = e['end_date'][:10]
            # 기본 기간 안에 포함 시 바로 추가
            if s_date_str <= ds_str <= e_date_str:
                res.append(e); continue
                
            rep = e.get('repeat', 'none')
            if rep == 'none' or ds_str < s_date_str: continue
            
            s_date = datetime.strptime(s_date_str, '%Y-%m-%d')
            if rep == 'daily': res.append(e)
            elif rep == 'weekly' and s_date.weekday() == ds.weekday(): res.append(e)
            elif rep == 'monthly' and s_date.day == ds.day: res.append(e)
            elif rep == 'yearly' and s_date.month == ds.month and s_date.day == ds.day: res.append(e)
        return res

    # ===== 다이어리 =====
    def get_diary(self): return self._load('diary')

    def add_diary(self, title, content, date=None, ev=None, led=None, con=None):
        items = self._load('diary')
        e = {'id': self._nid(items), 'title': title, 'content': content,
             'date': date or datetime.now().strftime('%Y-%m-%d'),
             'linked_events': ev or [], 'linked_ledger': led or [],
             'linked_contacts': con or [], 'created_at': datetime.now().isoformat()}
        items.append(e); self._save('diary', items); return e

    def update_diary(self, eid, **kw):
        items = self._load('diary')
        for e in items:
            if e['id'] == eid: e.update(kw); break
        self._save('diary', items)

    def delete_diary(self, eid):
        self._save('diary', [e for e in self._load('diary') if e['id'] != eid])

    # ===== 리마인더 (루틴 포함) =====
    def get_reminders(self): return self._load('reminders')

    def add_reminder(self, title, deadline, desc='', repeat='none'):
        items = self._load('reminders')
        r = {'id': self._nid(items), 'title': title, 'deadline': deadline,
             'description': desc, 'repeat': repeat, 'is_completed': False, 'created_at': datetime.now().isoformat()}
        items.append(r); self._save('reminders', items); return r

    def update_reminder(self, rid, **kw):
        items = self._load('reminders')
        for r in items:
            if r['id'] == rid: r.update(kw); break
        self._save('reminders', items)

    def delete_reminder(self, rid):
        self._save('reminders', [r for r in self._load('reminders') if r['id'] != rid])

    def toggle_reminder(self, rid):
        items = self._load('reminders')
        for r in items:
            if r['id'] == rid:
                is_done = not r.get('is_completed', False)
                r['is_completed'] = is_done
                # 완료되었고 반복 설정이 있으면 다음 일정 자동 생성
                if is_done and r.get('repeat', 'none') != 'none':
                    rep = r['repeat']
                    dl = datetime.strptime(r['deadline'], '%Y-%m-%d %H:%M')
                    if rep == 'daily': nd = dl + timedelta(days=1)
                    elif rep == 'weekly': nd = dl + timedelta(weeks=1)
                    elif rep == 'monthly': nd = _add_months(dl, 1)
                    elif rep == 'yearly': nd = _add_months(dl, 12)
                    else: nd = dl
                    
                    if dl != nd:
                        nr = r.copy(); nr['id'] = self._nid(items)
                        nr['is_completed'] = False
                        nr['deadline'] = nd.strftime('%Y-%m-%d %H:%M')
                        nr['created_at'] = datetime.now().isoformat()
                        items.append(nr)
                break
        self._save('reminders', items)

    # ===== 통합 검색 =====
    def search_all(self, kw):
        kw = kw.lower()
        res = []
        def chk(d, ks):
            for k in ks:
                if isinstance(d.get(k), str) and kw in d[k].lower(): return True
                if k == 'amount' and d.get('amount') and kw in str(d['amount']): return True
            return False
            
        for i in self.get_contacts():
            if chk(i, ['name','phone','nickname','email','address']): res.append({'type':'contacts','data':i})
        for i in self.get_ledger():
            if chk(i, ['tag','description','date','amount']): res.append({'type':'ledger','data':i})
        for i in self.get_events():
            if chk(i, ['title','description','location','start_date']): res.append({'type':'events','data':i})
        for i in self.get_diary():
            if chk(i, ['title','content','date']): res.append({'type':'diary','data':i})
        for i in self.get_reminders():
            if chk(i, ['title','description','deadline']): res.append({'type':'reminders','data':i})
        return res
