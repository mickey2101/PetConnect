from django.core.management.base import BaseCommand
import csv
import os
import re
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Import sample animal data from CSV files'

    def handle(self, *args, **options):
        # Import models here to avoid import issues
        from animals.models import Animal, Shelter
        
        # Path to the CSV files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'shelter_data')
        
        self.stdout.write(f"Looking for CSV files in: {data_dir}")
        
        
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {data_dir}"))
            self.stdout.write(self.style.WARNING("Creating directory..."))
            os.makedirs(data_dir, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Created directory: {data_dir}"))
            return
        
        # Create the three shelters
        shelters = self.create_shelters()
        
        # Generate sample data if no CSV files exist
        files = os.listdir(data_dir)
        csv_files = [f for f in files if f.endswith('.csv') or f.endswith('.xlsx')]
        
        if not csv_files:
            self.stdout.write(self.style.WARNING(f"No data files found in {data_dir}"))
            self.stdout.write("Generating sample animals directly...")
            self.generate_sample_animals(shelters)
            return
        
        # Process CSV files
        self.stdout.write(f"Found data files: {csv_files}")
        
        for file_name in csv_files:
            file_path = os.path.join(data_dir, file_name)
            
            # Determine which shelter this file belongs to
            shelter = self.determine_shelter_from_filename(file_name, shelters)
            self.stdout.write(f"Processing file: {file_path} for shelter: {shelter.name}")
            
            self.process_csv_file(file_path, shelter)

    def create_shelters(self):
        """Create the three specific shelters."""
        # Import models here to avoid import issues
        from animals.models import Shelter
        
        # Create RSPCA Surrey shelter
        rspca, created = Shelter.objects.get_or_create(
            name='RSPCA Hants and Surrey Border Branch',
            defaults={
                'address': '48 College Road',
                'city': 'Farnborough',
                'postal_code': 'GU14 6BZ',
                'phone': '01252 398 377',
                'email': 'info@rspcasurrey.org.uk',
                'website': 'https://www.rspcasurrey.org.uk/'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created shelter: {rspca.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing shelter: {rspca.name}'))
        
        # Create Humane Society shelter
        humane, created = Shelter.objects.get_or_create(
            name='Humane Society',
            defaults={
                'address': '1640 S Sepulveda Blvd',
                'city': 'Los Angeles',
                'postal_code': 'CA 90025',
                'phone': '(310) 479-5089',
                'email': 'info@humanesociety.org',
                'website': 'https://www.humanesociety.org/'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created shelter: {humane.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing shelter: {humane.name}'))
        
        # Create Diana Brimblecombe Animal Rescue Centre
        dbac, created = Shelter.objects.get_or_create(
            name='Diana Brimblecombe Animal Rescue Centre',
            defaults={
                'address': 'Nelsons Lane, Hurst',
                'city': 'Reading',
                'postal_code': 'RG10 0RR',
                'phone': '0118 934 4089',
                'email': 'info@dbarc.org.uk',
                'website': 'https://www.dbarc.org.uk/'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created shelter: {dbac.name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing shelter: {dbac.name}'))
        
        return {
            'rspca': rspca,
            'humane': humane,
            'dbarc': dbac
        }
    
    def determine_shelter_from_filename(self, file_name, shelters):
        """Determine which shelter a file belongs to based on its name."""
        file_name_lower = file_name.lower()
        
        if 'rspca' in file_name_lower or 'surrey' in file_name_lower:
            return shelters['rspca']
        elif 'humane' in file_name_lower:
            return shelters['humane']
        elif 'dbarc' in file_name_lower or 'diana' in file_name_lower or 'brimblecombe' in file_name_lower:
            return shelters['dbarc']
        else:
            # Default to RSPCA if can't determine
            return shelters['rspca']

    def clean_age(self, age_str):
        """
        Convert various age formats to years and months
        Returns a tuple of (years, months)
        """
        if not age_str or str(age_str).lower() in ['unknown', 'nan', '-']:
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

    def standardize_gender(self, gender_str):
        """
        Standardize gender to 'M', 'F', or 'U'
        """
        if not gender_str or str(gender_str).lower() in ['unknown', 'nan', '-']:
            return 'U'
        
        gender_str = str(gender_str).lower().strip()
        
        if gender_str in ['male', 'm', 'boy']:
            return 'M'
        elif gender_str in ['female', 'f', 'girl']:
            return 'F'
        else:
            return 'U'
    
    def determine_size(self, species, breed, weight_str=None):
        """
        Determine animal size based on species, breed, and weight
        """
        # Small dog breeds
        small_dog_breeds = ['chihuahua', 'yorkshire terrier', 'pomeranian', 'shih tzu', 'maltese', 
                           'toy poodle', 'miniature poodle', 'dachshund', 'jack russell', 'pug']
        
        # Medium dog breeds
        medium_dog_breeds = ['beagle', 'cocker spaniel', 'corgi', 'french bulldog', 'boston terrier',
                           'border collie', 'english bulldog', 'staffordshire bull terrier', 'whippet']
        
        # Large dog breeds
        large_dog_breeds = ['labrador', 'golden retriever', 'german shepherd', 'rottweiler', 'doberman',
                           'boxer', 'husky', 'great dane', 'mastiff', 'saint bernard', 'newfoundland']
        
        species_lower = species.lower()
        breed_lower = breed.lower() if breed else ''
        
        # Determine size based on species
        if species_lower == 'cat':
            return 'Small'
        elif species_lower == 'dog':
            # Try to determine from breed
            for breed_pattern in small_dog_breeds:
                if breed_pattern in breed_lower:
                    return 'Small'
            
            for breed_pattern in large_dog_breeds:
                if breed_pattern in breed_lower:
                    return 'Large'
            
            for breed_pattern in medium_dog_breeds:
                if breed_pattern in breed_lower:
                    return 'Medium'
            
            # If breed doesn't match any patterns, use a random size leaning toward medium
            return random.choice(['Small', 'Medium', 'Medium', 'Large'])
        elif species_lower in ['rabbit', 'guinea pig', 'hamster', 'mouse', 'rat', 'gerbil', 'ferret']:
            return 'Small'
        else:
            # For other species, make a best guess
            return 'Medium'
    
    def determine_energy_level(self, species, breed, age_years):
        """
        Determine energy level based on species, breed, and age
        """
        # High energy dog breeds
        high_energy_breeds = ['border collie', 'australian shepherd', 'jack russell', 'husky', 
                             'dalmatian', 'boxer', 'german shepherd', 'pointer', 'vizsla', 'weimaraner']
        
        # Low energy dog breeds
        low_energy_breeds = ['basset hound', 'bulldog', 'chow chow', 'greyhound', 'newfoundland', 
                            'saint bernard', 'shih tzu', 'pug', 'great dane']
        
        species_lower = species.lower()
        breed_lower = breed.lower() if breed else ''
        
        # Young animals typically have higher energy
        if age_years < 2:
            base_energy = 'High'
        elif age_years < 7:
            base_energy = 'Medium'
        else:
            base_energy = 'Low'
        
        # Modify based on breed for dogs
        if species_lower == 'dog':
            for breed_pattern in high_energy_breeds:
                if breed_pattern in breed_lower:
                    # Increase energy level
                    if base_energy == 'Low':
                        return 'Medium'
                    else:
                        return 'High'
            
            for breed_pattern in low_energy_breeds:
                if breed_pattern in breed_lower:
                    # Decrease energy level
                    if base_energy == 'High':
                        return 'Medium'
                    else:
                        return 'Low'
        
        # For cats, adjust based on age
        if species_lower == 'cat':
            if age_years < 1:
                return 'High'
            elif age_years < 5:
                return 'Medium'
            else:
                return 'Low'
        
        return base_energy

    def process_csv_file(self, file_path, shelter):
        """Process a CSV or Excel file and import animals"""
        try:
            # Check if it's a CSV or Excel file
            if file_path.endswith('.csv'):
                self.process_csv(file_path, shelter)
            elif file_path.endswith('.xlsx'):
                self.process_excel(file_path, shelter)
            else:
                self.stdout.write(self.style.ERROR(f'Unsupported file format: {file_path}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing {file_path}: {str(e)}'))
    
    def process_csv(self, file_path, shelter):
        """Process a CSV file"""
        with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            self.process_rows(reader, shelter)
    
    def process_excel(self, file_path, shelter):
        """Process an Excel file"""
        import pandas as pd
        
        # Read Excel file into a pandas DataFrame
        df = pd.read_excel(file_path)
        
        # Convert DataFrame to list of dictionaries
        rows = df.to_dict('records')
        
        self.process_rows(rows, shelter)
    
    def process_rows(self, rows, shelter):
        """Process rows of data"""
        # Import models here to avoid import issues
        from animals.models import Animal
        
        animals_created = 0
        animals_skipped = 0
        
        for row in rows:
            # Skip completely empty rows
            if not any(row.values()):
                continue
                
            # Handle both dictionary keys and attribute access
            def get_value(data, key_list):
                for key in key_list:
                    # Try dictionary access
                    if key in data:
                        value = data[key]
                        if value is not None and value != '':
                            return value
                    # Try attribute access
                    elif hasattr(data, key):
                        value = getattr(data, key)
                        if value is not None and value != '':
                            return value
                return None
            
            # Extract data - handle different column names
            name = get_value(row, ['Name', 'Pet Name', 'Animal Name'])
            species = get_value(row, ['Species', 'Type', 'Animal Type', 'Animal'])
            breed = get_value(row, ['Breed Type', 'Animal Breed', 'Breed'])
            
            # Skip if no name or species
            if not name or not species:
                animals_skipped += 1
                continue
            
            # Handle age
            age_str = get_value(row, ['Age', 'Age (Years)'])
            age_years_str = get_value(row, ['Years Old', 'Age (years)'])
            age_months_str = get_value(row, ['Months Old', 'Age (months)'])
            
            age_years = 0
            age_months = 0
            
            if age_str:
                years, months = self.clean_age(age_str)
                age_years = years
                age_months = months
            elif age_years_str is not None:
                try:
                    age_years = int(float(age_years_str))
                except (ValueError, TypeError):
                    age_years = 0
            
            if age_months_str is not None:
                try:
                    age_months = int(float(age_months_str))
                except (ValueError, TypeError):
                    age_months = 0
            
            # Handle gender
            gender_str = get_value(row, ['Gender', 'Sex', 'M/F'])
            gender = self.standardize_gender(gender_str)
            
            # Boolean fields with defaults
            vaccinated = get_value(row, ['Vaccinated', 'Vaccinations']) in ['Yes', 'yes', 'Y', 'y', 'true', 'True', '1', 1, True]
            neutered = get_value(row, ['Neutered/Spayed', 'Neutered', 'Spayed']) in ['Yes', 'yes', 'Y', 'y', 'true', 'True', '1', 1, True]
            good_with_kids = get_value(row, ['Kid Friendly', 'Good with Children', 'Child Friendly']) in ['Yes', 'yes', 'Y', 'y', 'true', 'True', '1', 1, True]
            good_with_cats = get_value(row, ['Cat Friendly', 'Good with Cats']) in ['Yes', 'yes', 'Y', 'y', 'true', 'True', '1', 1, True]
            good_with_dogs = get_value(row, ['Dog Friendly', 'Good with Dogs']) in ['Yes', 'yes', 'Y', 'y', 'true', 'True', '1', 1, True]
            
            # Status
            status_str = get_value(row, ['Status', 'Availability'])
            status = 'A'  # Default to Available
            
            if status_str and str(status_str).lower() in ['pending', 'on hold', 'reserved']:
                status = 'P'
            elif status_str and str(status_str).lower() in ['adopted', 'rehomed']:
                status = 'AD'
            
            # Health and behavior notes
            health_notes = get_value(row, ['Health', 'Medical Status', 'Health Notes']) or ''
            behavior_notes = get_value(row, ['Behavior', 'Behavior Notes', 'Temperament', 'Personality']) or ''
            
            # Determine size if not provided
            size_str = get_value(row, ['Size'])
            if not size_str:
                size = self.determine_size(species, breed)
            else:
                size_str = str(size_str).lower()
                if 'small' in size_str:
                    size = 'Small'
                elif 'large' in size_str:
                    size = 'Large'
                else:
                    size = 'Medium'
            
            # Determine energy level if not provided
            energy_str = get_value(row, ['Energy Level', 'Activity Level'])
            if not energy_str:
                energy_level = self.determine_energy_level(species, breed, age_years)
            else:
                energy_str = str(energy_str).lower()
                if any(term in energy_str for term in ['high', 'active', 'energetic']):
                    energy_level = 'High'
                elif any(term in energy_str for term in ['low', 'lazy', 'calm', 'quiet']):
                    energy_level = 'Low'
                else:
                    energy_level = 'Medium'
            
            # Description
            description = get_value(row, ['Description', 'About', 'Biography', 'Bio']) or f'A lovely {species} looking for a forever home.'
            
            # Create or update the animal
            animal, created = Animal.objects.get_or_create(
                name=name,
                species=species,
                shelter=shelter,
                defaults={
                    'breed': breed or '',
                    'age_years': age_years,
                    'age_months': age_months,
                    'gender': gender,
                    'vaccinated': vaccinated,
                    'neutered': neutered,
                    'good_with_kids': good_with_kids,
                    'good_with_cats': good_with_cats,
                    'good_with_dogs': good_with_dogs,
                    'health_notes': health_notes,
                    'behavior_notes': behavior_notes,
                    'description': description,
                    'status': status,
                    'arrival_date': timezone.now().date(),
                    # Add the new fields
                    'size': size,
                    'energy_level': energy_level,
                }
            )
            
            if created:
                animals_created += 1
                if animals_created % 10 == 0:
                    self.stdout.write(f'Created {animals_created} animals so far...')
        
        self.stdout.write(self.style.SUCCESS(f'Created {animals_created} animals, skipped {animals_skipped} rows'))
    
    def generate_sample_animals(self, shelters):
        """Generate sample animals if no CSV files are available"""
        # Import models here to avoid import issues
        from animals.models import Animal
        
        # Sample breeds
        dog_breeds = ['Labrador Retriever', 'German Shepherd', 'Poodle', 'Bulldog', 'Beagle', 
                      'Border Collie', 'Jack Russell Terrier', 'Husky', 'Golden Retriever',
                      'Staffordshire Bull Terrier', 'Cocker Spaniel', 'Dachshund', 'Boxer']
        
        cat_breeds = ['Siamese', 'Persian', 'Maine Coon', 'Ragdoll', 'Bengal', 
                      'British Shorthair', 'Domestic Shorthair', 'Domestic Longhair',
                      'Abyssinian', 'Russian Blue', 'Scottish Fold', 'Sphynx']
        
        small_animal_breeds = ['Dutch Rabbit', 'Netherland Dwarf Rabbit', 'Rex Rabbit',
                              'Guinea Pig', 'Syrian Hamster', 'Dwarf Hamster', 'Gerbil',
                              'Fancy Rat', 'Fancy Mouse', 'Chinchilla', 'Degu', 'Ferret']
        
        names = ['Max', 'Bella', 'Charlie', 'Luna', 'Cooper', 'Lucy', 'Milo', 'Daisy',
                'Buddy', 'Lily', 'Rocky', 'Sadie', 'Bear', 'Chloe', 'Duke', 'Zoe',
                'Tucker', 'Nala', 'Winston', 'Bailey', 'Bentley', 'Abby', 'Zeus', 'Roxy']
        
        # Distribution across shelters
        shelter_keys = list(shelters.keys())
        
        animals_created = 0
        
        # Create sample dogs
        for i in range(25):
            import random
            name = random.choice(names)
            breed = random.choice(dog_breeds)
            shelter = shelters[random.choice(shelter_keys)]
            age_years = random.randint(0, 10)
            
            size = self.determine_size('Dog', breed)
            energy_level = self.determine_energy_level('Dog', breed, age_years)
            
            animal, created = Animal.objects.get_or_create(
                name=name,
                species='Dog',
                breed=breed,
                shelter=shelter,
                defaults={
                    'age_years': age_years,
                    'age_months': random.randint(0, 11),
                    'gender': random.choice(['M', 'F']),
                    'vaccinated': random.choice([True, False]),
                    'neutered': random.choice([True, False]),
                    'good_with_kids': random.choice([True, False]),
                    'good_with_cats': random.choice([True, False]),
                    'good_with_dogs': random.choice([True, True, False]),  # More likely to be good with dogs
                    'health_notes': random.choice(['Healthy', 'Minor skin condition', 'Recovering from surgery', '']),
                    'behavior_notes': random.choice(['Friendly', 'Shy at first', 'Loves to play', 'Good on leash', '']),
                    'description': f'A lovely {breed} looking for a forever home. {random.choice(["Loves toys!", "Enjoys walks!", "Great companion!", "Very affectionate!"])}',
                    'status': random.choices(['A', 'P', 'AD'], weights=[0.8, 0.1, 0.1])[0],
                    'arrival_date': timezone.now().date() - timezone.timedelta(days=random.randint(1, 90)),
                    'size': size,
                    'energy_level': energy_level,
                }
            )
            
            if created:
                animals_created += 1
        
        # Create sample cats
        for i in range(25):
            import random
            name = random.choice(names)
            breed = random.choice(cat_breeds)
            shelter = shelters[random.choice(shelter_keys)]
            age_years = random.randint(0, 12)
            
            energy_level = self.determine_energy_level('Cat', breed, age_years)
            
            animal, created = Animal.objects.get_or_create(
                name=name,
                species='Cat',
                breed=breed,
                shelter=shelter,
                defaults={
                    'age_years': age_years,
                    'age_months': random.randint(0, 11),
                    'gender': random.choice(['M', 'F']),
                    'vaccinated': random.choice([True, False]),
                    'neutered': random.choice([True, False]),
                    'good_with_kids': random.choice([True, False]),
                    'good_with_cats': random.choice([True, True, False]),  # More likely to be good with cats
                    'good_with_dogs': random.choice([True, False]),
                    'health_notes': random.choice(['Healthy', 'Dental issues', 'Recovering from cold', '']),
                    'behavior_notes': random.choice(['Independent', 'Affectionate', 'Playful', 'Quiet', '']),
                    'description': f'A beautiful {breed} looking for a loving home. {random.choice(["Loves to curl up on laps!", "Enjoys catnip toys!", "Purrs loudly!", "Very gentle!"])}',
                    'status': random.choices(['A', 'P', 'AD'], weights=[0.8, 0.1, 0.1])[0],
                    'arrival_date': timezone.now().date() - timezone.timedelta(days=random.randint(1, 90)),
                    'size': 'Small',
                    'energy_level': energy_level,
                }
            )
            
            if created:
                animals_created += 1
        
        # Create sample small animals
        for i in range(10):
            import random
            name = random.choice(names)
            breed_info = random.choice(small_animal_breeds)
            
            # Split breed info to get species and breed
            if 'Rabbit' in breed_info:
                species = 'Rabbit'
                breed = breed_info
            elif 'Guinea Pig' in breed_info:
                species = 'Guinea Pig'
                breed = breed_info
            elif 'Hamster' in breed_info:
                species = 'Hamster'
                breed = breed_info
            else:
                parts = breed_info.split(' ', 1)
                if len(parts) > 1:
                    breed = parts[0]
                    species = parts[1]
                else:
                    species = breed_info
                    breed = ''
            
            shelter = shelters[random.choice(shelter_keys)]
            age_years = random.randint(0, 3)
            
            animal, created = Animal.objects.get_or_create(
                name=name,
                species=species,
                breed=breed,
                shelter=shelter,
                defaults={
                    'age_years': age_years,
                    'age_months': random.randint(0, 11),
                    'gender': random.choice(['M', 'F']),
                    'vaccinated': False,  # Small animals typically don't get vaccinated
                    'neutered': random.choice([True, False]),
                    'good_with_kids': random.choice([True, False]),
                    'good_with_cats': random.choice([True, False]),
                    'good_with_dogs': random.choice([True, False]),
                    'health_notes': random.choice(['Healthy', 'Dental check recommended', '']),
                    'behavior_notes': random.choice(['Active', 'Shy', 'Curious', 'Friendly', '']),
                    'description': f'A cute {species} looking for a caring home. {random.choice(["Very active!", "Loves treats!", "Easy to handle!", "Adorable!"])}',
                    'status': random.choices(['A', 'P', 'AD'], weights=[0.9, 0.05, 0.05])[0],
                    'arrival_date': timezone.now().date() - timezone.timedelta(days=random.randint(1, 60)),
                    'size': 'Small',
                    'energy_level': random.choice(['Low', 'Medium', 'High']),
                }
            )
            
            if created:
                animals_created += 1
                
        self.stdout.write(self.style.SUCCESS(f'Sample data generation complete! Created {animals_created} animals.'))