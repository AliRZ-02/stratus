ConfigMapNotFound:

Issues:
Pods fail to start because a referenced ConfigMap does not exist. Caused by: ConfigMap never created or was deleted, ConfigMap exists in a different namespace, incorrect/misspelled name in pod spec, or a Helm/Kustomize/operator deployment that failed to create it.

Diagnosis:
- Check pod events for "FailedMount" — note the exact ConfigMap name in the error
- List ConfigMaps in the pod's namespace to confirm it's missing
- Search across all namespaces to check if ConfigMap exists elsewhere (cross-namespace access is not supported)
- Compare ConfigMap name in pod/deployment spec exactly — check for typos or case mismatches
- If managed by Helm/Kustomize/operator: verify that tooling completed successfully

Mitigation:
- If missing: create the ConfigMap in the same namespace as the pod
- If in wrong namespace: recreate it in the correct namespace
- If name is wrong: fix the reference in the pod/deployment spec and redeploy
- If managed by tooling: re-run Helm/Kustomize or fix the operator that should have created it
