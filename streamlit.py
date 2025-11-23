# new.py — Perfume Recommender (Season + Gender) — clean floral, with images
# Run: streamlit run new.py

import re
import math
import unicodedata
from pathlib import Path
from typing import Dict, Tuple, Optional
import datetime  # for feedback timestamps

import numpy as np
import pandas as pd
import streamlit as st

# =========================
# --------- THEME ---------
# =========================
st.set_page_config(
    page_title="Perfume Recommender",
    page_icon="🌸",
    layout="wide",
)

# Accessibility toggle in sidebar
accessibility_toggle = st.sidebar.checkbox(
    "Enable larger text / high readability mode",
    value=False,
    help="Increase font size for easier reading across the app.",
)

FLORAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --ink:#111111;
  --card:#ffffffcc;
  --stroke:rgba(216,107,165,0.18);
  --bg1:#fff;
  --bg2:#fff6fb;
}

html, body, .stApp, [class*="css"] {
  color: var(--ink) !important;
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%) !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
}

label, .stMarkdown, .st-emotion-cache, .stRadio, .stSlider label { color: var(--ink) !important; }
div[role="radiogroup"] * { color: var(--ink) !important; }
.stSlider span, .stSlider div, .stSlider label { color: var(--ink) !important; }

h1,h2,h3,h4 { font-family: "Playfair Display", Georgia, serif !important; color: var(--ink) !important; }
.block-container { padding-top: 1.0rem; }

.floral-hero {
  width: 100%;
  background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(255,255,255,0.98));
  border: 1px solid var(--stroke);
  border-radius: 28px;
  padding: 28px 36px;
  box-shadow: 0 10px 28px rgba(216,107,165,0.10);
  display: grid;
  grid-template-columns: 96px 1fr;
  align-items: center;
  gap: 20px;
}
.hero-icon {
  width: 96px; height: 96px; border-radius: 24px;
  background: #fff;
  border: 1px solid rgba(216,107,165,0.25);
  display:flex; align-items:center; justify-content:center; font-size:48px; color: var(--ink);
}
.hero-title { font-size: 42px; line-height: 1.05; margin: 0 0 6px; color: var(--ink) !important; }
.hero-sub { font-size: 16px; color:#222 !important; opacity: 0.9; }

.card {
  background: var(--card);
  border: 1px solid var(--stroke);
  border-radius: 16px;
  padding: 16px;
  height: 100%;
  box-shadow: 0 6px 18px rgba(216,107,165,0.08);
  transition: transform .18s ease, box-shadow .18s ease;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(216,107,165,0.12); }
.card-title { font-family: "Playfair Display", Georgia, serif; font-size: 20px; margin: 0; color: var(--ink) !important; }
.card-brand { font-size: 13px; color: #3a3540; margin-top: 2px; margin-bottom: 10px; }
.card-notes { font-size: 13px; color: #2b2730; opacity: 0.95; line-height: 1.45; }

.perfume-img {
  border-radius: 12px;
  border: 1px solid rgba(216,107,165,0.2);
  overflow: hidden;
  margin: 8px 0 10px;
}

.feedback-card {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid rgba(216,107,165,0.35);
  padding: 16px 18px 12px;
  box-shadow: 0 6px 18px rgba(216,107,165,0.10);
}

.stAlert {
  border-radius: 12px !important;
  border: 1px solid rgba(0, 140, 90, 0.4) !important;
  background: #f3fff7 !important;
  color: #10351f !important;
}

/* --- FIX: Submit Feedback button is ALWAYS red --- */
.button-submit-feedback button {
    background-color: #ffffff !important;
    color: #d42b2b !important;
    border: 2px solid #d42b2b !important;
    font-weight: 600 !important;
}
.button-submit-feedback button:hover {
    background-color: #ffeaea !important;
    color: #b80000 !important;
}

</style>
"""
st.markdown(FLORAL_CSS, unsafe_allow_html=True)

# Larger text override
if accessibility_toggle:
    LARGE_TEXT_CSS = """
    <style>
    html, body, .stApp { font-size: 18px !important; }
    .stMarkdown, .stText, .card-notes, .card-brand,
    label, .stRadio, .stSlider, .stSelectbox, .stTextInput {
        font-size: 1.08rem !important;
    }
    h1, h2, h3 { font-size: 1.45rem !important; }
    </style>
    """
    st.markdown(LARGE_TEXT_CSS, unsafe_allow_html=True)

# =========================
# ----- DATA HELPERS ------
# =========================

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    for p in [Path("clean_perfume_data.csv"), Path("data/clean_perfume_data.csv"), Path("perfumes.csv")]:
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:
                pass
    return pd.DataFrame([
        {
            "name": "Aqua Bloom",
            "brand": "Maison Florale",
            "notes": "citrus, bergamot, neroli, aquatic",
            "gender": "Unisex",
            "season": "Summer",
            "image_url": "https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?q=80&w=800&auto=format&fit=crop",
        }
    ])


def slugify(s: str) -> str:
    s = str(s or "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


SEASON_KEYWORDS = {
    "summer": ("citrus", "bergamot", "lemon", "lime", "orange", "grapefruit", "aquatic", "marine", "ozonic", "green"),
    "fall": ("amber", "vanilla", "spice", "spicy", "cinnamon", "cardamom", "nutmeg", "tonka", "incense"),
    "winter": ("oud", "tobacco", "smoke", "boozy", "rum", "myrrh", "gourmand", "musk", "patchouli"),
}

GENDER_KEYWORDS = {
    "female": ("for women", "pour femme", "woman", "women"),
    "male": ("for men", "pour homme", "man", "men", "homme"),
    "unisex": ("unisex", "shared", "for all"),
}


def score_season_from_notes(notes: str) -> Dict[str, float]:
    text = slugify(notes)
    scores = {s: sum(1 for kw in kws if kw in text) for s, kws in SEASON_KEYWORDS.items()}
    total = sum(scores.values())
    if total == 0:
        return {k: 1/3 for k in scores}
    return {k: v/total for k, v in scores.items()}


def infer_gender(row):
    if "gender" in row and pd.notna(row["gender"]):
        g = str(row["gender"]).strip().lower()
        if g in ["male", "m", "man", "men"]: return "male"
        if g in ["female", "f", "woman", "women"]: return "female"
        if g in ["unisex", "uni"]: return "unisex"
    text = " ".join(str(row.get(x, "")).lower() for x in ["name", "notes", "brand"])
    for g, kws in GENDER_KEYWORDS.items():
        if any(kw in text for kw in kws):
            return g
    return "unisex"


def get_rating(row):
    for c in ["rating", "score", "avg_rating"]:
        if c in row and pd.notna(row[c]):
            try: return float(row[c])
            except: pass
    return np.nan


def get_reviews(row):
    for c in ["reviews", "votes", "n_ratings"]:
        if c in row and pd.notna(row[c]):
            try: return float(row[c])
            except: pass
    return np.nan


def choose_season(row):
    if "season" in row and pd.notna(row["season"]):
        val = str(row["season"]).lower().strip()
        if val in ["summer", "fall", "winter"]:
            out = {"summer":0,"fall":0,"winter":0}
            out[val] = 1
            return out
    return score_season_from_notes(str(row.get("notes", "")))


def normalize_series(s: pd.Series):
    s = s.astype(float)
    mn, mx = np.nanmin(s.values), np.nanmax(s.values)
    if not np.isfinite(mn) or not np.isfinite(mx) or mx - mn == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - mn) / (mx - mn)


def pick_image_url(row):
    for c in ["image_url", "img_url", "image"]:
        if c in row and pd.notna(row[c]):
            u = str(row[c]).strip()
            if u.startswith("http"): return u
    return None


# =========================
# ---- DATA INGESTION -----
# =========================
df = load_data()
df.columns = [c.lower().strip() for c in df.columns]

if "notes" not in df.columns:
    df["notes"] = ""

df["gender_inferred"] = df.apply(infer_gender, axis=1)
season_scores = df.apply(choose_season, axis=1)
df[["score_summer","score_fall","score_winter"]] = pd.DataFrame(list(season_scores))
df["rating_val"] = df.apply(get_rating, axis=1)
df["reviews_val"] = df.apply(get_reviews, axis=1)
df["rating_norm"] = normalize_series(df["rating_val"].fillna(df["rating_val"].median()))
df["pop_norm"] = normalize_series(df["reviews_val"].fillna(df["reviews_val"].median()))

# =========================
# --------- HERO ----------
# =========================
st.markdown("""
<div class="floral-hero">
  <div class="hero-icon">🌸</div>
  <div>
    <div class="hero-title">Perfume Recommender</div>
    <div class="hero-sub">Pick a season & a gender — get beautifully curated suggestions, with full transparency.</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================
# ------ CONTROLS ---------
# =========================
c1, c2, c3 = st.columns([1.2, 1.2, 3.0])

with c1:
    season_choice = st.radio("Season", ["Summer","Fall","Winter"], horizontal=True)

with c2:
    gender_choice = st.radio("Gender", ["Female","Male","Unisex"], horizontal=True)

with c3:
    top_k = st.slider("How many recommendations?", 5, 24, 12, 1)

# Explanation
with st.expander("How are these recommendations calculated?"):
    st.markdown(
        r"""
        Scoring formula:
        \[
        \text{Score} = 0.45 S_{season} + 0.25 S_{gender} + 0.20 S_{rating} + 0.10 S_{popularity}
        \]
        """
    )

# =========================
# ---- RECOMMENDATIONS ----
# =========================
season_key = season_choice.lower()
season_col = {"summer":"score_summer","fall":"score_fall","winter":"score_winter"}[season_key]

def gender_match_score(g_inf: str, g_user: str):
    g_inf = g_inf.lower()
    g_user = g_user.lower()
    if g_inf == g_user: return 1
    if g_inf == "unisex" or g_user == "unisex": return 0.7
    return 0.35

g_scores = df["gender_inferred"].apply(lambda x: gender_match_score(x, gender_choice))
final_score = (
    0.45*df[season_col] +
    0.25*g_scores +
    0.20*df["rating_norm"] +
    0.10*df["pop_norm"]
)

df_rec = df.assign(_score=final_score).sort_values("_score", ascending=False)
results = df_rec.head(top_k).copy()

# =========================
# ------ RESULT GRID ------
# =========================
st.markdown("### ✨ Your curated picks")

if results.empty:
    st.info("No matches found.")
else:
    cols = st.columns(3, gap="large")
    for i, (_, row) in enumerate(results.iterrows()):
        with cols[i % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{row["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-brand">{row["brand"]}</div>', unsafe_allow_html=True)

            img = pick_image_url(row)
            if img:
                try: st.image(img, use_container_width=True)
                except: pass

            notes = str(row["notes"])
            if notes:
                txt = notes[:260] + ("…" if len(notes) > 260 else "")
                st.markdown(f'<div class="card-notes"><b>Notes:</b> {txt}</div>',
                            unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# =========================
# ------ FEEDBACK BLOCK ----
# =========================
st.markdown("---")
st.markdown("### 💬 Help us refine your recommendations")
st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
st.markdown("#### 🌟 Share quick feedback")

feedback_match = st.selectbox(
    "How well do these recommendations match your taste?",
    ["Select an option", "Very well", "Somewhat", "Not really"],
)

feedback_comment = st.text_input("Optional comment (for example, what you liked or did not like)")

# --- FIXED BUTTON (always red) ---
st.markdown("<div class='button-submit-feedback'>", unsafe_allow_html=True)
submitted = st.button("Submit feedback")
st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if feedback_match == "Select an option":
        st.warning("Please choose a feedback option before submitting.")
    else:
        try:
            entry = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "season_choice": season_choice,
                "gender_choice": gender_choice,
                "top_k": top_k,
                "match_level": feedback_match,
                "comment": feedback_comment,
            }
            fb_path = Path("feedback_log.csv")
            if fb_path.exists():
                old = pd.read_csv(fb_path)
                new = pd.concat([old, pd.DataFrame([entry])], ignore_index=True)
            else:
                new = pd.DataFrame([entry])
            new.to_csv(fb_path, index=False)
            st.success("Thank you! Your feedback was recorded.")
        except:
            st.warning("Feedback could not be saved.")

st.markdown("</div>", unsafe_allow_html=True)
