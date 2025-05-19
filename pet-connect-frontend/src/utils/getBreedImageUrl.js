const getBreedImageUrl = (animal) => {
  if (!animal) return '/images/animal-placeholder.jpg';

  if (animal.photo_url) return animal.photo_url;

  // Normalize breed name for filename use
  const breed = animal.breed?.toLowerCase().replace(/[^a-z0-9]+/g, '_') || 'unknown';
  const species = animal.species?.toLowerCase() || 'unknown';

  // Supported species folder mapping
  const folderMap = {
    dog: 'dogs',
    cat: 'cats',
    'small animal': 'small_animals',
    bird: 'birds',
    reptile: 'reptiles'
  };

  const folder = folderMap[species] || 'unknown';
  const path = `/images/breeds/${folder}/${breed}.jpg`;

  return path;
};

export default getBreedImageUrl;
