KubePodCrashLooping:

Issues:
Pod container repeatedly crashes and restarts, entering "CrashLoopBackOff". Caused by: OOMKill (exit code 137), application error/exception (exit code 1), segfault (exit code 139), liveness probe too aggressive (kills healthy-but-slow container), missing dependency (ConfigMap, Secret, PVC), invalid image or startup command, or regression introduced by a recent rollout.

Diagnosis:
- Describe pod — check restart count, last termination reason ("OOMKilled", "Error"), and exit code
- Get previous container logs: "kubectl logs <pod> --previous" — look for stack traces, panics, connection errors
- Check pod events for: "BackOff", "OOMKilling", liveness probe failures, "CreateContainerConfigError"
- If "OOMKilled": compare memory usage metrics vs limit; check if growth is gradual (leak) or load-driven
- If liveness probe failures: check "timeoutSeconds" and "failureThreshold" in deployment spec — may be too tight
- If "CreateContainerConfigError": verify all referenced ConfigMaps, Secrets, and PVCs exist
- Correlate crash onset with recent rollout history — new image or config change often the trigger
- Check node conditions ("MemoryPressure", "DiskPressure") if multiple pods on the same node are affected

Mitigation:
- If OOMKilled: increase memory limit or fix memory leak
- If app error: fix bug or bad config; roll back deployment if regression
- If liveness probe killing pod: increase "timeoutSeconds"/"initialDelaySeconds"/"failureThreshold"
- If missing dependency: create the missing ConfigMap, Secret, or PVC
- If node pressure: evict or reschedule pod to a healthier node
