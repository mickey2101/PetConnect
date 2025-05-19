"""
Pet Connect Attribute Mapping Visualization

This script creates visualizations of the mapping between different shelter data formats,
helping to document how the data standardization process works.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

# Configuration
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

# New size mapping
SIZE_MAPPING = {
    'small': 'S', 's': 'S', 'tiny': 'S', 'petite': 'S', 'little': 'S',
    'medium': 'M', 'm': 'M', 'average': 'M', 'moderate': 'M',
    'large': 'L', 'l': 'L', 'big': 'L', 'huge': 'L', 'xl': 'L',
    'extra large': 'L', 'extra-large': 'L'
}

# New energy level mapping
ENERGY_MAPPING = {
    'low': 'L', 'l': 'L', 'calm': 'L', 'lazy': 'L', 'relaxed': 'L', 'minimal': 'L',
    'medium': 'M', 'm': 'M', 'moderate': 'M', 'average': 'M',
    'high': 'H', 'h': 'H', 'active': 'H', 'energetic': 'H', 'hyper': 'H'
}

def create_mapping_table():
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
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attribute Mapping Across Shelter Data Sources</title>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .present {
                background-color: #e6f7ff;
            }
            .header {
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Attribute Mapping Across Shelter Data Sources</h1>
        </div>
        <table>
            <tr>
                <th>Standardized Attribute</th>
    """
    
    # Add shelter files as column headers
    for shelter_file in shelter_files:
        html += f'<th>{shelter_file}</th>\n'
    html += '</tr>\n'
    
    # Add rows for each standardized attribute
    for col in all_std_columns:
        html += f'<tr>\n<td>{col}</td>\n'
        for shelter_file in shelter_files:
            value = mapping_df.loc[shelter_file, col]
            html += f'<td class="{("present" if not pd.isna(value) else "")}">{value if not pd.isna(value) else ""}</td>\n'
        html += '</tr>\n'
    
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

def create_value_mapping_tables():
    """
    Create visualizations for value mappings (gender, species, status, size, energy)
    """
    # Create DataFrames for each value mapping
    gender_df = pd.DataFrame({
        'Original Value': list(GENDER_MAPPING.keys()),
        'Standardized Value': list(GENDER_MAPPING.values())
    })
    
    species_df = pd.DataFrame({
        'Original Value': list(SPECIES_MAPPING.keys()),
        'Standardized Value': list(SPECIES_MAPPING.values())
    })
    
    status_df = pd.DataFrame({
        'Original Value': list(STATUS_MAPPING.keys()),
        'Standardized Value': list(STATUS_MAPPING.values())
    })
    
    # Add new mappings
    size_df = pd.DataFrame({
        'Original Value': list(SIZE_MAPPING.keys()),
        'Standardized Value': list(SIZE_MAPPING.values())
    })
    
    energy_df = pd.DataFrame({
        'Original Value': list(ENERGY_MAPPING.keys()),
        'Standardized Value': list(ENERGY_MAPPING.values())
    })
    
    # Save to CSV
    gender_df.to_csv(os.path.join(OUTPUT_DIR, 'gender_mapping.csv'), index=False)
    species_df.to_csv(os.path.join(OUTPUT_DIR, 'species_mapping.csv'), index=False)
    status_df.to_csv(os.path.join(OUTPUT_DIR, 'status_mapping.csv'), index=False)
    size_df.to_csv(os.path.join(OUTPUT_DIR, 'size_mapping.csv'), index=False)
    energy_df.to_csv(os.path.join(OUTPUT_DIR, 'energy_mapping.csv'), index=False)
    
    # Create HTML tables
    for mapping_name, df in [
        ('gender', gender_df),
        ('species', species_df),
        ('status', status_df),
        ('size', size_df),
        ('energy', energy_df)
    ]:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{mapping_name.title()} Value Mapping</title>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 80%;
                    margin: 0 auto;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{mapping_name.title()} Value Mapping</h1>
            </div>
            <table>
                <tr>
                    <th>Original Value</th>
                    <th>Standardized Value</th>
                </tr>
        """
        
        for _, row in df.iterrows():
            html += f"""
                <tr>
                    <td>{row['Original Value']}</td>
                    <td>{row['Standardized Value']}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        # Save HTML to file
        with open(os.path.join(OUTPUT_DIR, f'{mapping_name}_mapping.html'), 'w') as f:
            f.write(html)
        
        print(f"{mapping_name.title()} mapping saved to {os.path.join(OUTPUT_DIR, f'{mapping_name}_mapping.csv')}")
        print(f"HTML version saved to {os.path.join(OUTPUT_DIR, f'{mapping_name}_mapping.html')}")

def create_visualization():
    """
    Create visualizations of the attribute mappings
    """
    # Load the mapping data
    mapping_df = create_mapping_table()
    
    # Create a heatmap of the data presence
    plt.figure(figsize=(14, 10))
    heatmap_data = mapping_df.notna().astype(int)
    plt.imshow(heatmap_data, cmap='Blues')
    
    # Add labels
    plt.yticks(range(len(mapping_df.index)), mapping_df.index, fontsize=10)
    plt.xticks(range(len(mapping_df.columns)), mapping_df.columns, rotation=90, fontsize=8)
    
    # Add a color bar
    plt.colorbar(ticks=[0, 1], label='Attribute Present')
    
    # Add title and labels
    plt.title('Attribute Presence Across Shelter Data Sources')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'attribute_mapping_heatmap.png'))
    
    print(f"Attribute mapping heatmap saved to {os.path.join(VISUALIZATION_DIR, 'attribute_mapping_heatmap.png')}")
    
    # Create value mapping visualizations
    create_value_mapping_tables()

def create_data_flow_diagram():
    """
    Create a data flow diagram showing how data is transformed
    """
    plt.figure(figsize=(12, 8))
    
    # Define the stages
    stages = ['Raw Data', 'Data Cleaning', 'Standardization', 'Database Loading']
    processes = [
        'Import from CSVs\nHandle missing values', 
        'Column mapping\nData type conversion', 
        'Value normalization\nFormat standardization',
        'Django ORM\nDatabase storage'
    ]
    
    # Create a horizontal flow diagram
    for i, (stage, process) in enumerate(zip(stages, processes)):
        # Draw stage box
        plt.fill_between([i-0.4, i+0.4], [0.7, 0.7], [1.3, 1.3], 
                         color='lightblue', alpha=0.7, edgecolor='black')
        plt.text(i, 1, stage, ha='center', va='center', fontweight='bold')
        
        # Draw process box
        plt.fill_between([i-0.4, i+0.4], [-0.3, -0.3], [0.5, 0.5], 
                         color='lightgreen', alpha=0.7, edgecolor='black')
        plt.text(i, 0.1, process, ha='center', va='center', fontsize=9)
        
        # Draw arrows
        if i < len(stages) - 1:
            plt.arrow(i+0.4, 1, 0.2, 0, head_width=0.1, head_length=0.05, 
                      fc='black', ec='black')
            plt.arrow(i+0.4, 0.1, 0.2, 0, head_width=0.1, head_length=0.05, 
                      fc='black', ec='black')
    
    # Customize the plot
    plt.title('Pet Connect Data Processing Flow')
    plt.axis('off')
    plt.xlim(-0.5, len(stages) - 0.5)
    plt.ylim(-0.5, 1.5)
    
    # Save the figure
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'data_flow_diagram.png'))
    
    print(f"Data flow diagram saved to {os.path.join(VISUALIZATION_DIR, 'data_flow_diagram.png')}")

def main():
    """
    Main function to create attribute mapping visualizations
    """
    print("Pet Connect Attribute Mapping Visualization")
    print("------------------------------------------")
    
    # Create the visualizations
    create_visualization()
    
    # Create data flow diagram
    create_data_flow_diagram()

if __name__ == "__main__":
    main()