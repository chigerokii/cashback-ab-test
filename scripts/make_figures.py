"""Графики для README. Запуск из корня репозитория: python scripts/make_figures.py"""
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
BLUE='#2b6cb0'; LIGHT='#90cdf4'; GREY='#a0aec0'; ORANGE='#dd6b20'
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.titleweight':'bold','axes.spines.top':False,'axes.spines.right':False,
                     'axes.grid':True,'grid.alpha':.25,'axes.axisbelow':True,'legend.frameon':False})
f=lambda x,d=0: f'{x:,.{d}f}'.replace(',',' ').replace('.',',')

d=pd.read_csv('data/cashback.csv')
cats=['Air','Beauty shop','Book store','Children','Cinema','Clothes','Electronics','Fastfood','Fuel','House','Jewelry','Other','Pet shop','Pharmacies','Supermarkets','Transport']
ru={'Air':'Авиабилеты','Beauty shop':'Красота','Book store':'Книги','Children':'Детские товары','Cinema':'Кино','Clothes':'Одежда','Electronics':'Электроника',
    'Fastfood':'Фастфуд','Fuel':'Топливо','House':'Дом','Jewelry':'Ювелирка','Other':'Прочее','Pet shop':'Зоотовары','Pharmacies':'Аптеки','Supermarkets':'Супермаркеты','Transport':'Транспорт'}
d['spend_after']=d[cats].sum(axis=1); d['spend_before']=d[[c+'_before' for c in cats]].sum(axis=1)
d['cb_after']=d.cb_merch_last_3_month+d.cb_bank_last_3_month; d['cb_before']=d.cb_merch_before+d.cb_bank_before

# 1. KPI до/после
k={'Траты на клиента, ₽':(d.spend_before.mean(),d.spend_after.mean(),0),
   'Кэшбэк на клиента, ₽':(d.cb_before.mean(),d.cb_after.mean(),0),
   'Кэшбэк к тратам, %':(100*d.cb_before.sum()/d.spend_before.sum(),100*d.cb_after.sum()/d.spend_after.sum(),1),
   'Клиенты с кэшбэком, %':(100*(d.cb_before>0).mean(),100*(d.cb_after>0).mean(),0)}
fig,axes=plt.subplots(1,4,figsize=(13,3.3))
for ax,(name,(a,b,dec)) in zip(axes,k.items()):
    bars=ax.bar(['до','после'],[a,b],color=[GREY,BLUE],width=.6)
    ax.bar_label(bars,[f(a,dec),f(b,dec)],padding=3); ax.set_title(name,fontsize=10.5)
    ch=(b/a-1)*100; ax.text(0.5,0.92,f'{"+" if ch>0 else ""}{f(ch,0)}%',transform=ax.transAxes,ha='center',color=ORANGE,fontweight='bold')
    ax.set_yticks([]); ax.set_ylim(0,max(a,b)*1.3); ax.grid(False)
fig.suptitle('После обновления клиенты тратят больше, а кэшбэка получают меньше',fontweight='bold',y=1.03)
fig.tight_layout(); fig.savefig('images/kpi_before_after.png',bbox_inches='tight',dpi=130); plt.close()

# 2. Кэшбэк по числу коммуникаций
g=d.assign(n=d.cnt_communication.clip(upper=8)).groupby('n')
fig,ax=plt.subplots(figsize=(8,4))
ax.plot(g.cb_before.median().index,g.cb_before.median().values,'o-',color=GREY,label='до обновления')
ax.plot(g.cb_after.median().index,g.cb_after.median().values,'o-',color=BLUE,label='после обновления')
ax.set_xticks(range(9)); ax.set_xticklabels([*map(str,range(8)),'8+'])
ax.set_xlabel('Число коммуникаций о кэшбэке'); ax.set_ylabel('Медианный кэшбэк, ₽')
ax.set_title('После обновления кэшбэк достаётся тем, с кем банк чаще общается'); ax.legend()
fig.tight_layout(); fig.savefig('images/cashback_vs_communications.png',dpi=130); plt.close()

# 3. Изменение трат по категориям
ch=pd.Series({ru[c]:(d[c].sum()/d[c+'_before'].sum()-1)*100 for c in cats}).sort_values()
fig,ax=plt.subplots(figsize=(8,5))
bars=ax.barh(ch.index,ch.values,color=[BLUE if v>0 else ORANGE for v in ch.values])
ax.bar_label(bars,[f'{"+" if v>0 else ""}{f(v,0)}%' for v in ch.values],padding=3,fontsize=9)
ax.axvline(0,color='#4a5568',lw=.8); ax.set_xlim(min(ch.min()*1.6,-5),ch.max()*1.15); ax.set_xlabel('Изменение трат после обновления, %')
ax.set_title('Траты выросли почти во всех категориях, на электронику почти вдвое')
fig.tight_layout(); fig.savefig('images/spend_change_by_category.png',dpi=130); plt.close()
print(ch.round(1).to_string()); print({n:(round(a,1),round(b,1)) for n,(a,b,_) in k.items()})
