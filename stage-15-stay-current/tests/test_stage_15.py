"""
Every topic in this final stage is pure logic with no API call,
consistent with the other fully-offline stages, since currency
scoring, habit tracking, curation, and claim-checking are all
verifiable without a live model call.
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.topic_1_source_currency_scoring.main import currency_score
from src.topic_2_reading_loop_tracker.main import ReadingLoopTracker, LoopStage
from src.topic_3_signal_vs_noise_curation.main import score_source, curate_reading_list
from src.topic_4_claims_vs_verified.main import extract_claims, check_claim_has_backing


# --- topic 1: currency scoring ---

def test_recent_source_in_volatile_category_scores_high():
    result = currency_score("model_pricing_and_availability", date(2026, 10, 1), date(2026, 10, 12))
    assert result["confidence"] > 0.75


def test_old_source_in_volatile_category_scores_low():
    result = currency_score("model_pricing_and_availability", date(2025, 1, 1), date(2026, 10, 12))
    assert result["confidence"] < 0.35


def test_old_source_in_stable_category_still_scores_high():
    result = currency_score("mathematical_formulas", date(2020, 1, 1), date(2026, 10, 12))
    assert result["confidence"] > 0.75


# --- topic 2: reading loop tracker ---

def test_advancing_through_stages_in_order_succeeds():
    tracker = ReadingLoopTracker()
    tracker.start_topic("test")
    result = tracker.advance("test", LoopStage.ARTICLE_READ)
    assert result["success"] is True


def test_skipping_a_stage_is_rejected():
    tracker = ReadingLoopTracker()
    tracker.start_topic("test")
    result = tracker.advance("test", LoopStage.BUILT_SOMETHING)
    assert result["success"] is False


def test_advancing_an_unstarted_topic_fails():
    tracker = ReadingLoopTracker()
    result = tracker.advance("never started", LoopStage.ARTICLE_READ)
    assert result["success"] is False


def test_stuck_topics_detector_finds_incomplete_ones():
    tracker = ReadingLoopTracker()
    tracker.start_topic("stuck")
    tracker.advance("stuck", LoopStage.ARTICLE_READ)
    tracker.start_topic("complete")
    for stage in [LoopStage.ARTICLE_READ, LoopStage.DOCS_READ, LoopStage.BUILT_SOMETHING, LoopStage.REREAD_COMPLETE]:
        tracker.advance("complete", stage)
    stuck = tracker.topics_stuck_before_building()
    assert "stuck" in stuck
    assert "complete" not in stuck


# --- topic 3: signal vs noise curation ---

def test_high_overlap_source_scores_lower_than_low_overlap_source():
    high_overlap = score_source(0.8, 0.5, 0.9)
    low_overlap = score_source(0.8, 0.5, 0.1)
    assert low_overlap["score"] > high_overlap["score"]


def test_curation_keeps_exactly_the_requested_count():
    candidates = [("a", 0.9, 0.9, 0.1), ("b", 0.8, 0.8, 0.1), ("c", 0.5, 0.3, 0.5), ("d", 0.3, 0.2, 0.8)]
    kept, cut = curate_reading_list(candidates, keep_count=2)
    assert len(kept) == 2
    assert len(cut) == 2


def test_curation_keeps_the_highest_scoring_sources():
    candidates = [("best", 0.9, 0.9, 0.0), ("worst", 0.1, 0.1, 0.9)]
    kept, cut = curate_reading_list(candidates, keep_count=1)
    assert kept[0][0] == "best"


# --- topic 4: claims vs verified ---

def test_extract_claims_finds_verification_language():
    text = "This is confirmed to work. This is just a regular sentence."
    claims = extract_claims(text)
    assert len(claims) == 1
    assert "confirmed" in claims[0].lower()


def test_claim_with_matching_evidence_is_backed():
    result = check_claim_has_backing(
        "The multiplier is confirmed as 4.0x",
        ["test shows multiplier equals 4.0x confirmed"],
    )
    assert result["has_backing"] is True


def test_claim_with_no_matching_evidence_is_unbacked():
    result = check_claim_has_backing(
        "This scales to any production workload",
        ["test_real_multiplier_lands_in_confirmed_range asserts multiplier is 4.0"],
    )
    assert result["has_backing"] is False
