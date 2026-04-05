KubeJobFailed:

Issues:
Job fails to complete or exceeds retry limits. Caused by: application errors/exceptions in job container, "backoffLimit" exhausted, "activeDeadlineSeconds" exceeded, OOMKilled container, pod evicted due to node resource pressure, pod stuck Pending (scheduling constraints), or job process hanging waiting on external dependency.

Diagnosis:
- Describe Job — check "status.conditions" for "BackoffLimitExceeded" or "DeadlineExceeded"
- Check pod logs (including previous container logs if restarted) for errors, panics, exceptions, or last activity
- If "OOMKilled" in termination reason: job exceeds memory limit
- If "Evicted": check node for "MemoryPressure" or "DiskPressure"
- If pod "Pending": check events for "InsufficientCPU"/"InsufficientMemory" or node affinity issues
- If job runs but never finishes: check logs for hanging process or blocked external dependency
- Correlate failure onset with: Job spec changes, ConfigMap/Secret changes, or external service availability

Mitigation:
- If app error: fix application bug or invalid input data; debug with same image in a debug pod
- If "backoffLimitExceeded": fix root cause first; increase "backoffLimit" if transient failures expected
- If "DeadlineExceeded": increase "activeDeadlineSeconds" or optimize job performance
- If OOMKilled: increase memory limit in Job spec
- If evicted: add resource requests to protect job from eviction; resolve node pressure
- If Pending: fix resource requests or node selectors; ensure cluster has capacity
