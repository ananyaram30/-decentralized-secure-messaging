import React from 'react';

const WhyUseIt = () => {
  return (
    <section id="why-use-it" className="why-use-it">
      <div className="container">
        <h2 className="section-title">Why Use It</h2>
        
        <div className="why-grid">
          <div className="why-item">
            <h3>
              <i data-feather="shield"></i>
              Enhanced Privacy
            </h3>
            <p>Traditional messaging apps collect your data. DecSecMsg doesn't store any personal information and can't access your messages.</p>
          </div>
          
          <div className="why-item">
            <h3>
              <i data-feather="zap"></i>
              Censorship Resistant
            </h3>
            <p>Built on decentralized technology, your conversations can't be blocked, monitored, or shut down by any single entity.</p>
          </div>
          
          <div className="why-item">
            <h3>
              <i data-feather="users"></i>
              Global Access
            </h3>
            <p>Anyone with internet access can use DecSecMsg, without needing to provide personal identification or phone numbers.</p>
          </div>
          
          <div className="why-item">
            <h3>
              <i data-feather="lock"></i>
              Military-Grade Encryption
            </h3>
            <p>Your messages are protected with the same encryption standards used by military and financial institutions.</p>
          </div>
        </div>
        
        <div className="comparison-table">
          <h3>How We Compare</h3>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Feature</th>
                  <th>DecSecMsg</th>
                  <th>Traditional Apps</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>End-to-End Encryption</td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                </tr>
                <tr>
                  <td>No Phone Number Required</td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                  <td><i data-feather="x" className="icon-x"></i></td>
                </tr>
                <tr>
                  <td>Decentralized Storage</td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                  <td><i data-feather="x" className="icon-x"></i></td>
                </tr>
                <tr>
                  <td>No Data Collection</td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                  <td><i data-feather="x" className="icon-x"></i></td>
                </tr>
                <tr>
                  <td>Censorship Resistant</td>
                  <td><i data-feather="check" className="icon-check"></i></td>
                  <td><i data-feather="x" className="icon-x"></i></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyUseIt;
