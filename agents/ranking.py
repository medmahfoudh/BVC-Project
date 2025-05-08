# agents/ranking.py

from difflib import SequenceMatcher
from typing import List, Dict

class RankingAgent:
    def __init__(self, method: str = "fuzzy"):
        """
        method: one of
          - "fuzzy"   → SequenceMatcher ratio
          - "overlap" → Jaccard word-overlap
        """
        assert method in ("fuzzy", "overlap"), "method must be 'fuzzy' or 'overlap'"
        self.method = method

    def _fuzzy_score(self, query: str, text: str) -> float:
        return SequenceMatcher(None, query.lower(), text.lower()).ratio()

    def _overlap_score(self, query: str, text: str) -> float:
        qset = set(query.lower().split())
        tset = set(text.lower().split())
        if not qset or not tset:
            return 0.0
        return len(qset & tset) / len(qset | tset)

    def rank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        """
        Re‐ranks the candidates in place using the chosen lightweight method.
        Each candidate dict gains a "rank_score" key.
        """
        for cand in candidates:
            txt = cand.get("content", "")
            if self.method == "fuzzy":
                score = self._fuzzy_score(query, txt)
            else:
                score = self._overlap_score(query, txt)
            cand["rank_score"] = score

        # Sort descending by rank_score
        return sorted(candidates, key=lambda x: x["rank_score"], reverse=True)
