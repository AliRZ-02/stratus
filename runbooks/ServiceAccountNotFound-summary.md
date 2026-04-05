ServiceAccountNotFound:

Issues:
Pods fail to start because a referenced ServiceAccount does not exist. Caused by: SA never created or was deleted, SA exists in a different namespace, incorrect/misspelled "serviceAccountName" in pod spec, SA creation failed (quota, admission webhook), or pod scheduled before SA was created during namespace setup.

Diagnosis:
- Check pod events for "serviceaccount not found"
- Confirm SA exists in the same namespace as the pod ("kubectl get serviceaccount <name> -n <namespace>")
- Search across namespaces to check if SA exists elsewhere
- Compare "serviceAccountName" in deployment spec against actual SA names — check for typos, hyphens vs underscores
- If SA exists but pods still fail: verify "automountServiceAccountToken" is not set to "false"; for K8s 1.24+, confirm a token Secret was explicitly created if needed
- Correlate failure with recent rollouts, GitOps syncs, or namespace migrations that may have changed the SA reference or deleted the SA

Mitigation:
- If SA missing: create the ServiceAccount in the correct namespace
- If SA in wrong namespace: recreate it in the pod's namespace
- If name is wrong: fix "serviceAccountName" in the deployment spec and redeploy
- If SA was deleted by a controller/cleanup policy: restore it and prevent future deletion
- If token missing (K8s 1.24+): manually create a ServiceAccount token Secret
