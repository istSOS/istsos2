// Navbar.tsx
import React, { useState } from 'react';
import OSGEOLogo from '../public/osgeo.svg'
import './Navbar.css';

function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState<boolean>(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <a href="https://www.osgeo.org/" target="_blank">
          <img src={OSGEOLogo} className="nav__logo" alt="istsos logo" />
        </a>
      </div>
      <div className="navbar-toggle" onClick={toggleMenu}>
        <span className="navbar-toggle-icon"></span>
      </div>
      <ul className={`navbar-nav ${isMenuOpen ? 'show' : ''}`}>
        <li className="nav-item">
          <a href="#">About</a>
        </li>
        <li className="nav-item">
          <a href="#">Contact</a>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;