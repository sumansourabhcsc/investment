import streamlit.components.v1 as components


def show_footer():
    """
    Render the Taurus site-wide footer.
    Call this at the bottom of every page:

        from utils.footer import show_footer
        show_footer()
    """
    components.html("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: transparent;
    font-family: 'DM Mono', monospace;
    color: #e8e2d5;
    padding: 2.8rem 0 1.4rem 0;
}

.tf-top-line {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,245,212,0.4) 0%, rgba(0,201,255,0.2) 50%, transparent 100%);
    margin-bottom: 2.4rem;
}

.tf-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
    margin-bottom: 2.2rem;
}

.tf-heading {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #c8e6e2;
    margin-bottom: 0.9rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid rgba(0, 245, 212, 0.14);
    position: relative;
}

.tf-heading::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 28px; height: 1px;
    background: #00f5d4;
}

.tf-links { list-style: none; padding: 0; margin: 0; }
.tf-links li { margin-bottom: 0.48rem; }

.tf-links a {
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: rgba(200, 230, 226, 0.5);
    text-decoration: none;
    transition: color 0.2s;
}

.tf-links a:hover { color: rgba(0, 245, 212, 0.85); }

.tf-bottom {
    border-top: 1px solid rgba(0, 245, 212, 0.08);
    padding-top: 1.2rem;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
}

.tf-copy {
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    color: rgba(200, 230, 226, 0.3);
}

.tf-copy span { color: rgba(0, 245, 212, 0.55); }

.tf-legal { display: flex; gap: 1.2rem; }

.tf-legal a {
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    color: rgba(200, 230, 226, 0.28);
    text-decoration: none;
    text-transform: uppercase;
    transition: color 0.2s;
}

.tf-legal a:hover { color: rgba(0, 245, 212, 0.6); }

.tf-locale {
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    color: rgba(200, 230, 226, 0.28);
}
</style>
</head>
<body>

<div class="tf-top-line"></div>

<div class="tf-grid">

  <div>
    <div class="tf-heading">Get to Know Us</div>
    <ul class="tf-links">
      <li><a href="#">About Taurus</a></li>
      <li><a href="#">Careers</a></li>
      <li><a href="#">Press</a></li>
      <li><a href="#">Research</a></li>
    </ul>
  </div>

  <div>
    <div class="tf-heading">Connect with Us</div>
    <ul class="tf-links">
      <li><a href="#">GitHub</a></li>
      <li><a href="#">Twitter / X</a></li>
      <li><a href="#">LinkedIn</a></li>
      <li><a href="#">Discord</a></li>
    </ul>
  </div>

  <div>
    <div class="tf-heading">Tools &amp; Data</div>
    <ul class="tf-links">
      <li><a href="#">Portfolio Overview</a></li>
      <li><a href="#">Fund Details</a></li>
      <li><a href="#">Run Pipeline</a></li>
      <li><a href="#">API Docs</a></li>
    </ul>
  </div>

  <div>
    <div class="tf-heading">Let Us Help You</div>
    <ul class="tf-links">
      <li><a href="#">Your Account</a></li>
      <li><a href="#">Documentation</a></li>
      <li><a href="#">Support</a></li>
      <li><a href="#">System Status</a></li>
    </ul>
  </div>

</div>

<div class="tf-bottom">
  <div class="tf-copy">
    &copy; 2026 <span>Suman Sourabh PMS Pvt. Ltd.</span> &nbsp;&middot;&nbsp; All rights reserved
  </div>
  <div class="tf-legal">
    <a href="#">Privacy</a>
    <a href="#">Terms</a>
    <a href="#">Cookies</a>
  </div>
  <div class="tf-locale">Language: English &nbsp;|&nbsp; Country: India</div>
</div>

</body>
</html>
""", height=320, scrolling=False)
