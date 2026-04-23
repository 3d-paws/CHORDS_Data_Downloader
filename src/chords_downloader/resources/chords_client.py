from __future__ import annotations

import requests
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable


DATE_FMT = "%Y-%m-%d %H:%M:%S"


@dataclass(frozen=True)
class ChordsAuth:
    email:   str
    api_key: str

@dataclass(frozen=True)
class ChordsPortal:
    name:     str
    base_url: str

@dataclass(frozen=True)
class ChordsWindow:
    start:  datetime
    end:    datetime


class ChordsClientError(Exception):                     pass
class ChordsAuthError(ChordsClientError):               pass
class ChordsPermissionError(ChordsClientError):         pass
class ChordsNotFoundError(ChordsClientError):           pass
class ChordsValidationError(ChordsClientError):         pass
class ChordsServerError(ChordsClientError):             pass
class ChordsExcessDatapointsError(ChordsClientError):   pass


"""
NOTE: Insert docstring here.
"""
def _validate_common_inputs(portal_name: str, base_url: str, user_email: str,
                            api_key: str, start: datetime, end: datetime,) -> None:
    if not isinstance(portal_name, str):
        raise TypeError(f"portal_name must be str, got {type(portal_name)}")
    if not isinstance(base_url, str):
        raise TypeError(f"base_url must be str, got {type(base_url)}")
    if not isinstance(user_email, str):
        raise TypeError(f"user_email must be str, got {type(user_email)}")
    if not isinstance(api_key, str):
        raise TypeError(f"api_key must be str, got {type(api_key)}")
    if not isinstance(start, datetime):
        raise TypeError(f"start must be datetime, got {type(start)}")
    if not isinstance(end, datetime):
        raise TypeError(f"end must be datetime, got {type(end)}")
    if start >= end:
        raise ValueError("start must be before end")


"""
NOTE: Insert docstring here.
"""
def _format_dt(dt: datetime) -> str:
    return dt.strftime(DATE_FMT)


"""
NOTE: Insert docstring here.
"""
def _request_json(url: str, params:dict[str, Any], timeout:int=30) -> tuple[requests.Response, dict]:
    response = requests.get(url=url, params=params, timeout=timeout)

    try:
        payload = response.json()
    except Exception:
        payload ={}

    return response, payload


"""
NOTE: Insert docstring here.
"""
def _is_excess_datapoints(response: requests.Response, payload:dict) -> bool:
    if response.status_code == 413:
        return True
    
    errors = payload.get("errors")
    if not errors:
        return False
    
    if isinstance(errors, list):
        text = " ".join(str(e) for e in errors).lower()
    else:
        text = str(errors).lower()

    return (
        "too many datapoints" in text
        or "excess datapoints" in text
        or "exceeds" in text and "datapoint" in text
    )


"""
NOTE: Insert docstring here.
"""
def _raise_for_error(response:requests.Response, payload:dict, portal_name:str, context:str) -> None:
    status_code = response.status_code

    if _is_excess_datapoints(response, payload):
        raise ChordsExcessDatapointsError(f"{portal_name} {context}: excess datapoints requested")

    if status_code == 401:
        raise ChordsAuthError(f"{portal_name} {context}: unauthorized - invalid email/api_key")
    if status_code == 403:
        raise ChordsPermissionError(f"{portal_name} {context}: forbidden - access denied")
    if status_code == 404:
        raise ChordsNotFoundError(f"{portal_name} {context}: endpoint/instrument not found")
    if status_code == 422:
        raise ChordsValidationError(f"{portal_name} {context}: bad date range or parameters")
    if status_code in (500, 502, 503, 504):
        raise ChordsServerError(f"{portal_name} {context}: server error {status_code}")
    if status_code >= 400:
        raise ChordsClientError(f"{portal_name} {context}: unexpected HTTP {status_code}")

    if "errors" in payload and payload["errors"]:
        msg = payload["errors"]
        if isinstance(msg, list):
            msg = msg[0]
        text = str(msg)

        if "access denied" in text.lower() or "authentication required" in text.lower():
            raise ChordsAuthError(f"{portal_name} {context}: {text}")
        
        raise ChordsClientError(f"{portal_name} {context}: {text}")
    
    if "error" in payload:
        raise ChordsClientError(f"{portal_name} {context}: {text}")


"""
NOTE: Insert docstring here.
"""
def _extract_records(payload:dict) -> list[dict]:
    records = []
    features = payload.get("features", [])

    for feature in features:
        properties = feature.get("properties", {})
        data = properties.get("data", [])
        if isinstance(data, list):
            records.extend(data)
    
    return records


"""
NOTE: Insert docstring here.
"""
def _dedupe_records(records:list[dict]) -> list[dict]:
    seen = set()
    output = []

    for rec in records:
        time_val = rec.get("time")
        measurements = rec.get("measurements", {})
        measurement_key = tuple(sorted(measurements.items())) if isinstance(measurements, dict) else ()
        dedupe_key = (time_val, measurement_key)

        if dedupe_key not in seen:
            seen.add(dedupe_key)
            output.append(rec)
        
        output.sort(key=lambda r: r.get("time", ""))
        return output


"""
NOTE: Insert docstring here.
"""
def _fetch_with_reduction(
        portal_name: str,
        base_url: str, 
        user_email: str,
        api_key: str,
        start: datetime,
        end: datetime,
        endpoint_builder: Callable[[str], str],
        context: str,
        timeout: int=30,
        min_window: timedelta=timedelta(minutes=1)
) -> list[dict]:
    _validate_common_inputs(portal_name, base_url, user_email, api_key, start, end)

    queue = deque([start, end])
    all_records: list[dict] = []

    while queue:
        seg_start, seg_end = queue.popleft()

        url = endpoint_builder(base_url)
        params = {
            "start": _format_dt(seg_start),
            "end": _format_dt(seg_end),
            "email": user_email,
            "api_key": api_key
        }

        response, payload = _request_json(url, params=params, timeout=timeout)

        if _is_excess_datapoints(response, payload):
            span = seg_end - seg_start
            if span <= min_window:
                raise ChordsExcessDatapointsError(
                    f"{portal_name} {context}: still too many datapoints at minimum window {min_window}"
                )
            
            midpoint = seg_start + span/2
            queue.appendleft((midpoint, seg_end))
            queue.append((seg_start, midpoint))
            continue

        _raise_for_error(response, payload, portal_name, context)
        all_records.extend(_extract_records(payload))

    return _dedupe_records(all_records)


"""
NOTE: Insert docstring here.
"""
def fetch_instrument_records(
    portal_name: str,
    base_url: str,
    instrument_id: int,
    user_email: str,
    api_key: str,
    start: datetime,
    end: datetime
) -> list[dict]:
    if not isinstance(instrument_id, int):
        raise TypeError(f"Parameter 'instrument_id' must be type <int>, got {type(instrument_id)}")

    def endpoint_builder(base: str) -> str:
        return f"{base}/api/v1/data/{instrument_id}"
    
    return _fetch_with_reduction(
        portal_name=portal_name,
        base_url=base_url,
        user_email=user_email,
        api_key=api_key,
        start=start, 
        end=end,
        endpoint_builder=endpoint_builder,
        context=f"instrument #{instrument_id}"
    )


"""
NOTE: Insert docstring here.
"""
def fetch_portal_records(
        portal_name: str,
        base_url: str,
        user_email: str,
        api_key: str,
        start: datetime,
        end: datetime
) -> list[dict]:
    def endpoint_builder(base: str) -> str:
        return f"{base}/api/v1/data"
    
    return _fetch_with_reduction(
        portal_name=portal_name,
        base_url=base_url,
        user_email=user_email,
        api_key=api_key,
        start=start,
        end=end,
        endpoint_builder=endpoint_builder,
        context="portal-wide"
    )
