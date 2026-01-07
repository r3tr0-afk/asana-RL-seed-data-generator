"""
Base utilities for data generation: GID generation, temporal functions, distributions.
"""

import uuid
import random
import math
from datetime import datetime, timedelta
from typing import List, Optional, TypeVar, Dict

from utils.config import (
    SEED, NOW, HISTORY_START, HISTORY_END,
    BUSINESS_HOURS_START, BUSINESS_HOURS_END,
    DAY_OF_WEEK_WEIGHTS, COMPLETION_TIME_CONFIG,
)

random.seed(SEED)

T = TypeVar('T')


def generate_gid() -> str:
    """Generate unique GID in Asana's numeric format (16 digits from UUID)."""
    uid = uuid.uuid4()
    return str(uid.int)[:16].zfill(16)


def weighted_choice(options: List[T], weights: List[float]) -> T:
    """Select from options based on probability weights (normalized automatically)."""
    total = sum(weights)
    normalized = [w / total for w in weights]
    return random.choices(options, weights=normalized, k=1)[0]


def weighted_choice_dict(options_weights: Dict[T, float]) -> T:
    """Select from a dictionary of {option: weight}."""
    options = list(options_weights.keys())
    weights = list(options_weights.values())
    return weighted_choice(options, weights)


def random_timestamp(
    start: datetime,
    end: datetime,
    business_hours_only: bool = False,
    weekday_weighted: bool = True
) -> datetime:
    """
    Generate random timestamp with realistic patterns.
    Higher creation rates Mon-Wed, optional business hours constraint.
    """
    max_attempts = 100
    
    for _ in range(max_attempts):
        delta = end - start
        random_seconds = random.random() * delta.total_seconds()
        candidate = start + timedelta(seconds=random_seconds)
        
        if weekday_weighted:
            day_weight = DAY_OF_WEEK_WEIGHTS.get(candidate.weekday(), 1.0)
            if random.random() > day_weight / 1.3:  # Reject based on day weight
                continue
        
        if business_hours_only:
            if candidate.hour < BUSINESS_HOURS_START or candidate.hour >= BUSINESS_HOURS_END:
                continue
            if candidate.weekday() >= 5:
                continue
        
        return candidate
    
    # Fallback without constraints
    delta = end - start
    random_seconds = random.random() * delta.total_seconds()
    return start + timedelta(seconds=random_seconds)


def random_date(start: datetime, end: datetime, avoid_weekends: bool = True) -> Optional[datetime]:
    """Generate random date (midnight), 85% chance to avoid weekends."""
    max_attempts = 50
    
    for _ in range(max_attempts):
        delta = end - start
        random_days = random.randint(0, delta.days)
        candidate = start + timedelta(days=random_days)
        candidate = candidate.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if avoid_weekends and candidate.weekday() >= 5:
            if random.random() < 0.85:
                continue
        
        return candidate
    
    delta = end - start
    random_days = random.randint(0, delta.days)
    candidate = start + timedelta(days=random_days)
    return candidate.replace(hour=0, minute=0, second=0, microsecond=0)


def log_normal_days(mean: float = None, sigma: float = None) -> float:
    """
    Generate completion time using log-normal distribution.
    Models the 'long tail' of complex tasks - median ~4-5 days, some much longer.
    """
    if mean is None:
        mean = COMPLETION_TIME_CONFIG["log_normal_mean"]
    if sigma is None:
        sigma = COMPLETION_TIME_CONFIG["log_normal_sigma"]
    
    days = random.lognormvariate(mean, sigma)
    min_days = COMPLETION_TIME_CONFIG["min_days"]
    max_days = COMPLETION_TIME_CONFIG["max_days"]
    
    return max(min_days, min(max_days, days))


def calculate_completion_timestamp(
    created_at: datetime,
    min_days: float = 0.1,
    max_days: float = 30
) -> datetime:
    """Calculate completion time ensuring completed_at >= created_at and <= NOW."""
    days_to_complete = log_normal_days()
    days_to_complete = max(min_days, min(max_days, days_to_complete))
    
    completed_at = created_at + timedelta(days=days_to_complete)
    
    if completed_at > NOW:
        completed_at = NOW - timedelta(hours=random.randint(1, 48))
    
    if completed_at <= created_at:
        completed_at = created_at + timedelta(hours=random.randint(2, 24))
    
    return completed_at


def generate_due_date(
    created_at: datetime,
    distribution: Dict[str, float],
    project_due_date: Optional[datetime] = None
) -> Optional[datetime]:
    """Generate due date based on distribution, constrained by project due date if provided."""
    category = weighted_choice_dict(distribution)
    
    if category == "no_due_date":
        return None
    
    base_date = created_at.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if category == "within_week":
        days_ahead = random.randint(1, 7)
    elif category == "within_month":
        days_ahead = random.randint(8, 30)
    elif category == "one_to_three_months":
        days_ahead = random.randint(31, 90)
    elif category == "overdue":
        days_ahead = -random.randint(1, 14)
    else:
        days_ahead = random.randint(1, 30)
    
    due_date = base_date + timedelta(days=days_ahead)
    
    if project_due_date and due_date > project_due_date:
        due_date = project_due_date - timedelta(days=random.randint(0, 7))
    
    # Move weekend due dates to Friday/Monday (85% of the time)
    if due_date.weekday() >= 5 and random.random() < 0.85:
        if due_date.weekday() == 5:
            due_date -= timedelta(days=1)
        else:
            due_date += timedelta(days=1)
    
    return due_date


def generate_start_date(due_date: Optional[datetime], probability: float = 0.35) -> Optional[datetime]:
    """Generate start date 1-14 days before due date (if due date exists)."""
    if due_date is None or random.random() > probability:
        return None
    
    days_before = random.randint(1, 14)
    return due_date - timedelta(days=days_before)


def interpolate_timestamp(start: datetime, end: datetime, progress: float) -> datetime:
    """Get timestamp at specific progress point (0.0 to 1.0) between start and end."""
    delta = end - start
    offset = timedelta(seconds=delta.total_seconds() * progress)
    return start + offset


def generate_creation_wave(
    count: int,
    start: datetime,
    end: datetime,
    growth_curve: str = "linear"
) -> List[datetime]:
    """
    Generate creation timestamps following growth pattern.
    Supports 'linear', 'exponential' (more recent), or 's_curve' patterns.
    """
    timestamps = []
    
    for i in range(count):
        if growth_curve == "linear":
            progress = i / max(count - 1, 1)
        elif growth_curve == "exponential":
            progress = (math.exp(2 * i / count) - 1) / (math.e ** 2 - 1)
        elif growth_curve == "s_curve":
            x = i / max(count - 1, 1)
            progress = 1 / (1 + math.exp(-10 * (x - 0.5)))
        else:
            progress = random.random()
        
        progress += random.uniform(-0.05, 0.05)
        progress = max(0, min(1, progress))
        
        ts = interpolate_timestamp(start, end, progress)
        ts = random_timestamp(
            ts - timedelta(hours=12),
            ts + timedelta(hours=12),
            business_hours_only=False,
            weekday_weighted=True
        )
        timestamps.append(ts)
    
    return sorted(timestamps)


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


def random_subset(items: List[T], min_count: int = 1, max_count: int = None) -> List[T]:
    """Select random subset of items."""
    if max_count is None:
        max_count = len(items)
    
    max_count = min(max_count, len(items))
    min_count = min(min_count, max_count)
    
    count = random.randint(min_count, max_count)
    return random.sample(items, count)


def probability_check(probability: float) -> bool:
    """Return True with given probability."""
    return random.random() < probability
