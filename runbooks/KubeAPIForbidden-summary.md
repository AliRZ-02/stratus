KubeAPIForbidden: (403)

Issues:
API server returns 403 Forbidden, blocking operations for a user or service account. Caused by: missing rules in a Role/ClusterRole, subject not listed in Role/ClusterRoleBinding, binding deleted or modified, ClusterRole aggregation misconfiguration, namespace scope mismatch (ClusterRole vs Role), or admission webhook/OPA policy blocking the request.

Diagnosis:
- Confirm the exact denied permission: "kubectl auth can-i <verb> <resource> -n <namespace> --as=system:serviceaccount:<namespace>:<sa-name>"
- List all granted permissions: "kubectl auth can-i --list -n <namespace> --as=..."
- Describe the relevant Role/ClusterRole — verify it includes the required verb+resource rule
- Describe the RoleBinding/ClusterRoleBinding — confirm the subject is listed with correct name/namespace format ("system:serviceaccount:<ns>:<sa>")
- Check for aggregated ClusterRoles: verify "aggregationRule" labels and that child ClusterRoles still exist
- Check for admission webhooks: "kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations"
- Correlate error onset with: Role/Binding modifications, SA changes, deployments, cluster upgrades, namespace creation

Mitigation:
- If Role missing rules: add the required verb+resource to the Role/ClusterRole
- If subject missing from binding: add subject to the RoleBinding/ClusterRoleBinding
- If binding deleted: recreate RoleBinding/ClusterRoleBinding with correct subjects and role reference
- If namespace scope wrong: use RoleBinding for namespace-scoped resources; ClusterRoleBinding for cluster-wide
- If aggregation broken: fix "aggregationRule" labels or restore missing child ClusterRoles
- If admission webhook blocking: review and update webhook rules
