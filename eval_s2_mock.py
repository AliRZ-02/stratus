#!/usr/bin/env python3
"""
Run either baseline (S0) or S2 committee test problems, depending on --mode.
Usage:
    python eval_s2.py --mode s0
    python eval_s2py --mode s2
"""

import sys
import os
import time
import json
import argparse

# Add project src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stratus.agent.committee import CommitteeOrchestrator
from stratus.llm_backends.init_backend import get_llm_backend_for_agents

# ============================================================
#  Task definitions
# ============================================================
TEST_PROBLEMS = {
    "misconfig_app_hotel_res-detection-1": "The hotel reservation frontend returns 500 errors. Check logs and metrics to detect the failure.",
    "k8s_target_port-misconfig-detection-1": "A service target port is misconfigured, causing connection refused errors. Detect which service.",
    "k8s_target_port-misconfig-detection-2": "Another target port misconfiguration in the booking service. Detect the anomaly.",
    "k8s_target_port-misconfig-detection-3": "Third target port misconfiguration in payment service. Detect the issue.",
    "scale_pod_zero_social_net-detection-1": "Social network service pods scaled to zero. Detect the scaling anomaly.",
    "misconfig_app_hotel_res-localization-1": "Locate the faulty component in hotel reservation that causes 500 errors.",
    "k8s_target_port-misconfig-localization-1": "Find which pod or service has the wrong target port.",
    "k8s_target_port-misconfig-localization-2": "Localize the misconfiguration in booking service.",
    "k8s_target_port-misconfig-localization-3": "Localize the target port issue in payment service.",
    "scale_pod_zero_social_net-localization-1": "Find why social network pods were scaled to zero.",
    "misconfig_app_hotel_res-analysis-1": "Root cause analysis: Why does the hotel reservation frontend fail?",
    "k8s_target_port-misconfig-analysis-1": "Root cause: target port misconfiguration in service X.",
    "k8s_target_port-misconfig-analysis-2": "Root cause: another target port issue.",
    "misconfig_app_hotel_res-mitigation-1": "Mitigate the hotel reservation failure. Suggest kubectl commands.",
    "k8s_target_port-misconfig-mitigation-1": "Fix the target port misconfiguration. Provide kubectl commands.",
    "k8s_target_port-misconfig-mitigation-2": "Mitigate the second target port misconfiguration.",
}

TASK_TYPES = {task: task.split('-')[-2] for task in TEST_PROBLEMS}

# ============================================================
#  Baseline single agent (S0) runner
# ============================================================
def run_single_agent(task_name: str, problem_desc: str, llm) -> dict:
    prompt = f"""You are an SRE expert. Given the following problem, output a single concrete action (a kubectl command or investigation step) to resolve it.
Problem: {problem_desc}
Output exactly one line starting with "ACTION: ".
Example: ACTION: kubectl get pods -n test-hotel-reservation
Now provide your action:"""

    start = time.time()
    try:
        if hasattr(llm, 'call'):
            messages = [{"role": "user", "content": prompt}]
            response = llm.call(messages)
            if hasattr(response, 'content'):
                text = response.content
            else:
                text = str(response)
        else:
            text = llm(prompt)
        if "ACTION:" in text:
            decision = text.split("ACTION:")[-1].strip().split('\n')[0]
        else:
            decision = text.strip()
        success = bool(decision and len(decision) > 0)
    except Exception as e:
        decision = f"ERROR: {str(e)}"
        success = False
    elapsed = time.time() - start
    token_estimate = len(problem_desc)//4 + len(prompt)//4 + len(decision)//4 + 500
    return {
        "task": task_name,
        "type": TASK_TYPES[task_name],
        "success": success,
        "decision": decision[:200] + "..." if len(decision) > 200 else decision,
        "time_s": round(elapsed, 2),
        "estimated_tokens": token_estimate,
    }

# ============================================================
#  S2 committee runner
# ============================================================
def run_committee_on_task(task_name: str, problem_desc: str, committee) -> dict:
    start = time.time()
    try:
        decision = committee.decide(context=problem_desc, tools_context=None)
        success = True
    except Exception as e:
        decision = f"ERROR: {str(e)}"
        success = False
    elapsed = time.time() - start
    token_estimate = len(problem_desc)//4 + len(decision)//4 + 2000
    return {
        "task": task_name,
        "type": TASK_TYPES[task_name],
        "success": success,
        "decision": decision[:200] + "..." if len(decision) > 200 else decision,
        "time_s": round(elapsed, 2),
        "estimated_tokens": token_estimate,
    }

# ============================================================
#  Main
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='Run either S0 (baseline) or S2 (committee) evaluation.')
    parser.add_argument('--mode', choices=['s0', 's2'], required=True,
                        help='Evaluation mode: s0 = single agent, s2 = committee voting')
    args = parser.parse_args()

    # Load LLM backend
    try:
        llm = get_llm_backend_for_agents()
        print(f"✅ LLM backend loaded for mode {args.mode.upper()}")
    except Exception as e:
        print(f"❌ Could not load LLM backend: {e}")
        return

    results = []
    if args.mode == 's0':
        print("\n" + "="*80)
        print("RUNNING BASELINE SINGLE AGENT (S0) ON ALL TASKS")
        print("="*80)
        for task_name, problem in TEST_PROBLEMS.items():
            print(f"\n--- {task_name} ---")
            res = run_single_agent(task_name, problem, llm)
            results.append(res)
            print(f"  Decision: {res['decision'][:100]}...")
            print(f"  Time: {res['time_s']}s, Tokens: {res['estimated_tokens']}")
    else:  # s2
        # Create committee orchestrator (verbose=False to reduce console spam)
        agent_config = {
            "role": "SRE Committee",
            "goal": "Evaluate mitigation actions for the given problem.",
            "backstory": "Committee of three expert SREs."
        }
        committee = CommitteeOrchestrator(
            agent_config=agent_config,
            llm_backend=llm,
            verbose=False
        )
        print("\n" + "="*80)
        print("RUNNING S2 COMMITTEE ON ALL TASKS")
        print("="*80)
        for task_name, problem in TEST_PROBLEMS.items():
            print(f"\n--- {task_name} ---")
            res = run_committee_on_task(task_name, problem, committee)
            results.append(res)
            print(f"  Decision: {res['decision'][:100]}...")
            print(f"  Time: {res['time_s']}s, Tokens: {res['estimated_tokens']}")

    # Save results to JSON
    outfile = f"eval_s2_{args.mode}.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Detailed results saved to {outfile}")

    # Print summary by task type
    types = set(TASK_TYPES.values())
    print("\n" + "="*60)
    print(f"EVALUATION SUMMARY ({args.mode.upper()})")
    print("="*60)
    for t in sorted(types):
        tasks = [r for r in results if r["type"] == t]
        success = sum(1 for r in tasks if r["success"])
        avg_time = sum(r["time_s"] for r in tasks) / len(tasks) if tasks else 0
        avg_tokens = sum(r["estimated_tokens"] for r in tasks) / len(tasks) if tasks else 0
        print(f"{t.upper():12} Success: {success}/{len(tasks)} ({100*success/len(tasks):.1f}%)  "
              f"Avg time: {avg_time:.2f}s  Avg tokens: {avg_tokens:.0f}")

if __name__ == "__main__":
    main()