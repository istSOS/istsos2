import istsosLogo from "../assets/istsos.png";

const Dashboard = () => {
  return (
    <>
      <div className="app">
        <a href="https://istsos.org/" target="_blank">
          <img src={istsosLogo} className="logo" alt="istsos logo" />
        </a>

        <h3 style={{ color: "white", marginTop: "50px" }}>
          istSOS Web User Interface Project Task
        </h3>

        <ul style={{ color: "white", marginTop: "50px", textAlign: "left" }}>
          <li>We can use React.js for our web interface </li>
          <li>We can make web pages responsive for all devices</li>
          <li>Make interface functionality easy to use for users </li>
          <li>For responsive and fast development we can use Tailwind css</li>
          <li>
            We can use popular components liabrary as: Shadcn, headlessUi,
            MaterialUI etc.
          </li>
          <li>Also we can use core Vanilla css.</li>
        </ul>
      </div>
    </>
  );
};

export default Dashboard;
