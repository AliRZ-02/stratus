import re

def parse_ranked_choice_votes(llm_output):
    scores = {}
    matches = re.findall(r'VOTES: 1st=(\w+).*?2nd=(\w+).*?3rd=(\w+)', llm_output)
    for first, second, third in matches:
        scores[first] = scores.get(first, 0) + 1
        scores[second] = scores.get(second, 0) + 2
        scores[third] = scores.get(third, 0) + 3
    return scores

def get_winning_action(llm_output):
    match = re.search(r'WINNING ACTION:\s*(.+)', llm_output)
    return match.group(1).strip() if match else None

def log_deliberation_summary(llm_output, logger=None):
    winning_action = get_winning_action(llm_output)
    vote_scores = parse_ranked_choice_votes(llm_output)
    summary = "\n=== S2 VOTING SUMMARY ===\n"
    if vote_scores:
        summary += "Vote scores:\n"
        for persona, score in sorted(vote_scores.items(), key=lambda x: x[1]):
            summary += "  " + persona + ": " + str(score) + " points\n"
    if winning_action:
        summary += "Winning action: " + winning_action + "\n"
    else:
        summary += "WARNING: No WINNING ACTION found\n"
    summary += "=========================\n"
    if logger:
        logger.info(summary)
    else:
        print(summary)