import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta, datetime
import numpy as np
from pathlib import Path

from chords_downloader.resources.functions import *

@pytest.fixture
def dynamic_timestamps():
    now          = datetime.now()
    max_lookback = timedelta(weeks=103)

    return {
        "long_start":  (now - max_lookback),
        "end":          now,           
        "short_start": (now - timedelta(days=7))
    }


def test_reduce_datapoints_long_period(dynamic_timestamps):
    start = dynamic_timestamps["long_start"]
    end   = dynamic_timestamps["end"]

    # reduce_datapoints() parameters:
    error_message   = "413: Excess datapoints requested"
    id              = 1
    timestamp_start = start
    timestamp_end   = end
    portal_url      = "https://test.chordsrt.com/"
    user_email      = "test@chordsrt.com"
    api_key         = "dummy"
    fill_empty      = ""

    # Mock data from requests.get()
    mock_responses = [
        {   # First call fails, returns the following
            "features": [{"properties": {"data":[]}}],
            "errors": [{"message": "Too many datapoints"}]
        },
        {   # Second call succeeds, returns the following 
            "features": [{"properties": {"data":[
                {"time": "2026-03-01T12:00:00Z",
                 "test": "false",
                 "measurements":{"t1": 25.3}},
                {"time": "2026-03-01T12:01:00Z",
                 "test": "false",
                 "measurements": {"t1": 25.4}}
            ]}}]
        }
    ]


    response_call_count = 0

    def mock_requests_get(url, **kwargs):
        """Returns the appropriate mock data for the 1st and 2nd function call"""

        nonlocal response_call_count
        response = MagicMock()

        if response_call_count == 0: 
            all_fields = mock_responses[0]
        else: 
            all_fields = mock_responses[1]
        
        # When response.json() is called, store the mock output in all_fields
        response.json.return_value = all_fields 

        response_call_count += 1
        return response
    

    excess_dp_call_count = 0
    def mock_has_excess_datapoints(all_fields):
        """has_excess_datapoints() is called repeatedly, handles iterative calls"""
        nonlocal excess_dp_call_count
        excess_dp_call_count += 1

        if excess_dp_call_count == 1:
            return True
        
        return False
    

    # Set up mock behavior for the following functions
    with patch('chords_downloader.resources.functions.requests.get', side_effect=mock_requests_get) as mock_requests_get, \
        patch('chords_downloader.resources.functions.has_excess_datapoints', side_effect=mock_has_excess_datapoints), \
        patch('chords_downloader.resources.functions.write_compass_direction') as mock_write_compass:

        mock_write_compass.return_value = {
            "compass_dir": "N"
        }

        # Make the call the reduce_datapoints()
        result = reduce_datapoints(
            error_message, id, timestamp_start, timestamp_end,
            portal_url, user_email, api_key, fill_empty
        )

        # Logic checks
        assert mock_requests_get.call_count >= 2

        assert len(result) == 4
        time, measurements, test, total_measurements = result

        assert isinstance(time, list)
        assert isinstance(test, list)
        assert isinstance(measurements, list)
        
        assert len(time) >= 2
        assert total_measurements > 0

