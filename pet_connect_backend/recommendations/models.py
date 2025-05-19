# recommendations/models.py
from django.db import models
from django.contrib.auth.models import User
from animals.models import Animal

class AnimalRecommendation(models.Model):
    """Model to store recommendation scores between users and animals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='recommendations')
    score = models.FloatField(help_text="Match score between 0 and 1")
    preference_score = models.FloatField(default=0.0, help_text="Score based on user's explicit preferences")
    interaction_score = models.FloatField(default=0.0, help_text="Score based on user's viewing history")
    similarity_score = models.FloatField(default=0.0, help_text="Score based on content similarity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'animal')
        ordering = ['-score']
    
    def __str__(self):
        return f"Score: {self.score:.2f} for {self.user.username} and {self.animal.name}"
        
    def update_total_score(self, weights=None):
        """Update the total score based on component scores and optional weights"""
        if weights is None:
            weights = {
                'preference': 0.4,
                'interaction': 0.35,
                'similarity': 0.25
            }
        
        self.score = (
            self.preference_score * weights['preference'] +
            self.interaction_score * weights['interaction'] +
            self.similarity_score * weights['similarity']
        )
        self.save()