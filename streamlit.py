# app.py — Perfume Recommender (Season + Gender) — clean floral, with images
# Run: streamlit run app.py

import re
import math
import unicodedata
from pathlib import Path
from typing import Dict, Tuple, Optional

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

FLORAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

:root{
  --ink:#111111;            /* dark text for readability */
  --card:#ffffffcc;         /* slightly translucent white */
  --stroke:rgba(216,107,165,0.18);
  --bg1:#fff;               /* soft clean background */
  --bg2:#fff6fb;            /* hint of pink */
}

/* Force light UI + black text across themes */
html, body, .stApp, [class*="css"] {
  color: var(--ink) !important;
  background: linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%) !important;
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial;
}

/* Remove any dot wallpaper from previous version (none used now) */

/* Make radio/slider labels & ticks black and high-contrast */
label, .stMarkdown, .st-emotion-cache, .stRadio, .stSlider label { color: var(--ink) !important; }
div[role="radiogroup"] * { color: var(--ink) !important; }
.stSlider span, .stSlider div, .stSlider label { color: var(--ink) !important; }

/* Headings */
h1,h2,h3,h4 { font-family: "Playfair Display", Georgia, serif !important; color: var(--ink) !important; }
.block-container { padding-top: 1.0rem; }

/* Enlarged, full-width hero */
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

/* Cards (no top "bar", no badges) */
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

/* Perfume image styling */
.perfume-img {
  border-radius: 12px;
  border: 1px solid rgba(216,107,165,0.2);
  overflow: hidden;
  margin: 8px 0 10px;
}

/* Remove any unintended decorative bars above titles */
.card .decor, .decor { display:none !important; }
</style>
"""
st.markdown(FLORAL_CSS, unsafe_allow_html=True)

# =========================
# ----- DATA HELPERS ------
# =========================

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """
    Loads CSV from common paths; if absent, provides a tiny demo set.
    Expected (case-insensitive): name, brand, notes, rating, reviews, gender, season, url/image_url
    """
    for p in [Path("clean_perfume_data.csv"), Path("data/clean_perfume_data.csv"), Path("perfumes.csv")]:
        if p.exists():
            try:
                return pd.read_csv(p)
            except Exception:
                pass
    return pd.DataFrame([
        {"name":"Aqua Bloom", "brand":"Maison Florale", "notes":"citrus, bergamot, neroli, aquatic", "gender":"Unisex", "season":"Summer", "image_url":"https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?q=80&w=800&auto=format&fit=crop"},  # demo
        {"name":"Amber Veil", "brand":"Nocturne Atelier", "notes":"amber, vanilla, cinnamon, sandalwood", "gender":"Female", "season":"Fall", "image_url":"https://images.unsplash.com/photo-1590156223894-0b68d3c6a5d7?q=80&w=800&auto=format&fit=crop"},
        {"name":"Oud Ember", "brand":"Lune & Bois", "notes":"oud, tobacco, smoke, myrrh, patchouli", "gender":"Male", "season":"Winter", "image_url":"https://images.unsplash.com/photo-1563170351-be82bc888aa4?q=80&w=800&auto=format&fit=crop"},
    ])

def slugify(s: str) -> str:
    s = str(s or "")
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

SEASON_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "summer": ("citrus","bergamot","lemon","lime","orange","grapefruit","aquatic","marine","ozonic","green","mint","basil","neroli","aldehydic","fresh","tea"),
    "fall":   ("amber","vanilla","spice","spicy","cinnamon","cardamom","nutmeg","clove","tonka","resin","incense","woody","cedar","sandalwood","leather"),
    "winter": ("oud","tobacco","smoke","boozy","rum","whiskey","myrrh","labdanum","balsam","gourmand","chocolate","coffee","musk","patchouli"),
}
GENDER_KEYWORDS = {
    "female": ("for women","pour femme","woman","women"),
    "male":   ("for men","pour homme","man","men","homme"),
    "unisex": ("unisex","shared","for all"),
}

def score_season_from_notes(notes: str) -> Dict[str, float]:
    text = slugify(notes)
    scores = {s: sum(1 for kw in kws if kw in text) for s, kws in SEASON_KEYWORDS.items()}
    total = sum(scores.values())
    return ({k: 1/3 for k in scores} if total == 0 else {k: v/total for k, v in scores.items()})

def infer_gender(row: pd.Series) -> str:
    if "gender" in row and pd.notna(row["gender"]):
        g = str(row["gender"]).strip().lower()
        if g in ["male","m","man","men"]: return "male"
        if g in ["female","f","woman","women"]: return "female"
        if g in ["unisex","uni","shared"]: return "unisex"
    text = " ".join(str(row.get(k,"")) for k in ["name","notes","description","brand"]).lower()
    for g, kws in GENDER_KEYWORDS.items():
        if any(kw in text for kw in kws): return g
    return "unisex"

def get_rating(row: pd.Series) -> float:
    for col in ["rating","score","avg_rating","stars"]:
        if col in row and pd.notna(row[col]):
            try: return float(row[col])
            except: pass
    return np.nan

def get_reviews(row: pd.Series) -> float:
    for col in ["reviews","votes","n_ratings","num_reviews"]:
        if col in row and pd.notna(row[col]):
            try: return float(row[col])
            except: pass
    return np.nan

def choose_season(row: pd.Series) -> Dict[str, float]:
    if "season" in row and pd.notna(row["season"]):
        val = str(row["season"]).strip().lower()
        if val in ["summer","fall","autumn","winter"]:
            val = "fall" if val == "autumn" else val
            out = {"summer":0.0,"fall":0.0,"winter":0.0}; out[val]=1.0; return out
        tokens = re.split(r"[;/, ]+", val)
        valid = [("fall" if t=="autumn" else t) for t in tokens if t in ["summer","fall","winter"]]
        if valid:
            w = 1.0/len(valid); return {k:(w if k in valid else 0.0) for k in ["summer","fall","winter"]}
    return score_season_from_notes(str(row.get("notes","")))

def normalize_series(s: pd.Series) -> pd.Series:
    s = s.astype(float)
    m, M = np.nanmin(s.values), np.nanmax(s.values)
    if not np.isfinite(m) or not np.isfinite(M) or M - m == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - m) / (M - m)

def pick_image_url(row: pd.Series) -> Optional[str]:
    """
    Tries common image/url columns in order. Returns a URL or None.
    """
    cand_cols = ["image_url","img_url","image","img","photo","picture","thumbnail","url"]
    for c in cand_cols:
        if c in row and pd.notna(row[c]):
            u = str(row[c]).strip()
            if u.startswith("http"):
                return u
    return None

# =========================
# ---- DATA INGESTION -----
# =========================
df = load_data()
df.columns = [c.strip().lower() for c in df.columns]
if "notes" not in df.columns:
    df["notes"] = ""

df["gender_inferred"] = df.apply(infer_gender, axis=1)
season_scores = df.apply(choose_season, axis=1)
df[["score_summer","score_fall","score_winter"]] = pd.DataFrame(list(season_scores))
df["rating_val"] = df.apply(get_rating, axis=1)
df["reviews_val"] = df.apply(get_reviews, axis=1)
df["rating_norm"] = normalize_series(df["rating_val"].fillna(df["rating_val"].median()))
df["pop_norm"]    = normalize_series(df["reviews_val"].fillna(df["reviews_val"].median()))

# =========================
# --------- HERO ----------
# =========================
st.markdown(
    '''
    <div class="floral-hero">
      <div class="hero-icon">🌸</div>
      <div>
        <div class="hero-title">Perfume Recommender</div>
        <div class="hero-sub">Pick a season & a gender — get beautifully curated suggestions.</div>
      </div>
    </div>
    ''',
    unsafe_allow_html=True
)
st.write("")

# =========================
# ------ CONTROLS ---------
# =========================
c1, c2, c3 = st.columns([1.2, 1.2, 3.0])

with c1:
    season_choice = st.radio("Season", ["Summer", "Fall", "Winter"], horizontal=True, index=0)
with c2:
    gender_choice = st.radio("Gender", ["Female", "Male", "Unisex"], horizontal=True, index=0)
with c3:
    top_k = st.slider("How many recommendations?", min_value=5, max_value=24, value=12, step=1)

# =========================
# ---- RECOMMENDATION -----
# =========================
season_key = season_choice.lower()
season_col = {"summer":"score_summer","fall":"score_fall","winter":"score_winter"}[season_key]

def gender_match_score(g_inferred: str, user: str) -> float:
    g_inferred = (g_inferred or "").lower()
    user = user.lower()
    if g_inferred == user: return 1.0
    if g_inferred == "unisex" or user == "unisex": return 0.7
    return 0.35

g_scores = df["gender_inferred"].apply(lambda g: gender_match_score(g, gender_choice))
season_scores_vec = df[season_col].astype(float)

w_season, w_gender, w_rating, w_pop = 0.45, 0.25, 0.20, 0.10
final_score = (
    w_season * season_scores_vec +
    w_gender * g_scores +
    w_rating * df["rating_norm"].fillna(0.5) +
    w_pop    * df["pop_norm"].fillna(0.3)
)
df_rec = df.assign(_score=final_score).sort_values("_score", ascending=False)
results = df_rec.head(top_k).copy()

# =========================
# ------ RESULT GRID ------
# =========================
st.markdown("### ✨ Your curated picks")

if results.empty:
    st.info("No matches found. Try a different combination or provide a richer dataset.")
else:
    cols = st.columns(3, gap="large")
    for i, (_, row) in enumerate(results.iterrows()):
        with cols[i % 3]:
            name  = str(row.get("name", "Unknown")).strip()
            brand = str(row.get("brand", "—")).strip()
            notes = str(row.get("notes", "")).strip()
            img_u = pick_image_url(row)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            # Title & brand (no decorative bar, no badges)
            st.markdown(f'<div class="card-title">{name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-brand">{brand}</div>', unsafe_allow_html=True)

            # Image block
            if img_u:
                try:
                    st.image(img_u, use_container_width=True, output_format="auto")
                except Exception:
                    # image fetch failed → skip image
                    pass

            # Notes below image
            if notes:
                txt = notes[:260] + ("…" if len(notes) > 260 else "")
                st.markdown(f'<div class="card-notes"><b>Notes:</b> {txt}</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
