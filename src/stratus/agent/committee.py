# src/stratus/agent/committee.py

import json
import re
import os
from typing import Any, Dict, List, Optional

import litellm
from pydantic import BaseModel, Field

from stratus.llm_backends.init_backend import get_llm_backend_for_agents


class CommitteeOrchestrator(BaseModel):
    """
    Orchestrates a multi-persona debate and ranked-choice voting for agent decision-making.
    Implements the S2 voting scheme:
    - 3 distinct SRE personas debate the problem for 2 rounds
    - Each persona proposes an action in each round
    - After discussion, personas rank all unique proposals
    - The action with the lowest total score (highest rank) is selected
    """

    agent_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Agent configuration from YAML (role, goal, backstory)"
    )
    llm_backend: Any = Field(
        default=None,
        description="LLM backend instance for generating responses"
    )
    verbose: bool = Field(default=True, description="Enable verbose logging")

    personas: List[Dict[str, str]] = Field(
        default=[
            {
                "name": "Cautious Optimizer",
                "focus": "system stability, rollback plans, conservative approaches",
                "personality": "You prioritize system safety above all else. You always consider: 'What could go wrong? How do we undo this?'"
            },
            {
                "name": "Data-Driven Debugger",
                "focus": "logs, metrics, traces, root cause analysis",
                "personality": "You trust only the data. You analyze telemetry, trace graphs, and log patterns before acting."
            },
            {
                "name": "Fast-Action Fixer",
                "focus": "quick mitigation, service restoration, high-impact actions",
                "personality": "You prioritize restoring service quickly. You prefer decisive, high-impact actions that stop the bleeding."
            }
        ],
        description="Three personas for the committee debate"
    )

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, agent_config: Dict[str, Any], llm_backend: Any = None, **kwargs):
        super().__init__(agent_config=agent_config, llm_backend=llm_backend, **kwargs)
        if self.llm_backend is None:
            self.llm_backend = get_llm_backend_for_agents()

    def decide(self, context: str, tools_context: Optional[str] = None) -> str:
        """Run the full committee debate and voting process."""
        if self.verbose:
            print("\n" + "="*60)
            print("🏛️  SRE COMMITTEE CONVENING")
            print("="*60)
            print(f"📋 Context: {context[:200]}...")

        proposals = self._gather_initial_proposals(context, tools_context)

        if self.verbose:
            print("\n💬 ROUND 1 PROPOSALS:")
            for p in proposals:
                print(f"  • {p['persona']}: {p['proposal'][:100]}...")

        proposals = self._run_discussion_round(proposals, context, tools_context, round_num=1)
        proposals = self._run_discussion_round(proposals, context, tools_context, round_num=2)

        winning_action = self._ranked_choice_vote(proposals, context)

        if self.verbose:
            print("\n" + "="*60)
            print(f"✅ COMMITTEE DECISION: {winning_action[:150]}...")
            print("="*60 + "\n")

        return winning_action

    def _gather_initial_proposals(self, context: str, tools_context: Optional[str]) -> List[Dict]:
        proposals = []
        for persona in self.personas:
            prompt = self._build_persona_prompt(
                persona=persona,
                context=context,
                tools_context=tools_context,
                discussion_history="",
                round_num=0,
                is_proposal_round=True
            )
            response = self._call_llm(prompt)
            proposal = self._extract_action(response)
            proposals.append({
                "persona": persona["name"],
                "persona_def": persona,
                "proposal": proposal,
                "raw_response": response
            })
        return proposals

    def _run_discussion_round(self, proposals: List[Dict], context: str,
                              tools_context: Optional[str], round_num: int) -> List[Dict]:
        updated_proposals = []
        discussion_history = self._format_discussion_history(proposals)

        for persona in self.personas:
            prev_proposal = next((p for p in proposals if p["persona"] == persona["name"]), None)
            prompt = self._build_persona_prompt(
                persona=persona,
                context=context,
                tools_context=tools_context,
                discussion_history=discussion_history,
                round_num=round_num,
                is_proposal_round=False,
                previous_proposal=prev_proposal["proposal"] if prev_proposal else None
            )
            response = self._call_llm(prompt)
            refined_proposal = self._extract_action(response)
            updated_proposals.append({
                "persona": persona["name"],
                "persona_def": persona,
                "proposal": refined_proposal,
                "raw_response": response,
                "previous_proposal": prev_proposal["proposal"] if prev_proposal else None
            })
        return updated_proposals

    def _ranked_choice_vote(self, proposals: List[Dict], context: str) -> str:
        unique_proposals = list(set([p["proposal"] for p in proposals]))
        if len(unique_proposals) == 1:
            return unique_proposals[0]

        votes = []
        for persona in self.personas:
            prompt = f"""You are {persona['name']}, an expert SRE with focus on: {persona['focus']}.
{persona['personality']}

Based on the discussion and your expertise, rank the following action proposals from BEST (1) to WORST ({len(unique_proposals)}).

CONTEXT: {context[:500]}

PROPOSALS TO RANK:
{self._format_proposals_for_voting(unique_proposals)}

YOUR TASK: Output a JSON object mapping each proposal to your rank (1 = best, {len(unique_proposals)} = worst).

Example output format:
{{
    "proposal 1 text": 1,
    "proposal 2 text": 2,
    "proposal 3 text": 3
}}

Now provide your ranked votes:"""
            response = self._call_llm(prompt)
            parsed_votes = self._parse_votes(response, unique_proposals)
            if parsed_votes:
                votes.append({"persona": persona["name"], "votes": parsed_votes})

        scores = {proposal: 0 for proposal in unique_proposals}
        for vote in votes:
            for proposal, rank in vote["votes"].items():
                scores[proposal] += rank

        winner = min(scores, key=scores.get)
        if self.verbose:
            print("\n🗳️  VOTING RESULTS:")
            for proposal, score in scores.items():
                print(f"  • {proposal[:80]}... → Score: {score}")
            print(f"\n🏆 WINNER: {winner[:100]}...")
        return winner

    def _build_persona_prompt(self, persona: Dict, context: str, tools_context: Optional[str],
                              discussion_history: str, round_num: int, is_proposal_round: bool,
                              previous_proposal: Optional[str] = None) -> str:
        base_prompt = f"""You are {persona['name']}, an expert SRE with focus on: {persona['focus']}.

{persona['personality']}

{self.agent_config.get('backstory', '')}

## CURRENT PROBLEM CONTEXT:
{context}
"""
        if tools_context:
            base_prompt += f"\n## TOOL OUTPUT (if any):\n{tools_context}\n"
        if discussion_history:
            base_prompt += f"\n## DISCUSSION HISTORY:\n{discussion_history}\n"
        if round_num > 0 and previous_proposal:
            base_prompt += f"\n## YOUR PREVIOUS PROPOSAL:\n{previous_proposal}\n\nBased on the discussion above, refine your proposal. Consider the feedback and alternative approaches.\n"

        if is_proposal_round:
            base_prompt += """
## INSTRUCTIONS:
Propose a concrete action to mitigate the current system failure. Your proposal should be specific and actionable.

OUTPUT FORMAT:
First, briefly explain your reasoning (2-3 sentences). Then, on a new line starting with "ACTION:", provide the exact command or action to execute.

Example:
The logs show database connection failures. Restarting the database pod should resolve this.
ACTION: kubectl rollout restart deployment mongodb -n test-hotel-reservation
"""
        else:
            base_prompt += f"""
## INSTRUCTIONS (Round {round_num} of 2):
Review the proposals from other committee members. Then, either:
1. Defend your previous proposal with counter-arguments, OR
2. Refine your proposal based on new insights from others

OUTPUT FORMAT:
First, state whether you are DEFENDING or REFINING. Then explain your reasoning.
Finally, provide your (possibly updated) ACTION: on a new line.

Example:
DEFENDING: The database restart is still the best approach because...
ACTION: kubectl rollout restart deployment mongodb -n test-hotel-reservation
"""
        return base_prompt

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM with a prompt and return the response string."""
        try:
            # Try to use the LLM backend's call method with a messages list
            if hasattr(self.llm_backend, 'call'):
                # Some CrewAI versions expect a list of messages
                messages = [{"role": "user", "content": prompt}]
                response = self.llm_backend.call(messages)
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            else:
                # Fallback: use litellm directly with model from environment
                model = os.getenv('MODEL_AGENTS', 'ollama/gemma:2b')
                messages = [{"role": "user", "content": prompt}]
                response = litellm.completion(model=model, messages=messages)
                return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ LLM call failed: {e}")
            return "ACTION: kubectl get pods"

    def _extract_action(self, response: str) -> str:
        match = re.search(r'ACTION:\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        lines = response.strip().split('\n')
        for line in reversed(lines):
            if line.strip() and not line.strip().startswith(('#', '//', 'Note:', 'Example:')):
                return line.strip()
        return response.strip()

    def _format_discussion_history(self, proposals: List[Dict]) -> str:
        if not proposals:
            return ""
        history = ""
        for p in proposals:
            history += f"\n{p['persona']} proposes: {p['proposal']}\n"
        return history

    def _format_proposals_for_voting(self, proposals: List[str]) -> str:
        formatted = ""
        for i, prop in enumerate(proposals, 1):
            formatted += f"\n{i}. {prop}\n"
        return formatted

    def _parse_votes(self, response: str, unique_proposals: List[str]) -> Optional[Dict[str, int]]:
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                votes = json.loads(json_match.group())
                validated = {}
                for proposal in unique_proposals:
                    matched = False
                    for key, rank in votes.items():
                        if proposal in key or key in proposal:
                            validated[proposal] = int(rank)
                            matched = True
                            break
                    if not matched:
                        validated[proposal] = len(unique_proposals)
                return validated
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ Failed to parse votes: {e}")
        return None