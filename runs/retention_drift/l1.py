import numpy as np, shap, xgboost as xgb, sys
R='runs/retention_drift/'
m=xgb.XGBClassifier(); m.load_model(R+'archive/v2021/xgb.json')
X=np.load(R+'frame/X_eval.npy'); bg=np.load(R+'frame/background.npy')
den=np.load(R+'archive/v2021/denied_xgb.npy'); A=np.load(R+'archive/v2021/attr_xgb_kernel_default.npy')
n=40
ex=shap.KernelExplainer(lambda Z: m.predict_proba(Z)[:,1], bg[:50])
np.random.seed(20260925)
sv=np.asarray(ex.shap_values(X[den[:n]], nsamples=2048, l1_reg=sys.argv[1], silent=True))
if sv.ndim==3: sv=sv[...,0]
top=lambda r: frozenset(i for i in np.argsort(-r,kind='mergesort')[:4] if r[i]>0)
print(sys.argv[1], 'maxdiff', np.abs(sv-A[:n]).max(), 'setchanged', np.mean([top(a)!=top(b) for a,b in zip(sv,A[:n])]))
