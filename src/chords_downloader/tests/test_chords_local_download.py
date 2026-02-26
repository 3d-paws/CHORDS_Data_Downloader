import pytest
from datetime import timedelta, datetime
from pathlib import Path
from chords_downloader import chords_local_download as cld

now = datetime.now()
fmt = "%Y-%m-%d %H:%M:%S"

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


def test_main_raises_when_start_before_two_years():
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
    
    assert "timestamp_start before CHORDS cutoff" in str(excinfo.value)


def test_main_raises_when_start_in_future():
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
    
    assert "timestamp_start or timestamp_end in the future" in str(excinfo.value)


def test_main_raises_when_end_in_future():
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
    
    assert "timestamp_start or timestamp_end in the future" in str(excinfo.value)
