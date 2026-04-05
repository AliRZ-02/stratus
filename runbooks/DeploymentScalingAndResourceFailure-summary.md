DeploymentScalingAndResourceFailure:

Issues:
Deployment cannot reach desired replica count or pods are rejected at admission/scheduling. Caused by: cluster-wide CPU/memory capacity exhausted, namespace ResourceQuota exceeded, LimitRange constraints violated, resource requests set too high (typos, over-provisioning) or exceeding any single node's capacity, node taints/cordons reducing schedulable capacity, HPA unable to get metrics (metrics-server down), pods not passing readiness probes preventing scale-up completion, or deployment paused/conflicting HPA+manual scaling.

Diagnosis:
- Describe Deployment — check desired/current/ready/available replicas and events for "FailedCreate", "FailedScheduling", "exceeded quota"
- Describe pending pods — check events for "InsufficientCPU", "InsufficientMemory", or node affinity/taint rejections
- Check node allocatable resources — compare against pod requests to confirm capacity exhaustion
- Describe ResourceQuota and LimitRange in namespace — confirm whether quota or policy is the blocker
- If HPA is configured: describe HPA — check for "unable to get metrics" or "failed to compute desired"; verify metrics-server pods are Running
- Check for nodes that are tainted, cordoned, or recently removed that may have reduced capacity
- Check if resource requests were recently increased (could push previously schedulable pods over limit)
- Verify pod readiness — if pods are created but not Ready, scale-up stalls

Mitigation:
- If capacity exhausted: add nodes, expand node group, or fix cluster autoscaler
- If ResourceQuota exceeded: increase quota limits or right-size pod requests
- If LimitRange violated: adjust pod requests/limits to comply with namespace policy
- If resource requests too high (typo/over-provision): correct values in Deployment spec
- If HPA metrics unavailable: fix metrics-server (see "MetricsServerShowsNoData")
- If nodes tainted/cordoned: add matching tolerations to Deployment or restore node availability
- If pods not Ready: fix readiness probe or application startup issue
