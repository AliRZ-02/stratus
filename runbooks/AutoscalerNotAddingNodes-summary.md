AutoscalerNotAddingNodes

Issues:
Cluster autoscaler fails to provision new nodes despite pending/unschedulable pods. Caused by: node group max limit reached, cloud provider API errors or quota exceeded, insufficient RBAC permissions, pending pods with constraints unsatisfiable by any node group, or autoscaler pod itself is unhealthy.

Diagnosis:
- Check autoscaler pod logs for: "ScaleUpFailed", "node group limit reached", "failed to create node", "forbidden", "API rate limit exceeded"
- Compare current node count vs. configured max for each node group
- List pending pods — verify their resource requests, node selectors, and tolerations are satisfiable by an existing node group
- Confirm pending pods are not DaemonSet-owned (DaemonSets don't trigger autoscaling)
- Verify autoscaler service account RBAC has permissions to create nodes and interact with cloud provider APIs

Mitigation:
- If node group limit reached: increase "max-nodes" in autoscaler ConfigMap
- If cloud provider errors: check quotas, regional capacity, and instance type availability
- If RBAC issues: fix autoscaler service account role bindings in "kube-system"
- If pod scheduling constraints exclude all node groups: adjust pod node selectors/tolerations or add a compatible node group
- If autoscaler pod is unhealthy: restart deployment and investigate crash logs
