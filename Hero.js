import React from 'react';
import { Link } from 'react-router-dom';

const Hero = () => {
  return (
    <section className="hero">
      <div className="container">
        <div className="hero-content">
          <h1>Decentralized Secure Messaging</h1>
          <p className="tagline">Private. Decentralized. Blockchain-based.</p>
          <Link to="/register" className="btn btn-primary btn-lg">
            <i data-feather="send"></i> Get Started
          </Link>
        </div>
      </div>
    </section>
  );
};

export default Hero;
