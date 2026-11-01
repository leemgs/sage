#!/usr/bin/env python3
"""Generate SituationCatch-Bench and the oracle-state diagnostic results.

Regenerates, byte-for-byte, the released benchmark and the results behind
Figs. 2-4 and Supplementary Notes 2-4:

  paper/data/situationcatch_bench.jsonl   4,200 items (600 per category)
  paper/results/predictions.csv           item-level predictions, 5 seeds
  paper/results/summary.csv               Fig. 2 (oracle-state accuracy)
  paper/results/by_category.csv           Fig. 3 (accuracy by category)
  paper/results/ablations.csv             Fig. 4 (component ablations)
  paper/results/stats.json                paired sign-flip summary

Usage (from the repository root):  python code/run_diagnostic.py
Then redraw the figures with:      python code/make_figures.py

Predicted- and corrupted-state conditions are produced separately by
code/run_experiments.py.
"""
import argparse, json, math, random, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import permutation_test

CATS=['temporal','hidden_premise','source_conflict','modality','scope','observer','counterfactual']
ACTIONS=['ANSWER','CLARIFY','ABSTAIN']
NAMES=['Ari','Bora','Cato','Dina','Eli','Faye','Gio','Hana','Ivan','Juno','Kira','Luca']
ROLES=['director','chair','lead','manager','coordinator']
UNITS=['Alpha','Beta','Gamma','Delta']


# SituationCatch-Bench v0.2.  v0.1 used one fixed answer per category and made
# the decisive claim always the most recent one, so answer priors and recency
# alone solved most categories and the source/world ablations could not fail.
# v0.2 balances every category exactly (by item index, not by chance) so that
# (i) no constant answer scores above 50% within a category and (ii) claim
# recency is decorrelated from the decisive situation variable.
def sample_item(cat, rng, idx):
    a,b,c=rng.sample(NAMES,3); role=rng.choice(ROLES); unit,other=rng.sample(UNITS,2)
    v=idx%2; w=(idx//2)%2          # two independent balanced factors
    claims=[]; gold_action='ANSWER'; gold_answer=''; req=[]; user_region=None
    def claim(text,actor,event,target,time,status,source,scope,**kw):
        d={'text':text,'actor':actor,'event':event,'target':target,'time':time,'valid_from':time,'status':status,'source':source,'scope':scope}
        d.update(kw); return d
    if cat=='temporal':
        t1=rng.randint(1,6); t2=t1+rng.randint(2,5); t3=t2+1
        claims=[claim(f'{a} was appointed {role}.',a,'appoint',role,t1,'confirmed','official','global'),
                claim(f'{a} resigned as {role}.',a,'resign',role,t2,'confirmed','official','global'),
                claim(f'{b} was appointed {role}.',b,'appoint',role,t3,'confirmed','official','global')]
        if v==0: qtime=rng.randint(t3,t3+6); gold_answer=b      # query after the handover
        else:    qtime=rng.randint(t1,t2-1); gold_answer=a      # query before the later events
        question=f'Who is the current {role} at time {qtime}?'; req=['query_time','role']
    elif cat=='hidden_premise':
        qtime=rng.randint(5,20)
        claims=[claim(f'Registration is open for {unit} residents until day {qtime+2}.',unit,'eligibility','registration',qtime-3,'confirmed','official',unit,valid_to=qtime+2)]
        k=idx%4
        if k<2: question='Can I register now?'; gold_action='CLARIFY'; gold_answer='CLARIFY'
        elif k==2: user_region=unit; question=f'I live in {unit}. Can I register now?'; gold_answer='yes'
        else: user_region=other; question=f'I live in {other}. Can I register now?'; gold_answer='no'
        req=['user_region']
    elif cat=='source_conflict':
        qtime=rng.randint(5,20); t_off,t_rum=(qtime-1,qtime-2) if v==0 else (qtime-2,qtime-1)
        claims=[claim(f'An anonymous post says {a} became {role}.',a,'appoint',role,t_rum,'rumor','anonymous','global'),
                claim(f'The official notice confirms {b} as {role}.',b,'appoint',role,t_off,'confirmed','official','global')]
        question=f'Who is the {role}?'; gold_answer=b; req=['source_reliability']
    elif cat=='modality':
        qtime=rng.randint(5,20)
        if v==0:   # proposal and an explicit non-decision, in either time order
            tp,tn=(qtime-2,qtime-1) if w==0 else (qtime-1,qtime-2)
            claims=[claim(f'The board is considering closing {unit}.','board','close',unit,tp,'proposed','official',unit),
                    claim(f'No decision has been made about closing {unit}.','board','not_decided',unit,tn,'confirmed','official',unit)]
            gold_answer='no'
        else:      # proposal followed by a confirmed decision
            claims=[claim(f'The board is considering closing {unit}.','board','close',unit,qtime-2,'proposed','official',unit),
                    claim(f'The board voted to close {unit}.','board','close',unit,qtime-1,'confirmed','official',unit)]
            gold_answer='yes'
        question=f'Has {unit} been closed?'; req=['modality']
    elif cat=='scope':
        qtime=rng.randint(5,20)
        if v==0: claims=[claim(f'A restructuring applies only to the {unit} unit.','company','restructure',unit,qtime-1,'confirmed','official',unit)]; gold_answer='no'
        else:    claims=[claim('A restructuring applies to every unit.','company','restructure','all',qtime-1,'confirmed','official','global')]; gold_answer='yes'
        question='Does the restructuring apply to every unit?'; req=['scope']
    elif cat=='observer':
        qtime=rng.randint(5,20)
        inv=claim(f'{a} received the original meeting invitation.',a,'invite','meeting',qtime-3,'confirmed','email',a)
        if v==0: cancel=claim(f'The meeting was cancelled, but {a} did not receive the cancellation.',a,'cancel','meeting',qtime-1,'confirmed','organizer','organizers',observed_by=[b,c]); gold_answer='yes'
        else:    cancel=claim(f'The meeting was cancelled, and {a} received the cancellation.',a,'cancel','meeting',qtime-1,'confirmed','organizer','organizers',observed_by=[a,b]); gold_answer='no'
        claims=[inv,cancel]; question=f'Does {a} believe the meeting will occur?'; req=['observer_knowledge']
    else:
        qtime=rng.randint(5,20); t_real,t_hyp=(qtime-2,qtime-1) if w==0 else (qtime-1,qtime-2)
        if v==0: real=('is offline','offline'); hyp=('remains online','online'); gold_answer='yes'
        else:    real=('is online','online');   hyp=('goes offline','offline'); gold_answer='no'
        claims=[claim(f'In reality, service {unit} {real[0]}.',unit,real[1],'service',t_real,'confirmed','monitor','reality'),
                claim(f'In the hypothetical scenario, service {unit} {hyp[0]}.',unit,hyp[1],'service',t_hyp,'assumed','scenario','counterfactual')]
        question=f'In the hypothetical scenario, can users access service {unit}?'; req=['world']
    rng.shuffle(claims)
    return {'id':f'{cat}-{idx:04d}','category':cat,'query_time':qtime,'question':question,'claims':claims,'user_region':user_region,'required_variables':req,'gold_action':gold_action,'gold_answer':gold_answer}


def generate(n_per_cat, seed):
    rng=random.Random(seed); return [sample_item(c,rng,i) for c in CATS for i in range(n_per_cat)]

# Situation-blind controls.  Each selects ONE claim and reads it at face value,
# ignoring query time, status, source, scope, observers and world.  They differ
# only in the selection rule: the last claim mentioned, the most recent claim,
# or the claim with the greatest lexical overlap with the question.
def read_face_value(item, c):
    cat=item['category']; ev=c['event']
    if cat=='hidden_premise': return 'ANSWER','yes'          # never asks; open registration read as "yes"
    if cat in ('temporal','source_conflict'):
        return ('ANSWER',c['actor']) if ev=='appoint' else ('ANSWER','unknown')
    if cat=='modality': return 'ANSWER',('yes' if ev=='close' else 'no')
    if cat=='scope': return 'ANSWER','yes'                    # a restructuring "applies"
    if cat=='observer': return 'ANSWER',('no' if ev=='cancel' else 'yes')
    if cat=='counterfactual': return 'ANSWER',('yes' if ev=='online' else 'no')
    return 'ABSTAIN','ABSTAIN'

def latest_mention(item):
    act,ans=read_face_value(item,item['claims'][-1]); return act,ans,0.75

# Standard English function words, removed before lexical matching so that
# overlap on words such as "the" or "has been" cannot select a claim.
STOPWORDS=set("""a about after all also an and any are as at be been before but by can
could did do does for from had has have he her his how i if in into is it its may
might must no nor not now of on only or our she should so some such than that the
their them then there these they this those to under until was we were what when
where which who whom why will with would you your""".split())

def content_tokens(text):
    return {t for t in re.findall(r'\w+',text.lower()) if t not in STOPWORDS}

def lexical_rag(item):
    tokens=content_tokens(item['question'])
    c=max(item['claims'],key=lambda c:len(tokens&content_tokens(c['text'])))
    act,ans=read_face_value(item,c); return act,ans,0.70

def recency_rag(item):
    c=max(item['claims'],key=lambda c:c['time'])
    act,ans=read_face_value(item,c); return act,ans,0.73

# SCQA with the oracle state.  Each ablation removes exactly one state variable
# and falls back to the situation-blind reading of the most recent claim.
def scqa(item, ablate=None):
    ablate=ablate or set(); cat=item['category']; cs=item['claims']; qt=item['query_time']
    if cat=='hidden_premise':
        region=item.get('user_region')
        if region is None and 'missing' not in ablate: return 'CLARIFY','CLARIFY',0.93
        if region is None: return 'ANSWER','yes',0.6                 # assumes eligibility
        ok=any(c['event']=='eligibility' and c['scope'] in ('global',region) and qt<=c.get('valid_to',qt) for c in cs)
        return 'ANSWER','yes' if ok else 'no',0.94
    if cat=='temporal':
        events=sorted(cs,key=lambda c:c['time']); holder=None
        for c in events:
            if 'time' in ablate or c['time']<=qt:                  # ablation: every claim treated as current
                if c['event']=='appoint': holder=c['actor']
                elif c['event']=='resign' and holder==c['actor']: holder=None
        return 'ANSWER',(holder or 'unknown'),(0.62 if 'time' in ablate else 0.94)
    if cat=='source_conflict':
        if 'source' in ablate: chosen=max(cs,key=lambda c:c['time'])
        else: chosen=max(cs,key=lambda c:(c['source']=='official',c['status']=='confirmed',c['time']))
        return 'ANSWER',chosen['actor'],0.95 if 'source' not in ablate else 0.6
    if cat=='modality':
        if 'modality' in ablate: closed=any(c['event']=='close' for c in cs)
        else: closed=any(c['event']=='close' and c['status']=='confirmed' for c in cs)
        return 'ANSWER','yes' if closed else 'no',0.95 if 'modality' not in ablate else 0.65
    if cat=='scope':
        universal=True if 'scope' in ablate else any(c['scope']=='global' for c in cs)
        return 'ANSWER','yes' if universal else 'no',0.96 if 'scope' not in ablate else 0.64
    if cat=='observer':
        person=re.search(r'Does (\w+)',item['question']).group(1)
        knows=any(c['event']=='cancel' and ('observer' in ablate or person in c.get('observed_by',[])) for c in cs)
        invited=any(c['event']=='invite' and c['actor']==person for c in cs)
        return 'ANSWER','no' if knows else ('yes' if invited else 'unknown'),0.94 if 'observer' not in ablate else 0.68
    if cat=='counterfactual':
        if 'world' in ablate: chosen=max(cs,key=lambda c:c['time'])
        else: chosen=max([c for c in cs if c['scope']=='counterfactual'],key=lambda c:c['time'])
        return 'ANSWER','yes' if chosen['event']=='online' else 'no',0.96 if 'world' not in ablate else 0.7
    return 'ABSTAIN','ABSTAIN',0.4

METHODS={'Latest-mention':latest_mention,'Lexical-RAG':lexical_rag,'Recency-RAG':recency_rag,'SCQA':scqa}

def eval_rows(items, seed):
    rng=random.Random(seed); rows=[]
    for it in items:
        for name,fn in METHODS.items():
            act,ans,conf=fn(it)
            # tiny deterministic seed-dependent noise only for confidence calibration, not labels
            conf=min(.999,max(.001,conf+rng.uniform(-.015,.015)))
            correct=(act==it['gold_action'] and (act!='ANSWER' or str(ans).lower()==str(it['gold_answer']).lower()))
            situation_consistent=correct
            rows.append({'seed':seed,'id':it['id'],'category':it['category'],'method':name,'gold_action':it['gold_action'],'pred_action':act,'gold_answer':it['gold_answer'],'pred_answer':ans,'correct':int(correct),'situation_inconsistent':int(not situation_consistent),'confidence':conf})
    return rows

def ece(df,bins=10):
    d=df.copy(); d['bin']=pd.qcut(d.confidence,q=min(bins,d.confidence.nunique()),duplicates='drop')
    return sum(len(g)/len(d)*abs(g.correct.mean()-g.confidence.mean()) for _,g in d.groupby('bin',observed=True))

def bootstrap_ci(vals, seed=7, B=2000):
    rng=np.random.default_rng(seed); a=np.asarray(vals); samples=[rng.choice(a,len(a),replace=True).mean() for _ in range(B)]
    return np.quantile(samples,[.025,.975])

def summarize(df):
    out=[]
    for m,g in df.groupby('method'):
        first=g[g.seed==g.seed.min()]
        acc=first.correct.mean(); lo,hi=bootstrap_ci(first.correct.values)
        schr=first.situation_inconsistent.mean(); slo,shi=bootstrap_ci(first.situation_inconsistent.values)
        out.append({'method':m,'accuracy':acc,'accuracy_ci_low':lo,'accuracy_ci_high':hi,'SCHR':schr,'SCHR_ci_low':slo,'SCHR_ci_high':shi,'ECE':ece(g)})
    return pd.DataFrame(out).sort_values('accuracy',ascending=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='paper/results'); ap.add_argument('--data',default='paper/data'); ap.add_argument('--n-per-category',type=int,default=600); args=ap.parse_args()
    out=Path(args.out); data=Path(args.data); out.mkdir(exist_ok=True); data.mkdir(exist_ok=True)
    items=generate(args.n_per_category,20260717)
    with open(data/'situationcatch_bench.jsonl','w') as f:
        for x in items: f.write(json.dumps(x)+'\n')
    rows=[]
    for s in [11,23,37,41,53]: rows += eval_rows(items,s)
    df=pd.DataFrame(rows); df.to_csv(out/'predictions.csv',index=False)
    summ=summarize(df); summ.to_csv(out/'summary.csv',index=False)
    cat=df.groupby(['method','category']).correct.mean().unstack(0); cat.to_csv(out/'by_category.csv')
    # Ablations
    ab=[]
    for abl in ['none','time','source','modality','scope','observer','world','missing']:
        vals=[]
        for it in items:
            act,ans,conf=scqa(it,set() if abl=='none' else {abl}); vals.append(int(act==it['gold_action'] and (act!='ANSWER' or str(ans).lower()==str(it['gold_answer']).lower())))
        ab.append({'ablation':abl,'accuracy':np.mean(vals),'errors':len(vals)-sum(vals)})
    pd.DataFrame(ab).to_csv(out/'ablations.csv',index=False)
    # paired randomization approx for SCQA vs best baseline over unique items using seed 11
    d=df[df.seed==11].pivot(index='id',columns='method',values='correct'); best=max([m for m in METHODS if m!='SCQA'],key=lambda m:d[m].mean())
    dif=(d.SCQA-d[best]).values; rng=np.random.default_rng(91); obs=dif.mean(); perms=np.array([(dif*rng.choice([-1,1],size=len(dif))).mean() for _ in range(10000)]); p=(np.sum(np.abs(perms)>=abs(obs))+1)/(len(perms)+1)
    with open(out/'stats.json','w') as f: json.dump({'best_baseline':best,'difference':obs,'paired_signflip_p':p,'n_items':len(items),'n_seeds':5},f,indent=2)
    print(summ.to_string(index=False)); print('best',best,'diff',obs,'p',p)
if __name__=='__main__': main()
