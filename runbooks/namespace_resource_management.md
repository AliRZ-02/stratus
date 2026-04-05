Namespace: Resource Quotas Summary

Key Issues:
* Quota Exhaustion: Namespace has reached hard limits for CPU, Memory, Pod counts, or other objects (Services, PVCs).
* Forbidden Operations: "kubectl" or CI/CD pipelines returning "Forbidden" errors during resource creation.
* Scaling Blockage: HPA failing to add replicas because the namespace-wide quota is hit.

Diagnosis:
1.  Quota Status: "kubectl describe resourcequota -n <namespace>" to see current usage vs. hard limits.
2.  Event Analysis: "kubectl get events -n <namespace> --sort-by='.lastTimestamp'" — look for "exceeded quota" messages.
3.  Default Values: Check for "LimitRange" in the namespace; pods without explicit requests may be consuming more quota than intended via defaults.
4.  Resource Audit: Identify orphaned Jobs, completed CronJobs, or oversized Deployments consuming the budget.

Mitigation:
* Quota Adjustment: Increase the "hard" limits in the "ResourceQuota" object if the workload growth is legitimate.
* Cleanup: Delete finished Jobs, unused ConfigMaps/Secrets, or scale down non-essential Deployments.
* Request Tuning: Lower resource "requests" for pods in the namespace to fit more replicas within the existing quota.
* Isolation: Split large namespaces into smaller ones with dedicated quotas to prevent a single application from exhausting shared resources.