import pytest
from unittest.mock import patch, MagicMock
from datetime import timedelta, datetime
from pathlib import Path
from chords_downloader import chords_local_download as cld

now = datetime.now()
fmt = "%Y-%m-%d %H:%M:%S"

MOCK_JSON_RESPONSE = {
    "features": [{"properties": {"data": []}}]
}


def test_main_raises_when_start_after_end():
    portal_url     = "https://example.com"
    portal_name    = "3D-PAWS"
    data_path      = Path("/tmp")
    instrument_ids = [1]
    user_email     = "test@example.com"
    api_key        = "dummy"

    start_dt = now - timedelta(hours=1)
    end_dt   = now - timedelta(days=1)  
    start    = start_dt.strftime(fmt)
    end      = end_dt.strftime(fmt)

    with pytest.raises(ValueError) as excinfo:
        cld.main(
            portal_url,
            portal_name,
            data_path,
            instrument_ids,
            user_email,
            api_key,
            start,
            end,
        )

    assert "Starting time cannot be after end time" in str(excinfo.value)

@patch("chords_downloader.chords_local_download.requests.get")
@patch("chords_downloader.chords_local_download.resources")
def test_main_raises_when_start_before_two_years(mock_resources, mock_get):
    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_JSON_RESPONSE
    mock_get.return_value = mock_response
    
    # Mock resources functions so they don't crash or do real work
    mock_resources.has_errors.return_value = False
    mock_resources.has_excess_datapoints.return_value = False
    mock_resources.struct_has_data.return_value = False  # Empty data -> no file written

    portal_url     = "https://example.com"
    portal_name    = "3D-PAWS"
    data_path      = Path("/tmp")
    instrument_ids = [1]
    user_email     = "test@example.com"
    api_key        = "dummy"
    
    start_dt = now - timedelta(days=365*3)
    end_dt   = now - timedelta(days=1)  
    start    = start_dt.strftime(fmt)
    end      = end_dt.strftime(fmt)

    with pytest.warns(UserWarning, match="timestamp_start before CHORDS cutoff"):
        cld.main(
            portal_url,
            portal_name,
            data_path,
            instrument_ids,
            user_email,
            api_key,
            start,
            end,
        )

@patch("chords_downloader.chords_local_download.requests.get")
@patch("chords_downloader.chords_local_download.resources")
def test_main_raises_when_start_in_future(mock_resources, mock_get):
    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_JSON_RESPONSE
    mock_get.return_value = mock_response
    
    # Mock resources functions so they don't crash or do real work
    mock_resources.has_errors.return_value = False
    mock_resources.has_excess_datapoints.return_value = False
    mock_resources.struct_has_data.return_value = False  # Empty data -> no file written

    portal_url     = "https://example.com"
    portal_name    = "3D-PAWS"
    data_path      = Path("/tmp")
    instrument_ids = [1]
    user_email     = "test@example.com"
    api_key        = "dummy"
    
    start_dt = now + timedelta(days=1)
    end_dt   = now + timedelta(days=2)  
    start    = start_dt.strftime(fmt)
    end      = end_dt.strftime(fmt)

    with pytest.warns(UserWarning, match="timestamp_start or timestamp_end in the future"):
        cld.main(
            portal_url,
            portal_name,
            data_path,
            instrument_ids,
            user_email,
            api_key,
            start,
            end,
        )

@patch("chords_downloader.chords_local_download.requests.get")
@patch("chords_downloader.chords_local_download.resources")
def test_main_raises_when_end_in_future(mock_resources, mock_get):
    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_JSON_RESPONSE
    mock_get.return_value = mock_response
    
    # Mock resources functions so they don't crash or do real work
    mock_resources.has_errors.return_value = False
    mock_resources.has_excess_datapoints.return_value = False
    mock_resources.struct_has_data.return_value = False  # Empty data -> no file written

    portal_url     = "https://example.com"
    portal_name    = "3D-PAWS"
    data_path      = Path("/tmp")
    instrument_ids = [1]
    user_email     = "test@example.com"
    api_key        = "dummy"
    
    start_dt = now - timedelta(hours=1)
    end_dt   = now + timedelta(days=2)  
    start    = start_dt.strftime(fmt)
    end      = end_dt.strftime(fmt)

    with pytest.warns(UserWarning, match="timestamp_start or timestamp_end in the future"):
        cld.main(
            portal_url,
            portal_name,
            data_path,
            instrument_ids,
            user_email,
            api_key,
            start,
            end,
        )
