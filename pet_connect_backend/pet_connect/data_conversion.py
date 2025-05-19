"""
Pet Connect Data Conversion Script

This script handles the conversion and standardization of animal data from multiple shelters.
It processes CSV files, standardizes attributes, cleans data, and imports it into the SQLite database.
"""

import pandas as pd
import sqlite3
import os
import re
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATABASE_PATH = 'db.sqlite3'  # Use your existing Django database
DATA_DIR = 'shelter_data'
OUTPUT_DIR = 'output'
VISUALIZATION_DIR = os.path.join(OUTPUT_DIR, 'visualizations')

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

# Define mapping dictionaries for standardizing data
COLUMN_MAPPINGS = {
    'rspca_surrey.csv': {
        'Animal ID': 'animal_id_original',
        'Name': 'name',
        'Breed Type': 'breed',
        'Age': 'age_original',
        'Gender': 'gender_original',
        'Health': 'health_status',
        'Behavior': 'behavior_traits',
        'Location': 'location',
        'Availability': 'status_original',
        'Species': 'species',
        'Size': 'size_original',
        'Activity Level': 'energy_level_original'
    },
    'animal_rescue_center.csv': {
        'ID': 'animal_id_original',
        'Pet Name': 'name',
        'Animal Breed': 'breed',
        'Age (months)': 'age_months',
        'Sex': 'gender_original',
        'Medical Status': 'health_status',
        'Behavior Notes': 'behavior_traits',
        'Shelter Location': 'location',
        'Status': 'status_original',
        'Type': 'species',
        'Animal Size': 'size_original',
        'Energy': 'energy_level_original'
    },
    'battersea.csv': {
        'Pet ID': 'animal_id_original',
        'Name': 'name',
        'Type & Breed': 'breed',
        'Years': 'age_years',
        'Sex': 'gender_original',
        'Medical History': 'health_status',
        'Temperament': 'behavior_traits',
        'Branch': 'location',
        'Adoption Status': 'status_original',
        'Animal Type': 'species',
        'Size Category': 'size_original',
        'Activity Needs': 'energy_level_original'
    },
    'humane_society.csv': {
        'Ref Number': 'animal_id_original',
        'Animal Name': 'name',
        'Breed': 'breed',
        'Years Old': 'age_years',
        'Months Old': 'age_months',
        'M/F': 'gender_original',
        'Vaccinated': 'vaccinated',
        'Neutered/Spayed': 'neutered',
        'Kid Friendly': 'good_with_kids',
        'Cat Friendly': 'good_with_cats',
        'Dog Friendly': 'good_with_dogs',
        'Status': 'status_original',
        'Animal Type': 'species',
        'Size': 'size_original',
        'Energy Level': 'energy_level_original'
    }
}

# Value mapping dictionaries
GENDER_MAPPING = {
    'male': 'M', 'm': 'M', 'boy': 'M', 'masculine': 'M',
    'female': 'F', 'f': 'F', 'girl': 'F', 'feminine': 'F',
}

SPECIES_MAPPING = {
    'dog': 'Dog', 'puppy': 'Dog', 'canine': 'Dog', 'k9': 'Dog',
    'cat': 'Cat', 'kitten': 'Cat', 'feline': 'Cat',
    'bird': 'Bird', 'avian': 'Bird',
    'rabbit': 'Rabbit', 'bunny': 'Rabbit',
    'guinea pig': 'Guinea Pig',
    'hamster': 'Hamster',
    'small animal': 'Small Animal',
    'rat': 'Rat', 'mouse': 'Mouse'
}

STATUS_MAPPING = {
    'available': 'A', 'ready': 'A', 'adoptable': 'A',
    'pending': 'P', 'on hold': 'P', 'reserved': 'P',
    'adopted': 'AD', 'rehomed': 'AD', 'forever home': 'AD',
    'unavailable': 'NA', 'not available': 'NA', 'medical hold': 'NA'
}

# Size mapping
SIZE_MAPPING = {
    'small': 'Small', 's': 'Small', 'tiny': 'Small', 'petite': 'Small', 'little': 'Small',
    'medium': 'Medium', 'm': 'Medium', 'average': 'Medium', 'moderate': 'Medium',
    'large': 'Large', 'l': 'Large', 'big': 'Large', 'huge': 'Large', 'xl': 'Large',
    'extra large': 'Large', 'extra-large': 'Large'
}

# Energy level mapping
ENERGY_MAPPING = {
    'low': 'Low', 'l': 'Low', 'calm': 'Low', 'lazy': 'Low', 'relaxed': 'Low', 'minimal': 'Low',
    'medium': 'Medium', 'm': 'Medium', 'moderate': 'Medium', 'average': 'Medium',
    'high': 'High', 'h': 'High', 'active': 'High', 'energetic': 'High', 'hyper': 'High'
}

# Connect to the database
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

def create_shelter_mapping_table():
    """
    Create a visualization of the mapping between different shelter data formats
    """
    # Create a DataFrame to show the mapping
    shelter_files = list(COLUMN_MAPPINGS.keys())
    all_std_columns = set()
    
    # Collect all standard columns
    for mapping in COLUMN_MAPPINGS.values():
        all_std_columns.update(mapping.values())
    
    all_std_columns = sorted(list(all_std_columns))
    
    # Create a DataFrame with shelters as rows and standard columns as columns
    mapping_df = pd.DataFrame(index=shelter_files, columns=all_std_columns)
    
    # Fill in the mapping
    for shelter_file, mapping in COLUMN_MAPPINGS.items():
        for orig_col, std_col in mapping.items():
            mapping_df.loc[shelter_file, std_col] = orig_col
    
    # Save the mapping table to CSV
    mapping_df.to_csv(os.path.join(OUTPUT_DIR, 'attribute_mapping.csv'))
    
    # Create an HTML version with better formatting
    html = """
    <html>
    <head>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
                font-family: Arial, sans-serif;
            }
            th, td {
                border: 1px solid #dddddd;
                text-align: left;
                padding: 8px;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .highlight {
                background-color: #e6f7ff;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <h2>Attribute Mapping Across Shelter Data Sources</h2>
        <table>
            <tr>
                <th>Standardized Attribute</th>
    """
    
    # Add shelter files as column headers
    for shelter_file in shelter_files:
        html += f"<th>{shelter_file}</th>\n"
    
    html += "</tr>\n"
    
    # Add rows for each standardized attribute
    for col in all_std_columns:
        html += f"<tr>\n<td class='highlight'>{col}</td>\n"
        for shelter_file in shelter_files:
            value = mapping_df.loc[shelter_file, col]
            html += f"<td>{value if not pd.isna(value) else ''}</td>\n"
        html += "</tr>\n"
    
    html += """
        </table>
    </body>
    </html>
    """
    
    # Save HTML to file
    with open(os.path.join(OUTPUT_DIR, 'attribute_mapping.html'), 'w') as f:
        f.write(html)
    
    print(f"Attribute mapping table saved to {os.path.join(OUTPUT_DIR, 'attribute_mapping.csv')}")
    print(f"HTML version saved to {os.path.join(OUTPUT_DIR, 'attribute_mapping.html')}")
    
    return mapping_df

def clean_age(age_str):
    """
    Convert various age formats to years and months
    Returns a tuple of (years, months)
    """
    if pd.isna(age_str):
        return (0, 0)
    
    age_str = str(age_str).lower().strip()
    years = 0
    months = 0
    
    # Extract years
    years_match = re.search(r'(\d+)\s*(?:years?|yrs?|y(?:ear)?s?(?:\s*old)?)', age_str)
    if years_match:
        years = int(years_match.group(1))
    
    # Extract months
    months_match = re.search(r'(\d+)\s*(?:months?|mos?)', age_str)
    if months_match:
        months = int(months_match.group(1))
    
    # Extract weeks (convert to months)
    weeks_match = re.search(r'(\d+)\s*(?:weeks?|wks?)', age_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        months += round(weeks / 4.3)  # Approximately 4.3 weeks per month
    
    # If only a number is provided, assume years if >= 2, otherwise months
    if re.match(r'^\d+$', age_str):
        num = int(age_str)
        if num >= 2:
            years = num
        else:
            months = num * 12
    
    # If specified as just "X y/o", assume years
    yo_match = re.search(r'(\d+)\s*y/o', age_str)
    if yo_match:
        years = int(yo_match.group(1))
    
    # Ensure months are between 0-11 (roll into years if >= 12)
    if months >= 12:
        additional_years = months // 12
        years += additional_years
        months = months % 12
    
    return (years, months)

def standardize_gender(gender_str):
    """
    Standardize gender to 'M', 'F', or 'U'
    """
    if pd.isna(gender_str):
        return 'U'
    
    gender_str = str(gender_str).lower().strip()
    
    if gender_str in GENDER_MAPPING:
        return GENDER_MAPPING[gender_str]
    
    # Check if the gender string contains any of the mapping keys
    for key, value in GENDER_MAPPING.items():
        if key in gender_str:
            return value
    
    return 'U'  # Unknown

def standardize_species(species_str):
    """
    Standardize species names
    """
    if pd.isna(species_str):
        return None
    
    species_str = str(species_str).lower().strip()
    
    if species_str in SPECIES_MAPPING:
        return SPECIES_MAPPING[species_str]
    
    # Check if the species string contains any of the mapping keys
    for key, value in SPECIES_MAPPING.items():
        if key in species_str:
            return value
    
    # If we can't determine the species, return original with proper capitalization
    return species_str.title()

def standardize_status(status_str):
    """
    Standardize status to 'A', 'P', 'AD', or 'NA'
    """
    if pd.isna(status_str):
        return 'A'  # Default to available
    
    status_str = str(status_str).lower().strip()
    
    if status_str in STATUS_MAPPING:
        return STATUS_MAPPING[status_str]
    
    # Check if the status string contains any of the mapping keys
    for key, value in STATUS_MAPPING.items():
        if key in status_str:
            return value
    
    return 'A'  # Default to available

def standardize_size(size_str):
    """
    Standardize size to 'Small', 'Medium', or 'Large'
    """
    if pd.isna(size_str):
        return 'Medium'  # Default to medium
    
    size_str = str(size_str).lower().strip()
    
    if size_str in SIZE_MAPPING:
        return SIZE_MAPPING[size_str]
    
    # Check if the size string contains any of the mapping keys
    for key, value in SIZE_MAPPING.items():
        if key in size_str:
            return value
    
    # Default to Medium if we can't determine the size
    return 'Medium'

def standardize_energy_level(energy_str):
    """
    Standardize energy level to 'Low', 'Medium', or 'High'
    """
    if pd.isna(energy_str):
        return 'Medium'  # Default to medium
    
    energy_str = str(energy_str).lower().strip()
    
    if energy_str in ENERGY_MAPPING:
        return ENERGY_MAPPING[energy_str]
    
    # Check if the energy string contains any of the mapping keys
    for key, value in ENERGY_MAPPING.items():
        if key in energy_str:
            return value
    
    # Try to extract from behavior traits if energy not specified
    if 'active' in energy_str or 'energetic' in energy_str or 'playful' in energy_str:
        return 'High'
    elif 'calm' in energy_str or 'relaxed' in energy_str or 'quiet' in energy_str:
        return 'Low'
    
    # Default to Medium if we can't determine the energy level
    return 'Medium'

def infer_size_from_breed(breed_str, species):
    """
    Infer animal size based on breed and species
    """
    if pd.isna(breed_str) or pd.isna(species):
        return 'Medium'
    
    breed_str = str(breed_str).lower()
    species = str(species).lower()
    
    # For dogs
    if 'dog' in species:
        small_breeds = ['chihuahua', 'yorkie', 'yorkshire', 'terrier', 'pomeranian', 
                       'dachshund', 'shih tzu', 'maltese', 'toy', 'miniature', 'mini']
        large_breeds = ['labrador', 'shepherd', 'retriever', 'mastiff', 'rottweiler', 
                       'great dane', 'saint bernard', 'newfoundland', 'bernese',
                       'husky', 'malamute', 'boxer', 'doberman', 'great']
        
        for small in small_breeds:
            if small in breed_str:
                return 'Small'
        
        for large in large_breeds:
            if large in breed_str:
                return 'Large'
    
    # For cats (most cats are medium size)
    elif 'cat' in species:
        small_breeds = ['kitten', 'dwarf', 'munchkin']
        large_breeds = ['maine coon', 'ragdoll', 'bengal', 'savannah', 'norwegian']
        
        for small in small_breeds:
            if small in breed_str:
                return 'Small'
        
        for large in large_breeds:
            if large in breed_str:
                return 'Large'
    
    # For small animals
    elif any(x in species for x in ['hamster', 'guinea pig', 'mouse', 'rat', 'gerbil']):
        return 'Small'
    
    # For rabbits
    elif 'rabbit' in species:
        if any(x in breed_str for x in ['dwarf', 'mini', 'small']):
            return 'Small'
        elif any(x in breed_str for x in ['giant', 'large', 'flemish']):
            return 'Large'
    
    return 'Medium'

def infer_energy_from_breed_and_age(breed_str, species, age_months):
    """
    Infer energy level based on breed, species and age
    """
    if pd.isna(breed_str) or pd.isna(species):
        return 'Medium'
    
    breed_str = str(breed_str).lower()
    species = str(species).lower()
    
    # Young animals tend to have higher energy
    if age_months < 12:
        return 'High'
    elif age_months > 84:  # 7 years or older
        return 'Low'
    
    # For dogs
    if 'dog' in species:
        high_energy_breeds = ['terrier', 'collie', 'shepherd', 'retriever', 'husky', 
                             'pointer', 'setter', 'spaniel', 'beagle', 'boxer']
        low_energy_breeds = ['bulldog', 'mastiff', 'basset', 'pug', 'shih tzu', 
                            'chow chow', 'saint bernard', 'great dane']
        
        for high in high_energy_breeds:
            if high in breed_str:
                return 'High'
        
        for low in low_energy_breeds:
            if low in breed_str:
                return 'Low'
    
    # For cats
    elif 'cat' in species:
        high_energy_breeds = ['bengal', 'abyssinian', 'siamese', 'burmese', 'oriental']
        low_energy_breeds = ['persian', 'ragdoll', 'himalayan', 'exotic', 'british shorthair']
        
        for high in high_energy_breeds:
            if high in breed_str:
                return 'High'
        
        for low in low_energy_breeds:
            if low in breed_str:
                return 'Low'
    
    return 'Medium'

def standardize_boolean(bool_str):
    """
    Standardize boolean values to 1 or 0
    """
    if pd.isna(bool_str):
        return 0
    
    if isinstance(bool_str, bool):
        return 1 if bool_str else 0
    
    bool_str = str(bool_str).lower().strip()
    
    if bool_str in ['yes', 'y', 'true', 't', '1', 'oui', 'si', 'tak']:
        return 1
    else:
        return 0

def extract_behavior_traits(behavior_str):
    """
    Extract behavior traits into standardized boolean attributes
    Returns a dict with good_with_kids, good_with_cats, good_with_dogs
    """
    traits = {
        'good_with_kids': 1,  # Default to true
        'good_with_cats': 1,
        'good_with_dogs': 1
    }
    
    if pd.isna(behavior_str):
        return traits
    
    behavior_str = str(behavior_str).lower().strip()
    
    # Look for negative statements about kids
    if any(phrase in behavior_str for phrase in [
        'not good with kids', 'not suitable for kids', 'no kids',
        'not good with children', 'no children', 'adult only'
    ]):
        traits['good_with_kids'] = 0
    
    # Look for negative statements about cats
    if any(phrase in behavior_str for phrase in [
        'not good with cats', 'no cats', 'chases cats', 
        'high prey drive', 'no felines'
    ]):
        traits['good_with_cats'] = 0
    
    # Look for negative statements about dogs
    if any(phrase in behavior_str for phrase in [
        'not good with dogs', 'no dogs', 'dog aggressive', 
        'doesn\'t like dogs', 'no canines'
    ]):
        traits['good_with_dogs'] = 0
    
    return traits

def extract_health_status(health_str):
    """
    Extract health status into standardized boolean attributes
    Returns a dict with vaccinated, neutered
    """
    status = {
        'vaccinated': 0,  # Default to false
        'neutered': 0
    }
    
    if pd.isna(health_str):
        return status
    
    health_str = str(health_str).lower().strip()
    
    # Check vaccination status
    if any(phrase in health_str for phrase in [
        'vaccinated', 'up-to-date on vaccines', 'up to date on shots',
        'has had shots', 'fully vaccinated'
    ]):
        status['vaccinated'] = 1
    
    # Check neutered/spayed status
    if any(phrase in health_str for phrase in [
        'neutered', 'spayed', 'fixed', 'desexed', 'castrated'
    ]):
        status['neutered'] = 1
    
    return status

def detect_outliers(df, column, min_val=None, max_val=None):
    """
    Detect outliers in a column using IQR or explicit bounds
    Returns a DataFrame of outliers
    """
    if min_val is not None and max_val is not None:
        return df[(df[column] < min_val) | (df[column] > max_val)]
    
    # Use IQR method if no bounds provided
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] < lower_bound) | (df[column] > upper_bound)]

def clean_and_standardize_data(file_path, shelter_name):
    """
    Clean and standardize data from a shelter CSV file
    Returns a cleaned DataFrame
    """
    print(f"\nProcessing file: {file_path} for shelter: {shelter_name}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    print(f"Original data shape: {df.shape}")
    
    # Get the file name from the path
    file_name = os.path.basename(file_path)
    
    # Apply column mapping if available
    if file_name in COLUMN_MAPPINGS:
        df = df.rename(columns=COLUMN_MAPPINGS[file_name])
        print(f"Applied column mapping for {file_name}")
    else:
        print(f"No column mapping found for {file_name}")
    
    # Track data cleaning metrics
    metrics = {
        'original_rows': len(df),
        'missing_crucial_data': 0,
        'age_outliers': 0,
        'duplicates': 0,
        'final_rows': 0
    }
    
    # Add shelter_id
    # First, check if the shelter exists in the database
    cursor.execute("SELECT id FROM animals_shelter WHERE name = ?", (shelter_name,))
    shelter_id_result = cursor.fetchone()
    
    if shelter_id_result:
        shelter_id = shelter_id_result[0]
    else:
        # Insert a new shelter
        cursor.execute(
            "INSERT INTO animals_shelter (name) VALUES (?)",
            (shelter_name,)
        )
        shelter_id = cursor.lastrowid
        conn.commit()
    
    df['shelter_id'] = shelter_id
    
    # Create a backup of original data
    original_df = df.copy()
    
    # Ensure key columns exist (with defaults if needed)
    required_columns = {
        'name': None,
        'breed': 'Unknown',
        'gender_original': None,
        'species': None,
        'status_original': 'A'
    }
    
    for col, default in required_columns.items():
        if col not in df.columns:
            df[col] = default
    
    # Standardize age
    if 'age_original' in df.columns:
        # Apply the clean_age function and create two new columns
        age_results = df['age_original'].apply(clean_age)
        df['age_years'] = [result[0] for result in age_results]
        df['age_months'] = [result[1] for result in age_results]
    elif 'age_years' not in df.columns:
        df['age_years'] = 0
    
    if 'age_months' not in df.columns:
        df['age_months'] = 0
    
    # Calculate total age in months for analysis
    df['total_age_months'] = df['age_years'] * 12 + df['age_months']
    
    # Detect age outliers
    age_outliers = detect_outliers(
        df[df['total_age_months'].notna()],
        'total_age_months',
        min_val=0,
        max_val=300  # 25 years in months
    )
    metrics['age_outliers'] = len(age_outliers)
    
    # Handle age outliers
    # Fix negative ages
    df.loc[df['total_age_months'] < 0, ['age_years', 'age_months', 'total_age_months']] = 0, 0, 0
    # Cap extremely old ages
    df.loc[df['total_age_months'] > 300, 'total_age_months'] = 300
    df.loc[df['total_age_months'] > 300, 'age_years'] = 25
    df.loc[df['total_age_months'] > 300, 'age_months'] = 0
    
    # Standardize gender
    df['gender'] = df['gender_original'].apply(standardize_gender)
    
    # Standardize species if present
    if 'species' in df.columns:
        df['species'] = df['species'].apply(standardize_species)
    else:
        # Try to extract species from breed
        df['species'] = df['breed'].apply(lambda x: 
            standardize_species(x.split()[0]) if not pd.isna(x) and ' ' in x else 'Unknown')
    
    # Default to 'Dog' if still unknown
    df.loc[df['species'].isna(), 'species'] = 'Dog'
    
    # Standardize status
    df['status'] = df['status_original'].apply(standardize_status)
    
    # Standardize size
    if 'size_original' in df.columns:
        df['size'] = df['size_original'].apply(standardize_size)
    else:
        # Infer size from breed and species
        df['size'] = df.apply(lambda row: infer_size_from_breed(row['breed'], row['species']), axis=1)
    
    # Standardize energy level
    if 'energy_level_original' in df.columns:
        df['energy_level'] = df['energy_level_original'].apply(standardize_energy_level)
    else:
        # Infer energy level from breed, species and age
        df['energy_level'] = df.apply(
            lambda row: infer_energy_from_breed_and_age(
                row['breed'], row['species'], row['total_age_months']
            ), 
            axis=1
        )
    
    # Extract behavior traits if present
    if 'behavior_traits' in df.columns:
        # Apply extract_behavior_traits to get a dictionary for each row
        behavior_dicts = df['behavior_traits'].apply(extract_behavior_traits).tolist()
        
        # Extract the individual traits from the dictionaries
        for trait in ['good_with_kids', 'good_with_cats', 'good_with_dogs']:
            df[trait] = [d[trait] for d in behavior_dicts]
    else:
        # Set default behavior traits if not present
        for trait in ['good_with_kids', 'good_with_cats', 'good_with_dogs']:
            if trait not in df.columns:
                df[trait] = 1  # Default to good with all
    
    # Extract health status if present
    if 'health_status' in df.columns:
        # Apply extract_health_status to get a dictionary for each row
        health_dicts = df['health_status'].apply(extract_health_status).tolist()
        
        # Extract the individual statuses from the dictionaries
        for status in ['vaccinated', 'neutered']:
            df[status] = [d[status] for d in health_dicts]
    else:
        # Set default health status if not present
        for status in ['vaccinated', 'neutered']:
            if status not in df.columns:
                df[status] = 0  # Default to not vaccinated/neutered
    
    # Standardize boolean columns
    for col in ['vaccinated', 'neutered', 'good_with_kids', 'good_with_cats', 'good_with_dogs']:
        if col in df.columns:
            df[col] = df[col].apply(standardize_boolean)
    
    # Identify rows with missing crucial data
    missing_crucial_data = df[
        df['name'].isna() | 
        df['gender'].isna() | 
        (df['species'].isna()) |
        (df['breed'].isna())
    ]
    metrics['missing_crucial_data'] = len(missing_crucial_data)
    
    # Remove rows with missing crucial data
    df = df.dropna(subset=['name', 'gender', 'species', 'breed'])
    
    # Fill remaining NaN values with defaults
    df['breed'] = df['breed'].fillna('Mixed')
    df['age_years'] = df['age_years'].fillna(0)
    df['age_months'] = df['age_months'].fillna(0)
    if 'health_status' in df.columns:
        df['health_status'] = df['health_status'].fillna('Unknown')
    if 'behavior_traits' in df.columns:
        df['behavior_traits'] = df['behavior_traits'].fillna('Unknown')
    df['status'] = df['status'].fillna('A')
    df['size'] = df['size'].fillna('Medium')
    df['energy_level'] = df['energy_level'].fillna('Medium')
    
    # Add arrival_date if not present (set to 30 days ago by default)
    if 'arrival_date' not in df.columns:
        df['arrival_date'] = pd.Timestamp.now() - pd.Timedelta(days=30)
    
    # Remove duplicate entries
    duplicates = df[df.duplicated(subset=['name', 'breed', 'species', 'gender'], keep='first')]
    metrics['duplicates'] = len(duplicates)
    df = df.drop_duplicates(subset=['name', 'breed', 'species', 'gender'], keep='first')
    
    metrics['final_rows'] = len(df)
    
    # Log cleaning results
    print(f"Data cleaning results for {file_name}:")
    print(f"  Original rows: {metrics['original_rows']}")
    print(f"  Rows with missing crucial data: {metrics['missing_crucial_data']}")
    print(f"  Age outliers detected: {metrics['age_outliers']}")
    print(f"  Duplicates removed: {metrics['duplicates']}")
    print(f"  Final rows: {metrics['final_rows']}")
    
    # Save cleaned data to CSV for reference
    output_path = os.path.join(OUTPUT_DIR, f"cleaned_{file_name}")
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    
    # Create visualizations to document the cleaning process
    visualize_cleaning_process(original_df, df, file_name)
    
    return df

def visualize_cleaning_process(original_df, cleaned_df, file_name):
    """
    Create visualizations to document the cleaning process
    """
    # Create a figure with multiple subplots
    file_base = os.path.splitext(file_name)[0]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Data Cleaning Visualization for {file_name}', fontsize=16)
    
    # 1. Compare original vs. cleaned data sizes
    axes[0, 0].bar(['Original', 'Cleaned'], [len(original_df), len(cleaned_df)])
    axes[0, 0].set_title('Data Size Comparison')
    axes[0, 0].set_ylabel('Number of Records')
    
    # 2. Gender distribution before and after
    if 'gender_original' in original_df.columns:
        gender_orig = original_df['gender_original'].value_counts()
        axes[0, 1].pie(gender_orig, labels=gender_orig.index, autopct='%1.1f%%')
        axes[0, 1].set_title('Original Gender Distribution')
    
    gender_clean = cleaned_df['gender'].value_counts()
    axes[1, 0].pie(gender_clean, labels=gender_clean.index, autopct='%1.1f%%')
    axes[1, 0].set_title('Cleaned Gender Distribution')
    
    # 3. Status distribution after cleaning
    status_clean = cleaned_df['status'].value_counts()
    axes[1, 1].bar(status_clean.index, status_clean.values)
    axes[1, 1].set_title('Status Distribution After Cleaning')
    
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_cleaning.png"))
    
    # Create additional visualizations
    
    # 4. Age distribution
    plt.figure(figsize=(10, 6))
    if 'total_age_months' in cleaned_df.columns:
        sns.histplot(cleaned_df['total_age_months'], kde=True, bins=30)
        plt.title(f'Age Distribution for {file_base}')
        plt.xlabel('Age (Months)')
        plt.ylabel('Count')
        plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_age_distribution.png"))
    
    # 5. Species distribution
    if 'species' in cleaned_df.columns:
        plt.figure(figsize=(10, 6))
        species_counts = cleaned_df['species'].value_counts()
        species_counts.plot(kind='bar')
        plt.title(f'Species Distribution for {file_base}')
        plt.xlabel('Species')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_species_distribution.png"))
    
    # 6. Size distribution
    plt.figure(figsize=(10, 6))
    size_clean = cleaned_df['size'].value_counts()
    plt.pie(size_clean, labels=size_clean.index, autopct='%1.1f%%')
    plt.title(f'Size Distribution for {file_base}')
    plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_size_distribution.png"))

    # 7. Energy level distribution
    plt.figure(figsize=(10, 6))
    energy_clean = cleaned_df['energy_level'].value_counts()
    plt.pie(energy_clean, labels=energy_clean.index, autopct='%1.1f%%')
    plt.title(f'Energy Level Distribution for {file_base}')
    plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_energy_distribution.png"))

    # 8. Species vs Size comparison
    plt.figure(figsize=(12, 8))
    if 'species' in cleaned_df.columns and 'size' in cleaned_df.columns:
        species_size = pd.crosstab(cleaned_df['species'], cleaned_df['size'])
        species_size.plot(kind='bar', stacked=True)
        plt.title(f'Species vs Size for {file_base}')
        plt.xlabel('Species')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_species_size.png"))

    # 9. Species vs Energy comparison
    plt.figure(figsize=(12, 8))
    if 'species' in cleaned_df.columns and 'energy_level' in cleaned_df.columns:
        species_energy = pd.crosstab(cleaned_df['species'], cleaned_df['energy_level'])
        species_energy.plot(kind='bar', stacked=True)
        plt.title(f'Species vs Energy Level for {file_base}')
        plt.xlabel('Species')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, f"{file_base}_species_energy.png"))

def import_data_to_database(cleaned_df):
    """
    Import cleaned data into the animals_animal table (Django model)
    """
    # Map DataFrame columns to Django Animal model fields
    django_animal_columns = {
        'name': 'name',
        'species': 'species',
        'breed': 'breed',
        'age_years': 'age_years',
        'age_months': 'age_months',
        'gender': 'gender',
        'shelter_id': 'shelter_id',
        'vaccinated': 'vaccinated',
        'neutered': 'neutered',
        'good_with_kids': 'good_with_kids',
        'good_with_cats': 'good_with_cats',
        'good_with_dogs': 'good_with_dogs',
        'behavior_traits': 'behavior_notes',
        'health_status': 'health_notes',
        'status': 'status',
        'arrival_date': 'arrival_date',
        'size': 'size',  # Added size field
        'energy_level': 'energy_level'  # Added energy_level field
    }
    
    # Filter df to include only columns that exist in both the DataFrame and the mapping
    columns_to_import = [col for col in django_animal_columns.keys() if col in cleaned_df.columns]
    django_columns = [django_animal_columns[col] for col in columns_to_import]
    
    # Prepare placeholders for SQL query
    placeholders = ', '.join(['?'] * len(columns_to_import))
    columns_str = ', '.join(django_columns)
    
    # Get the current time for created_at and updated_at fields
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert data into the animals_animal table
    for _, row in cleaned_df.iterrows():
        # Check if animal with same name, breed, species already exists for this shelter
        cursor.execute(
            "SELECT id FROM animals_animal WHERE name = ? AND breed = ? AND species = ? AND shelter_id = ?",
            (row['name'], row['breed'], row['species'], row['shelter_id'])
        )
        existing_animal = cursor.fetchone()
        
        if existing_animal:
            print(f"Animal already exists: {row['name']} ({row['species']}, {row['breed']})")
            continue
        
        # Prepare values for insertion
        values = [row[col] for col in columns_to_import]
        
        try:
            # Insert into the animals_animal table (adjust table name if needed)
            cursor.execute(
                f"INSERT INTO animals_animal ({columns_str}, created_at, updated_at) VALUES ({placeholders}, ?, ?)",
                values + [now, now]
            )
        except sqlite3.Error as e:
            print(f"Error inserting animal: {e}")
            print(f"Animal data: {row[columns_to_import]}")
            continue
    
    conn.commit()
    print(f"Imported {len(cleaned_df)} animals into the database")

def process_all_shelter_files():
    """
    Process all shelter files in the data directory
    """
    # Mapping of file names to shelter names
    shelter_mapping = {
        'rspca_surrey.csv': 'RSPCA Surrey',
        'animal_rescue_center.csv': 'Animal Rescue Center',
        'battersea.csv': 'Battersea Dogs & Cats Home',
        'humane_society.csv': 'Local Humane Society'
    }
    
    # Create the attribute mapping table
    create_shelter_mapping_table()
    
    # Process each shelter file
    all_cleaned_data = []
    
    for file_name, shelter_name in shelter_mapping.items():
        file_path = os.path.join(DATA_DIR, file_name)
        if os.path.exists(file_path):
            cleaned_df = clean_and_standardize_data(file_path, shelter_name)
            if cleaned_df is not None:
                all_cleaned_data.append(cleaned_df)
                import_data_to_database(cleaned_df)
    
    # Combine all cleaned data
    if all_cleaned_data:
        combined_df = pd.concat(all_cleaned_data, ignore_index=True)
        combined_df.to_csv(os.path.join(OUTPUT_DIR, 'all_cleaned_data.csv'), index=False)
        print(f"Combined data saved to {os.path.join(OUTPUT_DIR, 'all_cleaned_data.csv')}")

def show_data_stats():
    """
    Display statistics about the data in the database
    """
    print("\nDatabase Statistics:")
    
    cursor.execute("SELECT COUNT(*) FROM animals_shelter")
    shelter_count = cursor.fetchone()[0]
    print(f"Number of shelters: {shelter_count}")
    
    cursor.execute("SELECT name, city FROM animals_shelter")
    shelters = cursor.fetchall()
    print("Shelters in database:")
    for name, city in shelters:
        print(f"  - {name} ({city if city else 'Unknown location'})")
    
    cursor.execute("SELECT COUNT(*) FROM animals_animal")
    animal_count = cursor.fetchone()[0]
    print(f"Number of animals: {animal_count}")
    
    cursor.execute("""
        SELECT species, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY species 
        ORDER BY count DESC
    """)
    species_counts = cursor.fetchall()
    print("Animals by species:")
    for species, count in species_counts:
        print(f"  - {species}: {count}")
    
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY status 
        ORDER BY count DESC
    """)
    status_counts = cursor.fetchall()
    print("Animals by status:")
    for status, count in status_counts:
        status_name = {
            'A': 'Available',
            'P': 'Pending',
            'AD': 'Adopted',
            'NA': 'Not Available'
        }.get(status, status)
        print(f"  - {status_name}: {count}")
    
    # Add statistics for size and energy level
    cursor.execute("""
        SELECT size, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY size 
        ORDER BY count DESC
    """)
    size_counts = cursor.fetchall()
    print("Animals by size:")
    for size, count in size_counts:
        print(f"  - {size}: {count}")
    
    cursor.execute("""
        SELECT energy_level, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY energy_level 
        ORDER BY count DESC
    """)
    energy_counts = cursor.fetchall()
    print("Animals by energy level:")
    for energy, count in energy_counts:
        print(f"  - {energy}: {count}")
    
    # Add cross-tabulation statistics
    cursor.execute("""
        SELECT species, size, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY species, size 
        ORDER BY species, size
    """)
    species_size_counts = cursor.fetchall()
    print("\nAnimals by species and size:")
    current_species = None
    for species, size, count in species_size_counts:
        if species != current_species:
            print(f"  {species}:")
            current_species = species
        print(f"    - {size}: {count}")
    
    cursor.execute("""
        SELECT species, energy_level, COUNT(*) as count 
        FROM animals_animal 
        GROUP BY species, energy_level 
        ORDER BY species, energy_level
    """)
    species_energy_counts = cursor.fetchall()
    print("\nAnimals by species and energy level:")
    current_species = None
    for species, energy, count in species_energy_counts:
        if species != current_species:
            print(f"  {species}:")
            current_species = species
        print(f"    - {energy}: {count}")

def main():
    """
    Main function to run the data conversion process
    """
    print("Pet Connect Data Conversion Script")
    print("----------------------------------")
    
    # Process all shelter files
    process_all_shelter_files()
    
    # Show data statistics
    show_data_stats()
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    main()