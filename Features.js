import React from 'react';

const Features = () => {
  return (
    <section id="features" className="features">
      <div className="container">
        <h2 className="section-title">Key Features</h2>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="user-x"></i>
            </div>
            <h3>No Phone Numbers</h3>
            <p>Use your blockchain wallet to authenticate. No personal information required.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="lock"></i>
            </div>
            <h3>End-to-End Encryption</h3>
            <p>Messages are encrypted on your device and can only be decrypted by the recipient.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="users"></i>
            </div>
            <h3>Group Chat</h3>
            <p>Create secure group conversations with multiple participants.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="database"></i>
            </div>
            <h3>Decentralized Storage</h3>
            <p>Your messages are stored on IPFS and blockchain, not on centralized servers.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="eye-off"></i>
            </div>
            <h3>Full Privacy</h3>
            <p>No one, not even us, can read your messages or track your activity.</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <i data-feather="shield"></i>
            </div>
            <h3>Open Source</h3>
            <p>All code is open source and transparent. No hidden backdoors.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Features;
