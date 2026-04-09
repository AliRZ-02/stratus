# ECE1770H Stratus Enhancements

## Testing
- You can test on the AIOpsLab problems with our Stratus enhancements by going to the following branches of this repo. To run the actual AIOpsLab problems, follow the instructions in the main README on how to get an environment setup locally to test it.

- S0
    - main
- S1
    - features/s1
- S2
    - s2-voting
- S3
    - features/s3

## Results
- The testing results were conducted on the following AIOpsLab problems

```yaml
detection:
  - k8s_target_port-misconfig-detection-1
  - k8s_target_port-misconfig-detection-2
  - k8s_target_port-misconfig-detection-3
  - auth_miss_mongodb-detection-1
  - revoke_auth_mongodb-detection-1
  - revoke_auth_mongodb-detection-2
  - user_unregistered_mongodb-detection-1
  - user_unregistered_mongodb-detection-2
  - pod_failure_hotel_res-detection-1
  - pod_kill_hotel_res-detection-1

mitigation:
  - k8s_target_port-misconfig-mitigation-1
```

You can see the raw results in results.zip. The `<RUN_NUMBER>/stratus_output/stratus_run_stats.json` contains token usage, whereas the `run-cleaned.log` file contains Time and Success/Failure Information (Ctrl-F for `== Evaluation ==`).
