"""
Pet Connect Sample Data Generator

This script creates sample CSV files with animal data in different formats
to test the data conversion and cleaning process.
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# Configuration
DATA_DIR = 'shelter_data'

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Lists for generating random pet data
dog_breeds = [
    'Labrador Retriever', 'German Shepherd', 'Golden Retriever', 'Bulldog', 'Beagle', 
    'Poodle', 'Rottweiler', 'Yorkshire Terrier', 'Boxer', 'Dachshund', 'Shih Tzu', 
    'Siberian Husky', 'Chihuahua', 'Great Dane', 'Border Collie', 'Cocker Spaniel', 
    'Doberman', 'Australian Shepherd', 'Corgi', 'Dalmatian', 'English Setter', 
    'French Bulldog', 'Great Pyrenees', 'Irish Setter', 'Jack Russell Terrier', 
    'Komondor', 'Lhasa Apso', 'Maltese', 'Newfoundland', 'Old English Sheepdog', 
    'Pit Bull', 'Pug', 'Rhodesian Ridgeback', 'Saint Bernard', 'Toy Poodle', 
    'Vizsla', 'Weimaraner', 'Xoloitzcuintli', 'Bichon Frise', 'Akita', 'Basenji', 
    'Bernese Mountain Dog', 'Collie', 'Miniature Schnauzer', 'English Mastiff', 
    'Pomeranian', 'Staffordshire Bull Terrier', 'Shetland Sheepdog', 'Whippet', 
    'Bloodhound', 'Bull Terrier', 'Cane Corso', 'Irish Wolfhound', 'Leonberger', 
    'Malamute', 'Norwegian Elkhound', 'Papillon', 'Samoyed', 'Schipperke', 
    'Spinone Italiano', 'Pekingese', 'Chinese Crested', 'Brussels Griffon', 
    'Basset Hound', 'Afghan Hound', 'Havanese', 'Finnish Spitz', 'Dutch Shepherd', 
    'Chesapeake Bay Retriever', 'Belgian Malinois', 'Soft Coated Wheaten Terrier', 
    'West Highland White Terrier', 'Welsh Corgi', 'American Eskimo Dog', 'Blue Heeler', 
    'Chow Chow', 'German Shorthaired Pointer', 'Greyhound', 'Italian Greyhound', 
    'Keeshond', 'Airedale Terrier', 'Bouvier des Flandres', 'Flat-Coated Retriever', 
    'Kuvasz', 'Saluki', 'Scottish Terrier', 'Smooth Fox Terrier', 'Tibetan Terrier', 
    'Welsh Springer Spaniel', 'Wirehaired Pointing Griffon', 'American Foxhound', 
    'English Foxhound', 'Harrier', 'Bedlington Terrier', 'Australian Cattle Dog', 
    'Border Terrier', 'Gordon Setter', 'Irish Terrier', 'Greater Swiss Mountain Dog', 
    'Mixed Breed'
]

cat_breeds = [
    'Siamese', 'Persian', 'Maine Coon', 'Ragdoll', 'Bengal', 'Abyssinian', 
    'British Shorthair', 'Sphynx', 'Scottish Fold', 'Birman', 'American Shorthair', 
    'Oriental', 'Devon Rex', 'Norwegian Forest Cat', 'Domestic Shorthair', 
    'Domestic Longhair', 'Burmese', 'Russian Blue', 'Egyptian Mau', 'Balinese', 
    'Cornish Rex', 'Himalayan', 'Manx', 'Ocicat', 'Tonkinese', 'Turkish Angora', 
    'American Curl', 'American Wirehair', 'Australian Mist', 'Bombay', 'Chartreux', 
    'Colorpoint Shorthair', 'Cymric', 'European Shorthair', 'Exotic Shorthair', 
    'Havana Brown', 'Japanese Bobtail', 'Khao Manee', 'Korat', 'Kurilian Bobtail', 
    'LaPerm', 'Munchkin', 'Nebelung', 'Ojos Azules', 'Peterbald', 'Pixie-Bob', 
    'Raas', 'Ragamuffin', 'Selkirk Rex', 'Serengeti', 'Siberian', 'Singapura', 
    'Snowshoe', 'Sokoke', 'Somali', 'Thai', 'Tiffanie', 'Toyger', 'Turkish Van', 
    'York Chocolate', 'California Spangled', 'Chantilly-Tiffany', 'Chausie', 
    'Dragon Li', 'German Rex', 'Javanese', 'Lykoi', 'Minskin', 'Napoleon', 
    'Savannah', 'Scottish Straight', 'Skookum', 'Thai Lilac', 'Ukrainian Levkoy', 
    'British Longhair', 'Burmilla', 'Cheetoh', 'Colorpoint', 'Cyprus', 'Donskoy', 
    'Dwelf', 'European Burmese', 'Foldex', 'German Rex', 'Highlander', 'Lambkin', 
    'New Zealand Longhair', 'Oregon Rex', 'Persian Tabby', 'Ragdoll Tabby', 
    'Sam Sawet', 'Seychellois', 'Sterling', 'Tonkinese Tabby', 'Aegean', 
    'American Bobtail', 'American Keuda', 'Asian', 'Asian Semi-longhair', 'Brazilian Shorthair', 
    'Mixed Breed'
]

small_animal_breeds = [
    'Dwarf Rabbit', 'Holland Lop Rabbit', 'Dutch Rabbit', 'Teddy Guinea Pig',
    'Abyssinian Guinea Pig', 'Syrian Hamster', 'Dwarf Hamster', 'Fancy Rat',
    'Mongolian Gerbil', 'African Pygmy Hedgehog', 'Chinchilla', 'Ferret',
    'New Zealand White Rabbit', 'Flemish Giant Rabbit', 'Mini Rex Rabbit',
    'American Rabbit', 'Belgian Hare', 'California Rabbit', 'English Lop Rabbit',
    'French Lop Rabbit', 'Netherland Dwarf Rabbit', 'Polish Rabbit', 'Rex Rabbit',
    'Satin Rabbit', 'Tan Rabbit', 'American Fuzzy Lop', 'Angora Rabbit', 'Britannia Petite',
    'Checkered Giant', 'English Angora', 'Florida White', 'Harlequin Rabbit',
    'Havana Rabbit', 'Himalayan Rabbit', 'Jersey Wooly', 'Lionhead Rabbit',
    'Mini Lop', 'Mini Satin', 'Palomino Rabbit', 'Rhinelander Rabbit', 'Silver Fox Rabbit',
    'American Guinea Pig', 'Coronet Guinea Pig', 'Peruvian Guinea Pig', 'Silkie Guinea Pig',
    'Texel Guinea Pig', 'White Crested Guinea Pig', 'Alpaca Guinea Pig', 'Baldwin Guinea Pig',
    'Himalayan Guinea Pig', 'Merino Guinea Pig', 'Sheba Guinea Pig', 'Teasel Guinea Pig',
    'Campbell Dwarf Hamster', 'Chinese Hamster', 'Roborovski Dwarf Hamster', 'Winter White Dwarf Hamster',
    'Dumbo Rat', 'Hairless Rat', 'Hooded Rat', 'Manx Rat', 'Rex Rat', 'Satin Rat',
    'Algerian Gerbil', 'Fat-tailed Gerbil', 'Pallid Gerbil', 'Shaws Jird', 'Bushy-tailed Jird',
    'Long-tailed Chinchilla', 'Short-tailed Chinchilla', 'Beige Chinchilla', 'Black Velvet Chinchilla',
    'Ebony Chinchilla', 'White Chinchilla', 'Violet Chinchilla', 'Sable Ferret', 'Albino Ferret',
    'Cinnamon Ferret', 'Champagne Ferret', 'Chocolate Ferret', 'Silver Ferret', 'Black Sable Ferret',
    'Panda Ferret', 'European Hedgehog', 'Long-eared Hedgehog', 'Egyptian Spiny Mouse',
    'Agouti Mouse', 'Fancy Mouse', 'Zebra Mouse', 'Deer Mouse', 'Harvest Mouse',
    'Spiny Mouse', 'Sugar Glider', 'European Hamster', 'Prairie Dog', 'Degu',
    'Short-tailed Possum', 'Mixed Breed'
]

bird_breeds = [
    'Cockatiel', 'Budgerigar', 'Canary', 'Lovebird', 'Conure', 'African Grey Parrot',
    'Parakeet', 'Finch', 'Cockatoo', 'Macaw', 'Amazon Parrot', 'Ringneck Parakeet',
    'Eclectus Parrot', 'Quaker Parrot', 'Bourke\'s Parrot', 'Cockatiel Lutino',
    'Cockatiel Pearl', 'Cockatiel Pied', 'Cockatiel Cinnamon', 'Cockatiel Whiteface',
    'English Budgie', 'American Budgie', 'Opaline Budgie', 'Spangle Budgie', 'Recessive Pied Budgie',
    'Yellow Canary', 'Red Factor Canary', 'Gloster Canary', 'Yorkshire Canary', 'Norwich Canary',
    'Belgian Fancy Canary', 'Border Fancy Canary', 'Fife Fancy Canary', 'Roller Canary', 'Waterslager Canary',
    'Fischer\'s Lovebird', 'Peach-faced Lovebird', 'Masked Lovebird', 'Black-masked Lovebird', 'Abyssinian Lovebird',
    'Sun Conure', 'Green Cheek Conure', 'Blue Crown Conure', 'Jenday Conure', 'Nanday Conure',
    'Cherry-headed Conure', 'Mitred Conure', 'Dusky Conure', 'Half Moon Conure', 'Patagonian Conure',
    'Timneh Grey Parrot', 'Congo African Grey', 'Blue Front Amazon', 'Yellow-naped Amazon', 'Double Yellow-headed Amazon',
    'Orange-winged Amazon', 'Yellow-crowned Amazon', 'Mealy Amazon', 'White-fronted Amazon', 'Lilac-crowned Amazon',
    'Blue and Gold Macaw', 'Scarlet Macaw', 'Green-winged Macaw', 'Military Macaw', 'Severe Macaw',
    'Hyacinth Macaw', 'Red-shouldered Macaw', 'Blue-throated Macaw', 'Red-fronted Macaw', 'Spix\'s Macaw',
    'Umbrella Cockatoo', 'Moluccan Cockatoo', 'Sulfur-crested Cockatoo', 'Goffin\'s Cockatoo', 'Bare-eyed Cockatoo',
    'Major Mitchell\'s Cockatoo', 'Ducorps\' Cockatoo', 'Gang-gang Cockatoo', 'Palm Cockatoo', 'Red-tailed Black Cockatoo',
    'Zebra Finch', 'Gouldian Finch', 'Society Finch', 'Spice Finch', 'Star Finch',
    'Owl Finch', 'Diamond Firetail Finch', 'Red Avadavat', 'Java Sparrow', 'Diamond Dove',
    'Ringneck Dove', 'Senegal Parrot', 'Meyer\'s Parrot', 'Red-bellied Parrot', 'Brown-headed Parrot', 'Mixed Breed'
]

reptile_breeds = [
    'Bearded Dragon', 'Leopard Gecko', 'Ball Python', 'Corn Snake', 'Crested Gecko',
    'Green Anole', 'Russian Tortoise', 'Red-eared Slider', 'Blue-tongued Skink', 'Veiled Chameleon',
    'Panther Chameleon', 'Jackson\'s Chameleon', 'Greek Tortoise', 'Sulcata Tortoise', 'Red-footed Tortoise',
    'African Fat-tailed Gecko', 'Gargoyle Gecko', 'Tokay Gecko', 'Mediterranean House Gecko', 'Day Gecko',
    'King Snake', 'Milk Snake', 'Hognose Snake', 'Garter Snake', 'Rat Snake',
    'Rosy Boa', 'Rainbow Boa', 'Green Tree Python', 'Carpet Python', 'Reticulated Python',
    'Boa Constrictor', 'Gopher Snake', 'Blood Python', 'Western Hognose', 'Eastern Hognose',
    'Burmese Python', 'Savannah Monitor', 'Nile Monitor', 'Black-throated Monitor', 'Ackie Monitor',
    'Argentine Tegu', 'Colombian Tegu', 'Red Tegu', 'Blue Tegu', 'Gold Tegu',
    'Chinese Water Dragon', 'Green Iguana', 'Desert Iguana', 'Spiny-tailed Iguana', 'Rhinoceros Iguana',
    'Uromastyx', 'Frilled Dragon', 'Sailfin Dragon', 'Box Turtle', 'Painted Turtle',
    'Map Turtle', 'Musk Turtle', 'Mud Turtle', 'Softshell Turtle', 'Diamondback Terrapin',
    'Alligator Snapping Turtle', 'Pink-tongued Skink', 'Schneider\'s Skink', 'Solomon Island Skink', 'Fire Skink',
    'Plated Lizard', 'Caiman Lizard', 'Basilisk', 'Horned Lizard', 'Collared Lizard',
    'Gila Monster', 'African Bullfrog', 'Pacman Frog', 'Whites Tree Frog', 'Leopard Frog',
    'Fire-bellied Toad', 'American Toad', 'Red-eyed Tree Frog', 'Poison Dart Frog', 'Tomato Frog',
    'Cuban Tree Frog', 'Clawed Frog', 'Pixie Frog', 'Tiger Salamander', 'Axolotl',
    'Fire Salamander', 'Spotted Salamander', 'Marbled Salamander', 'Newt', 'Mudpuppy'
]

pet_names = [
    'Max', 'Bella', 'Charlie', 'Lucy', 'Cooper', 'Luna', 'Buddy', 'Daisy',
    'Rocky', 'Molly', 'Jack', 'Sadie', 'Bear', 'Maggie', 'Duke', 'Sophie',
    'Oliver', 'Chloe', 'Tucker', 'Bailey', 'Leo', 'Stella', 'Bentley', 'Nala',
    'Milo', 'Zoe', 'Jax', 'Lola', 'Zeus', 'Penny', 'Winston', 'Ruby', 'Gus',
    'Rosie', 'Sam', 'Gracie', 'Finn', 'Coco', 'Murphy', 'Willow', 'Oscar',
    'Lily', 'Louie', 'Piper', 'Shadow', 'Emma', 'Scout', 'Millie', 'Dexter',
    'Abby', 'Toby', 'Chloe', 'Rex', 'Izzy', 'Lucky', 'Pepper', 'Blue', 'Dixie',
    'Angel', 'Riley', 'Oreo', 'Peanut', 'Jasper', 'Bandit', 'Baxter', 'Belle',
    'Titan', 'Nova', 'Rusty', 'Roxy', 'Apollo', 'Princess', 'Simba', 'Mocha',
    'Bruno', 'Holly', 'Thor', 'Misty', 'Hunter', 'Callie', 'Jackson', 'Ellie',
    'Ranger', 'Layla', 'Marley', 'Athena', 'Samson', 'Leia', 'Bruce', 'Pixie',
    'Diesel', 'Diamond', 'Brutus', 'Amber', 'Ace', 'Trixie', 'Cash', 'Bonnie',
    'Archie', 'Poppy', 'Maverick', 'Raven', 'Whiskey', 'Maya', 'Koda', 'Skye',
    'George', 'Fiona', 'Henry', 'Olive', 'Chase', 'Pearl', 'King', 'Sunny',
    'Ozzy', 'Summer', 'Tank', 'Sasha', 'Sammy', 'Belle', 'Buster', 'Annie',
    'Prince', 'Sugar', 'Teddy', 'Minnie', 'Jake', 'Precious', 'Rufus', 'Lady',
    'Walter', 'Phoebe', 'Barney', 'Violet', 'Otis', 'Ginger', 'Rocket', 'Kiki',
    'Atlas', 'Blossom', 'Hank', 'Winnie', 'Frank', 'Mia', 'Copper', 'Baby'
]

# New lists for additional attributes
size_options = ['Tiny', 'Small', 'Medium', 'Large', 'X-Large', 'Giant']

energy_level_options = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

health_status_options = [
    'Healthy, vaccinated', 'Good health, needs vaccines', 
    'Healthy, neutered and vaccinated', 'Minor health issues, vaccinated',
    'Needs dental work, otherwise healthy', 'Good health, not neutered',
    'Recovering from surgery, otherwise healthy', 'Senior with arthritis',
    'Healthy, recently spayed', 'Overweight but otherwise healthy',
    'Underweight, needs special diet', 'Healthy with seasonal allergies',
    'Chronic condition, managed with medication', 'Blind but adapts well',
    'Deaf but adapts well', 'Partial hearing loss', 'Vision impaired, adapts well',
    'Metabolic disorder, special diet', 'Allergies, managed with medication',
    'Dental issues, needs soft food', 'Fully vaccinated, excellent health',
    'FIV+ (cats), otherwise healthy', 'FeLV+ (cats), otherwise healthy',
    'Heartworm positive, undergoing treatment', 'Hypothyroidism, on medication',
    'Hyperthyroidism, on medication', 'Diabetes, managed with insulin',
    'Recovering from injury, making progress', 'Special needs, but good quality of life',
    'Heart murmur, monitor only', 'Seizure disorder, controlled with medication'
]

behavior_traits_options = [
    'Friendly and outgoing', 'Shy but affectionate', 'Good with children',
    'Prefers adults only', 'Gets along with other pets', 'Not good with cats',
    'Not good with dogs', 'High energy, needs exercise', 'Calm and laid-back',
    'Playful and curious', 'Well-trained and obedient', 'Needs basic training',
    'Independent nature', 'Very affectionate', 'Protective instincts',
    'Anxious in new situations', 'Good for first-time owners',
    'Experienced owner preferred', 'House trained', 'Crate trained',
    'Loyal and devoted', 'Intelligent and trainable', 'Timid, needs patience',
    'Vocal and expressive', 'Quiet and reserved', 'Social with other animals',
    'Loves car rides', 'Enjoys being held', 'Lap pet', 'Energetic player',
    'Enjoys fetch games', 'Water-loving', 'Enjoys walks', 'Cuddle buddy',
    'Food motivated', 'Toy motivated', 'Fearful of loud noises', 'Gentle with smaller animals',
    'Territorial', 'Selective with friends', 'Separation anxiety', 'Confident and bold',
    'Inquisitive explorer', 'Enjoys being brushed', 'Loves attention', 
    'Chill and relaxed', 'Watches TV with you', 'Follows you everywhere',
    'Loves meeting new people', 'Cautious with strangers', 'Enjoys playtime',
    'Mellow companion', 'Perfect apartment pet', 'Needs yard space',
    'Adventure buddy', 'Snuggle expert', 'Sunbathing enthusiast'
]

status_options = ['Available', 'Pending', 'Adopted', 'Medical Hold', 'Quarantine', 'Foster Care']

def generate_rspca_data(num_records=100):
    """
    Generate sample data in RSPCA format
    """
    data = []
    for i in range(1, num_records + 1):
        species = random.choice(['Dog', 'Cat', 'Bird', 'Small Animal', 'Reptile'])
        
        # Select appropriate breed based on species
        if species == 'Dog':
            breed = random.choice(dog_breeds)
        elif species == 'Cat':
            breed = random.choice(cat_breeds)
        elif species == 'Bird':
            breed = random.choice(bird_breeds)
        elif species == 'Reptile':
            breed = random.choice(reptile_breeds)
        else:  # Small Animal
            breed = random.choice(small_animal_breeds)
        
        # Generate random age
        if random.random() < 0.8:  # Most animals are younger
            years = random.randint(0, 5)
            months = random.randint(0, 11)
        else:  # Some are older
            years = random.randint(6, 15)
            months = 0
        
        # Format age in different ways to test cleaning logic
        age_formats = [
            f"{years} years {months} months",
            f"{years}y {months}m",
            f"{years} y/o",
            f"{years}.{months} years"
        ]
        
        # Generate size based on species and breed characteristics
        if species == 'Dog':
            if 'Chihuahua' in breed or 'Terrier' in breed or 'Toy' in breed:
                size = random.choice(['Tiny', 'Small'])
            elif 'Great' in breed or 'Mastiff' in breed or 'Dane' in breed:
                size = random.choice(['X-Large', 'Giant'])
            else:
                size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Cat':
            size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Bird':
            if 'Macaw' in breed or 'Cockatoo' in breed:
                size = random.choice(['Medium', 'Large'])
            else:
                size = random.choice(['Tiny', 'Small'])
        elif species == 'Reptile':
            if 'Python' in breed or 'Monitor' in breed or 'Iguana' in breed:
                size = random.choice(['Medium', 'Large', 'X-Large'])
            else:
                size = random.choice(['Tiny', 'Small', 'Medium'])
        else:  # Small Animal
            size = random.choice(['Tiny', 'Small'])
        
        # Generate energy level
        if species == 'Dog':
            if 'Retriever' in breed or 'Shepherd' in breed or 'Collie' in breed:
                energy = random.choice(['High', 'Very High'])
            elif 'Bulldog' in breed or 'Mastiff' in breed:
                energy = random.choice(['Low', 'Medium'])
            else:
                energy = random.choice(energy_level_options)
        elif species == 'Cat':
            if 'Siamese' in breed or 'Bengal' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(['Low', 'Medium'])
        elif species == 'Bird':
            energy = random.choice(['Medium', 'High', 'Very High'])
        elif species == 'Reptile':
            energy = random.choice(['Very Low', 'Low'])
        else:  # Small Animal
            if 'Hamster' in breed or 'Gerbil' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(energy_level_options)
        
        data.append({
            'Animal ID': f"RSPCA-{i:04d}",
            'Name': random.choice(pet_names),
            'Species': species,
            'Breed Type': breed,
            'Age': random.choice(age_formats),
            'Gender': random.choice(['Male', 'Female', 'M', 'F']),
            'Size': size,
            'Energy Level': energy,
            'Health': random.choice(health_status_options),
            'Behavior': random.choice(behavior_traits_options),
            'Location': random.choice(['Surrey Branch', 'London Branch', 'Kent Branch', 'Hampshire Branch']),
            'Availability': random.choice(status_options),
            'Good with Kids': random.choice(['Yes', 'No', 'Unknown']),
            'Good with Cats': random.choice(['Yes', 'No', 'Unknown']),
            'Good with Dogs': random.choice(['Yes', 'No', 'Unknown'])
        })
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, 'rspca_surrey.csv')
    df.to_csv(file_path, index=False)
    print(f"Generated {num_records} RSPCA records to {file_path}")
    return df

def generate_animal_rescue_data(num_records=100):
    """
    Generate sample data in Animal Rescue Center format
    """
    data = []
    for i in range(1, num_records + 1):
        species = random.choice(['Dog', 'Cat', 'Bird', 'Small Animal', 'Reptile'])
        
        # Select appropriate breed based on species
        if species == 'Dog':
            breed = random.choice(dog_breeds)
        elif species == 'Cat':
            breed = random.choice(cat_breeds)
        elif species == 'Bird':
            breed = random.choice(bird_breeds)
        elif species == 'Reptile':
            breed = random.choice(reptile_breeds)
        else:  # Small Animal
            breed = random.choice(small_animal_breeds)
        
        # Generate random age in months
        if random.random() < 0.8:  # Most animals are younger
            age_months = random.randint(1, 60)  # Up to 5 years
        else:  # Some are older
            age_months = random.randint(61, 180)  # 5-15 years
        
        # Generate size
        if species == 'Dog':
            if 'Chihuahua' in breed or 'Terrier' in breed or 'Toy' in breed:
                size = random.choice(['Tiny', 'Small'])
            elif 'Great' in breed or 'Mastiff' in breed or 'Dane' in breed:
                size = random.choice(['X-Large', 'Giant'])
            else:
                size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Cat':
            size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Bird':
            if 'Macaw' in breed or 'Cockatoo' in breed:
                size = random.choice(['Medium', 'Large'])
            else:
                size = random.choice(['Tiny', 'Small'])
        elif species == 'Reptile':
            if 'Python' in breed or 'Monitor' in breed or 'Iguana' in breed:
                size = random.choice(['Medium', 'Large', 'X-Large'])
            else:
                size = random.choice(['Tiny', 'Small', 'Medium'])
        else:  # Small Animal
            size = random.choice(['Tiny', 'Small'])
        
        # Generate energy level
        if species == 'Dog':
            if 'Retriever' in breed or 'Shepherd' in breed or 'Collie' in breed:
                energy = random.choice(['High', 'Very High'])
            elif 'Bulldog' in breed or 'Mastiff' in breed:
                energy = random.choice(['Low', 'Medium'])
            else:
                energy = random.choice(energy_level_options)
        elif species == 'Cat':
            if 'Siamese' in breed or 'Bengal' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(['Low', 'Medium'])
        elif species == 'Bird':
            energy = random.choice(['Medium', 'High', 'Very High'])
        elif species == 'Reptile':
            energy = random.choice(['Very Low', 'Low'])
        else:  # Small Animal
            if 'Hamster' in breed or 'Gerbil' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(energy_level_options)
        
        # Generate behavior notes with potential compatibility issues
        behavior_notes = random.choice(behavior_traits_options)
        
        # Randomly add incompatibilities to test extraction
        if random.random() < 0.2:
            behavior_notes += "; not good with kids"
        if random.random() < 0.2:
            behavior_notes += "; doesn't get along with cats"
        if random.random() < 0.2:
            behavior_notes += "; not compatible with other dogs"
        
        data.append({
            'ID': f"ARC-{i:04d}",
            'Pet Name': random.choice(pet_names),
            'Type': species,
            'Animal Breed': breed,
            'Age (months)': age_months,
            'Sex': random.choice(['M', 'F', 'Unknown']),
            'Size': size,
            'Energy Level': energy,
            'Medical Status': random.choice(health_status_options),
            'Behavior Notes': behavior_notes,
            'Shelter Location': random.choice(['Animal Rescue Center, London', 'Animal Rescue Center, Manchester', 'Animal Rescue Center, Birmingham', 'Animal Rescue Center, Leeds']),
            'Status': random.choice(['Available', 'On Hold', 'Adopted', 'Not Available']),
            'Good With Children': random.choice(['Yes', 'No', 'Unknown']),
            'Good With Other Animals': random.choice(['Yes', 'No', 'Unknown']),
            'Special Needs': random.choice(['Yes', 'No'])
        })
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, 'animal_rescue_center.csv')
    df.to_csv(file_path, index=False)
    print(f"Generated {num_records} Animal Rescue Center records to {file_path}")
    return df

def generate_battersea_data(num_records=100):
    """
    Generate sample data in Battersea format
    """
    data = []
    for i in range(1, num_records + 1):
        species = random.choice(['Dog', 'Cat', 'Small Animal', 'Bird', 'Reptile'])
        
        # Select appropriate breed based on species
        if species == 'Dog':
            breed = random.choice(dog_breeds)
        elif species == 'Cat':
            breed = random.choice(cat_breeds)
        elif species == 'Bird':
            breed = random.choice(bird_breeds)
        elif species == 'Reptile':
            breed = random.choice(reptile_breeds)
        else:  # Small Animal
            breed = random.choice(small_animal_breeds)
        
        # Generate random age
        years = random.randint(0, 12)
        
        # Generate health notes
        health_status = random.choice(health_status_options)
        vaccinated = "vaccinated" in health_status.lower()
        neutered = "neutered" in health_status.lower() or "spayed" in health_status.lower()
        
        # Generate size
        if species == 'Dog':
            if 'Chihuahua' in breed or 'Terrier' in breed or 'Toy' in breed:
                size = random.choice(['Tiny', 'Small'])
            elif 'Great' in breed or 'Mastiff' in breed or 'Dane' in breed:
                size = random.choice(['X-Large', 'Giant'])
            else:
                size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Cat':
            size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Bird':
            if 'Macaw' in breed or 'Cockatoo' in breed:
                size = random.choice(['Medium', 'Large'])
            else:
                size = random.choice(['Tiny', 'Small'])
        elif species == 'Reptile':
            if 'Python' in breed or 'Monitor' in breed or 'Iguana' in breed:
                size = random.choice(['Medium', 'Large', 'X-Large'])
            else:
                size = random.choice(['Tiny', 'Small', 'Medium'])
        else:  # Small Animal
            size = random.choice(['Tiny', 'Small'])
        
        # Generate energy level
        if species == 'Dog':
            if 'Retriever' in breed or 'Shepherd' in breed or 'Collie' in breed:
                energy = random.choice(['High', 'Very High'])
            elif 'Bulldog' in breed or 'Mastiff' in breed:
                energy = random.choice(['Low', 'Medium'])
            else:
                energy = random.choice(energy_level_options)
        elif species == 'Cat':
            if 'Siamese' in breed or 'Bengal' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(['Low', 'Medium'])
        elif species == 'Bird':
            energy = random.choice(['Medium', 'High', 'Very High'])
        elif species == 'Reptile':
            energy = random.choice(['Very Low', 'Low'])
        else:  # Small Animal
            if 'Hamster' in breed or 'Gerbil' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(energy_level_options)
        
        data.append({
            'Pet ID': f"BDH-{i:04d}",
            'Name': random.choice(pet_names),
            'Animal Type': species,
            'Type & Breed': f"{species} - {breed}",
            'Years': years,
            'Sex': random.choice(['Male', 'Female']),
            'Size': size,
            'Energy Level': energy,
            'Medical History': health_status,
            'Vaccinated': 'Yes' if vaccinated else 'No',
            'Neutered/Spayed': 'Yes' if neutered else 'No',
            'Temperament': random.choice(behavior_traits_options),
            'Branch': random.choice(['London', 'Old Windsor', 'Brands Hatch']),
            'Adoption Status': random.choice(['Available for Adoption', 'Reserved', 'Adopted', 'In Foster Care']),
            'Child Friendly': random.choice(['Yes', 'No', 'Unknown']),
            'Cat Friendly': random.choice(['Yes', 'No', 'Unknown']),
            'Dog Friendly': random.choice(['Yes', 'No', 'Unknown'])
        })
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, 'battersea.csv')
    df.to_csv(file_path, index=False)
    print(f"Generated {num_records} Battersea records to {file_path}")
    return df

def generate_humane_society_data(num_records=100):
    """
    Generate sample data in Humane Society format
    """
    data = []
    for i in range(1, num_records + 1):
        species = random.choice(['Dog', 'Cat', 'Small Animal', 'Bird', 'Reptile'])
        
        # Select appropriate breed based on species
        if species == 'Dog':
            breed = random.choice(dog_breeds)
        elif species == 'Cat':
            breed = random.choice(cat_breeds)
        elif species == 'Bird':
            breed = random.choice(bird_breeds)
        elif species == 'Reptile':
            breed = random.choice(reptile_breeds)
        else:  # Small Animal
            breed = random.choice(small_animal_breeds)
        
        # Generate random age
        years = random.randint(0, 10)
        months = random.randint(0, 11) if years == 0 else 0  # Only add months for young animals
        
        # Generate boolean attributes
        good_with_kids = random.choice([True, False, 'Yes', 'No', 1, 0])
        good_with_cats = random.choice([True, False, 'Yes', 'No', 1, 0])
        good_with_dogs = random.choice([True, False, 'Yes', 'No', 1, 0])
        
        # Generate size
        if species == 'Dog':
            if 'Chihuahua' in breed or 'Terrier' in breed or 'Toy' in breed:
                size = random.choice(['Tiny', 'Small'])
            elif 'Great' in breed or 'Mastiff' in breed or 'Dane' in breed:
                size = random.choice(['X-Large', 'Giant'])
            else:
                size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Cat':
            size = random.choice(['Small', 'Medium', 'Large'])
        elif species == 'Bird':
            if 'Macaw' in breed or 'Cockatoo' in breed:
                size = random.choice(['Medium', 'Large'])
            else:
                size = random.choice(['Tiny', 'Small'])
        elif species == 'Reptile':
            if 'Python' in breed or 'Monitor' in breed or 'Iguana' in breed:
                size = random.choice(['Medium', 'Large', 'X-Large'])
            else:
                size = random.choice(['Tiny', 'Small', 'Medium'])
        else:  # Small Animal
            size = random.choice(['Tiny', 'Small'])
        
        # Generate energy level
        if species == 'Dog':
            if 'Retriever' in breed or 'Shepherd' in breed or 'Collie' in breed:
                energy = random.choice(['High', 'Very High'])
            elif 'Bulldog' in breed or 'Mastiff' in breed:
                energy = random.choice(['Low', 'Medium'])
            else:
                energy = random.choice(energy_level_options)
        elif species == 'Cat':
            if 'Siamese' in breed or 'Bengal' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(['Low', 'Medium'])
        elif species == 'Bird':
            energy = random.choice(['Medium', 'High', 'Very High'])
        elif species == 'Reptile':
            energy = random.choice(['Very Low', 'Low'])
        else:  # Small Animal
            if 'Hamster' in breed or 'Gerbil' in breed:
                energy = random.choice(['Medium', 'High'])
            else:
                energy = random.choice(energy_level_options)
        
        data.append({
            'Ref Number': f"HS-{i:04d}",
            'Animal Name': random.choice(pet_names),
            'Animal Type': species,
            'Breed': breed,
            'Years Old': years,
            'Months Old': months,
            'M/F': random.choice(['M', 'F']),
            'Size': size,
            'Energy Level': energy,
            'Vaccinated': random.choice(['Yes', 'No', 'Partial']),
            'Neutered/Spayed': random.choice(['Yes', 'No']),
            'Kid Friendly': good_with_kids,
            'Cat Friendly': good_with_cats,
            'Dog Friendly': good_with_dogs,
            'Status': random.choice(['Available', 'Pending', 'Adopted', 'Unavailable']),
            'Arrival Date': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%Y-%m-%d'),
            'Special Needs': random.choice(['Yes', 'No']),
            'House Trained': random.choice(['Yes', 'No', 'In Progress']),
            'Temperament': ', '.join(random.sample(behavior_traits_options, k=random.randint(1, 3)))
        })
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(data)
    file_path = os.path.join(DATA_DIR, 'humane_society.csv')
    df.to_csv(file_path, index=False)
    print(f"Generated {num_records} Humane Society records to {file_path}")
    return df

def generate_all_sample_data():
    """
    Generate sample data for all shelter formats
    """
    print("Generating sample data for testing...")
    
    # Generate data for each shelter format
    generate_rspca_data(100)
    generate_animal_rescue_data(100)
    generate_battersea_data(100)
    generate_humane_society_data(100)
    
    print("Sample data generation complete!")

if __name__ == "__main__":
    generate_all_sample_data()