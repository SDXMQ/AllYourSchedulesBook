"""Personal Manager - 개인형 인적관리 프로그램"""
import tkinter as tk
import calendar as cal_mod
from datetime import datetime
import sys, os

# Add src to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_manager import DataManager
from settings import (t, get_colors, set_lang, set_theme, get_lang, get_theme,
                       fmt_money, get_days, get_months, fmt_month_year,
                       LANGUAGES, THEMES, get_theme_name, t_tag)
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

C = {}
FN = 'Segoe UI'

def _apply_colors():
    global C
    C.update(get_colors())

_apply_colors()

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

class Modal:
    def __init__(s,parent,title,w=450,h=500):
        s.parent=parent
        s.ov=tk.Frame(parent,bg=C['overlay']); s.ov.place(relx=0,rely=0,relwidth=1,relheight=1)
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
    def buttons(s,save,save_text=None):
        if save_text is None: save_text=t('save')
        f=tk.Frame(s.body,bg=C['card']); f.pack(fill='x',pady=(14,4))
        _btn(f,t('cancel'),s.close,bg=C['hover']).pack(side='right',padx=(8,0))
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
        _btn(bf,t('cancel'),s.close,bg=C['hover']).pack(side='right',padx=(8,0))
        _btn(bf,t('confirm'),lambda:[s.close(),on_yes()],bg=C['red']).pack(side='right')
    def close(s): s.ov.destroy(); s.fr.destroy()

# ═══════════ SEARCH & GLOBAL ═══════════
class SearchPage(tk.Frame):
    def __init__(s,p,dm,app):
        super().__init__(p,bg=C['bg']); s.dm=dm; s.app=app
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,t('nav_search'),22,True).pack(side='left')
        
        sf2=tk.Frame(s,bg=C['bg']); sf2.pack(fill='x',padx=30)
        s.inp=_entry(sf2); s.inp.pack(side='left',fill='x',expand=True,ipady=6,padx=(0,8))
        s.inp.insert(0,t('search_ph'))
        s.inp.bind('<FocusIn>',lambda e:s.inp.delete(0,'end') if s.inp.get()==t('search_ph') else None)
        s.inp.bind('<FocusOut>',lambda e:s.inp.insert(0,t('search_ph')) if not s.inp.get() else None)
        s.inp.bind('<Return>',lambda e:s.do_search())
        _btn(sf2,t('nav_search'),s.do_search,px=24,py=7).pack(side='right')
        
        s.tt=_lbl(s,'',12,fg=C['tx2']); s.tt.pack(anchor='w',padx=30,pady=(16,4))
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
    def do_search(s):
        q=s.inp.get().strip()
        if not q or q==t('search_ph'): return
        for w in s.sf.inner.winfo_children(): w.destroy()
        res=s.dm.search_all(q)
        s.tt.config(text=f"{t('search_res')}{len(res)}")
        if not res: _lbl(s.sf.inner,t('search_empty'),12,fg=C['tx2']).pack(pady=40); return
        for it in res:
            f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1,cursor='hand2'); f.pack(fill='x',pady=4,ipady=8)
            l=tk.Frame(f,bg=C['card'],cursor='hand2'); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
            tp=t(f"type_{it['type']}")
            lbl_type = _lbl(l,f"[{tp}]",11,True,fg=C['acc_l'],bg=C['card'],cursor='hand2'); lbl_type.pack(anchor='w')
            d=it['data']
            tit=d.get('title') or d.get('name') or (t_tag(d.get('tag')) if d.get('tag') else None) or 'Item'
            lbl_tit = _lbl(l,tit,13,bg=C['card'],cursor='hand2'); lbl_tit.pack(anchor='w',pady=2)
            desc=d.get('description') or d.get('content') or d.get('phone') or str(d.get('amount',''))
            lbl_desc = _lbl(l,desc[:60]+('...' if len(desc)>60 else ''),10,fg=C['tx2'],bg=C['card'],cursor='hand2'); lbl_desc.pack(anchor='w')
            
            for w in (f, l, lbl_type, lbl_tit, lbl_desc):
                w.bind('<Button-1>', lambda e, k=it['type']: s.app.show(k))

# ═══════════ CONTACTS ═══════════
class ContactsPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,t('nav_contacts'),22,True).pack(side='left')
        _btn(h,t('add'),s._add).pack(side='right')
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        cs=s.dm.get_contacts()
        if not cs: _lbl(s.sf.inner,t('contacts_empty'),12,fg=C['tx2']).pack(pady=40); return
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
        _btn(r,t('edit'),lambda:s._edit(c),bg=C['hover'],sz=10,px=10,py=4).pack(pady=2)
        _btn(r,t('delete'),lambda:Confirm(s,t('confirm_delete'),lambda:s._do_del(c['id'])),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _do_del(s,cid): s.dm.delete_contact(cid); s.refresh()
    def _add(s):
        m=Modal(s,t('contacts_add_title'),400,500)
        en=m.field(t('name')); ep=m.field(t('phone')); enk=m.field(t('nickname')); ee=m.field(t('email')); ea=m.field(t('address'))
        def sv():
            if not en.get().strip(): m.warn(t('name_required')); return
            s.dm.add_contact(en.get(),ep.get(),enk.get(),ee.get(),ea.get()); m.close(); s.refresh()
        m.buttons(sv,t('add'))
    def _edit(s,c):
        m=Modal(s,t('contacts_edit_title'),400,480)
        en=m.field(t('name'),c.get('name','')); ep=m.field(t('phone'),c.get('phone',''))
        enk=m.field(t('nickname'),c.get('nickname','')); ee=m.field(t('email'),c.get('email','')); ea=m.field(t('address'),c.get('address',''))
        def sv():
            s.dm.update_contact(c['id'],name=en.get(),phone=ep.get(),nickname=enk.get(),email=ee.get(),address=ea.get()); m.close(); s.refresh()
        m.buttons(sv, t('edit'))

# ═══════════ DIARY ═══════════
class DiaryPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        s.list_fr=tk.Frame(s,bg=C['bg']); s.edit_fr=tk.Frame(s,bg=C['bg'])
        s._build_list(); s._show_list()
    def _build_list(s):
        h=tk.Frame(s.list_fr,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,t('nav_diary'),22,True).pack(side='left')
        _btn(h,t('add'),lambda:s._editor(None)).pack(side='right')
        s.sf=ScrollFrame(s.list_fr); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
    def _show_list(s):
        s.edit_fr.pack_forget(); s.list_fr.pack(fill='both',expand=True); s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_diary()
        if not items: _lbl(s.sf.inner,t('diary_empty'),12,fg=C['tx2']).pack(pady=40); return
        for e in sorted(items,key=lambda x:x.get('date',''),reverse=True): s._card(e)
    def _card(s,e):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=4,ipady=8)
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
        tp=tk.Frame(l,bg=C['card']); tp.pack(fill='x')
        _lbl(tp,e.get('title',''),14,True,bg=C['card']).pack(side='left')
        _lbl(tp,e.get('date',''),10,fg=C['tx2'],bg=C['card']).pack(side='right')
        pv=(e.get('content','')[:80]+'...') if len(e.get('content',''))>80 else e.get('content','')
        _lbl(l,pv,10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,0))
        r=tk.Frame(f,bg=C['card']); r.pack(side='right',padx=12,pady=8)
        _btn(r,t('open'),lambda:s._editor(e),bg=C['hover'],sz=10,px=10,py=4).pack(pady=2)
        _btn(r,t('delete'),lambda:Confirm(s.list_fr,t('confirm_delete_short'),lambda:s._ddel(e['id'])),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _ddel(s,eid): s.dm.delete_diary(eid); s.refresh()
    def _editor(s,ex):
        s.list_fr.pack_forget()
        for w in s.edit_fr.winfo_children(): w.destroy()
        s.edit_fr.pack(fill='both',expand=True)
        h=tk.Frame(s.edit_fr,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _btn(h,t('back'),s._show_list,bg=C['hover'],sz=11).pack(side='left')
        _lbl(h,t('diary_edit_title') if ex else t('diary_new_title'),18,True).pack(side='left',padx=16)
        sf=ScrollFrame(s.edit_fr); sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        inner=sf.inner
        _lbl(inner,t('title'),10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        et=_entry(inner); et.pack(fill='x',ipady=4)
        _lbl(inner,t('date_label'),10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        edt=_entry(inner); edt.pack(fill='x',ipady=4)
        _lbl(inner,t('content'),10,fg=C['tx2']).pack(anchor='w',pady=(8,2))
        txt=tk.Text(inner,font=(FN,11),bg=C['inp'],fg=C['tx'],insertbackground=C['tx'],relief='flat',highlightbackground=C['brd'],highlightcolor=C['acc'],highlightthickness=1,height=10,wrap='word')
        txt.pack(fill='x',pady=(2,8))
        if ex: et.insert(0,ex.get('title','')); edt.insert(0,ex.get('date','')); txt.insert('1.0',ex.get('content',''))
        else: edt.insert(0,datetime.now().strftime('%Y-%m-%d'))
        
        def sv():
            if not et.get().strip(): return
            if ex: s.dm.update_diary(ex['id'],title=et.get(),content=txt.get('1.0','end-1c'),date=edt.get())
            else: s.dm.add_diary(et.get(),txt.get('1.0','end-1c'),edt.get())
            s._show_list()
        bf=tk.Frame(inner,bg=C['bg']); bf.pack(fill='x',pady=(16,8))
        _btn(bf,t('save'),sv).pack(side='right')

# ═══════════ SETTINGS ═══════════
class SettingsPage(tk.Frame):
    def __init__(s,p,dm,app):
        super().__init__(p,bg=C['bg']); s.dm=dm; s.app=app
        st=s.dm.get_settings()
        s.sel_lang=st.get('language','en'); s.sel_theme=st.get('theme','dark_purple')
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s._build()
        
    def restore_scroll(s, fraction):
        s.sf.canvas.yview_moveto(fraction)

    def _build(s):
        inner=s.sf.inner
        _lbl(inner,t('nav_settings'),22,True).pack(anchor='w',pady=(24,20))
        
        # PIN
        pf=tk.Frame(inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1)
        pf.pack(fill='x',pady=(0,16),ipady=12)
        _lbl(pf,'PIN / Security',16,True,bg=C['card']).pack(anchor='w',padx=20,pady=(16,12))
        st=s.dm.get_settings()
        s.use_pin=tk.BooleanVar(value=st.get('use_pin',False))
        tk.Checkbutton(pf,text=t('pin_enable'),variable=s.use_pin,font=(FN,11),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card']).pack(anchor='w',padx=20)
        pwf=tk.Frame(pf,bg=C['card']); pwf.pack(fill='x',padx=20,pady=10)
        _lbl(pwf,t('pin_setup'),10,fg=C['tx2'],bg=C['card']).pack(anchor='w')
        s.pin_e=_entry(pwf,show='*'); s.pin_e.pack(fill='x',pady=4); s.pin_e.insert(0,st.get('pin',''))

        # Lang
        lf=tk.Frame(inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1)
        lf.pack(fill='x',pady=(0,16),ipady=12)
        _lbl(lf,t('settings_language'),16,True,bg=C['card']).pack(anchor='w',padx=20,pady=(16,12))
        s.lang_var=tk.StringVar(value=s.sel_lang)
        lg=tk.Frame(lf,bg=C['card']); lg.pack(fill='x',padx=20,pady=(0,12))
        for i,(code,name) in enumerate(LANGUAGES.items()):
            row,col=divmod(i,3)
            bf=tk.Frame(lg,bg=C['card']); bf.grid(row=row,column=col,sticky='w',padx=8,pady=4)
            rb=tk.Radiobutton(bf,text=name,variable=s.lang_var,value=code,font=(FN,11),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card'],command=lambda c=code:s._pick_lang(c))
            rb.pack(side='left')

        # Theme
        tf=tk.Frame(inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1)
        tf.pack(fill='x',pady=(0,16),ipady=12)
        _lbl(tf,t('settings_theme'),16,True,bg=C['card']).pack(anchor='w',padx=20,pady=(16,12))
        s.theme_fr=tk.Frame(tf,bg=C['card']); s.theme_fr.pack(fill='x',padx=20,pady=(0,12))
        s._build_themes()

        abf=tk.Frame(inner,bg=C['bg']); abf.pack(fill='x',pady=(8,20))
        _btn(abf,t('settings_apply'),s._apply,sz=13,px=28,py=10).pack(side='right')

    def _build_themes(s):
        for w in s.theme_fr.winfo_children(): w.destroy()
        for i,tkey in enumerate(THEMES):
            cols=THEMES[tkey]
            row,col=divmod(i,4)
            card=tk.Frame(s.theme_fr,bg=C['card'],highlightthickness=2,highlightbackground=C['acc'] if tkey==s.sel_theme else C['brd'],cursor='hand2')
            card.grid(row=row,column=col,padx=6,pady=6,sticky='nsew')
            prev=tk.Frame(card,bg=cols['bg'],height=6); prev.pack(fill='x')
            bar=tk.Frame(card,bg=cols['bg'],height=28); bar.pack(fill='x',padx=8,pady=(4,0))
            for ck in ['acc','grn','red','blu']:
                sw=tk.Frame(bar,bg=cols[ck],width=20,height=20); sw.pack(side='left',padx=2); sw.pack_propagate(False)
            nl=tk.Label(card,text=get_theme_name(tkey),font=(FN,10),bg=C['card'],fg=C['acc'] if tkey==s.sel_theme else C['tx'],padx=8,pady=6)
            nl.pack()
            for w in [card,prev,bar,nl]:
                w.bind('<Button-1>',lambda e,k=tkey:s._pick_theme(k))
    def _pick_lang(s,code): s.sel_lang=code
    def _pick_theme(s,key): s.sel_theme=key; s._build_themes()
    def _apply(s):
        st=s.dm.get_settings()
        st.update({'language':s.sel_lang,'theme':s.sel_theme,'use_pin':s.use_pin.get(),'pin':s.pin_e.get()})
        s.dm.save_settings(st)
        set_lang(s.sel_lang); set_theme(s.sel_theme); _apply_colors()
        
        # Get current scroll position from canvas (yview returns tuple of (top, bottom))
        y_pos = s.sf.canvas.yview()[0]
        # Complete rebuild UI, tell it to open 'settings' and retain that scroll pos
        s.app.rebuild(page='settings', scroll_pos=y_pos)

# ═══════════ CALENDAR & LEDGER ═══════════
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
        _btn(nav,t('add_event'),s._add_ev,sz=11,px=12).pack(side='right',padx=(0,10))
        s.gf=tk.Frame(s,bg=C['bg']); s.gf.pack(fill='both',expand=True,padx=30)
        for i,d in enumerate(get_days()):
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
        s.ml.config(text=fmt_month_year(s.yr,s.mo))
        cal=cal_mod.Calendar(firstweekday=6); weeks=cal.monthdayscalendar(s.yr,s.mo)
        today=datetime.now()
        for ri,week in enumerate(weeks):
            for ci,day in enumerate(week):
                c,dl,el=s.cells[ri][ci]
                if day==0:
                    dl.config(text='',bg=C['bg']); el.config(text='',bg=C['bg']); c.config(bg=C['bg'])
                    for w in(c,dl,el): w.unbind('<Button-1>')
                    continue
                dl.config(text=str(day),bg=C['card']); el.config(bg=C['card']); c.config(bg=C['card'])
                ds=f'{s.yr:04d}-{s.mo:02d}-{day:02d}'
                # Get daily repeating events using new method
                de=s.dm.get_daily_events(ds)
                etxts=[f'- {e["title"][:10]}' for e in de[:2]]
                if len(de)>2: etxts.append(f'+{len(de)-2}')
                el.config(text='\n'.join(etxts) if de else '')
                ist=(s.yr==today.year and s.mo==today.month and day==today.day)
                if ist: c.config(bg=C['acc']); dl.config(bg=C['acc'],fg='white'); el.config(bg=C['acc'],fg='white')
                elif s.sel==ds: c.config(bg=C['acc_d']); dl.config(bg=C['acc_d']); el.config(bg=C['acc_d'])
                else: dl.config(fg=C['red'] if ci==0 else C['blu'] if ci==6 else C['tx'])
                for w in(c,dl,el): w.bind('<Button-1>',lambda e,d=ds:s._sel(d))
        for ri in range(len(weeks),6):
            for ci in range(7):
                c,dl,el=s.cells[ri][ci]
                dl.config(text='',bg=C['bg']); el.config(text='',bg=C['bg']); c.config(bg=C['bg'])
        if s.sel: s._show_ev(s.sel)
    def _sel(s,ds): s.sel=ds; s.refresh(); s._show_ev(ds)
    def _show_ev(s,ds):
        s.et.config(text=t('schedule_of').format(date=ds))
        for w in s.el.winfo_children(): w.destroy()
        evts=s.dm.get_daily_events(ds)
        if not evts: _lbl(s.el,t('no_events'),10,fg=C['tx2'],bg=C['card']).pack(anchor='w'); return
        for e in evts:
            r=tk.Frame(s.el,bg=C['card']); r.pack(fill='x',pady=2)
            lbl=f"● {e['title']}"
            if e.get('repeat') and e['repeat']!='none': lbl+=f" ↺"
            _lbl(r,lbl,11,bg=C['card']).pack(side='left')
            if e.get('location'): _lbl(r,f"({e['location']})",10,fg=C['tx2'],bg=C['card']).pack(side='left',padx=4)
            if e.get('people'): _lbl(r, f"@{','.join(e['people'][:2])}", 10, fg=C['blu'], bg=C['card']).pack(side='left', padx=4)
            ts=e['start_date'][11:16] if len(e['start_date'])>10 else ''
            if ts:
                te=e['end_date'][11:16] if len(e['end_date'])>10 else ''
                _lbl(r,f" {ts}~{te}",10,fg=C['acc_l'],bg=C['card']).pack(side='left')
            _btn(r,'x',lambda eid=e['id']:Confirm(s,t('confirm_delete_event'),lambda:s._ddel(eid)),bg=C['red'],sz=9,px=6,py=1).pack(side='right')
    def _ddel(s,eid): s.dm.delete_event(eid); s.refresh()
    def _prev(s): s.mo-=1; (s.mo,s.yr)=(12,s.yr-1) if s.mo<1 else (s.mo,s.yr); s.sel=None; s.refresh()
    def _next(s): s.mo+=1; (s.mo,s.yr)=(1,s.yr+1) if s.mo>12 else (s.mo,s.yr); s.sel=None; s.refresh()
    def _jump(s): pass # Token limit logic simplified
    def _add_ev(s):
        m=Modal(s,t('event_add_title'),480,640)
        et=m.field(t('event_name'))
        
        # Routine
        _lbl(m.body,t('repeat'),10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,2))
        rv=tk.StringVar(value='none')
        rf=tk.Frame(m.body,bg=C['card']); rf.pack(fill='x')
        for kv,nm in [('none','none'),('daily','daily'),('weekly','weekly'),('monthly','monthly'),('yearly','yearly')]:
            tk.Radiobutton(rf,text=t('repeat_'+kv),value=kv,variable=rv,font=(FN,10),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card']).pack(side='left')

        dd=s.sel or datetime.now().strftime('%Y-%m-%d')
        sd,st=m.field(t('start'),dd),None
        ed=m.field(t('end'),dd)
        el=m.field(t('location'))
        
        c_vars = {}
        _lbl(m.body, t('attendees'), 10, fg=C['tx2'], bg=C['card']).pack(anchor='w', pady=(8,2))
        cf = tk.Frame(m.body, bg=C['card']); cf.pack(fill='x')
        for c in s.dm.get_contacts()[:8]:
            v = tk.BooleanVar()
            tk.Checkbutton(cf, text=c['name'], variable=v, font=(FN,10), bg=C['card'], fg=C['tx'], selectcolor=C['acc'], activebackground=C['card']).pack(side='left', padx=2)
            c_vars[c['name']] = v
            
        edesc=m.field(t('description'))
        def sv():
            if not et.get().strip(): return
            ppl = [n for n, v in c_vars.items() if v.get()]
            s.dm.add_event(et.get(),sd.get(),ed.get(),el.get(),ppl,edesc.get(),repeat=rv.get()); m.close(); s.refresh()
        m.buttons(sv,t('add'))

class ReminderPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,t('nav_reminder'),22,True).pack(side='left')
        _btn(h,t('add'),s._add).pack(side='right')
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_reminders()
        if not items: _lbl(s.sf.inner,t('reminder_empty'),12,fg=C['tx2']).pack(pady=40); return
        now=datetime.now()
        for r in sorted(items,key=lambda x:x.get('deadline','')): s._card(r,now)
    def _card(s,r,now):
        f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=4,ipady=8)
        done=r.get('is_completed',False)
        l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='both',expand=True,padx=16,pady=8)
        tp=tk.Frame(l,bg=C['card']); tp.pack(fill='x')
        chk=tk.Label(tp,text='[v]' if done else '[ ]',font=(FN,14),bg=C['card'],fg=C['grn'] if done else C['tx'],cursor='hand2')
        chk.pack(side='left',padx=(0,8)); chk.bind('<Button-1>',lambda e:s._tog(r['id']))
        tit=r.get('title','')
        if r.get('repeat') and r['repeat']!='none': tit+=f" ↺ ({t('repeat_'+r['repeat'])})"
        _lbl(tp,tit,14,True,fg=C['tx2'] if done else C['tx'],bg=C['card']).pack(side='left')
        rt=tk.Frame(f,bg=C['card']); rt.pack(side='right',padx=12,pady=8)
        _btn(rt,t('delete'),lambda:s._ddel(r['id']),bg=C['red'],sz=10,px=10,py=4).pack(pady=2)
    def _tog(s,rid): s.dm.toggle_reminder(rid); s.refresh()
    def _ddel(s,rid): s.dm.delete_reminder(rid); s.refresh()
    def _add(s):
        m=Modal(s,t('reminder_add_title'),420,400)
        et=m.field(t('title')); ed=m.field(t('deadline'),datetime.now().strftime('%Y-%m-%d 23:59'))
        edesc=m.field(t('description'))
        _lbl(m.body,t('repeat'),10,fg=C['tx2'],bg=C['card']).pack(anchor='w',pady=(4,2))
        rv=tk.StringVar(value='none')
        rf=tk.Frame(m.body,bg=C['card']); rf.pack(fill='x')
        for kv,nm in [('none','none'),('daily','daily'),('weekly','weekly'),('monthly','monthly')]:
            tk.Radiobutton(rf,text=t('repeat_'+kv),value=kv,variable=rv,font=(FN,10),bg=C['card'],fg=C['tx'],selectcolor=C['acc'],activebackground=C['card']).pack(side='left')
        def sv():
            if not et.get().strip(): return
            s.dm.add_reminder(et.get(),ed.get(),edesc.get(),repeat=rv.get()); m.close(); s.refresh()
        m.buttons(sv,t('add'))

class LedgerPage(tk.Frame):
    def __init__(s,p,dm):
        super().__init__(p,bg=C['bg']); s.dm=dm; s.ft=None
        h=tk.Frame(s,bg=C['bg']); h.pack(fill='x',padx=30,pady=(24,12))
        _lbl(h,t('nav_ledger'),22,True).pack(side='left')
        _btn(h,t('add'),s._add).pack(side='right')
        _btn(h,t('nav_stats'),s._stats,bg=C['acc_l']).pack(side='right',padx=(0,8))
        s.sf=ScrollFrame(s); s.sf.pack(fill='both',expand=True,padx=30,pady=(0,20))
        s.refresh()
        
    def _stats(s):
        m = Modal(s, t('stats_title'), 800, 500)
        ctrl=tk.Frame(m.body,bg=C['card']); ctrl.pack(fill='x',pady=10)
        ysv=tk.IntVar(value=datetime.now().year)
        msv=tk.IntVar(value=datetime.now().month)
        tk.Spinbox(ctrl,from_=2000,to=2099,textvariable=ysv,font=(FN,12),width=6,bg=C['inp'],fg=C['tx']).pack(side='left',padx=4)
        tk.Spinbox(ctrl,from_=1,to=12,textvariable=msv,font=(FN,12),width=4,bg=C['inp'],fg=C['tx']).pack(side='left',padx=4)
        
        chart_fr=tk.Frame(m.body,bg=C['card']); chart_fr.pack(fill='both',expand=True,pady=(0,10))
        
        def _draw():
            for w in chart_fr.winfo_children(): w.destroy()
            y,m_v=ysv.get(),msv.get()
            ld=s.dm.get_ledger('expense')
            exp=[e for e in ld if e['date'].startswith(f"{y:04d}-{m_v:02d}")]
            if not exp:
                _lbl(chart_fr,t('stats_nodata'),14,fg=C['tx2'],bg=C['card']).pack(expand=True); return
            tags={}
            for e in exp: tags[e['tag']]=tags.get(e['tag'],0)+e['amount']
            ls=[t_tag(k) for k in tags.keys()]; vs=list(tags.values())
            
            fig=Figure(figsize=(7,3),facecolor=C['card'])
            ax=fig.add_subplot(121)
            ax.pie(vs,labels=ls,autopct='%1.1f%%',textprops={'color':C['tx']},colors=['#7c3aed','#ec4899','#f97316','#f59e0b','#10b981','#3b82f6'])
            ax.set_title(t('chart_pie'),color=C['tx'])
            
            ax2=fig.add_subplot(122)
            ax2.bar(ls,vs,color='#7c3aed')
            ax2.tick_params(colors=C['tx'])
            ax2.set_facecolor(C['card'])
            ax2.set_title(t('chart_bar'),color=C['tx'])
            
            canvas=FigureCanvasTkAgg(fig,master=chart_fr)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both',expand=True)
            
        _btn(ctrl,'조회',_draw,px=16,py=4).pack(side='left',padx=16)
        _draw()
        
    def refresh(s):
        for w in s.sf.inner.winfo_children(): w.destroy()
        items=s.dm.get_ledger(s.ft)
        for e in sorted(items,key=lambda x:x.get('date',''),reverse=True):
            f=tk.Frame(s.sf.inner,bg=C['card'],highlightbackground=C['brd'],highlightthickness=1); f.pack(fill='x',pady=3,ipady=6)
            ii=e['type']=='income'; clr=C['grn'] if ii else C['red']; sign='+' if ii else '-'
            l=tk.Frame(f,bg=C['card']); l.pack(side='left',fill='x',expand=True,padx=14,pady=4)
            tp=tk.Frame(l,bg=C['card']); tp.pack(fill='x')
            _lbl(tp,t_tag(e.get('tag','')),11,True,bg=C['card']).pack(side='left')
            _lbl(tp,e.get('date',''),10,fg=C['tx2'],bg=C['card']).pack(side='right')
            r=tk.Frame(f,bg=C['card']); r.pack(side='right',padx=14,pady=4)
            _lbl(r,f"{sign}{fmt_money(e['amount'])}",13,True,fg=clr,bg=C['card']).pack()
            _btn(r,'x',lambda eid=e['id']:s.dm.delete_ledger(eid) or s.refresh(),bg=C['red'],sz=9,px=6,py=2).pack(pady=(4,0))
    def _add(s):
        m=Modal(s,t('ledger_add_title'),440,650)
        tv=tk.StringVar(value='expense')
        tk.Radiobutton(m.body,text=t('income'),variable=tv,value='income',bg=C['card'],fg=C['tx'],selectcolor=C['acc']).pack(anchor='w')
        tk.Radiobutton(m.body,text=t('expense'),variable=tv,value='expense',bg=C['card'],fg=C['tx'],selectcolor=C['acc']).pack(anchor='w')
        ea=m.field(t('amount'))

        _lbl(m.body, t('tag'), 10, fg=C['tx2'], bg=C['card']).pack(anchor='w', pady=(8,2))
        tgv = tk.StringVar(value='')
        tgf = tk.Frame(m.body, bg=C['card']); tgf.pack(fill='x')
        def _build_tags():
            for w in tgf.winfo_children(): w.destroy()
            for i, tg in enumerate(s.dm.get_tags()):
                rf = tk.Frame(tgf, bg=C['card']); rf.grid(row=i//3, column=i%3, sticky='w', padx=2, pady=1)
                tk.Radiobutton(rf, text=t_tag(tg), variable=tgv, value=tg, font=(FN,10), bg=C['card'], fg=C['tx'], selectcolor=C['acc'], activebackground=C['card']).pack(side='left')
        _build_tags()
        
        ct=m.field(t('custom_tag'))

        def sv():
            try: amt = float(ea.get())
            except ValueError:
                m.warn(t('amount_error'))
                return
            t_str = ct.get().strip() or tgv.get().strip()
            if not t_str:
                m.warn(t('tag_required'))
                return
            if ct.get().strip() and not s.dm.is_default_tag(ct.get().strip()):
                s.dm.add_tag(ct.get().strip())
                _build_tags()
            s.dm.add_ledger(tv.get(), amt, t_str); m.close(); s.refresh()
        m.buttons(sv,t('add'))


# ═══════════ MAIN W/ PIN LOCK ═══════════
class PersonalManager:
    def __init__(s):
        s.root=tk.Tk(); s.root.title('SDXMQ Schedules Book'); s.root.geometry('1100x750')
        s.root.configure(bg=C['bg']); s.root.minsize(900,600)
        s.dm=DataManager()
        st=s.dm.get_settings()
        set_lang(st.get('language','en')); set_theme(st.get('theme','dark_purple'))
        _apply_colors()
        s.mbtns=[]; s.cur=None; s.sb_fr=None; s.content=None
        s.pages_cache = {}
        
        if st.get('use_pin',False) and st.get('pin',''):
            s._pin_lock(st.get('pin'))
        else:
            s.rebuild()

    def _pin_lock(s, pin):
        for w in s.root.winfo_children(): w.destroy()
        pf=tk.Frame(s.root,bg=C['card'],highlightthickness=2,highlightbackground=C['acc_l'])
        pf.place(relx=0.5,rely=0.5,anchor='center',width=300,height=250)
        _lbl(pf,"SDXMQ's\nSchedules Book",16,True,bg=C['card']).pack(pady=(20,10))
        _lbl(pf,t('pin_prompt'),10,fg=C['tx2'],bg=C['card']).pack()
        pe=_entry(pf,show='*',justify='center'); pe.pack(pady=10)
        ef=_lbl(pf,'',10,fg=C['red'],bg=C['card']); ef.pack()
        def chk():
            if pe.get()==pin: s.rebuild()
            else: ef.config(text=t('pin_wrong')); pe.delete(0,'end')
        _btn(pf,t('open'),chk,px=30).pack(pady=10)
        pe.bind('<Return>',lambda e:chk())

    def rebuild(s, page='search', scroll_pos=0.0):
        s.root.configure(bg=C['bg'])
        for w in s.root.winfo_children(): w.destroy()
        s.mbtns=[]
        s._sb()
        s.content=tk.Frame(s.root,bg=C['bg']); s.content.pack(side='right',fill='both',expand=True)
        s.show(page)
        
        # If we selected settings and want to restore scroll...
        if page == 'settings' and scroll_pos > 0:
            s.root.update_idletasks() # let the frame render
            if 'settings' in s.pages_cache:
                s.pages_cache['settings'].restore_scroll(scroll_pos)

    def _sb(s):
        s.sb_fr=tk.Frame(s.root,bg=C['sb'],width=200); s.sb_fr.pack(side='left',fill='y'); s.sb_fr.pack_propagate(False)
        _lbl(s.sb_fr,"SDXMQ's\nSchedules Book",16,True,bg=C['sb']).pack(pady=(28,24))
        tk.Frame(s.sb_fr,bg=C['brd'],height=1).pack(fill='x',padx=16,pady=(0,12))
        
        # Removed stats so Ledger acts as the entrypoint for Ledger + Stats
        navs=[('search','nav_search'),
              ('contacts','nav_contacts'),
              ('calendar','nav_calendar'),
              ('reminder','nav_reminder'),
              ('ledger','nav_ledger'),
              ('diary','nav_diary'),
              ('settings','nav_settings')]
        
        for key,tkey in navs:
            b=tk.Label(s.sb_fr,text=f'  {t(tkey)}',font=(FN,13),bg=C['sb'],fg=C['tx2'],anchor='w',padx=20,pady=10,cursor='hand2')
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
        
        # Instantiate correctly
        if key=='search': pg = SearchPage(s.content,s.dm,s)
        elif key=='contacts': pg = ContactsPage(s.content,s.dm)
        elif key=='calendar': pg = CalendarPage(s.content,s.dm)
        elif key=='reminder': pg = ReminderPage(s.content,s.dm)
        elif key=='ledger': pg = LedgerPage(s.content,s.dm)
        elif key=='diary': pg = DiaryPage(s.content,s.dm)
        elif key=='settings': pg = SettingsPage(s.content,s.dm,s)
        else:
            pg = tk.Frame(s.content, bg=C['bg'])
            _lbl(pg,"Not implemented yet.",14).pack(pady=40)
            
        pg.pack(fill='both',expand=True)
        s.pages_cache[key] = pg

    def run(s): s.root.mainloop()

if __name__=='__main__': PersonalManager().run()
