"""Personal Manager - 개인형 인적관리 프로그램 (단일 창, 팝업 없음)"""
import tkinter as tk
from tkinter import ttk
import calendar as cal_mod
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_manager import DataManager

C = {'bg':'#0d1117','sb':'#161b22','card':'#1c2333','inp':'#0d1117',
     'hover':'#2d333b','acc':'#7c3aed','acc_d':'#6d28d9','acc_l':'#a78bfa',
     'tx':'#e6edf3','tx2':'#8b949e','brd':'#30363d','grn':'#3fb950',
     'red':'#f85149','yel':'#d29922','blu':'#58a6ff','overlay':'#0a0a12'}
FN='Segoe UI'

class ScrollFrame(tk.Frame):
    def __init__(s,p,bg=None):
        super().__init__(p,bg=bg or C['bg'])
        s.vsb=tk.Scrollbar(s,orient='vertical')
        s.canvas=tk.Canvas(s,bg=bg or C['bg'],highlightthickness=0,bd=0,yscrollcommand=s.vsb.set)
        s.vsb.config(command=s.canvas.yview)
        s.inner=tk.Frame(s.canvas,bg=bg or C['bg'])
        s._wid=s.canvas.create_window((0,0),window=s.inner,anchor='nw')
        s.vsb.pack(side='right',fill='y')
        s.canvas.pack(side='left',fill='both',expand=True)
        s.inner.bind('<Configure>',lambda e:s.canvas.configure(scrollregion=s.canvas.bbox('all')))
        s.canvas.bind('<Configure>',lambda e:s.canvas.itemconfig(s._wid,width=e.width))
        s.canvas.bind('<Enter>',lambda e:s.canvas.bind_all('<MouseWheel>',s._mw))
        s.canvas.bind('<Leave>',lambda e:s.canvas.unbind_all('<MouseWheel>'))
    def _mw(s,e): s.canvas.yview_scroll(int(-1*(e.delta/120)),'units')

def _btn(p,text,cmd,bg=None,fg='white',sz=11,px=16,py=6):
    _b=bg or C['acc']
    b=tk.Label(p,text=text,font=(FN,sz),bg=_b,fg=fg,padx=px,pady=py,cursor='hand2')
    b.bind('<Button-1>',lambda e:cmd())
    b.bind('<Enter>',lambda e:b.config(bg=C['acc_d'] if _b==C['acc'] else C['hover']))
    b.bind('<Leave>',lambda e:b.config(bg=_b))
    return b

def _entry(p,**kw):
    return tk.Entry(p,font=(FN,11),bg=C['inp'],fg=C['tx'],insertbackground=C['tx'],
                    relief='flat',highlightbackground=C['brd'],highlightcolor=C['acc'],highlightthickness=1,**kw)

def _lbl(p,text,sz=11,bold=False,fg=None,bg=None,**kw):
    return tk.Label(p,text=text,font=(FN,sz,'bold' if bold else 'normal'),bg=bg or C['bg'],fg=fg or C['tx'],**kw)

# ─── Inline Modal (팝업 대신 사용) ───
class Modal:
    def __init__(s,parent,title,w=450,h=500):
        s.parent=parent
        s.ov=tk.Frame(parent,bg=C['overlay'])
        s.ov.place(relx=0,rely=0,relwidth=1,relheight=1)
        s.fr=tk.Frame(parent,bg=C['card'],highlightbackground=C['acc_l'],highlightthickness=2)
        s.fr.place(relx=0.5,rely=0.5,anchor='center',width=w,height=h)
        tb=tk.Frame(s.fr,bg=C['card']); tb.pack(fill='x',padx=20,pady=(14,0))
        _lbl(tb,title,16,True,bg=C['card']).pack(side='left')
        x=_lbl(tb,'✕',14,bg=C['card'],fg=C['tx2'],cursor='hand2'); x.pack(side='right')
        x.bind('<Button-1>',lambda e:s.close()); x.bind('<Enter>',lambda e:x.config(fg=C['red'])); x.bind('<Leave>',lambda e:x.config(fg=C['tx2']))
        s.body=tk.Frame(s.fr,bg=C['card']); s.body.pack(fill='both',expand=True,padx=24,pady=10)
        s.wl=None
    def field(s,label,default=''):
        _lbl(s.body,label,10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(8,2))
        e=_entry(s.body); e.pack(fill='x',ipady=4)
        if default: e.insert(0,default)
        return e
    def buttons(s,save,save_text='저장'):
        f=tk.Frame(s.body,bg=C['card']); f.pack(fill='x',pady=(14,4))
        _btn(f,'취소',s.close,bg=C['hover']).pack(side='right',padx=(8,0))
        _btn(f,save_text,save).pack(side='right'); return f
    def warn(s,msg):
        if s.wl: s.wl.destroy()
        s.wl=_lbl(s.body,msg,10,fg=C['red'],bg=C['card']); s.wl.pack(anchor='w')
    def close(s): s.ov.destroy(); s.fr.destroy()

class Confirm:
    def __init__(s,parent,msg,on_yes):
        s.ov=tk.Frame(parent,bg=C['overlay']); s.ov.place(relx=0,rely=0,relwidth=1,relheight=1)
        s.fr=tk.Frame(parent,bg=C['card'],highlightbackground=C['yel'],highlightthickness=2)
        s.fr.place(relx=0.5,rely=0.5,anchor='center',width=360,height=160)
        bd=tk.Frame(s.fr,bg=C['card']); bd.pack(fill='both',expand=True,padx=24,pady=20)
        _lbl(bd,msg,13,bg=C['card']).pack(pady=(8,20))
        bf=tk.Frame(bd,bg=C['card']); bf.pack()
        def yes(): s.close(); on_yes()
        _btn(bf,'취소',s.close,bg=C['hover']).pack(side='right',padx=(8,0))
        _btn(bf,'확인',yes,bg=C['red']).pack(side='right')
    def close(s): s.ov.destroy(); s.fr.destroy()

# ═══════════ CONTACTS ═══════════
class ContactsPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,'연락처',22,True).pack(side='left')
        _btn(h,'+ 추가',s._add).pack(side='right')
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        cs=s.dm.get_contacts()
        if not cs: _lbl(s.sf.inner,'연락처가 없습니다.',12,fg=C['tx2']).pack(pady=40); return
        for c in cs: s._card(c)
    def _card(s,c):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=4,ipady=8)
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
        n=c['name']+(f"  ({c['nickname']})" if c.get('nickname') else '')
        _lbl(l,n,14,True,bg=C['card']).pack(anchor='w')
        if c.get('phone'): _lbl(l,f"Tel: {c['phone']}",10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        if c.get('email'): _lbl(l,f"Email: {c['email']}",10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        if c.get('address'): _lbl(l,f"Addr: {c['address']}",10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        r=tk.Frame(f,bg=C['card']); r.pack(side='right',padx=12,pady=8)
        _btn(r,'수정',lambda:s._edit(c),bg=C['hover'],sz=10,px=10,py=4).pack(pady=2)
        _btn(r,'삭제',lambda:Confirm(s,'정말 삭제하시겠습니까?',lambda:s._do_del(c['id'])),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _do_del(s,cid): s.dm.delete_contact(cid); s.refresh()
    def _add(s):
        m=Modal(s,'연락처 추가',400,500)
        en=m.field('이름'); ep=m.field('전화번호'); enk=m.field('별명'); ee=m.field('이메일'); ea=m.field('주소')
        def sv():
            if not en.get().strip(): m.warn('이름을 입력하세요.'); return
            s.dm.add_contact(en.get(),ep.get(),enk.get(),ee.get(),ea.get()); m.close(); s.refresh()
        m.buttons(sv,'추가')
    def _edit(s,c):
        m=Modal(s,'연락처 수정',400,420)
        en=m.field('이름',c.get('name','')); ep=m.field('전화번호',c.get('phone',''))
        enk=m.field('별명',c.get('nickname','')); ee=m.field('이메일',c.get('email','')); ea=m.field('주소',c.get('address',''))
        def sv():
            s.dm.update_contact(c['id'],name=en.get(),phone=ep.get(),nickname=enk.get(),email=ee.get(),address=ea.get()); m.close(); s.refresh()
        m.buttons(sv)

# ═══════════ LEDGER ═══════════
class LedgerPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm; s.ft=None
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,'가계부',22,True).pack(side='left')
        _btn(h,'+ 추가',s._add).pack(side='right')
        tf=tk.Frame(s,bg=C['bg']); tf.pack(fill='x',padx=30)
        s.tabs={}
        for txt,val in [('전체',None),('소득','income'),('지출','expense')]:
            b=tk.Label(tf,text=txt,font=(FN,12),bg=C['card'],fg=C['tx'],padx=16,pady=6,cursor='hand2')
            b.pack(side='left',padx=(0,4)); b.bind('<Button-1>',lambda e,v=val:s._filter(v)); s.tabs[val]=b
        s.slbl=_lbl(s,'',12,fg=C['tx2']); s.slbl.pack(fill='x',padx=30,pady=8)
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
    def _filter(s,t): s.ft=t; s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_ledger(s.ft)
        inc=sum(e['amount'] for e in s.dm.get_ledger('income'))
        exp=sum(e['amount'] for e in s.dm.get_ledger('expense'))
        s.slbl.config(text=f'소득: {inc:,.0f}원  |  지출: {exp:,.0f}원  |  잔액: {inc-exp:,.0f}원')
        for k,b in s.tabs.items(): b.config(bg=C['acc'] if k==s.ft else C['card'])
        if not items: _lbl(s.sf.inner,'내역이 없습니다.',12,fg=C['tx2']).pack(pady=40); return
        for e in sorted(items,key=lambda x:x.get('date',''),reverse=True): s._row(e)
    def _row(s,e):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=3,ipady=6)
        ii=e['type']=='income'; clr=C['grn'] if ii else C['red']; sign='+' if ii else '-'
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='x',expand=True,padx=14,pady=4)
        t=tk.Frame(l,bg=C['card']); t.pack(fill='x')
        _lbl(t,e.get('tag',''),11,True,bg=C['card']).pack(side='left')
        _lbl(t,e.get('date',''),10,fg=C['tx2'],bg=C['card']).pack(side='right')
        if e.get('description'): _lbl(l,e['description'],10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        r=tk.Frame(f,bg=C['card']); r.pack(side='right',padx=14,pady=4)
        _lbl(r,f"{sign}{e['amount']:,.0f}원",13,True,fg=clr,bg=C['card']).pack()
        _btn(r,'x',lambda:Confirm(s,'삭제하시겠습니까?',lambda:s._ddel(e['id'])),bg=C['red'],sz=9,px=6,py=2).pack(pady=(4,0))
    def _ddel(s,eid): s.dm.delete_ledger(eid); s.refresh()
    def _add(s):
        m=Modal(s,'가계부 추가',440,580)
        _lbl(m.body,'유형',10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(8,2))
        tv=tk.StringVar(value='expense')
        tf=tk.Frame(m.body,bg=C['card']); tf.pack(fill='x')
        for txt,val in [('소득','income'),('지출','expense')]:
            tk.Radiobutton(tf,text=txt,variable=tv,value=val,font=(FN,11),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card'],activeforeground=C['tx']).pack(side='left',padx=(0,12))
        ea=m.field('금액')
        _lbl(m.body,'태그',10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(8,2))
        tgv=tk.StringVar()
        tgf=tk.Frame(m.body,bg=C['card']); tgf.pack(fill='x')
        def _build_tags():
            for w in tgf.winfo_children(): w.destroy()
            for i,t in enumerate(s.dm.get_tags()):
                rf=tk.Frame(tgf,bg=C['card']); rf.grid(row=i//3,column=i%3,sticky='w',padx=2,pady=1)
                tk.Radiobutton(rf,text=t,variable=tgv,value=t,font=(FN,10),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card']).pack(side='left')
                if not s.dm.is_default_tag(t):
                    db=tk.Label(rf,text='x',font=(FN,8),bg=C['card'],fg=C['red'],cursor='hand2',padx=2)
                    db.pack(side='left')
                    db.bind('<Button-1>',lambda e,tag=t:_del_tag(tag))
        def _del_tag(tag):
            s.dm.delete_tag(tag)
            if tgv.get()==tag: tgv.set('')
            _build_tags()
        _build_tags()
        _lbl(m.body,'직접 입력:',10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,2))
        ct=_entry(m.body); ct.pack(fill='x',ipady=4)
        ed=m.field('설명'); edt=m.field('날짜 (YYYY-MM-DD)',datetime.now().strftime('%Y-%m-%d'))
        def sv():
            try: amt=float(ea.get())
            except: m.warn('올바른 금액을 입력하세요.'); return
            tag=ct.get().strip() or tgv.get()
            if not tag: m.warn('태그를 선택/입력하세요.'); return
            if ct.get().strip(): s.dm.add_tag(ct.get().strip())
            s.dm.add_ledger(tv.get(),amt,tag,ed.get(),edt.get()); m.close(); s.refresh()
        m.buttons(sv,'추가')

# ═══════════ CALENDAR ═══════════
class CalendarPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        now=datetime.now(); s.yr,s.mo=now.year,now.month; s.sel=None; s._build()
    def _build(s):
        nav=tk.Frame(s,bg=C['bg']); nav.pack(fill='x',padx=30,pady=(24,10))
        _btn(nav,'◀',s._prev,bg=C['card'],sz=14,px=12).pack(side='left')
        s.ml=_lbl(nav,'',18,True); s.ml.pack(side='left',expand=True)
        s.ml.config(cursor='hand2'); s.ml.bind('<Button-1>',lambda e:s._jump())
        _btn(nav,'▶',s._next,bg=C['card'],sz=14,px=12).pack(side='right')
        _btn(nav,'+ 일정',s._add_ev,sz=11,px=12).pack(side='right',padx=(0,10))
        s.gf=tk.Frame(s,bg=C['bg']); s.gf.pack(fill='both',expand=True,padx=30)
        for i,d in enumerate(['일','월','화','수','목','금','토']):
            fg=C['red'] if i==0 else C['blu'] if i==6 else C['tx']
            _lbl(s.gf,d,11,True,fg=fg).grid(row=0,column=i,sticky='nsew',pady=4)
        s.cells=[]
        for r in range(6):
            row=[]
            for co in range(7):
                c=tk.Frame(s.gf,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1)
                c.grid(row=r+1,column=co,sticky='nsew',padx=1,pady=1)
                dl=tk.Label(c,text='',font=(FN,10),bg=C['card'],fg=C['tx'],anchor='ne',padx=4,pady=2); dl.pack(fill='x')
                el=tk.Label(c,text='',font=(FN,8),bg=C['card'],fg=C['acc_l'],anchor='nw',padx=4,wraplength=100,justify='left'); el.pack(fill='both',expand=True)
                row.append((c,dl,el))
            s.cells.append(row)
        for i in range(7): s.gf.columnconfigure(i,weight=1)
        for i in range(7): s.gf.rowconfigure(i,weight=1 if i>0 else 0,minsize=55)
        s.ep=tk.Frame(s,bg=C['card'],height=140); s.ep.pack(fill='x',padx=30,pady=(8,20)); s.ep.pack_propagate(False)
        s.et=_lbl(s.ep,'',12,True,bg=C['card']); s.et.pack(anchor='w',padx=12,pady=(8,4))
        s.el_sf=ScrollFrame(s.ep,bg=C['card']); s.el_sf.pack(fill='both',expand=True,padx=12,pady=(0,8))
        s.el=s.el_sf.inner
        s.refresh()
    def refresh(s):
        s.ml.config(text=f'{s.yr}년 {s.mo}월')
        cal=cal_mod.Calendar(firstweekday=6); weeks=cal.monthdayscalendar(s.yr,s.mo)
        events=s.dm.get_events(); today=datetime.now()
        for ri,week in enumerate(weeks):
            for ci,day in enumerate(week):
                c,dl,el=s.cells[ri][ci]
                if day==0:
                    dl.config(text='',bg=C['bg']); el.config(text='',bg=C['bg']); c.config(bg=C['bg'])
                    for w in(c,dl,el): w.unbind('<Button-1>')
                    continue
                dl.config(text=str(day),bg=C['card']); el.config(bg=C['card']); c.config(bg=C['card'])
                ds=f'{s.yr:04d}-{s.mo:02d}-{day:02d}'
                de=[e for e in events if e['start_date'][:10]<=ds<=e['end_date'][:10]]
                etxts=[f'- {e["title"][:10]}' for e in de[:2]]
                if len(de)>2: etxts.append(f'  +{len(de)-2}건')
                el.config(text='\n'.join(etxts) if de else '')
                ist=(s.yr==today.year and s.mo==today.month and day==today.day)
                if ist: c.config(bg=C['acc']); dl.config(bg=C['acc'],fg='white'); el.config(bg=C['acc'],fg='white')
                elif s.sel==ds: c.config(bg=C['acc_d']); dl.config(bg=C['acc_d']); el.config(bg=C['acc_d'])
                else:
                    fg=C['red'] if ci==0 else C['blu'] if ci==6 else C['tx']
                    dl.config(fg=fg)
                for w in(c,dl,el): w.bind('<Button-1>',lambda e,d=ds:s._sel(d))
        for ri in range(len(weeks),6):
            for ci in range(7):
                c,dl,el=s.cells[ri][ci]
                dl.config(text='',bg=C['bg']); el.config(text='',bg=C['bg']); c.config(bg=C['bg'])
        if s.sel: s._show_ev(s.sel)
    def _sel(s,ds): s.sel=ds; s.refresh(); s._show_ev(ds)
    def _show_ev(s,ds):
        s.et.config(text=f'{ds} 일정')
        for w in s.el.winfo_children(): w.destroy()
        evts=[e for e in s.dm.get_events() if e['start_date'][:10]<=ds<=e['end_date'][:10]]
        if not evts: _lbl(s.el,'일정이 없습니다.',10,fg=C['tx2'],bg=C['card']).pack(anchor='w'); return
        for e in evts:
            r=tk.Frame(s.el,bg=C['card']); r.pack(fill='x',pady=2)
            _lbl(r,f"● {e['title']}",11,bg=C['card']).pack(side='left')
            if e.get('location'): _lbl(r,f"  ({e['location']})",10,fg=C['tx2'],bg=C['card']).pack(side='left')
            ts=e['start_date'][11:16] if len(e['start_date'])>10 else ''
            if ts:
                te=e['end_date'][11:16] if len(e['end_date'])>10 else ''
                _lbl(r,f"  {ts}~{te}",10,fg=C['acc_l'],bg=C['card']).pack(side='left')
            _btn(r,'x',lambda eid=e['id']:Confirm(s,'일정을 삭제하시겠습니까?',lambda:s._ddel(eid)),bg=C['red'],sz=9,px=6,py=1).pack(side='right')
    def _ddel(s,eid): s.dm.delete_event(eid); s.refresh()
    def _prev(s):
        s.mo-=1
        if s.mo<1: s.mo=12; s.yr-=1
        s.sel=None; s.refresh()
    def _next(s):
        s.mo+=1
        if s.mo>12: s.mo=1; s.yr+=1
        s.sel=None; s.refresh()
    def _jump(s):
        m=Modal(s,'날짜 이동',300,250)
        _lbl(m.body,'년도',10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        sy=tk.Spinbox(m.body,from_=2000,to=2099,font=(FN,12),width=8,bg=C['inp'],fg=C['tx'],buttonbackground=C['card'])
        sy.delete(0,'end'); sy.insert(0,str(s.yr)); sy.pack(anchor='w',ipady=3)
        _lbl(m.body,'월',10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(8,0))
        sm=tk.Spinbox(m.body,from_=1,to=12,font=(FN,12),width=4,bg=C['inp'],fg=C['tx'],buttonbackground=C['card'])
        sm.delete(0,'end'); sm.insert(0,str(s.mo)); sm.pack(anchor='w',ipady=3)
        def go(): s.yr=int(sy.get()); s.mo=int(sm.get()); s.sel=None; m.close(); s.refresh()
        m.buttons(go)
    def _add_ev(s):
        m=Modal(s,'일정 추가',480,640)
        et=m.field('일정명')
        allday=tk.BooleanVar(value=True)
        tk.Checkbutton(m.body,text='종일 일정',variable=allday,font=(FN,11),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card'],activeforeground=C['tx'],command=lambda:_tt()).pack(anchor='w',pady=(8,0))
        def _dr(lb,dd,dt='09:00'):
            _lbl(m.body,lb,10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,2))
            f=tk.Frame(m.body,bg=C['card']); f.pack(fill='x')
            de=_entry(f,width=12); de.insert(0,dd); de.pack(side='left',ipady=3)
            te=_entry(f,width=8); te.insert(0,dt); te.pack(side='left',padx=(8,0),ipady=3)
            return de,te
        dd=s.sel or datetime.now().strftime('%Y-%m-%d')
        sd,st=_dr('시작 (YYYY-MM-DD)',dd,'09:00'); ed,et2=_dr('종료 (YYYY-MM-DD)',dd,'10:00')
        def _tt():
            state='disabled' if allday.get() else 'normal'; st.config(state=state); et2.config(state=state)
        _tt()
        el=m.field('장소')
        _lbl(m.body,'참석자',10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(8,2))
        pf=tk.Frame(m.body,bg=C['card']); pf.pack(fill='x')
        pvs={}
        for c in s.dm.get_contacts()[:8]:
            v=tk.BooleanVar()
            tk.Checkbutton(pf,text=c['name'],variable=v,font=(FN,10),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card']).pack(anchor='w')
            pvs[c['id']]=(c['name'],v)
        edesc=m.field('설명')
        def sv():
            if not et.get().strip(): m.warn('일정명을 입력하세요.'); return
            ss=sd.get(); ee=ed.get()
            if not allday.get(): ss+=' '+st.get(); ee+=' '+et2.get()
            ppl=[n for _,(n,v) in pvs.items() if v.get()]
            s.dm.add_event(et.get(),ss,ee,el.get(),ppl,edesc.get()); m.close(); s.refresh()
        m.buttons(sv,'추가')

# ═══════════ DIARY ═══════════
class DiaryPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        s.list_fr=tk.Frame(s,bg=C['bg']); s.edit_fr=tk.Frame(s,bg=C['bg'])
        s._build_list(); s._show_list()
    def _build_list(s):
        h=tk.Frame(s.list_fr,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,'다이어리',22,True).pack(side='left')
        _btn(h,'+ 추가',lambda:s._editor(None)).pack(side='right')
        s.sf=ScrollFrame(s.list_fr); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
    def _show_list(s):
        s.edit_fr.pack_forget(); s.list_fr.pack(fill='both',expand=True); s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_diary()
        if not items: _lbl(s.sf.inner,'다이어리가 없습니다.',12,fg=C['tx2']).pack(pady=40); return
        for e in sorted(items,key=lambda x:x.get('date',''),reverse=True): s._card(e)
    def _card(s,e):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=4,ipady=8)
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
        t=tk.Frame(l,bg=C['card']); t.pack(fill='x')
        _lbl(t,e.get('title',''),14,True,bg=C['card']).pack(side='left')
        _lbl(t,e.get('date',''),10,fg=C['tx2'],bg=C['card']).pack(side='right')
        pv=(e.get('content','')[:80]+'...') if len(e.get('content',''))>80 else e.get('content','')
        _lbl(l,pv,10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,0))
        bf=tk.Frame(l,bg=C['card']); bf.pack(anchor='w',pady=(4,0))
        if e.get('linked_events'): _lbl(bf,f"[일정 {len(e['linked_events'])}]",9,fg=C['acc_l'],bg=C['card']).pack(side='left',padx=(0,6))
        if e.get('linked_ledger'): _lbl(bf,f"[가계부 {len(e['linked_ledger'])}]",9,fg=C['grn'],bg=C['card']).pack(side='left',padx=(0,6))
        if e.get('linked_contacts'): _lbl(bf,f"[인물 {len(e['linked_contacts'])}]",9,fg=C['blu'],bg=C['card']).pack(side='left')
        r=tk.Frame(f,bg=C['card']); r.pack(side='right',padx=12,pady=8)
        _btn(r,'열기',lambda:s._editor(e),bg=C['hover'],sz=10,px=10,py=4).pack(pady=2)
        _btn(r,'삭제',lambda:Confirm(s.list_fr,'삭제하시겠습니까?',lambda:s._ddel(e['id'])),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _ddel(s,eid): s.dm.delete_diary(eid); s.refresh()
    def _editor(s,ex):
        s.list_fr.pack_forget()
        for w in s.edit_fr.winfo_children(): w.destroy()
        s.edit_fr.pack(fill='both',expand=True)
        h=tk.Frame(s.edit_fr,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _btn(h,'← 뒤로',s._show_list,bg=C['hover'],sz=11).pack(side='left')
        _lbl(h,'다이어리 편집' if ex else '새 다이어리',18,True).pack(side='left',padx=16)
        sf=ScrollFrame(s.edit_fr); sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        inner=sf.inner
        _lbl(inner,'제목',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        et=_entry(inner); et.pack(fill='x',ipady=4)
        _lbl(inner,'날짜 (YYYY-MM-DD)',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        edt=_entry(inner); edt.pack(fill='x',ipady=4)
        _lbl(inner,'본문',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        txt=tk.Text(inner,font=(FN,11),bg=C['inp'],fg=C['tx'],insertbackground=C['tx'],relief='flat',highlightbackground=C['brd'],highlightcolor=C['acc'],highlightthickness=1,height=10,wrap='word')
        txt.pack(fill='x',pady=(2,8))
        if ex: et.insert(0,ex.get('title','')); edt.insert(0,ex.get('date','')); txt.insert('1.0',ex.get('content',''))
        else: edt.insert(0,datetime.now().strftime('%Y-%m-%d'))
        evv={}; events=s.dm.get_events()
        if events:
            _lbl(inner,'연결할 일정:',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
            le=ex.get('linked_events',[]) if ex else []
            for ev in events[:6]:
                v=tk.BooleanVar(value=ev['id'] in le)
                tk.Checkbutton(inner,text=ev['title'],variable=v,font=(FN,10),bg=C['bg'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['bg']).pack(anchor='w')
                evv[ev['id']]=v
        lev={}; ledger=s.dm.get_ledger()
        if ledger:
            _lbl(inner,'연결할 가계부:',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
            ll=ex.get('linked_ledger',[]) if ex else []
            for le in ledger[:6]:
                v=tk.BooleanVar(value=le['id'] in ll)
                sg='+' if le['type']=='income' else '-'
                tk.Checkbutton(inner,text=f"{le.get('date','')} {le.get('tag','')} {sg}{le['amount']:,.0f}원",variable=v,font=(FN,10),bg=C['bg'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['bg']).pack(anchor='w')
                lev[le['id']]=v
        cov={}; contacts=s.dm.get_contacts()
        if contacts:
            _lbl(inner,'함께한 사람:',10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
            lc=ex.get('linked_contacts',[]) if ex else []
            for co in contacts[:8]:
                v=tk.BooleanVar(value=co['id'] in lc)
                tk.Checkbutton(inner,text=co['name'],variable=v,font=(FN,10),bg=C['bg'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['bg']).pack(anchor='w')
                cov[co['id']]=v
        wl=[None]
        def sv():
            if not et.get().strip():
                if wl[0]: wl[0].destroy()
                wl[0]=_lbl(inner,'제목을 입력하세요.',10,fg=C['red']); wl[0].pack(anchor='w'); return
            le=[k for k,v in evv.items() if v.get()]; ll=[k for k,v in lev.items() if v.get()]; lc=[k for k,v in cov.items() if v.get()]
            if ex: s.dm.update_diary(ex['id'],title=et.get(),content=txt.get('1.0','end-1c'),date=edt.get(),linked_events=le,linked_ledger=ll,linked_contacts=lc)
            else: s.dm.add_diary(et.get(),txt.get('1.0','end-1c'),edt.get(),le,ll,lc)
            s._show_list()
        bf=tk.Frame(inner,bg=C['bg']); bf.pack(fill='x',pady=(16,8))
        _btn(bf,'저장',sv).pack(side='right')

# ═══════════ REMINDER ═══════════
class ReminderPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,'리마인더',22,True).pack(side='left')
        _btn(h,'+ 추가',s._add).pack(side='right')
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_reminders()
        if not items: _lbl(s.sf.inner,'리마인더가 없습니다.',12,fg=C['tx2']).pack(pady=40); return
        now=datetime.now()
        for r in sorted(items,key=lambda x:x.get('deadline','')): s._card(r,now)
    def _card(s,r,now):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=4,ipady=8)
        done=r.get('is_completed',False)
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
        t=tk.Frame(l,bg=C['card']); t.pack(fill='x')
        chk=tk.Label(t,text='[v]' if done else '[ ]',font=(FN,14),bg=C['card'],fg=C['grn'] if done else C['tx'],cursor='hand2')
        chk.pack(side='left',padx=(0,8)); chk.bind('<Button-1>',lambda e:s._tog(r['id']))
        _lbl(t,r.get('title',''),14,True,fg=C['tx2'] if done else C['tx'],bg=C['card']).pack(side='left')
        try:
            dl=datetime.strptime(r['deadline'][:10],'%Y-%m-%d'); diff=(dl-now).days
            if done: dt,dc='완료',C['grn']
            elif diff<0: dt,dc=f'D+{abs(diff)} (기한 초과)',C['red']
            elif diff==0: dt,dc='D-Day!',C['yel']
            else: dt,dc=f'D-{diff}',C['acc_l']
        except: dt,dc='',C['tx2']
        _lbl(t,dt,11,True,fg=dc,bg=C['card']).pack(side='right')
        _lbl(l,f"마감: {r.get('deadline','')}",10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        if r.get('description'): _lbl(l,r['description'],10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        rt=tk.Frame(f,bg=C['card']); rt.pack(side='right',padx=12,pady=8)
        _btn(rt,'수정',lambda:s._edit(r),bg=C['hover'],sz=10,px=10,py=4).pack(pady=2)
        _btn(rt,'삭제',lambda:Confirm(s,'삭제하시겠습니까?',lambda:s._ddel(r['id'])),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _tog(s,rid): s.dm.toggle_reminder(rid); s.refresh()
    def _ddel(s,rid): s.dm.delete_reminder(rid); s.refresh()
    def _add(s):
        m=Modal(s,'리마인더 추가',420,360)
        et=m.field('제목'); ed=m.field('마감 기한 (YYYY-MM-DD HH:MM)',datetime.now().strftime('%Y-%m-%d 23:59'))
        edesc=m.field('설명')
        def sv():
            if not et.get().strip(): m.warn('제목을 입력하세요.'); return
            s.dm.add_reminder(et.get(),ed.get(),edesc.get()); m.close(); s.refresh()
        m.buttons(sv,'추가')
    def _edit(s,r):
        m=Modal(s,'리마인더 수정',420,360)
        et=m.field('제목',r.get('title','')); ed=m.field('마감 기한',r.get('deadline',''))
        edesc=m.field('설명',r.get('description',''))
        def sv():
            s.dm.update_reminder(r['id'],title=et.get(),deadline=ed.get(),description=edesc.get()); m.close(); s.refresh()
        m.buttons(sv)

# ═══════════ MAIN ═══════════
class PersonalManager:
    def __init__(s):
        s.root=tk.Tk(); s.root.title('Personal Manager'); s.root.geometry('1100x750')
        s.root.configure(bg=C['bg']); s.root.minsize(900,600)
        s.dm=DataManager(); s.mbtns=[]; s.cur=None
        s._sb()
        s.content=tk.Frame(s.root,bg=C['bg']); s.content.pack(side='right',fill='both',expand=True)
        s.show('contacts')
    def _sb(s):
        sb=tk.Frame(s.root,bg=C['sb'],width=200); sb.pack(side='left',fill='y'); sb.pack_propagate(False)
        _lbl(sb,'Personal\nManager',16,True,bg=C['sb']).pack(pady=(28,24))
        tk.Frame(sb,bg=C['brd'],height=1).pack(fill='x',padx=16,pady=(0,12))
        for key,text in [('contacts','연락처'),('ledger','가계부'),('calendar','달력'),('diary','다이어리'),('reminder','리마인더')]:
            b=tk.Label(sb,text=f'  {text}',font=(FN,13),bg=C['sb'],fg=C['tx2'],anchor='w',padx=20,pady=10,cursor='hand2')
            b.pack(fill='x'); b.bind('<Button-1>',lambda e,k=key:s.show(k))
            b.bind('<Enter>',lambda e,b=b:b.config(bg=C['hover']) if b!=s._ab() else None)
            b.bind('<Leave>',lambda e,b=b:b.config(bg=C['sb']) if b!=s._ab() else None)
            s.mbtns.append((key,b))
    def _ab(s):
        for k,b in s.mbtns:
            if k==s.cur: return b
    def show(s,key):
        s.cur=key
        for k,b in s.mbtns: b.config(bg=C['acc'] if k==key else C['sb'],fg='white' if k==key else C['tx2'])
        for w in s.content.winfo_children(): w.destroy()
        cls={'contacts':ContactsPage,'ledger':LedgerPage,'calendar':CalendarPage,'diary':DiaryPage,'reminder':ReminderPage}
        cls[key](s.content,s.dm).pack(fill='both',expand=True)
    def run(s): s.root.mainloop()

if __name__=='__main__': PersonalManager().run()
