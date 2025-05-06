import React from 'react';

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="how-it-works">
      <div className="container">
        <h2 className="section-title">How It Works</h2>
        
        <div className="steps">
          <div className="step">
            <div className="step-icon">
              <i data-feather="user"></i>
            </div>
            <h3>Blockchain Identity</h3>
            <p>Connect with your blockchain wallet for authentication. No phone numbers or emails required.</p>
          </div>
          
          <div className="step">
            <div className="step-icon">
              <i data-feather="lock"></i>
            </div>
            <h3>End-to-End Encryption</h3>
            <p>Your messages are encrypted on your device and can only be read by the intended recipient.</p>
          </div>
          
          <div className="step">
            <div className="step-icon">
              <i data-feather="box"></i>
            </div>
            <h3>Decentralized Storage</h3>
            <p>Messages are stored on the blockchain and IPFS, not on centralized servers.</p>
          </div>
        </div>
        
        <div className="encryption-diagram">
          <div className="diagram-step">
            <div className="icon"><i data-feather="edit-2"></i></div>
            <div className="text">You write a message</div>
          </div>
          
          <div className="diagram-arrow">→</div>
          
          <div className="diagram-step">
            <div className="icon"><i data-feather="key"></i></div>
            <div className="text">Message is encrypted</div>
          </div>
          
          <div className="diagram-arrow">→</div>
          
          <div className="diagram-step">
            <div className="icon"><i data-feather="send"></i></div>
            <div className="text">Sent via blockchain</div>
          </div>
          
          <div className="diagram-arrow">→</div>
          
          <div className="diagram-step">
            <div className="icon"><i data-feather="unlock"></i></div>
            <div className="text">Recipient decrypts</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
