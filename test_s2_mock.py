#!/usr/bin/env python3
"""
Standalone test for S2 Voting Scheme (CommitteeOrchestrator)
Tests the voting logic without requiring a Kubernetes cluster or AIOpsLab.
"""

import sys
import os

# Add the project's src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from stratus.agent.committee import CommitteeOrchestrator
from stratus.llm_backends.init_backend import get_llm_backend_for_agents

def test_s2_voting():
    """Test the committee voting logic with a mock problem."""
    
    # Load LLM backend from your .env configuration
    try:
        llm = get_llm_backend_for_agents()
        print("✅ LLM backend loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load LLM backend: {e}")
        print("Check your .env file for correct LLM configuration.")
        return False
    
    # Create the committee orchestrator
    agent_config = {
        "role": "SRE Committee",
        "goal": "Test the voting mechanism",
        "backstory": "You are a committee of three expert SREs testing the voting system."
    }
    
    committee = CommitteeOrchestrator(
        agent_config=agent_config,
        llm_backend=llm,
        verbose=True
    )
    
    # Mock problem context (simulates a failure scenario)
    test_context = """
    Problem: The 'frontend' service is returning 500 errors.
    The 'search' service logs show connection refused to MongoDB.
    The 'geo' pod is in CrashLoopBackOff state.
    The namespace is 'test-hotel-reservation'.
    """
    
    print("\n" + "="*60)
    print("Testing S2 Committee with mock problem:")
    print(test_context)
    print("="*60)
    
    # Run the committee decision
    try:
        result = committee.decide(context=test_context, tools_context=None)
        print("\n" + "="*60)
        print(f"✅ Committee decision: {result}")
        print("="*60)
        return True
    except Exception as e:
        print(f"\n❌ Committee failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_s2_voting()
    sys.exit(0 if success else 1)