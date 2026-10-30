#!/usr/bin/env python
import csv
from datetime import datetime
import json
from typing import List, Dict, Any

# Fixed constants
LACTATING_ACTIVITY_TYPE_ID = '00000000-0000-0000-0000-000000000014'
# PARCEL_ID = "urn:farmcalendar:Parcel:00000000-0000-0000-0000-000000000001"


def translate_csv_into_bulk_data(csv_file_path: str) -> List[Dict[str, Any]]:
    """
    Read CSV file and transform into bulk API format.

    Each row represents an activity for an animal. Multiple rows can reference the same animal.
    Animals are grouped by their CIA (national ID).

    CSV Columns mapping:
    - CIA -> nationalID and name
    - CAsoc -> isMemberOfAnimalGroup.hasName
    - Birthdate -> birthdate (DD.MM.YYYY)
    - Species -> species
    - Breed -> breed
    - Sex -> sex (Female=1, Male=2)
    - ParcelID -> hasAgriParcel
    - Test date -> hasStartDatetime
    - Lactation number -> hasLactationNumber
    - Control -> hasControl
    - Milk (L) -> hasMilkYield.hasValue
    - Fat (%) -> hasFat.hasValue
    - Protein (%) -> hasProtein.hasValue
    - RCS -> hasRCS.hasValue
    - Lactose (%) -> hasLactose.hasValue (new field)
    - Dry matter (%) -> hasDryMatter.hasValue
    - Urea (mg/L) -> hasUrea.hasValue
    - Days in milk -> hasDaysInMilk
    - Total milk (L) -> hasTotalMilkYield.hasValue

    Args:
        csv_file_path: Path to CSV file

    Returns:
        List of dictionaries in bulk API format
    """

    # Dictionary to store animals and their activities
    # Key: CIA (national ID), Value: {'animal': animal_data, 'activities': []}
    animals_dict = {}

    # Map Spanish sex to integer values expected by API
    sex_mapping = {
        'Female': 1,
        'Male': 2,
        'Hembra': 1,
        'Macho': 2
    }

    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')

        for row in reader:
            cia = row['CIA']

            # If this animal doesn't exist yet, create its animal data
            if cia not in animals_dict:
                # Parse birthdate from DD.MM.YYYY to ISO format
                birth_date = datetime.strptime(row['Birthdate'], '%d.%m.%Y')

                # Format animal data (only once per animal)
                animal_data = {
                    "nationalID": cia,
                    "name": cia,  # Using CIA as name as agreed
                    "description": "",  # Empty as per discussion
                    "hasAgriParcel": row['ParcelID'],  # Now using ParcelID column
                    "sex": sex_mapping.get(row['Sex'], 1),  # Default to Female if mapping fails
                    "isCastrated": False,  # Not in CSV, default to False
                    "species": row['Species'],
                    "breed": row['Breed'],
                    "birthdate": birth_date.isoformat() + 'Z',
                    "isMemberOfAnimalGroup": {
                        "hasName": row['CAsoc']
                    },
                    "status": 1  # Active status
                }

                # Initialize animal entry with empty activities list
                animals_dict[cia] = {
                    'animal': animal_data,
                    'activities': []
                }

            # Parse the test date for the activity
            test_date = datetime.strptime(row['Test date'], '%d.%m.%Y')

            # Add the activity from this row to the animal's activities list
            activity = {
                "activityType": LACTATING_ACTIVITY_TYPE_ID,
                "title": f"Lactation {row['Lactation number']} - Production Check",
                "details": f"Milk recording on {row['Test date']}",
                # "hasStartDatetime": test_date.isoformat() + 'T00:00:00Z',
                "hasStartDatetime": test_date.strftime('%Y-%m-%dT08:00:00Z'),
                "hasEndDatetime": None,
                "hasDaysInMilk": float(row['Days in milk']),
                "hasLactationNumber": float(row['Lactation number']),
                "hasControl": row['Control'],
                "hasTotalMilkYield": {
                    "unit": "Liters",
                    "hasValue": float(row['Total milk (L)'].replace(',', '.'))
                },
                "hasMilkYield": {
                    "unit": "Liters",
                    "hasValue": float(row['Milk (L)'].replace(',', '.'))
                },
                "hasRCS": {
                    "unit": "NMB",
                    "hasValue": float(row['RCS'].replace(',', '.'))
                },
                "hasUrea": {
                    "unit": "mgL",
                    "hasValue": float(row['Urea (mg/L)'].replace(',', '.'))
                },
                "hasFat": {
                    "unit": "Percentage",
                    "hasValue": float(row['Fat (%)'].replace(',', '.'))
                },
                "hasProtein": {
                    "unit": "Percentage",
                    "hasValue": float(row['Protein (%)'].replace(',', '.'))
                },
                "hasLactose": {  # New field from CSV
                    "unit": "Percentage",
                    "hasValue": float(row['Lactose (%)'].replace(',', '.'))
                },
                "hasDryMatter": {
                    "unit": "Percentage",
                    "hasValue": float(row['Dry matter (%)'].replace(',', '.'))
                }
            }

            animals_dict[cia]['activities'].append(activity)

    # Convert dictionary values to list format expected by API
    bulk_data = list(animals_dict.values())

    return bulk_data

def save_bulk_data_as_json(bulk_data, json_path):
    with open(json_path, 'w') as f:
        json.dump(bulk_data, f, indent=4)
        print(f'Saved to file: "{json_path}" .')
        print(f'This data is already in the format necessary for posting in the "/api/v1/bulk/animal-lactating-activities" endpoint of FarmCalendar.')

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python translate_to_fc_data.py <input_csv_path> <output_json_path>")
        print("Example: python translate_to_fc_data.py example_farm_animals_bulk.csv farm_calendar_animals_bulk.json")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_json = sys.argv[2]

    bulk_data = translate_csv_into_bulk_data(csv_file_path=input_csv)
    save_bulk_data_as_json(bulk_data, output_json)
