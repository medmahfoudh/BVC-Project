# agents/summarization.py

from transformers import pipeline, Pipeline
from typing import List, Dict

class SummarizationAgent:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn",
        device: int    = -1  # -1 = CPU, or GPU id
    ):
        """
        Loads a HuggingFace summarization pipeline.
        """
        # instantiate once
        self.summarizer: Pipeline = pipeline(
            "summarization",
            model=model_name,
            device=device
        )

    def summarize(
        self,
        passages: List[Dict],
        max_length: int = 150,
        min_length: int = 40
    ) -> str:
        """
        passages: list of dicts, each with 'content' key
        Returns a summary string:
          - Tries to summarize all passages at once (with truncation).
          - If that fails (too long), falls back to summarizing each passage then joining.
        """
        # 1) Concatenate top passages into one big text
        full_text = " ".join([p["content"] for p in passages])

        try:
            # 2) Attempt single‐shot summarization with truncation
            output = self.summarizer(
                full_text,
                max_length=max_length,
                min_length=min_length,
                truncation=True,     # <-- ensure no index‐out‐of‐range
                do_sample=False
            )
            return output[0]["summary_text"].strip()

        except Exception as e:
            # 3) Fallback: summarize each passage individually
            summaries = []
            for p in passages:
                try:
                    out = self.summarizer(
                        p["content"],
                        max_length=max_length,
                        min_length=min_length,
                        truncation=True,
                        do_sample=False
                    )
                    summaries.append(out[0]["summary_text"].strip())
                except Exception:
                    # if even a single passage fails, just take the raw text
                    summaries.append(p["content"][: max_length] + "…")
            # Join mini‐summaries
            return "\n\n".join(summaries)
