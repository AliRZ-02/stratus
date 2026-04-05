Issue:
- Namespace stuck in Terminating state. Caused by resources with unprocessed finalizers, absent or failed operator controllers, deleted CRDs leaving orphaned resources, or API server connectivity issues preventing finalizer processing.

Diagnosis:
- Check metadata.finalizers on the namespace; list all remaining resources; verify responsible controller pods are running; check for orphaned resources whose CRD/API group no longer exists; confirm API server health and responsiveness.

Mitigation:
- If controller is present but unhealthy, restore it so finalizers are processed. If controller is gone, manually remove finalizers from blocked resources. If CRDs are deleted, manually patch orphaned resources to strip finalizers. If kubernetes finalizer is stuck with no remaining resources, check kube-controller-manager logs for namespace controller errors.