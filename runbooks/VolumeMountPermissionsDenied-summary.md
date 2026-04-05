VolumeMountPermissionsDenied:

Issues:
Containers can mount volumes but fail to read/write due to permission errors, causing "CrashLoopBackOff". Caused by: mismatch between container "runAsUser"/"fsGroup" and volume file ownership, missing or incorrect "fsGroup" in pod security context, storage backend overriding Kubernetes fsGroup settings, or security context changed in a recent rollout.

Diagnosis:
- Check pod logs for "permission denied" errors — note the specific path and operation (read/write/execute)
- Check pod events for "FailedMount" with permission-related messages
- Describe pod security context — note "runAsUser" and "fsGroup" values
- Exec into pod or run "ls -la" on the mount path to inspect actual file ownership and permissions
- Compare container UID/GID against volume ownership — mismatch is the most common root cause
- If recently rolled out: compare new deployment security context against previous; correlate with error onset
- If permissions look correct: check whether the storage backend has its own permission model overriding "fsGroup"

Mitigation:
- If UID/GID mismatch: set "fsGroup" in pod "securityContext" to match volume ownership, or use an "initContainer" to "chown" the volume
- If storage backend overrides fsGroup: configure permissions directly on the backend storage
- If regression from rollout: revert security context change in deployment spec
- If SELinux/seccomp: review and adjust security context policies
