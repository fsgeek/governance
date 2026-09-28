"""Adversary re-analysis: identical tree sample (optionally different sampler seed), fixed violation check."""
import sys, json, pickle, numpy as np
sys.path.insert(0,"scripts/policy_kill"); import run
S=sys.argv[1]; sseed=int(sys.argv[2])
def violates_fixed(m, Xprobe, thr, level, features):
    t=m["tree"].tree_; used={run.FEATURES[m["feats"][j]]:j for j in range(len(m["feats"]))}
    for fname,sign in run.MONO.items():
        if fname not in used or fname not in features: continue
        j=used[fname]; cuts=np.unique(t.threshold[t.feature==j])
        if len(cuts)==0: continue
        up=np.nextafter(cuts.astype(np.float32), np.float32(np.inf)).astype(float)
        grid=np.concatenate([[cuts.min()-1.0], up])
        Z=np.repeat(Xprobe,len(grid),axis=0); col=m["feats"][j]; Z[:,col]=np.tile(grid,len(Xprobe))
        p=run.p_default(m,Z).reshape(len(Xprobe),len(grid))
        v=p if level=="prob" else (p>=thr).astype(float)
        if ((np.diff(v,axis=1)*sign)< -1e-12).any(): return True
    return False
Xtr,ytr,Xva,yva,Xte,yte,n=run.frame()
run.SEED=sseed; trees=run.sample_trees(Xtr,ytr,Xva,yva); run.SEED=20260928
best=min(m["val_logloss"] for m in trees)
probe=Xva[np.random.RandomState(run.SEED+1).choice(len(Xva),run.N_PROBE,replace=False)]
out={"sampler_seed":sseed,"by_eps":{}}; rng=np.random.RandomState(7)
noMI=set(run.MONO)-{"mortgage_insurance_pct"}
for eps in [0.005,0.01,0.015,0.02]:
    R=[m for m in trees if m["val_logloss"]<=best*(1+eps)]
    if len(R)<2: out["by_eps"][str(eps)]={"n_R":len(R)}; continue
    thrs=[run.decline_threshold(m,Xva) for m in R]
    D=np.stack([(run.p_default(m,Xte)>=th) for m,th in zip(R,thrs)]).astype(float)
    def pf(idx): s=D[idx].mean(0); return np.minimum(s,1-s)
    pfR=pf(np.arange(len(R))); aR=pfR>0
    def jac(idx): a=pf(idx)>0; return (a&aR).sum()/(a|aR).sum()
    e={"n_R":len(R),"declined_share_mean":float(D.mean())}
    for name,chk in (("orig",run.violates),("fixed",violates_fixed)):
        viol=[chk(m,probe,th,"decision",noMI) for m,th in zip(R,thrs)]
        fico=[chk(m,probe,th,"decision",{"fico_range_low"}) for m,th in zip(R,thrs)]
        keep=np.array([k for k in range(len(R)) if not viol[k]])
        keepF=np.array([k for k in range(len(R)) if not fico[k]])
        d={"n_RP":len(keep),"retention":len(keep)/len(R),"fico_only_n_RP":len(keepF)}
        if len(keep)>=2:
            d["jaccard"]=float(jac(keep)); d["delta_mean_pflip"]=float(pf(keep).mean()-pfR.mean())
            d["jaccard_fico_only"]=float(jac(keepF)) if len(keepF)>=2 else None
            nul=np.array([jac(rng.choice(len(R),len(keep),replace=False)) for _ in range(1000)])
            d["null_p05_p50"]=[float(np.percentile(nul,5)),float(np.percentile(nul,50))]; d["frac_null_leq"]=float((nul<=d["jaccard"]).mean())
            # leave-one-violator-out / leave-one-member-out fragility
            jl=[]
            for k in range(len(R)):
                idxR=np.array([i for i in range(len(R)) if i!=k]); kk=np.array([i for i in keep if i!=k])
                Dm=D[idxR].mean(0); aRm=np.minimum(Dm,1-Dm)>0; a=(pf(kk)>0)
                jl.append(float((a&aRm).sum()/(a|aRm).sum()))
            d["loo_jaccard_min_max"]=[min(jl),max(jl)]; d["loo_frac_above_0.70"]=float(np.mean(np.array(jl)>0.70))
            d["violator_leafsizes"]=[int(R[k]["tree"].min_samples_leaf) for k in range(len(R)) if viol[k]]
            d["violator_rank_by_valloss"]=[int(r) for r in np.argsort(np.argsort([m["val_logloss"] for m in R]))[np.array(viol,bool)]]
            # disagreement contribution: share of ambiguous-only-because-of-violators
        e[name]=d
    # ambiguity singletons: applicants where exactly one member dissents
    cnt=D.sum(0); e["amb_by_single_dissenter_frac"]=float(((cnt==1)|(cnt==len(R)-1)).sum()/aR.sum())
    out["by_eps"][str(eps)]=e
json.dump(out,open(f"{S}/rerun_{sseed}.json","w"),indent=1); print(json.dumps(out,indent=1))
