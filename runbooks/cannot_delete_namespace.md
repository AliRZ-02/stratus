Issue:
- Namespace stuck in Terminating state indefinitely. Caused by unprocessed finalizers on the namespace or its resources, missing/failed custom resource controllers (e.g. Istio, Prometheus Operator, cert-manager), deleted CRDs leaving orphaned resources, or a stuck kube-controller-manager namespace controller.

Diagnosis:
- Check metadata.finalizers on the namespace; list all remaining resources and their finalizers; inspect controller pod status and logs for finalizer processing errors; check for deleted CRDs whose resources still exist in the namespace; review API server logs for finalizer timeout/errors.

Mitigation:
- If controller is healthy, resolve its errors so it can process finalizers. If controller is missing/deleted, manually patch and remove finalizers from affected resources. If CRDs were deleted, manually remove finalizers from orphaned resources. If kubernetes finalizer is stuck, verify kube-controller-manager health and check namespace controller logs.