import sys, numpy as np
sys.path.insert(0,"scripts/policy_kill"); import run
from sklearn.tree import DecisionTreeClassifier
rng=np.random.RandomState(0); n=20000
X=np.zeros((n,11)); X[:,0]=rng.randint(620,820,n).astype(float); X[:,1]=rng.randint(10,50,n); X[:,2]=rng.randint(40,97,n)
# SYNTHETIC test fixture: default prob INCREASES with FICO (violation) - single split
y=(rng.rand(n) < np.where(X[:,0]>700,0.3,0.05)).astype(int)
for depth in (1,2):
    t=DecisionTreeClassifier(max_depth=depth,min_samples_leaf=500).fit(X[:,[0,1,2]],y)
    m={"feats":np.array([0,1,2]),"tree":t}
    print("depth",depth,"fico cuts",np.unique(t.tree_.threshold[t.tree_.feature==0]))
    thr=run.decline_threshold(m,X)
    print(" violates decision:",run.violates(m,X[:1000],thr,"decision",{"fico_range_low"}),
          " prob:",run.violates(m,X[:1000],thr,"prob",{"fico_range_low"}))
    c=np.unique(t.tree_.threshold[t.tree_.feature==0])[0]
    print(" float32(c+1e-6)<=c ?", np.float32(c+1e-6)<=c)
