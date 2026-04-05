PodSecretAccessFailure:

Issues:
Pods fail to start or crash because a referenced Secret is inaccessible. Caused by: Secret does not exist or was deleted, Secret is in a different namespace, incorrect/misspelled Secret name or key, insufficient RBAC permissions for the pod's service account, invalid "imagePullSecrets" (wrong type or bad credentials), or admission webhook/PodSecurityPolicy blocking access.

Diagnosis:
- Check pod events for "FailedMount", "secret not found", or "forbidden" — note the exact Secret name and error type
- Confirm Secret exists in the same namespace as the pod (cross-namespace access not supported natively)
- If "forbidden": verify the pod's service account has a Role/RoleBinding granting "get" on Secrets in that namespace
- If image pull failure: confirm "imagePullSecrets" references a Secret of type "kubernetes.io/dockerconfigjson" with valid credentials
- If "FailedMount": verify Secret key names in "volumeMounts"/"env.valueFrom" exactly match keys in the Secret's data
- Check if Secret type matches its intended usage; verify data is not empty or malformed

Mitigation:
- If Secret missing: recreate it in the correct namespace
- If name/key mismatch: fix references in the pod/deployment spec and redeploy
- If RBAC issue: create or fix Role and RoleBinding for the pod's service account
- If "imagePullSecrets" invalid: recreate the Secret with correct registry credentials
- If admission controller blocking: review webhook/PSP policies restricting Secret access
