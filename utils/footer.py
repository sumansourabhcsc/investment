import streamlit as st


def show_footer():
    """
    Render the Taurus site-wide footer.
    Call this at the bottom of every page:

        from utils.footer import show_footer
        show_footer()
    """
    st.markdown("""
<style>
/* ── Footer wrapper ── */
.taurus-footer {
    margin-top: 4rem;
    border-top: 1px solid rgba(0, 245, 212, 0.12);
    padding: 2.8rem 0 1.4rem 0;
    font-family: 'DM Mono', monospace;
}

/* ── Column grid ── */
.tf-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
    margin-bottom: 2.2rem;
}

@media (max-width: 700px) {
    .tf-grid { grid-template-columns: repeat(2, 1fr); }
}

/* ── Column heading ── */
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

/* ── Links ── */
.tf-links { list-style: none; padding: 0; margin: 0; }

.tf-links li { margin-bottom: 0.48rem; }

.tf-links a {
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: rgba(200, 230, 226, 0.5);
    text-decoration: none;
    transition: color 0.2s, letter-spacing 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.tf-links a::before {
    content: '›';
    color: rgba(0, 245, 212, 0);
    transition: color 0.2s, transform 0.2s;
    font-size: 0.85rem;
    transform: translateX(-4px);
}

.tf-links a:hover {
    color: rgba(0, 245, 212, 0.85);
    letter-spacing: 0.07em;
}

.tf-links a:hover::before {
    color: rgba(0, 245, 212, 0.85);
    transform: translateX(0);
}

/* ── Bottom bar ── */
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

.tf-copy span {
    color: rgba(0, 245, 212, 0.45);
}

.tf-legal {
    display: flex;
    gap: 1.2rem;
}

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

<div class="taurus-footer">

  <!-- ── 4-column link grid ── -->
  <div class="tf-grid">

    <!-- Col 1 -->
    <div>
      <div class="tf-heading">Get to Know Us</div>
      <ul class="tf-links">
        <li><a href="#">About Taurus</a></li>
        <li><a href="#">Careers</a></li>
        <li><a href="#">Press</a></li>
        <li><a href="#">Research</a></li>
      </ul>
    </div>

    <!-- Col 2 -->
    <div>
      <div class="tf-heading">Connect with Us</div>
      <ul class="tf-links">
        <li><a href="#">GitHub</a></li>
        <li><a href="#">Twitter / X</a></li>
        <li><a href="#">LinkedIn</a></li>
        <li><a href="#">Discord</a></li>
      </ul>
    </div>

    <!-- Col 3 -->
    <div>
      <div class="tf-heading">Tools &amp; Data</div>
      <ul class="tf-links">
        <li><a href="#">Portfolio Overview</a></li>
        <li><a href="#">Fund Details</a></li>
        <li><a href="#">Run Pipeline</a></li>
        <li><a href="#">API Docs</a></li>
      </ul>
    </div>

    <!-- Col 4 -->
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

  <!-- ── Bottom bar ── -->
  <div class="tf-bottom">
    <div class="tf-copy">
      © 2025 <span>Suman Sourabh PMS Pvt. Ltd.</span> · All rights reserved
    </div>
    <div class="tf-legal">
      <a href="#">Privacy</a>
      <a href="#">Terms</a>
      <a href="#">Cookies</a>
    </div>
    <div class="tf-locale">Language: English &nbsp;|&nbsp; Country: India</div>
  </div>

</div>
""", unsafe_allow_html=True)
