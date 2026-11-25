"""BM25 ranking: unit behaviour plus the labelled check (frozen snapshot, no model, no network)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from app import retrieval
from app.pipeline import rank_candidates, rank_candidates_overlap
import retrieval_check as rc


def test_stemming_joins_word_forms_and_drops_boilerplate():
    assert retrieval.tokens("Tumors imaging") == retrieval.tokens("tumor images")[:1] + retrieval.tokens("imaging")
    assert retrieval.tokens("The applicant shall submit a grant application") == ["shall"]


def test_rare_terms_outweigh_common_ones_and_title_counts_more():
    docs = [("Marine mammals", "rescue of stranded animals"), ("Cybersecurity", "marine marine marine"), ("Other", "other text")]
    s = retrieval.BM25(docs).scores("marine mammals")
    assert s[0] > s[1] > s[2] == 0


def test_zero_overlap_records_are_never_ranked():
    d = [{"source_record_id": "1", "title": "Battery storage", "description": "grid"},
         {"source_record_id": "2", "title": "Marine fisheries", "description": "fish stocks"}]
    ranked, skipped, none = rank_candidates(d, {"lanes": ["fisheries"]}, 5)
    assert [x[0]["source_record_id"] for x in ranked] == ["2"] and none == 1 and skipped == 0


def test_labelled_check_bm25_beats_word_overlap_on_the_frozen_snapshot():
    details, queries = rc.load()
    base = rc.evaluate(rank_candidates_overlap, details, queries, 10)
    new = rc.evaluate(rank_candidates, details, queries, 10)
    mean = lambda rows, k: sum(r[k] for r in rows) / len(rows)
    assert mean(new, "recall") > mean(base, "recall") + 0.2
    assert mean(new, "mrr") >= 0.8


def test_short_field_names_are_kept_only_as_capitals():
    assert retrieval.tokens("AI for science") == ["ai", "science"]
    assert retrieval.tokens("ML for imaging") == ["ml", "imag"]
    assert retrieval.tokens("US tumors") == retrieval.tokens("tumors")
    assert retrieval.tokens("OF TO ai ml") == []          # stop words stay out; lower-case two-letter words are not topics
    assert retrieval.tokens("they may go to it") == []


def test_ai_query_finds_ai_record():
    docs = [("AI for materials", "machine learning"), ("Fisheries", "fish stocks")]
    s = retrieval.BM25(docs).scores("AI")
    assert s[0] > 0 and s[1] == 0
