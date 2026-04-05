KubeDaemonSetNotReady:

Issues:
DaemonSet has fewer ready pods than desired on one or more nodes. Impact varies by DaemonSet role — CNI failure breaks networking, log/metrics collector causes observability gaps, security agent creates coverage holes. Caused by: application crash ("CrashLoopBackOff"), scheduling failure (node taint without matching toleration, insufficient resources), image pull failure, node resource pressure ("MemoryPressure", "DiskPressure"), or in-progress rolling update.

Diagnosis:
- Describe DaemonSet — identify number of not-ready pods and which nodes they are on
- Check failing pod status: "CrashLoopBackOff" = app issue; "Pending" = scheduling issue; "ImagePullBackOff" = image issue
- Check pod logs and events for the specific failure reason
- Compare affected nodes vs healthy nodes — look for node-specific conditions (taints, resource pressure, labels)
- Check node conditions: "MemoryPressure", "DiskPressure", "PIDPressure"
- Verify DaemonSet tolerations match taints on affected nodes
- Check if a rollout is in progress ("kubectl rollout status") — temporary not-ready is expected during updates

Mitigation:
- If "CrashLoopBackOff": fix application config or resource spec; check for breaking changes in recent DaemonSet update
- If "Pending" due to taint: add matching toleration to DaemonSet spec
- If "Pending" due to resources: free node resources or reduce DaemonSet resource requests
- If "ImagePullBackOff": fix image name/tag or registry credentials
- If node pressure: resolve disk/memory issue on affected node
- If mid-rollout: wait for rollout to complete; if stuck, check update strategy and "maxUnavailable"
