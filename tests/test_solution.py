## Student Name:
## Student ID: 

"""
Public test suite for the meeting slot suggestion exercise.

Students can run these tests locally to check basic correctness of their implementation.
The hidden test suite used for grading contains additional edge cases and will not be
available to students.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from solution import suggest_slots


def test_single_event_blocks_overlapping_slots():
    """
    Functional requirement:
    Slots overlapping an event must not be suggested.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "10:00" not in slots
    assert "10:30" not in slots
    assert "11:15" in slots

def test_event_outside_working_hours_is_ignored():
    """
    Constraint:
    Events completely outside working hours should not affect availability.
    """
    events = [{"start": "07:00", "end": "08:00"}]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")

    assert "09:00" in slots
    assert "16:00" in slots

def test_unsorted_events_are_handled():
    """
    Constraint:
    Event order should not affect correctness.
    """
    events = [
        {"start": "13:00", "end": "14:00"},
        {"start": "09:30", "end": "10:00"},
        {"start": "11:00", "end": "12:00"},
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert  slots[1] == "10:15"
    assert "09:30" not in slots

def test_lunch_break_blocks_all_slots_during_lunch():
    """
    Constraint:
    No meeting may start during the lunch break (12:00–13:00).
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")

    assert "12:00" not in slots
    assert "12:15" not in slots
    assert "12:30" not in slots
    assert "12:45" not in slots

def test_no_available_slots_returns_empty_list():
    """
    Edge case:
    When the entire day is blocked by events, function should return empty list.
    """
    events = [
        {"start": "09:00", "end": "12:00"},
        {"start": "13:00", "end": "17:00"},
    ]
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")
    
    assert slots == []

def test_event_partially_overlapping_working_hours():
    """
    Constraint:
    Events that partially overlap working hours should block only the overlapping portion.
    """
    events = [
        {"start": "08:00", "end": "10:00"},  # Starts before work, ends during work
        {"start": "16:00", "end": "18:00"},  # Starts during work, ends after work
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")
    
    # 10:00 should not be available (event ends exactly at 10:00)
    assert "10:00" not in slots
    assert "10:15" in slots
    # 16:00 should not be available (event starts at 16:00)
    assert "16:00" not in slots
    assert "15:30" in slots  # Should be available before 16:00

def test_multiple_overlapping_events():
    """
    Functional requirement:
    Multiple overlapping events should be handled correctly.
    """
    events = [
        {"start": "10:00", "end": "11:00"},
        {"start": "10:30", "end": "11:30"},  # Overlaps with first event
        {"start": "11:15", "end": "12:00"},  # Overlaps with second event
    ]
    slots = suggest_slots(events, meeting_duration=30, day="2026-02-01")
    
    # No slots should be available between 10:00 and 12:00
    assert "10:00" not in slots
    assert "10:15" not in slots
    assert "10:30" not in slots
    assert "11:00" not in slots
    assert "11:15" not in slots
    assert "11:30" not in slots
    # But 12:15 should be available (after lunch)
    assert "12:15" not in slots  # Still in lunch break
    assert "13:15" in slots  # After lunch and after events

def test_long_meeting_duration():
    """
    Edge case:
    Very long meetings should only show slots where they fit entirely within working hours.
    """
    events = []
    slots = suggest_slots(events, meeting_duration=480, day="2026-02-01")  # 8 hours
    
    # An 8-hour meeting starting at 9:00 would end at 17:00, which is exactly at end of work
    # This should be valid (meetings can end exactly at work end time)
    assert len(slots) == 1
    assert "09:00" in slots
    
    # A meeting longer than 8 hours should have no slots
    slots_longer = suggest_slots(events, meeting_duration=481, day="2026-02-01")  # 8 hours 1 minute
    assert len(slots_longer) == 0

def test_meeting_ending_at_lunch_boundary():
    """
    Edge case:
    Meetings that would end exactly at lunch start should be valid.
    Meetings that would start exactly at lunch end should be valid.
    """
    events = []
    slots = suggest_slots(events, meeting_duration=60, day="2026-02-01")
    
    # A 60-minute meeting starting at 11:00 would end at 12:00 (lunch start)
    # This should be valid
    assert "11:00" in slots
    
    # A 60-minute meeting starting at 13:00 would start exactly when lunch ends
    # This should be valid
    assert "13:00" in slots

def test_very_short_meeting_duration():
    """
    Edge case:
    Very short meetings (15 minutes) should have many available slots.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=15, day="2026-02-01")
    
    # Should have slots before 10:00, after 11:00, avoiding lunch
    assert "09:00" in slots
    assert "09:45" in slots
    assert "10:00" not in slots
    assert "10:45" not in slots
    assert "11:00" not in slots  # Can't start exactly when event ends
    assert "11:15" in slots
    assert "12:00" not in slots  # Lunch break
    assert "13:00" in slots

def test_friday_meetings_must_not_start_after_1500():
    """
    New requirement:
    Meetings scheduled on Fridays must not start after 15:00.
    Slots starting after 15:00 on Fridays should be excluded.
    """
    events = []
    slots = suggest_slots(events, meeting_duration=30, day="Fri")
    
    # Slots before 15:00 should be available
    assert "09:00" in slots
    assert "14:00" in slots
    assert "14:45" in slots
    
    # Slots at or after 15:00 should be excluded
    assert "15:00" not in slots
    assert "15:15" not in slots
    assert "15:30" not in slots
    assert "16:00" not in slots
    assert "16:45" not in slots

def test_friday_constraint_with_events():
    """
    New requirement:
    Friday constraint should work correctly even when there are existing events.
    """
    events = [{"start": "10:00", "end": "11:00"}]
    slots = suggest_slots(events, meeting_duration=30, day="Fri")
    
    # Should have slots before 10:00 and after 11:00, but only up to 15:00
    assert "09:00" in slots
    assert "09:30" in slots
    # 09:45 would end at 10:15, which conflicts with event 10:00-11:00, so it's excluded
    assert "10:00" not in slots  # Blocked by event
    assert "11:15" in slots
    assert "14:30" in slots  # Valid slot before 15:00
    assert "14:45" in slots  # Last valid slot before 15:00 (ends at 15:15, but start is before 15:00)
    assert "15:00" not in slots  # Friday constraint
    assert "15:15" not in slots  # Friday constraint

def test_non_friday_days_unaffected():
    """
    New requirement:
    Non-Friday days should not be affected by the Friday constraint.
    """
    events = []
    
    # Test Monday - should have all slots including after 15:00
    slots_mon = suggest_slots(events, meeting_duration=30, day="Mon")
    assert "15:00" in slots_mon
    assert "15:15" in slots_mon
    assert "16:00" in slots_mon
    # 16:45 would end at 17:15, which is after working hours (17:00), so it's excluded
    assert "16:30" in slots_mon  # Last valid slot (ends at 17:00)
    
    # Test Tuesday - should have all slots including after 15:00
    slots_tue = suggest_slots(events, meeting_duration=30, day="Tue")
    assert "15:00" in slots_tue
    assert "15:15" in slots_tue
    assert "16:00" in slots_tue
    
    # Test Wednesday - should have all slots including after 15:00
    slots_wed = suggest_slots(events, meeting_duration=30, day="Wed")
    assert "15:00" in slots_wed
    assert "15:15" in slots_wed
    assert "16:00" in slots_wed
    
    # Test Thursday - should have all slots including after 15:00
    slots_thu = suggest_slots(events, meeting_duration=30, day="Thu")
    assert "15:00" in slots_thu
    assert "15:15" in slots_thu
    assert "16:00" in slots_thu

def test_friday_edge_case_exactly_1500():
    """
    Edge case:
    Test that Friday slot at exactly 15:00 is excluded.
    The requirement "must not start after 15:00" is interpreted as excluding 15:00 and later.
    Note: The constraint only applies to start time, not end time.
    """
    events = []
    
    # Test with 60-minute meeting - 14:00 start is valid (ends at 15:00)
    slots = suggest_slots(events, meeting_duration=60, day="Fri")
    assert "14:00" in slots
    
    # Test with 15-minute meeting - 14:45 start is valid (ends at 15:00)
    slots_short = suggest_slots(events, meeting_duration=15, day="Fri")
    assert "14:45" in slots_short
    
    # 15:00 start should be excluded regardless of meeting duration
    assert "15:00" not in slots
    assert "15:00" not in slots_short
