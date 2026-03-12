"""데이터 관리 모듈 - Base64 인코딩 JSON 파일 기반 저장/로드"""
import json, base64, os
from datetime import datetime


DEFAULT_TAGS = ['식사', '취미', '쇼핑', '생필품', '공과금', '저축']

class DataManager:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self._files = {k: os.path.join(self.base_dir, f'{k}.txt')
                       for k in ('contacts', 'ledger', 'events', 'diary', 'reminders', 'tags', 'settings')}
        if not self._load('tags'):
            self._save('tags', list(DEFAULT_TAGS))

    # ===== 설정 =====
    def get_settings(self):
        data = self._load('settings')
        if isinstance(data, dict):
            return data
        return {'language': 'ko', 'theme': 'dark_purple'}

    def save_settings(self, settings):
        self._save('settings', settings)

    def _load(self, key):
        fp = self._files[key]
        if not os.path.exists(fp):
            return []
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                enc = f.read().strip()
                return json.loads(base64.b64decode(enc).decode('utf-8')) if enc else []
        except Exception:
            return []

    def _save(self, key, data):
        fp = self._files[key]
        enc = base64.b64encode(json.dumps(data, ensure_ascii=False).encode('utf-8')).decode('utf-8')
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(enc)

    def _nid(self, items):
        return max((i.get('id', 0) for i in items), default=0) + 1

    # ===== 연락처 =====
    def get_contacts(self):
        return self._load('contacts')

    def add_contact(self, name, phone='', nickname='', email='', address=''):
        items = self.get_contacts()
        c = {'id': self._nid(items), 'name': name, 'phone': phone,
             'nickname': nickname, 'email': email, 'address': address,
             'created_at': datetime.now().isoformat()}
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
             'description': desc, 'date': date or datetime.now().strftime('%Y-%m-%d'),
             'created_at': datetime.now().isoformat()}
        items.append(e); self._save('ledger', items); return e

    def update_ledger(self, eid, **kw):
        items = self._load('ledger')
        for e in items:
            if e['id'] == eid: e.update(kw); break
        self._save('ledger', items)

    def delete_ledger(self, eid):
        self._save('ledger', [e for e in self._load('ledger') if e['id'] != eid])

    # ===== 태그 =====
    def get_tags(self):
        return self._load('tags')

    def add_tag(self, tag):
        tags = self.get_tags()
        if tag not in tags: tags.append(tag); self._save('tags', tags)

    def delete_tag(self, tag):
        """커스텀 태그만 삭제 가능 (기본 태그는 삭제 불가)"""
        if tag in DEFAULT_TAGS:
            return False
        tags = self.get_tags()
        if tag in tags:
            tags.remove(tag)
            self._save('tags', tags)
            return True
        return False

    def is_default_tag(self, tag):
        return tag in DEFAULT_TAGS

    # ===== 일정 (달력) =====
    def get_events(self):
        return self._load('events')

    def add_event(self, title, start, end, location='', people=None, desc=''):
        items = self._load('events')
        e = {'id': self._nid(items), 'title': title, 'start_date': start,
             'end_date': end, 'location': location, 'people': people or [],
             'description': desc, 'created_at': datetime.now().isoformat()}
        items.append(e); self._save('events', items); return e

    def update_event(self, eid, **kw):
        items = self._load('events')
        for e in items:
            if e['id'] == eid: e.update(kw); break
        self._save('events', items)

    def delete_event(self, eid):
        self._save('events', [e for e in self._load('events') if e['id'] != eid])

    # ===== 다이어리 =====
    def get_diary(self):
        return self._load('diary')

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

    # ===== 리마인더 =====
    def get_reminders(self):
        return self._load('reminders')

    def add_reminder(self, title, deadline, desc=''):
        items = self._load('reminders')
        r = {'id': self._nid(items), 'title': title, 'deadline': deadline,
             'description': desc, 'is_completed': False,
             'created_at': datetime.now().isoformat()}
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
            if r['id'] == rid: r['is_completed'] = not r.get('is_completed', False); break
        self._save('reminders', items)
