PVProvisioningAndAccessFailure:

Issues:
Pods stuck in "Pending" or "ContainerCreating" because PVC is unbound or PV is inaccessible. Caused by: storage backend provisioning failure (quota, capacity, permissions, timeout), PVC/PV requirements mismatch (access mode, capacity, StorageClass, node affinity), StorageClass missing or misconfigured, CSI driver failure, node volume attachment limit reached, or storage backend unavailable.

Diagnosis:
- Check pod events for "FailedMount", "FailedAttachVolume", or "FailedScheduling" with volume-related messages
- Describe the PVC — confirm it is in "Bound" phase; if "Pending", check StorageClass and provisioner availability
- Check PVC/PV events for: "ProvisioningFailed", "FailedBinding", "StorageClassNotFound", "WaitForFirstConsumer"
- If "ProvisioningFailed": inspect error message — quota exceeded, no capacity, permission denied, or backend timeout
- If "FailedBinding": compare PVC requirements (access mode, size, StorageClass) against available PVs
- If PVC is Bound but pod still fails: check node volume attachment limits and whether PV's storage path still exists
- List PVs in "Released" or "Failed" state for signs of recurring backend issues

Mitigation:
- If StorageClass missing: recreate it or fix the PVC reference
- If provisioning quota exceeded: increase storage quota in cloud provider
- If access mode / capacity mismatch: adjust PVC spec or create a matching PV manually
- If CSI/provisioner unhealthy: restart the provisioner pod and investigate logs
- If node attachment limit reached: reschedule pod to a different node or reduce volume count
- If backend unavailable: restore storage backend connectivity; verify PV's volumeHandle still exists
