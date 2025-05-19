"""
Pet Connect Data Exploration Script

This script analyzes the animal data in the database and creates visualizations
to help understand patterns, distributions, and potential issues.
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Configuration
DATABASE_PATH = 'db.sqlite3'  # Your existing Django database
OUTPUT_DIR = 'output'
VISUALIZATION_DIR = os.path.join(OUTPUT_DIR, 'visualizations')

# Ensure output directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VISUALIZATION_DIR, exist_ok=True)

def explore_animal_data():
    """
    Explore animal data from the database and generate statistics and visualizations
    """
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Load animal data into a DataFrame
    query = """
    SELECT a.id, a.name, a.species, a.breed, a.age_years, a.age_months, 
           a.gender, a.vaccinated, a.neutered, a.health_notes, 
           a.good_with_kids, a.good_with_cats, a.good_with_dogs, 
           a.behavior_notes, a.status, a.arrival_date, a.shelter_id,
           a.size, a.energy_level,
           s.name as shelter_name
    FROM animals_animal a
    LEFT JOIN animals_shelter s ON a.shelter_id = s.id
    """
    animals_df = pd.read_sql_query(query, conn)
    
    # Convert arrival_date to datetime
    animals_df['arrival_date'] = pd.to_datetime(animals_df['arrival_date'])
    
    # Calculate total age in months
    animals_df['total_age_months'] = animals_df['age_years'] * 12 + animals_df['age_months']
    
    # Calculate days since arrival
    now = pd.Timestamp.now()
    animals_df['days_since_arrival'] = (now - animals_df['arrival_date']).dt.days
    
    # Print basic statistics
    print("Animal Database Statistics:")
    print(f"Total number of animals: {len(animals_df)}")
    print(f"Number of species: {animals_df['species'].nunique()}")
    print(f"Number of breeds: {animals_df['breed'].nunique()}")
    print(f"Number of size categories: {animals_df['size'].nunique()}")
    print(f"Number of energy levels: {animals_df['energy_level'].nunique()}")
    
    # 1. Age distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(animals_df['total_age_months'], kde=True, bins=30)
    plt.title('Distribution of Animal Ages')
    plt.xlabel('Age (Months)')
    plt.ylabel('Count')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'age_distribution.png'))
    
    # 2. Species distribution
    plt.figure(figsize=(10, 6))
    species_counts = animals_df['species'].value_counts()
    species_counts.plot(kind='bar')
    plt.title('Distribution of Animal Species')
    plt.xlabel('Species')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'species_distribution.png'))
    
    # 3. Gender distribution by species
    plt.figure(figsize=(12, 7))
    gender_by_species = pd.crosstab(animals_df['species'], animals_df['gender'])
    gender_by_species.plot(kind='bar', stacked=True)
    plt.title('Gender Distribution by Species')
    plt.xlabel('Species')
    plt.ylabel('Count')
    plt.legend(title='Gender')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'gender_by_species.png'))
    
    # 4. Adoption status distribution
    plt.figure(figsize=(10, 6))
    status_counts = animals_df['status'].value_counts()
    status_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Distribution of Adoption Status')
    plt.ylabel('')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'status_distribution.png'))
    
    # 5. Time since arrival analysis
    plt.figure(figsize=(10, 6))
    sns.histplot(animals_df['days_since_arrival'], kde=True, bins=30)
    plt.title('Days Since Arrival')
    plt.xlabel('Days')
    plt.ylabel('Count')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'days_since_arrival.png'))
    
    # 5.1 Days since arrival by status
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='status', y='days_since_arrival', data=animals_df)
    plt.title('Days Since Arrival by Status')
    plt.xlabel('Status')
    plt.ylabel('Days')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'days_by_status.png'))
    
    # 6. Behavior traits analysis (good with kids, cats, dogs)
    behavior_cols = ['good_with_kids', 'good_with_cats', 'good_with_dogs']
    behavior_df = pd.DataFrame({
        col: animals_df[col].value_counts() for col in behavior_cols
    })
    
    plt.figure(figsize=(12, 6))
    behavior_df.plot(kind='bar')
    plt.title('Behavior Traits Distribution')
    plt.xlabel('Compatibility')
    plt.ylabel('Count')
    plt.xticks([0, 1], ['No', 'Yes'])
    plt.legend(title='Trait')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'behavior_traits.png'))
    
    # 7. Size distribution
    plt.figure(figsize=(10, 6))
    size_counts = animals_df['size'].value_counts()
    plt.pie(size_counts, labels=size_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Animal Sizes')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'size_distribution.png'))
    
    # 8. Energy level distribution
    plt.figure(figsize=(10, 6))
    energy_counts = animals_df['energy_level'].value_counts()
    plt.pie(energy_counts, labels=energy_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Energy Levels')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'energy_distribution.png'))
    
    # 9. Size distribution by species
    plt.figure(figsize=(14, 8))
    size_by_species = pd.crosstab(animals_df['species'], animals_df['size'])
    size_by_species.plot(kind='bar', stacked=True)
    plt.title('Size Distribution by Species')
    plt.xlabel('Species')
    plt.ylabel('Count')
    plt.legend(title='Size')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'size_by_species.png'))
    
    # 10. Energy level by species
    plt.figure(figsize=(14, 8))
    energy_by_species = pd.crosstab(animals_df['species'], animals_df['energy_level'])
    energy_by_species.plot(kind='bar', stacked=True)
    plt.title('Energy Level Distribution by Species')
    plt.xlabel('Species')
    plt.ylabel('Count')
    plt.legend(title='Energy Level')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'energy_by_species.png'))
    
    # 11. Energy level by age group
    # Create age groups
    bins = [0, 12, 36, 84, 300]  # 0-1yr, 1-3yrs, 3-7yrs, 7+yrs
    labels = ['Puppy/Kitten (0-1yr)', 'Young (1-3yrs)', 'Adult (3-7yrs)', 'Senior (7+yrs)']
    animals_df['age_group'] = pd.cut(animals_df['total_age_months'], bins=bins, labels=labels)
    
    plt.figure(figsize=(14, 8))
    energy_by_age = pd.crosstab(animals_df['age_group'], animals_df['energy_level'])
    energy_by_age.plot(kind='bar', stacked=True)
    plt.title('Energy Level Distribution by Age Group')
    plt.xlabel('Age Group')
    plt.ylabel('Count')
    plt.legend(title='Energy Level')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'energy_by_age.png'))
    
    # 12. Size by energy level
    plt.figure(figsize=(12, 8))
    size_by_energy = pd.crosstab(animals_df['size'], animals_df['energy_level'])
    size_by_energy.plot(kind='bar', stacked=True)
    plt.title('Size Distribution by Energy Level')
    plt.xlabel('Size')
    plt.ylabel('Count')
    plt.legend(title='Energy Level')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'size_by_energy.png'))
    
    # 13. Days since arrival by size
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='size', y='days_since_arrival', data=animals_df)
    plt.title('Days Since Arrival by Size')
    plt.xlabel('Size')
    plt.ylabel('Days')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'days_by_size.png'))
    
    # 14. Days since arrival by energy level
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='energy_level', y='days_since_arrival', data=animals_df)
    plt.title('Days Since Arrival by Energy Level')
    plt.xlabel('Energy Level')
    plt.ylabel('Days')
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'days_by_energy.png'))
    
    # 15. Detect outliers using boxplots
    plt.figure(figsize=(12, 10))
    
    # Age outliers
    plt.subplot(2, 2, 1)
    sns.boxplot(y=animals_df['total_age_months'])
    plt.title('Age Outliers')
    plt.ylabel('Age (Months)')
    
    # Days since arrival outliers
    plt.subplot(2, 2, 2)
    sns.boxplot(y=animals_df['days_since_arrival'])
    plt.title('Days Since Arrival Outliers')
    plt.ylabel('Days')
    
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'outliers_boxplot.png'))
    
    # 16. Identify specific outliers
    # Age outliers - animals older than 20 years (240 months)
    age_outliers = animals_df[animals_df['total_age_months'] > 240]
    print(f"\nAge outliers (animals older than 20 years): {len(age_outliers)}")
    if len(age_outliers) > 0:
        print(age_outliers[['id', 'name', 'species', 'breed', 'age_years', 'age_months', 'total_age_months']])
    
    # Extremely long shelter stays
    stay_outliers = animals_df[animals_df['days_since_arrival'] > 365]  # More than a year
    print(f"\nStay outliers (animals in shelter for more than a year): {len(stay_outliers)}")
    if len(stay_outliers) > 0:
        print(stay_outliers[['id', 'name', 'species', 'breed', 'days_since_arrival', 'status']])
    
    # 17. Check for data completeness
    missing_data = animals_df.isnull().sum()
    print("\nMissing data in each column:")
    print(missing_data[missing_data > 0])  # Only show columns with missing values
    
    # 18. Create a correlation matrix for numerical columns
    numerical_cols = ['age_years', 'age_months', 'total_age_months', 'days_since_arrival',
                     'vaccinated', 'neutered', 'good_with_kids', 'good_with_cats', 'good_with_dogs']
    
    plt.figure(figsize=(12, 10))
    corr_matrix = animals_df[numerical_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Numerical Variables')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'correlation_matrix.png'))
    
    # 19. Animals by shelter
    plt.figure(figsize=(12, 6))
    shelter_counts = animals_df['shelter_name'].value_counts()
    shelter_counts.plot(kind='bar')
    plt.title('Animals by Shelter')
    plt.xlabel('Shelter')
    plt.ylabel('Number of Animals')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'animals_by_shelter.png'))
    
    # 20. Analyze success factors - what attributes correlate with shorter shelter stays?
    available_animals = animals_df[animals_df['status'] == 'A']
    adopted_animals = animals_df[animals_df['status'] == 'AD']
    
    if len(adopted_animals) > 0:
        # Compare average stay duration by different attributes
        plt.figure(figsize=(15, 10))
        
        # By size
        plt.subplot(2, 2, 1)
        sns.barplot(x='size', y='days_since_arrival', data=adopted_animals)
        plt.title('Average Days Until Adoption by Size')
        plt.xlabel('Size')
        plt.ylabel('Days')
        
        # By energy level
        plt.subplot(2, 2, 2)
        sns.barplot(x='energy_level', y='days_since_arrival', data=adopted_animals)
        plt.title('Average Days Until Adoption by Energy Level')
        plt.xlabel('Energy Level')
        plt.ylabel('Days')
        
        # By species
        plt.subplot(2, 2, 3)
        top_species = adopted_animals['species'].value_counts().nlargest(5).index
        species_subset = adopted_animals[adopted_animals['species'].isin(top_species)]
        sns.barplot(x='species', y='days_since_arrival', data=species_subset)
        plt.title('Average Days Until Adoption by Species')
        plt.xlabel('Species')
        plt.ylabel('Days')
        plt.xticks(rotation=45)
        
        # By age group
        plt.subplot(2, 2, 4)
        sns.barplot(x='age_group', y='days_since_arrival', data=adopted_animals)
        plt.title('Average Days Until Adoption by Age Group')
        plt.xlabel('Age Group')
        plt.ylabel('Days')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'adoption_success_factors.png'))
    
    # Create a detailed data summary and save to CSV
    summary = {
        'Category': [],
        'Count': [],
        'Percentage': []
    }
    
    # Add species summary
    for species, count in species_counts.items():
        summary['Category'].append(f'Species: {species}')
        summary['Count'].append(count)
        summary['Percentage'].append(f'{count/len(animals_df)*100:.1f}%')
    
    # Add status summary
    for status, count in status_counts.items():
        status_name = {
            'A': 'Available',
            'P': 'Pending',
            'AD': 'Adopted',
            'NA': 'Not Available'
        }.get(status, status)
        summary['Category'].append(f'Status: {status_name}')
        summary['Count'].append(count)
        summary['Percentage'].append(f'{count/len(animals_df)*100:.1f}%')
    
    # Add gender summary
    gender_counts = animals_df['gender'].value_counts()
    for gender, count in gender_counts.items():
        gender_name = {'M': 'Male', 'F': 'Female', 'U': 'Unknown'}.get(gender, gender)
        summary['Category'].append(f'Gender: {gender_name}')
        summary['Count'].append(count)
        summary['Percentage'].append(f'{count/len(animals_df)*100:.1f}%')
    
    # Add size summary
    for size, count in size_counts.items():
        summary['Category'].append(f'Size: {size}')
        summary['Count'].append(count)
        summary['Percentage'].append(f'{count/len(animals_df)*100:.1f}%')
    
    # Add energy level summary
    for energy, count in energy_counts.items():
        summary['Category'].append(f'Energy Level: {energy}')
        summary['Count'].append(count)
        summary['Percentage'].append(f'{count/len(animals_df)*100:.1f}%')
    
    # Add behavior traits summary
    for col in behavior_cols:
        trait_name = col.replace('good_with_', '').capitalize()
        good_count = animals_df[col].sum()
        bad_count = len(animals_df) - good_count
        
        summary['Category'].append(f'Good with {trait_name}: Yes')
        summary['Count'].append(good_count)
        summary['Percentage'].append(f'{good_count/len(animals_df)*100:.1f}%')
        
        summary['Category'].append(f'Good with {trait_name}: No')
        summary['Count'].append(bad_count)
        summary['Percentage'].append(f'{bad_count/len(animals_df)*100:.1f}%')
    
    # Save summary to CSV
    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(os.path.join(OUTPUT_DIR, 'animal_data_summary.csv'), index=False)
    
    # Perform some specific analyses on size and energy level
    
    # 21. Create a heatmap of size vs energy level distribution
    plt.figure(figsize=(10, 8))
    size_energy_heatmap = pd.crosstab(animals_df['size'], animals_df['energy_level'], normalize='all') * 100
    sns.heatmap(size_energy_heatmap, annot=True, fmt='.1f', cmap='YlGnBu')
    plt.title('Size vs Energy Level Distribution (%)')
    plt.xlabel('Energy Level')
    plt.ylabel('Size')
    plt.tight_layout()
    plt.savefig(os.path.join(VISUALIZATION_DIR, 'size_energy_heatmap.png'))
    
    # 22. Analysis of adoption rate by size and energy level
    if 'AD' in animals_df['status'].values:
        adoption_by_size = pd.crosstab(animals_df['size'], animals_df['status']).apply(
            lambda x: x['AD'] / x.sum() * 100 if 'AD' in x else 0, axis=1
        )
        
        adoption_by_energy = pd.crosstab(animals_df['energy_level'], animals_df['status']).apply(
            lambda x: x['AD'] / x.sum() * 100 if 'AD' in x else 0, axis=1
        )
        
        plt.figure(figsize=(12, 5))
        
        plt.subplot(1, 2, 1)
        adoption_by_size.plot(kind='bar')
        plt.title('Adoption Rate by Size')
        plt.xlabel('Size')
        plt.ylabel('Adoption Rate (%)')
        
        plt.subplot(1, 2, 2)
        adoption_by_energy.plot(kind='bar')
        plt.title('Adoption Rate by Energy Level')
        plt.xlabel('Energy Level')
        plt.ylabel('Adoption Rate (%)')
        
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'adoption_rate_by_attributes.png'))
    
    # Close the database connection
    conn.close()
    
    print("\nData exploration complete. Visualizations saved to 'visualizations' directory.")
    print(f"Summary saved to {os.path.join(OUTPUT_DIR, 'animal_data_summary.csv')}")
    
    return animals_df

def explore_potential_adopter_preferences():
    """
    Analyze potential adopter preferences from user data
    """
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Check if user preferences table exists
    try:
        # Load user preference data into a DataFrame
        query = """
        SELECT up.id, up.user_id, up.preferred_species, up.preferred_size, 
               up.preferred_energy_level, up.good_with_children, 
               up.good_with_other_pets, up.created_at
        FROM users_userpreference up
        """
        prefs_df = pd.read_sql_query(query, conn)
        
        if len(prefs_df) == 0:
            print("No user preference data available.")
            conn.close()
            return None
        
        # Print basic statistics
        print("\nUser Preferences Statistics:")
        print(f"Total number of users with preferences: {len(prefs_df)}")
        
        # 1. Preferred species distribution
        plt.figure(figsize=(10, 6))
        species_counts = prefs_df['preferred_species'].value_counts()
        species_counts.plot(kind='bar')
        plt.title('Distribution of Preferred Species')
        plt.xlabel('Species')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'preferred_species.png'))
        
        # 2. Preferred size distribution
        plt.figure(figsize=(10, 6))
        size_counts = prefs_df['preferred_size'].value_counts()
        plt.pie(size_counts, labels=size_counts.index, autopct='%1.1f%%')
        plt.title('Distribution of Preferred Sizes')
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'preferred_size.png'))
        
        # 3. Preferred energy level distribution
        plt.figure(figsize=(10, 6))
        energy_counts = prefs_df['preferred_energy_level'].value_counts()
        plt.pie(energy_counts, labels=energy_counts.index, autopct='%1.1f%%')
        plt.title('Distribution of Preferred Energy Levels')
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'preferred_energy.png'))
        
        # 4. Good with children preference
        plt.figure(figsize=(8, 6))
        children_counts = prefs_df['good_with_children'].value_counts()
        plt.pie(children_counts, labels=['No', 'Yes'] if 0 in children_counts.index else ['Yes', 'No'], 
                autopct='%1.1f%%')
        plt.title('Good with Children Preference')
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'good_with_children_pref.png'))
        
        # 5. Good with other pets preference
        plt.figure(figsize=(8, 6))
        pets_counts = prefs_df['good_with_other_pets'].value_counts()
        plt.pie(pets_counts, labels=['No', 'Yes'] if 0 in pets_counts.index else ['Yes', 'No'], 
                autopct='%1.1f%%')
        plt.title('Good with Other Pets Preference')
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'good_with_pets_pref.png'))
        
        # 6. Size preference by species preference
        plt.figure(figsize=(12, 7))
        size_by_species = pd.crosstab(prefs_df['preferred_species'], prefs_df['preferred_size'])
        size_by_species.plot(kind='bar', stacked=True)
        plt.title('Size Preference by Species Preference')
        plt.xlabel('Preferred Species')
        plt.ylabel('Count')
        plt.legend(title='Preferred Size')
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'size_by_species_pref.png'))
        
        # 7. Energy level preference by species preference
        plt.figure(figsize=(12, 7))
        energy_by_species = pd.crosstab(prefs_df['preferred_species'], prefs_df['preferred_energy_level'])
        energy_by_species.plot(kind='bar', stacked=True)
        plt.title('Energy Level Preference by Species Preference')
        plt.xlabel('Preferred Species')
        plt.ylabel('Count')
        plt.legend(title='Preferred Energy Level')
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALIZATION_DIR, 'energy_by_species_pref.png'))
        
        print("User preference exploration complete. Visualizations saved to 'visualizations' directory.")
    
    except sqlite3.OperationalError as e:
        print(f"Error accessing user preferences: {e}")
    
    # Close the database connection
    conn.close()
    
    return None

def analyze_match_potential():
    """
    Analyze the match potential between available animals and user preferences
    """
    # Connect to the database
    conn = sqlite3.connect(DATABASE_PATH)
    
    try:
        # Load animal data
        animal_query = """
        SELECT a.id, a.species, a.size, a.energy_level, 
               a.good_with_kids, a.good_with_cats, a.good_with_dogs, a.status
        FROM animals_animal a
        WHERE a.status = 'A'  -- Only available animals
        """
        animals_df = pd.read_sql_query(animal_query, conn)
        
        # Load user preferences
        prefs_query = """
        SELECT up.id, up.user_id, up.preferred_species, up.preferred_size, 
               up.preferred_energy_level, up.good_with_children, 
               up.good_with_other_pets
        FROM users_userpreference up
        """
        
        try:
            prefs_df = pd.read_sql_query(prefs_query, conn)
            
            if len(prefs_df) == 0 or len(animals_df) == 0:
                print("Not enough data for match potential analysis.")
                conn.close()
                return
            
            # Count how many animals match each preference combination
            match_counts = []
            
            for _, pref in prefs_df.iterrows():
                # Filter animals matching this user's preferences
                matching_animals = animals_df.copy()
                
                # Filter by species if specified
                if pd.notna(pref['preferred_species']):
                    matching_animals = matching_animals[matching_animals['species'] == pref['preferred_species']]
                
                # Filter by size if specified
                if pd.notna(pref['preferred_size']):
                    matching_animals = matching_animals[matching_animals['size'] == pref['preferred_size']]
                
                # Filter by energy level if specified
                if pd.notna(pref['preferred_energy_level']):
                    matching_animals = matching_animals[matching_animals['energy_level'] == pref['preferred_energy_level']]
                
                # Filter by good with children if required
                if pref['good_with_children'] == 1:
                    matching_animals = matching_animals[matching_animals['good_with_kids'] == 1]
                
                # Filter by good with other pets if required
                if pref['good_with_other_pets'] == 1:
                    matching_animals = matching_animals[
                        (matching_animals['good_with_cats'] == 1) | 
                        (matching_animals['good_with_dogs'] == 1)
                    ]
                
                # Count matches
                match_counts.append({
                    'user_id': pref['user_id'],
                    'preferred_species': pref['preferred_species'],
                    'preferred_size': pref['preferred_size'],
                    'preferred_energy_level': pref['preferred_energy_level'],
                    'matches': len(matching_animals)
                })
            
            match_df = pd.DataFrame(match_counts)
            
            # Create a visualization of match distribution
            plt.figure(figsize=(10, 6))
            sns.histplot(match_df['matches'], kde=True, bins=20)
            plt.title('Distribution of Potential Matches per User')
            plt.xlabel('Number of Matching Animals')
            plt.ylabel('Number of Users')
            plt.savefig(os.path.join(VISUALIZATION_DIR, 'match_distribution.png'))
            
            # Analyze match rates by preference
            if len(match_df) > 0:
                # Average matches by species preference
                plt.figure(figsize=(12, 6))
                species_match = match_df.groupby('preferred_species')['matches'].mean().reset_index()
                sns.barplot(x='preferred_species', y='matches', data=species_match)
                plt.title('Average Number of Matches by Preferred Species')
                plt.xlabel('Preferred Species')
                plt.ylabel('Average Matches')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig(os.path.join(VISUALIZATION_DIR, 'matches_by_species.png'))
                
                # Average matches by size preference
                plt.figure(figsize=(10, 6))
                size_match = match_df.groupby('preferred_size')['matches'].mean().reset_index()
                sns.barplot(x='preferred_size', y='matches', data=size_match)
                plt.title('Average Number of Matches by Preferred Size')
                plt.xlabel('Preferred Size')
                plt.ylabel('Average Matches')
                plt.savefig(os.path.join(VISUALIZATION_DIR, 'matches_by_size.png'))
                
                # Average matches by energy level preference
                plt.figure(figsize=(10, 6))
                energy_match = match_df.groupby('preferred_energy_level')['matches'].mean().reset_index()
                sns.barplot(x='preferred_energy_level', y='matches', data=energy_match)
                plt.title('Average Number of Matches by Preferred Energy Level')
                plt.xlabel('Preferred Energy Level')
                plt.ylabel('Average Matches')
                plt.savefig(os.path.join(VISUALIZATION_DIR, 'matches_by_energy.png'))

                # Identify preference combinations with few matches
                few_matches = match_df[match_df['matches'] < 3]
                if len(few_matches) > 0:
                    print("\nPreference combinations with few matches:")
                    print(few_matches[['preferred_species', 'preferred_size', 'preferred_energy_level', 'matches']])

                    # Create visualization of underserved preferences
                    plt.figure(figsize=(14, 8))
                    sns.heatmap(
                        pd.crosstab(
                            few_matches['preferred_species'],
                            [few_matches['preferred_size'], few_matches['preferred_energy_level']]
                        ),
                        cmap='YlOrRd',
                        annot=True,
                        fmt='d'
                    )
                    plt.title('Underserved Preference Combinations (< 3 matches)')
                    plt.tight_layout()
                    plt.savefig(os.path.join(VISUALIZATION_DIR, 'underserved_preferences.png'))
                            
                print("Match potential analysis complete. Visualizations saved to 'visualizations' directory.")
                        
        except Exception as e:
            print(f"Error during match analysis: {e}")
    
    except Exception as e:
        print(f"Error loading animal data: {e}")
    
    finally:
        # Close the database connection
        conn.close()
                
def main():
    """
    Main function to run the data exploration
    """
    print("Pet Connect Data Exploration Script")
    print("----------------------------------")
    
    # Explore the animal data
    animal_data = explore_animal_data()
    
    # Explore user preferences if available
    explore_potential_adopter_preferences()
    
    # Analyze match potential
    analyze_match_potential()
    
    # Generate a final summary report
    generate_summary_report(animal_data)
    
def generate_summary_report(animal_data):
    """
    Generate a final summary report with key insights
    """
    if animal_data is None:
        print("No animal data available for summary report.")
        return
    
    # Create an HTML report
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pet Connect Data Exploration Summary</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            h2 { color: #3498db; margin-top: 30px; }
            .metric { margin: 10px 0; }
            .metric span { font-weight: bold; }
            .insight { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
            img { max-width: 100%; margin: 20px 0; border: 1px solid #ddd; }
            .footer { margin-top: 50px; color: #7f8c8d; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <h1>Pet Connect Data Exploration Summary</h1>
        <p>Generated on """ + datetime.now().strftime("%B %d, %Y at %H:%M") + """</p>
        
        <h2>Key Metrics</h2>
    """
    
    # Add key metrics
    html += f"""
        <div class="metric"><span>Total Animals:</span> {len(animal_data)}</div>
        <div class="metric"><span>Species:</span> {animal_data['species'].nunique()}</div>
        <div class="metric"><span>Size Categories:</span> {animal_data['size'].nunique()}</div>
        <div class="metric"><span>Energy Levels:</span> {animal_data['energy_level'].nunique()}</div>
    """
    
    # Add insights
    html += """
        <h2>Key Insights</h2>
    """
    
    # Species distribution
    top_species = animal_data['species'].value_counts().nlargest(3)
    html += f"""
        <div class="insight">
            <h3>Species Distribution</h3>
            <p>The top 3 species in the database are:</p>
            <ul>
    """
    for species, count in top_species.items():
        percentage = count / len(animal_data) * 100
        html += f"<li>{species}: {count} animals ({percentage:.1f}%)</li>"
    html += """
            </ul>
        </div>
    """
    
    # Size distribution
    size_dist = animal_data['size'].value_counts()
    html += f"""
        <div class="insight">
            <h3>Size Distribution</h3>
            <p>The size distribution of animals is:</p>
            <ul>
    """
    for size, count in size_dist.items():
        percentage = count / len(animal_data) * 100
        html += f"<li>{size}: {count} animals ({percentage:.1f}%)</li>"
    html += """
            </ul>
        </div>
    """
    
    # Energy level distribution
    energy_dist = animal_data['energy_level'].value_counts()
    html += f"""
        <div class="insight">
            <h3>Energy Level Distribution</h3>
            <p>The energy level distribution of animals is:</p>
            <ul>
    """
    for energy, count in energy_dist.items():
        percentage = count / len(animal_data) * 100
        html += f"<li>{energy}: {count} animals ({percentage:.1f}%)</li>"
    html += """
            </ul>
        </div>
    """
    
    # Age distribution
    avg_age_months = animal_data['total_age_months'].mean()
    html += f"""
        <div class="insight">
            <h3>Age Distribution</h3>
            <p>The average age of animals is {avg_age_months:.1f} months ({avg_age_months/12:.1f} years).</p>
        </div>
    """
    
    # Status distribution
    status_dist = animal_data['status'].value_counts()
    html += f"""
        <div class="insight">
            <h3>Adoption Status</h3>
            <ul>
    """
    status_map = {'A': 'Available', 'P': 'Pending', 'AD': 'Adopted', 'NA': 'Not Available'}
    for status, count in status_dist.items():
        percentage = count / len(animal_data) * 100
        status_name = status_map.get(status, status)
        html += f"<li>{status_name}: {count} animals ({percentage:.1f}%)</li>"
    html += """
            </ul>
        </div>
    """
    
    # Days since arrival
    avg_days = animal_data['days_since_arrival'].mean()
    html += f"""
        <div class="insight">
            <h3>Time in Shelter</h3>
            <p>Animals spend an average of {avg_days:.1f} days in the shelter.</p>
        </div>
    """
    
    # Add visualizations
    html += """
        <h2>Key Visualizations</h2>
        <div class="visualizations">
            <img src="../visualizations/species_distribution.png" alt="Species Distribution">
            <img src="../visualizations/size_distribution.png" alt="Size Distribution">
            <img src="../visualizations/energy_distribution.png" alt="Energy Level Distribution">
            <img src="../visualizations/size_by_species.png" alt="Size by Species">
            <img src="../visualizations/energy_by_species.png" alt="Energy Level by Species">
            <img src="../visualizations/size_energy_heatmap.png" alt="Size vs Energy Level">
        </div>
    """
    
    # Finish HTML
    html += """
        <div class="footer">
            <p>Pet Connect Data Exploration - Generated by the Pet Connect Data Analysis System</p>
        </div>
    </body>
    </html>
    """
    
    # Save HTML report
    with open(os.path.join(OUTPUT_DIR, 'exploration_summary.html'), 'w') as f:
        f.write(html)
    
    print(f"\nSummary report generated: {os.path.join(OUTPUT_DIR, 'exploration_summary.html')}")

if __name__ == "__main__":
    main()