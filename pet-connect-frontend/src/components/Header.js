import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';

const Header = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <header className="header">
      <div className="header-container">
        <div className="logo">
          <Link to="/" className="logo-link">
            <h1>Pet Connect</h1>
          </Link>
        </div>

        <nav className="nav-menu">
          <ul className="nav-list">
            <li className="nav-item">
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
                Home
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink to="/animals" className={({ isActive }) => isActive ? 'active' : ''}>
                Animals
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink to="/recommendations" className={({ isActive }) => isActive ? 'active' : ''}>
                Recommendations
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>
                About
              </NavLink>
            </li>
            {currentUser ? (
              <>

                <li className="nav-item">
                  <NavLink to="/preferences" className={({ isActive }) => isActive ? 'active' : ''}>
                    Preferences
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/profile" className={({ isActive }) => isActive ? 'active' : ''}>
                    Profile: {currentUser.username}
                  </NavLink>
                </li>
                <li className="nav-item">
                  <button onClick={handleLogout} className="logout-button">
                    Logout
                  </button>
                </li>

              </>
            ) : (
              <>
                <li className="nav-item">
                  <NavLink to="/login" className={({ isActive }) => isActive ? 'active' : ''}>
                    Login
                  </NavLink>
                </li>
                <li className="nav-item">
                  <NavLink to="/register" className={({ isActive }) => isActive ? 'active' : ''}>
                    Register
                  </NavLink>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;