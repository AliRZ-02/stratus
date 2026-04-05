PodStuckInTerminatingState:

Issues:
Pod stuck in "Terminating" indefinitely, blocking rolling updates and resource cleanup. Caused by: finalizer not being processed (controller missing or PVC still bound), container process not responding to SIGTERM (no graceful shutdown handler), node is "NotReady" preventing cleanup, volume detachment failure, or "terminationGracePeriodSeconds" not yet elapsed.

Diagnosis:
- Describe pod — check "metadata.finalizers" for what is blocking deletion:
  - "kubernetes.io/pvc-protection": PVC still in use
  - "foregroundDeletion": child resources still exist
  - Custom finalizer: check if owning controller/operator is running
- Check pod events for volume detachment errors or deletion-related failures
- Verify node health — a "NotReady" node cannot complete pod termination
- Check "terminationGracePeriodSeconds" — pod may still be in grace period
- If no events and no finalizers: process inside container may be ignoring "SIGTERM"

Mitigation:
- If finalizer stuck (controller missing): manually patch pod to remove finalizer after confirming dependent resources are cleaned up
- If PVC blocking: verify PVC is not actively used by another pod; deletion will proceed once unbound
- If node NotReady: drain/recover the node; or force-delete pod if node is confirmed dead
- If SIGTERM ignored: fix application to handle shutdown signals; as last resort use "kubectl delete pod --force --grace-period=0"
- If grace period: wait for it to elapse; reduce "terminationGracePeriodSeconds" if too long
