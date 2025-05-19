import React from 'react';
import { Link } from 'react-router-dom';

const AboutPage = () => {
  return (
    <div className="about-page">
      <div className="about-header">
        <h1>About Pet Connect</h1>
        <p>Finding the perfect animal companion through AI-powered recommendations</p>
      </div>
      
      <div className="about-section">
        <h2>Our Mission</h2>
        <p>
          Pet Connect was created to revolutionize the animal adoption process by using
          advanced AI recommendation technology to match adopters with their ideal companions.
          Our goal is to increase successful adoptions, reduce shelter overcrowding, and
          create lasting bonds between animals and their new families.
        </p>
      </div>
           
      <div className="about-section">
        <h2>Our Technology</h2>
        <p>
          Pet Connect uses a hybrid recommendation system that combines content-based filtering
          and collaborative filtering approaches. This means our system considers both the specific
          attributes of animals and the patterns in user behavior to generate personalized recommendations.
        </p>
        <p>
          As you browse different animals, our system learns your preferences and adapts its
          recommendations in real-time. This adaptive approach helps you discover animals you
          might not have considered otherwise, increasing the chances of a successful adoption.
        </p>
      </div>
      
      <div className="about-section">
        <h2>Get Started Today</h2>
        <p>
          Ready to find your perfect animal companion? Create an account and start exploring
          our database of adorable animals looking for their forever homes.
        </p>
        <div className="cta-buttons">
          <Link to="/register" className="primary-button">Sign Up</Link>
          <Link to="/animals" className="secondary-button">Browse Animals</Link>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;