"""
Community trust score: computed from photos and confirmations.
Trust badge granted when score meets threshold.
"""

TRUST_BADGE_THRESHOLD = 0.5
MAX_PHOTOS_WEIGHT = 10
MAX_CONFIRMATIONS_WEIGHT = 10


def compute_trust_score(community_photos_count: int, confirmations_count: int) -> float:
    """Returns a score in [0, 1]. Badge when >= TRUST_BADGE_THRESHOLD."""
    photo_component = min(community_photos_count, MAX_PHOTOS_WEIGHT) / MAX_PHOTOS_WEIGHT
    confirm_component = min(confirmations_count, MAX_CONFIRMATIONS_WEIGHT) / MAX_CONFIRMATIONS_WEIGHT
    # Weight confirmations slightly higher than photos
    score = 0.4 * photo_component + 0.6 * confirm_component
    return round(min(1.0, score), 2)


def has_trust_badge(trust_score: float) -> bool:
    return trust_score >= TRUST_BADGE_THRESHOLD
