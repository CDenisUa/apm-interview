// Styles
import './ChepioTechFooter.css'

/**
 * Developer credit strip — "Designed by Chepio".
 *
 * Drop in as the LAST element of the page so it sits in its own bottom band,
 * visually separate from the main content. Links to https://chepio.tech.
 *
 * Requires the logo at `public/images/chepio-tech/logo_designed.svg`.
 */
function ChepioTechFooter() {
  return (
    <footer className="chepio-footer">
      <div className="chepio-footer__inner">
        <a
          href="https://chepio.tech"
          target="_blank"
          rel="noopener noreferrer"
          className="chepio-footer__link"
          aria-label="Developed by Chepio"
        >
          <img
            src="/images/chepio-tech/logo_designed.svg"
            alt="chepio.tech"
            className="chepio-footer__logo"
          />
        </a>
      </div>
    </footer>
  )
}

export default ChepioTechFooter
