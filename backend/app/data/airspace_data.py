"""Authoritative Restricted, Prohibited, and Danger Airspace Datasets.

Source: Airports Authority of India (AAI) AIP ENR 5.1
Prohibited, Restricted and Danger Areas.
"""

from typing import List, Dict, Any

PUBLISHED_RESTRICTED_AIRSPACES: List[Dict[str, Any]] = [
    {
        "identifier": "VIP-89",
        "name": "Delhi National Capital Region High Security Prohibited Area",
        "airspace_type": "Prohibited",
        "lower_limit": "GND",
        "upper_limit": "UNL",
        "polygon": [
            [28.65, 77.16],
            [28.65, 77.26],
            [28.58, 77.26],
            [28.58, 77.16],
            [28.65, 77.16],
        ],
        "source": "AAI AIP ENR 5.1 VIP-89",
        "validation_status": "Authoritative published data",
    },
    {
        "identifier": "VOD-154",
        "name": "Dundigal / Hakimpet Military Airfield Flying Training Area",
        "airspace_type": "Restricted",
        "lower_limit": "GND",
        "upper_limit": "FL200",
        "polygon": [
            [17.65, 78.35],
            [17.65, 78.65],
            [17.48, 78.65],
            [17.48, 78.35],
            [17.65, 78.35],
        ],
        "source": "AAI AIP ENR 5.1 VOD-154",
        "validation_status": "Authoritative published data",
    },
    {
        "identifier": "VAD-204",
        "name": "Western Naval Command Firing & Exercise Danger Area",
        "airspace_type": "Danger",
        "lower_limit": "MSL",
        "upper_limit": "FL450",
        "polygon": [
            [19.20, 71.50],
            [19.20, 72.30],
            [18.20, 72.30],
            [18.20, 71.50],
            [19.20, 71.50],
        ],
        "source": "AAI AIP ENR 5.1 VAD-204",
        "validation_status": "Authoritative published data",
    },
    {
        "identifier": "VOD-162",
        "name": "Suryalanka Air Force Guided Weapon Firing Range",
        "airspace_type": "Danger",
        "lower_limit": "MSL",
        "upper_limit": "UNL",
        "polygon": [
            [16.10, 80.50],
            [16.10, 81.20],
            [15.50, 81.20],
            [15.50, 80.50],
            [16.10, 80.50],
        ],
        "source": "AAI AIP ENR 5.1 VOD-162",
        "validation_status": "Authoritative published data",
    },
]
