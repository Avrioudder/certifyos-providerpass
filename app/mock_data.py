"""
Realistic enterprise healthcare provider intake and primary-source verification dataset.
Mirrors real-world CAQH, state medical board, DEA, NPDB, and OIG data feeds.
"""

from typing import List, Dict, Any

MOCK_PROVIDERS: List[Dict[str, Any]] = [
    {
        "intake": {
            "provider_id": "PRV-101",
            "npi": "1487629012",
            "full_name": "Dr. Katherine M. Vance",
            "specialty": "Cardiovascular Disease",
            "taxonomy_code": "207RC0000X",
            "state_licenses": [
                {
                    "state": "CA",
                    "license_number": "A145892",
                    "status": "ACTIVE",
                    "expiration_date": "2027-08-31"
                },
                {
                    "state": "NY",
                    "license_number": "298411",
                    "status": "ACTIVE",
                    "expiration_date": "2026-11-30"
                }
            ],
            "dea_number": "BV9018423",
            "practice_address": "850 3rd Avenue, Suite 1400, New York, NY 10022",
            "hospital_affiliations": ["Mount Sinai Hospital", "Lenox Hill Hospital"],
            "malpractice_claims_declared": 0,
            "submitted_date": "2026-10-28"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1487629012",
                "legal_name": "KATHERINE M VANCE",
                "other_names": ["KATHERINE VANCE-RIOS"],
                "taxonomy": "207RC0000X",
                "status": "ACTIVE"
            },
            "state_boards": [
                {
                    "board": "Medical Board of California",
                    "license_number": "A145892",
                    "name_on_record": "KATHERINE VANCE-RIOS",
                    "status": "CURRENT / ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-08-31"
                },
                {
                    "board": "New York State Board of Medicine",
                    "license_number": "298411",
                    "name_on_record": "KATHERINE M VANCE",
                    "status": "REGISTERED",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2026-11-30"
                }
            ],
            "dea": {
                "registration_number": "BV9018423",
                "name": "KATHERINE M VANCE",
                "schedules": ["2", "2N", "3", "3N", "4", "5"],
                "registered_state": "CA",
                "status": "ACTIVE",
                "expiration_date": "2027-04-30",
                "ny_cross_state_certificate": "EXPIRED"
            },
            "npdb": {
                "practitioner_id": "NPDB-984401",
                "adverse_actions": [],
                "malpractice_payments": [],
                "sanctions": []
            },
            "oig_sam": {
                "leie_status": "CLEAR",
                "sam_exclusion": "NONE",
                "checked_date": "2026-11-01"
            },
            "directory_verification": {
                "address_type": "CLINICAL_SUITE",
                "usps_deliverable": True,
                "npi_roster_match": True,
                "cms_directory_flag": "PASS"
            }
        }
    },
    {
        "intake": {
            "provider_id": "PRV-102",
            "npi": "1730192845",
            "full_name": "Dr. Marcus A. Brody",
            "specialty": "Orthopaedic Surgery",
            "taxonomy_code": "207X00000X",
            "state_licenses": [
                {
                    "state": "TX",
                    "license_number": "T84920",
                    "status": "ACTIVE",
                    "expiration_date": "2027-12-31"
                }
            ],
            "dea_number": "FB4491021",
            "practice_address": "6400 Fannin St, Suite 2200, Houston, TX 77030",
            "hospital_affiliations": ["Houston Methodist Hospital", "Memorial Hermann Texas Medical Center"],
            "malpractice_claims_declared": 0,
            "submitted_date": "2026-10-30"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1730192845",
                "legal_name": "MARCUS A BRODY",
                "other_names": [],
                "taxonomy": "207X00000X",
                "status": "ACTIVE"
            },
            "state_boards": [
                {
                    "board": "Texas Medical Board",
                    "license_number": "T84920",
                    "name_on_record": "MARCUS A BRODY",
                    "status": "ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-12-31"
                }
            ],
            "dea": {
                "registration_number": "FB4491021",
                "name": "MARCUS A BRODY",
                "schedules": ["2", "2N", "3", "3N", "4", "5"],
                "registered_state": "TX",
                "status": "ACTIVE",
                "expiration_date": "2027-09-30"
            },
            "npdb": {
                "practitioner_id": "NPDB-411294",
                "adverse_actions": [],
                "malpractice_payments": [],
                "sanctions": []
            },
            "oig_sam": {
                "leie_status": "CLEAR",
                "sam_exclusion": "NONE",
                "checked_date": "2026-11-01"
            },
            "directory_verification": {
                "address_type": "HOSPITAL_MEDICAL_OFFICE_BUILDING",
                "usps_deliverable": True,
                "npi_roster_match": True,
                "cms_directory_flag": "PASS"
            }
        }
    },
    {
        "intake": {
            "provider_id": "PRV-103",
            "npi": "1942385109",
            "full_name": "Dr. Eleanor Chen",
            "specialty": "Psychiatry & Neurology",
            "taxonomy_code": "2084P0800X",
            "state_licenses": [
                {
                    "state": "FL",
                    "license_number": "ME149021",
                    "status": "ACTIVE",
                    "expiration_date": "2027-01-31"
                },
                {
                    "state": "GA",
                    "license_number": "083921",
                    "status": "ACTIVE",
                    "expiration_date": "2026-12-31"
                }
            ],
            "dea_number": "BC5581902",
            "practice_address": "1200 S Pine Island Rd, Suite 101, Plantation, FL 33324",
            "hospital_affiliations": ["HCA Florida Westside Hospital"],
            "malpractice_claims_declared": 0,
            "submitted_date": "2026-10-25"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1942385109",
                "legal_name": "ELEANOR CHEN",
                "other_names": [],
                "taxonomy": "2084P0800X",
                "status": "ACTIVE"
            },
            "state_boards": [
                {
                    "board": "Florida Board of Medicine",
                    "license_number": "ME149021",
                    "name_on_record": "ELEANOR CHEN",
                    "status": "CLEAR / ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-01-31"
                },
                {
                    "board": "Georgia Composite Medical Board",
                    "license_number": "083921",
                    "name_on_record": "ELEANOR CHEN",
                    "status": "ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2026-12-31"
                }
            ],
            "dea": {
                "registration_number": "BC5581902",
                "name": "ELEANOR CHEN",
                "schedules": ["3", "3N", "4", "5"],
                "registered_state": "FL",
                "status": "ACTIVE",
                "expiration_date": "2028-02-28"
            },
            "npdb": {
                "practitioner_id": "NPDB-773019",
                "adverse_actions": [],
                "malpractice_payments": [
                    {
                        "date_of_payment": "2024-03-15",
                        "amount": 140000,
                        "allegation": "Failure to monitor medication adverse reaction during outpatient psychotherapy",
                        "outcome": "Settled without admission of liability",
                        "settling_entity": "Physicians Protective Trust"
                    }
                ],
                "sanctions": []
            },
            "directory_verification": {
                "address_type": "COMMERCIAL_MAIL_RECEIVING_AGENCY (UPS STORE)",
                "usps_deliverable": True,
                "npi_roster_match": False,
                "cms_directory_flag": "POTENTIAL_GHOST_LOCATION"
            },
            "oig_sam": {
                "leie_status": "CLEAR",
                "sam_exclusion": "NONE",
                "checked_date": "2026-11-01"
            }
        }
    },
    {
        "intake": {
            "provider_id": "PRV-104",
            "npi": "1033284918",
            "full_name": "Dr. Arthur Pendelton",
            "specialty": "Internal Medicine",
            "taxonomy_code": "207R00000X",
            "state_licenses": [
                {
                    "state": "OH",
                    "license_number": "35-081293",
                    "status": "ACTIVE",
                    "expiration_date": "2026-10-01"
                }
            ],
            "dea_number": "AP1920394",
            "practice_address": "4500 Spring Grove Ave, Cincinnati, OH 45232",
            "hospital_affiliations": ["University of Cincinnati Medical Center"],
            "malpractice_claims_declared": 2,
            "submitted_date": "2026-10-18"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1033284918",
                "legal_name": "ARTHUR PENDELTON",
                "other_names": [],
                "taxonomy": "207R00000X",
                "status": "DEACTIVATED"
            },
            "state_boards": [
                {
                    "board": "State Medical Board of Ohio",
                    "license_number": "35-081293",
                    "name_on_record": "ARTHUR PENDELTON",
                    "status": "SUSPENDED / REVOKED",
                    "disciplinary_actions": "Formal Order of Revocation entered 2024-05-12 for billing violations",
                    "expiration_date": "2024-10-01"
                }
            ],
            "dea": {
                "registration_number": "AP1920394",
                "name": "ARTHUR PENDELTON",
                "schedules": [],
                "registered_state": "OH",
                "status": "SURRENDERED_FOR_CAUSE",
                "expiration_date": "2024-06-30"
            },
            "npdb": {
                "practitioner_id": "NPDB-110294",
                "adverse_actions": [
                    {
                        "action_type": "Revocation of Medical License",
                        "date": "2024-05-12",
                        "adjudicating_agency": "State Medical Board of Ohio"
                    }
                ],
                "malpractice_payments": [
                    {"amount": 450000, "date": "2023-01-14"},
                    {"amount": 320000, "date": "2023-09-22"}
                ],
                "sanctions": ["Exclusion from state Medicaid provider panels"]
            },
            "oig_sam": {
                "leie_status": "EXCLUDED",
                "exclusion_type": "1128(a)(1) - Conviction of program-related crimes",
                "exclusion_date": "2024-07-20",
                "sam_exclusion": "ACTIVE_EXCLUSION_RECIPROCAL",
                "checked_date": "2026-11-01"
            },
            "directory_verification": {
                "address_type": "VACANT_COMMERCIAL",
                "usps_deliverable": False,
                "npi_roster_match": False,
                "cms_directory_flag": "FAIL_NON_OPERATIONAL"
            }
        }
    },
    {
        "intake": {
            "provider_id": "PRV-105",
            "npi": "1598204910",
            "full_name": "Dr. Sophia Ramirez",
            "specialty": "Pediatrics",
            "taxonomy_code": "208000000X",
            "state_licenses": [
                {
                    "state": "IL",
                    "license_number": "036128490",
                    "status": "ACTIVE",
                    "expiration_date": "2027-07-31"
                }
            ],
            "dea_number": "SR8391024",
            "practice_address": "233 E Erie St, Suite 400, Chicago, IL 60611",
            "hospital_affiliations": ["Ann & Robert H. Lurie Children's Hospital"],
            "malpractice_claims_declared": 0,
            "submitted_date": "2026-10-31"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1598204910",
                "legal_name": "SOPHIA RAMIREZ",
                "other_names": [],
                "taxonomy": "208000000X",
                "status": "ACTIVE"
            },
            "state_boards": [
                {
                    "board": "Illinois Department of Financial and Professional Regulation",
                    "license_number": "036128490",
                    "name_on_record": "SOPHIA RAMIREZ",
                    "status": "ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-07-31"
                }
            ],
            "dea": {
                "registration_number": "SR8391024",
                "name": "SOPHIA RAMIREZ",
                "schedules": ["2", "2N", "3", "3N", "4", "5"],
                "registered_state": "IL",
                "status": "ACTIVE_EXPIRING_IMMINENT",
                "expiration_date": "2026-11-06"
            },
            "npdb": {
                "practitioner_id": "NPDB-551029",
                "adverse_actions": [],
                "malpractice_payments": [],
                "sanctions": []
            },
            "oig_sam": {
                "leie_status": "CLEAR",
                "sam_exclusion": "NONE",
                "checked_date": "2026-11-01"
            },
            "directory_verification": {
                "address_type": "CLINICAL_OUTPATIENT_CENTER",
                "usps_deliverable": True,
                "npi_roster_match": True,
                "cms_directory_flag": "PASS"
            }
        }
    },
    {
        "intake": {
            "provider_id": "PRV-106",
            "npi": "1295810239",
            "full_name": "Dr. Julian Hayes",
            "specialty": "Neurology",
            "taxonomy_code": "2084N0400X",
            "state_licenses": [
                {
                    "state": "WA",
                    "license_number": "MD60849120",
                    "status": "ACTIVE",
                    "expiration_date": "2027-09-15"
                },
                {
                    "state": "OR",
                    "license_number": "MD194022",
                    "status": "ACTIVE",
                    "expiration_date": "2027-03-31"
                }
            ],
            "dea_number": "JH9918234",
            "practice_address": "1100 9th Ave, Seattle, WA 98101",
            "hospital_affiliations": ["Virginia Mason Medical Center", "Swedish Medical Center"],
            "malpractice_claims_declared": 0,
            "submitted_date": "2026-10-29"
        },
        "primary_sources": {
            "nppes": {
                "npi": "1295810239",
                "legal_name": "JULIAN HAYES",
                "other_names": [],
                "taxonomy": "2084N0400X",
                "status": "ACTIVE"
            },
            "state_boards": [
                {
                    "board": "Washington Medical Commission",
                    "license_number": "MD60849120",
                    "name_on_record": "JULIAN HAYES",
                    "status": "ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-09-15"
                },
                {
                    "board": "Oregon Medical Board",
                    "license_number": "MD194022",
                    "name_on_record": "JULIAN HAYES",
                    "status": "ACTIVE",
                    "disciplinary_actions": "NONE",
                    "expiration_date": "2027-03-31"
                }
            ],
            "dea": {
                "registration_number": "JH9918234",
                "name": "JULIAN HAYES",
                "schedules": ["2", "2N", "3", "3N", "4", "5"],
                "registered_state": "WA",
                "status": "ACTIVE",
                "expiration_date": "2027-11-30"
            },
            "npdb": {
                "practitioner_id": "NPDB-301928",
                "adverse_actions": [],
                "malpractice_payments": [],
                "sanctions": []
            },
            "oig_sam": {
                "leie_status": "CLEAR",
                "sam_exclusion": "NONE",
                "checked_date": "2026-11-01"
            },
            "directory_verification": {
                "address_type": "AMBULATORY_CARE_FACILITY",
                "usps_deliverable": True,
                "npi_roster_match": True,
                "cms_directory_flag": "PASS"
            }
        }
    }
]
