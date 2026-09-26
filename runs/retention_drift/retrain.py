import numpy as np, sys, shap
from sklearn.ensemble import GradientBoostingClassifier
R='runs/retention_drift/'
X=np.load(R+'frame/X_train.npy'); y=np.load(R+'frame/y_train.npy'); Xe=np.load(R+'frame/X_eval.npy'); bg=np.load(R+'frame/background.npy')
m=GradientBoostingClassifier(n_estimators=200,max_depth=3,learning_rate=0.1,random_state=20260925).fit(X,y)
p=m.predict_proba(Xe)[:,1]
for o in sys.argv[1:]:
    pa=np.load(R+f'archive/{o}/p_gbc.npy'); den=np.load(R+f'archive/{o}/denied_gbc.npy')
    nd=np.sort(np.argsort(-p,kind='mergesort')[:200])
    sv=np.asarray(shap.TreeExplainer(m,data=bg,feature_perturbation='interventional').shap_values(Xe))
    if sv.ndim==3: sv=sv[...,1]
    A=np.load(R+f'archive/{o}/attr_gbc_tree.npy')
    top=lambda r: frozenset(i for i in np.argsort(-r,kind='mergesort')[:4] if r[i]>0)
    print(o,'max|dP|',np.abs(p-pa).max(),'denied flips',len(set(den)^set(nd))//2,'R_tree',np.mean([top(sv[i])!=top(A[i]) for i in den]))
