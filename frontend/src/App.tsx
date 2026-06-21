// Styles
import './App.css'

function App() {
  return (
    <div className="app">
      <main className="app__main">
        <h1 className="app__title">Business Modernization Portal</h1>
        <p className="app__subtitle">Frontend is ready for development.</p>
      </main>

      {/* Developer credit strip */}
      <footer className="footer-credit-strip">
        <div className="footer-credit-strip__inner">
          <a
            href="https://chepio.tech"
            target="_blank"
            rel="noopener noreferrer"
            className="footer-credit-link"
            aria-label="Developed by Chepio"
          >
            <img
              src="/images/chepio-tech/logo_designed.svg"
              alt="chepio.tech"
              className="footer-credit-logo"
            />
          </a>
        </div>
      </footer>
    </div>
  )
}

export default App
