IngressFailure:

Issues:
Ingress not routing traffic — returns 502/503 (no reachable backend) or 404 (no matching rule). Caused by: ingress controller pods down or crashing, IngressClass mismatch (controller ignoring resource), no address assigned to Ingress, backend service has no endpoints, path/hostname rule mismatch, missing "rewrite-target" annotation stripping path prefix, or NetworkPolicy blocking controller-to-backend traffic.

Diagnosis:
- Describe Ingress — check "status.loadBalancer", rules, paths, "ingressClassName", and backend service references
- Check ingress controller pods (e.g. "ingress-nginx" namespace) — if "CrashLoopBackOff", controller is the root cause
- If no address assigned: verify "ingressClassName" matches the running controller's class
- Check backend Service — confirm it exists and has ready endpoints
- Review ingress controller logs for: "no matching rule", "backend not found", "502", or "404" messages
- **For 404s specifically:** compare exact request hostname and path against Ingress rules; check "pathType" ("Exact" vs "Prefix"); verify "rewrite-target" annotation if path prefix needs stripping
- Test with "curl" from inside cluster to bypass ingress and isolate backend vs. routing issue
- Check NetworkPolicies for rules blocking ingress controller → backend pod traffic

Mitigation:
- If controller down: fix CrashLoopBackOff (check resource limits, config errors); restart controller
- If IngressClass mismatch: set correct "spec.ingressClassName" in Ingress resource
- If backend has no endpoints: fix pod readiness or service selector
- If 404 due to path mismatch: correct path rules or "pathType"; add "rewrite-target" annotation if needed
- If NetworkPolicy blocking: add egress/ingress rules for controller ↔ backend traffic
- If DNS not resolving ingress hostname: configure external DNS to point to ingress controller's external IP
