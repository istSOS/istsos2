import OSGEOLogo from "../assets/osgeo.svg";
import { Link } from "react-router-dom";

const navLinks = [
  {
    path: "/",
    title: "Home",
  },
  {
    path: "/about",
    title: "About",
  },
  {
    path: "/contact",
    title: "Contact",
  },
];

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">
          <img src={OSGEOLogo} className="nav__logo" alt="istsos logo" />
        </Link>
      </div>

      <ul className="navbar-nav">
        {navLinks.map((nav, index) => (
          <li
            key={index}
            style={{ cursor: "pointer", marginLeft: "10px", color: "white" }}
          >
            <Link to={nav.path}>{nav.title}</Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default Navbar;
