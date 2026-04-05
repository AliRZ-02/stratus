PVCinLostState:

Issues:
PVC is in "Lost" phase, making persistent storage inaccessible to pods. Caused by: underlying PV was deleted (manually or via "Delete" reclaim policy), storage backend resource removed or unreachable, PV in "Failed" or "Released" state, binding mismatch between PVC and PV "claimRef", or storage provisioner failure breaking volume binding.

Diagnosis:
- Check PVC events for "VolumeLost" or "VolumeNotFound" — note the specific backend error
- Describe the bound PV — check its phase ("Failed", "Released", or missing entirely)
- If PV is "Released": data may still exist on backend; previous PVC was deleted but volume was retained
- If PV is "Failed": storage backend reported an error — verify backend (NFS, cloud disk) is reachable
- If PV is gone: check whether reclaim policy was "Delete" and PV was removed with the old PVC
- Check PV "claimRef" — confirm it references the current PVC (not a stale or different one)
- Check provisioner pod health; correlate Lost state onset with pod mount failure timestamps

Mitigation:
- If PV is "Released" with data intact: manually re-bind by removing "claimRef" from PV, then recreate PVC
- If PV deleted and data lost: restore from backup; recreate PV/PVC
- If backend unreachable: restore storage backend connectivity; confirm underlying disk/NFS export exists
- If "claimRef" mismatch: patch PV to reference the correct PVC
- If provisioner is failing: fix or restart provisioner; investigate its logs
