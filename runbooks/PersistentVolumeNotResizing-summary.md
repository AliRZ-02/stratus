PersistentVolumeNotResizing:

Issues:
PVC resize request is not being applied. Caused by: StorageClass has "allowVolumeExpansion: false", storage backend does not support online/offline expansion, volume expansion controller pod unhealthy, or filesystem resize pending (volume expanded but pod not restarted).

Diagnosis:
- Check PVC events for "VolumeResizeFailed" or "FileSystemResizePending"
- If "FileSystemResizePending": backend expansion succeeded — pod just needs to be restarted to trigger filesystem resize
- Describe StorageClass — confirm "allowVolumeExpansion: true" is set
- If StorageClass allows expansion but still failing: verify storage backend supports resize for this volume type/size range
- Check volume expansion controller pods in "kube-system" — confirm they are "Running"
- Compare PV capacity vs PVC requested capacity — if PV already shows new size, issue is controller sync

Mitigation:
- If "FileSystemResizePending": restart the pod using the volume
- If StorageClass blocks expansion: update StorageClass to set "allowVolumeExpansion: true" (if backend supports it)
- If backend doesn't support resize: migrate data to a new, larger PVC
- If expansion controller unhealthy: restart it and check logs for processing errors
- If PV/PVC size out of sync: investigate controller logs for synchronization errors
