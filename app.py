"""Extra Point team generator. Keep this file and all images in one folder.

Run: streamlit run app.py
Uses Streamlit's native placeholders and progress animation, plus CSS.
"""

import base64
import io
import random
import time
from html import escape
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError


st.set_page_config(page_title="The Extra Point Podcast", page_icon="🏈", layout="wide")
APP_FOLDER = Path(__file__).resolve().parent

# Change these to adjust the raffle. Timing includes preparation and frame updates.
SHUFFLE_SECONDS = 4.0
SHUFFLE_FRAMES = 28

# Your PNGs stay beside app.py. No badges folder is required.
teams = [
    # NFC Teams
    {"name": "Dallas Cowboys", "logo": "dal.png"},
    {"name": "Arizona Cardinals", "logo": "ari.png"},
    {"name": "Atlanta Falcons", "logo": "atl.png"},
    {"name": "Carolina Panthers", "logo": "car.png"},
    {"name": "Chicago Bears", "logo": "chi.png"},
    {"name": "Detroit Lions", "logo": "det.png"},
    {"name": "Green Bay Packers", "logo": "gb.png"},
    {"name": "Los Angeles Rams", "logo": "lar.png"},
    {"name": "Minnesota Vikings", "logo": "min.png"},
    {"name": "New Orleans Saints", "logo": "no.png"},
    {"name": "New York Giants", "logo": "nyg.png"},
    {"name": "Philadelphia Eagles", "logo": "phi.png"},
    {"name": "San Francisco 49ers", "logo": "sf.png"},
    {"name": "Seattle Seahawks", "logo": "sea.png"},
    {"name": "Tampa Bay Buccaneers", "logo": "tb.png"},
    {"name": "Washington Commanders", "logo": "was.png"},
    # AFC Teams
    {"name": "Baltimore Ravens", "logo": "bal.png"},
    {"name": "Buffalo Bills", "logo": "buf.png"},
    {"name": "Cincinnati Bengals", "logo": "cin.png"},
    {"name": "Cleveland Browns", "logo": "cle.png"},
    {"name": "Denver Broncos", "logo": "den.png"},
    {"name": "Houston Texans", "logo": "hou.png"},
    {"name": "Indianapolis Colts", "logo": "ind.png"},
    {"name": "Jacksonville Jaguars", "logo": "jax.png"},
    {"name": "Kansas City Chiefs", "logo": "kc.png"},
    {"name": "Las Vegas Raiders", "logo": "lv.png"},
    {"name": "Los Angeles Chargers", "logo": "lac.png"},
    {"name": "Miami Dolphins", "logo": "mia.png"},
    {"name": "New England Patriots", "logo": "ne.png"},
    {"name": "New York Jets", "logo": "nyj.png"},
    {"name": "Pittsburgh Steelers", "logo": "pit.png"},
    {"name": "Tennessee Titans", "logo": "ten.png"},
]

for index, team in enumerate(teams):
    team["conference"] = "NFC" if index < 16 else "AFC"
    team["abbreviation"] = Path(team["logo"]).stem.upper()


@st.cache_data(show_spinner=False)
def read_image(filename, modified_ns):
    """Cache valid image bytes; changing the file invalidates the cache."""
    try:
        data = (APP_FOLDER / filename).read_bytes()
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        return data
    except (OSError, ValueError, UnidentifiedImageError):
        return None


def image_bytes(filename):
    try:
        modified_ns = (APP_FOLDER / filename).stat().st_mtime_ns
    except OSError:
        return None
    return read_image(filename, modified_ns)


@st.cache_data(show_spinner=False)
def badge_data_uri(filename, modified_ns):
    """Make a small in-memory display copy; original PNGs are never changed."""
    data = read_image(filename, modified_ns)
    if data is None:
        return None
    try:
        with Image.open(io.BytesIO(data)) as source:
            image = source.convert("RGBA")
            image.thumbnail((448, 448), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
    except (OSError, ValueError):
        return None


def badge_source(filename):
    try:
        modified_ns = (APP_FOLDER / filename).stat().st_mtime_ns
    except OSError:
        return None
    return badge_data_uri(filename, modified_ns)


def reset_picks():
    st.session_state.ep_selected = None
    st.session_state.ep_history = []
    st.session_state.ep_used = set()
    st.session_state.ep_pick_count = 0
    st.session_state.ep_draw_requested = False


def request_draw():
    # Only the Generate Team button calls this callback.
    st.session_state.ep_draw_requested = True


if "ep_selected" not in st.session_state:
    reset_picks()
for key, value in {
    "ep_draw_requested": False,
    "ep_conference": "All teams",
    "ep_no_repeats": True,
    "ep_animate": True,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Consume this one-shot request before rendering or animating anything.
# A normal widget rerun or browser rerun cannot replay the previous draw.
draw_requested = st.session_state.ep_draw_requested
st.session_state.ep_draw_requested = False

st.html("""
<style>
/* Podcast palette. These styles also keep the app readable in dark mode. */
.stApp {background: #f4f6fc; color: #101b35;}
[data-testid="stHeader"] {background: rgba(244,246,252,.94);}
.stMainBlockContainer {max-width: 1120px; padding-top: 4.5rem; padding-bottom: 1.5rem;}
.st-key-ep_brand [data-testid="stImage"] {margin:0 auto; width:100%; max-width:950px;}
/* Fill a shallow banner by cropping excess blue space, without stretching the artwork. */
.st-key-ep_brand img {width:100%; height:clamp(125px,21vw,250px);
    max-height:none; object-fit:cover; object-position:center 40%;
    border:0; border-radius:0; box-shadow:none;}
.st-key-ep_brand [data-testid="stCaptionContainer"] p {
    font-size: .72rem; line-height: 1.35; color: #64718b;
}
.ep-heading {text-align:center; margin: 0 0 4px;}
.ep-heading h1 {font-size:clamp(1.8rem,4vw,2.5rem); font-weight:850;
    letter-spacing:-1.3px; color:#101b35; margin:0; padding:0;}
.ep-brand-fallback {text-align:center; padding:4px 0 10px;}
.ep-brand-fallback strong {color:#e23c45; font-size:1.6rem; letter-spacing:3px;}
.ep-brand-fallback span {display:block; color:#2455c7; font-size:.68rem;
    font-weight:800; letter-spacing:5px;}
.st-key-ep_stage {position:relative; overflow:hidden; min-height:432px;
    border-radius:26px; padding:23px 18px 19px;
    border:1px solid #2a3d67;
    background:radial-gradient(ellipse at 50% 35%,#183773 0%,#0d1935 57%,#091225 100%);
    box-shadow:0 18px 45px rgba(19,42,89,.15);}
.st-key-ep_stage:before {content:""; position:absolute; top:0; left:14%;
    width:72%; height:3px; background:linear-gradient(90deg,#2455c7,#6f9aff,#e23c45);}
.ep-status {text-align:center; color:#a9bee7; font-size:.69rem;
    font-weight:800; letter-spacing:3px; margin:0;}
.ep-status .ep-dot {display:inline-block; width:7px; height:7px;
    background:#e23c45; border-radius:50%; margin-right:7px;}
.ep-status.is-shuffling .ep-dot {animation:ep-blink .55s infinite alternate;}
.ep-stage-name {text-align:center; color:white; font-size:clamp(1.4rem,3vw,1.9rem);
    line-height:1.2; font-weight:850; letter-spacing:-.5px;
    margin:0; min-height:2.35rem;}
.ep-stage-meta {text-align:center; color:#adbfde; font-size:.8rem;
    margin:0; min-height:1.3rem;}
.ep-idle {width:230px;height:230px;display:flex;align-items:center;
    justify-content:center;position:relative;margin:0 auto;}
.ep-idle:before {content:"";position:absolute;inset:20px;border-radius:50%;
    border:1px dashed #476baf;animation:ep-orbit 35s linear infinite;}
.ep-idle:after {content:"";position:absolute;inset:36px;border-radius:50%;
    border:1px solid #304a79;}
.ep-idle span {font-size:94px;font-weight:850;color:#eef4ff;
    text-shadow:0 0 35px rgba(87,139,255,.45);}
.ep-fallback {height:230px;display:flex;align-items:center;justify-content:center;
    font-size:70px;font-weight:850;color:white;letter-spacing:3px;}
.st-key-ep_controls {padding:13px 5px 0;}
.st-key-ep_controls [data-testid="stMarkdownContainer"] p {color:#1c2d4e;}
.st-key-ep_controls [data-testid="stWidgetLabel"] p {font-weight:650;}
.st-key-ep_controls [role="radiogroup"] {gap:1rem;}
.ep-eyebrow {font-size:1rem;letter-spacing:2.5px;font-weight:850;
    color:#2455c7;margin-bottom:8px;}
.ep-stats {display:flex;gap:0; margin:9px 0 11px;padding:13px 0;
    border-top:1px solid #dce3f1;border-bottom:1px solid #dce3f1;}
.ep-stat {flex:1; border-right:1px solid #dce3f1; padding-left:18px;}
.ep-stat:first-child {padding-left:0;}
.ep-stat:last-child {border:0;}
.ep-stat strong {display:block;font-size:1.5rem;line-height:1.1;color:#12213e;}
.ep-stat span {color:#69768e;font-size:.68rem;letter-spacing:.5px;}
.st-key-ep_generate button {background:#2455c7;border:0;border-radius:13px;
    min-height:52px;box-shadow:0 7px 20px #2455c72b;transition:transform .2s,background .2s;}
.st-key-ep_generate button p {color:white!important;font-size:1rem;font-weight:800;}
.st-key-ep_generate button:hover:not(:disabled) {background:#1944b0;transform:translateY(-2px);}
.st-key-ep_generate button:disabled {opacity:.55;}
.st-key-ep_reset button {border-radius:11px;background:white;color:#30466b;
    border:1px solid #d6dfef;min-height:40px;}
.st-key-ep_reset button p {color:#30466b!important;}
.ep-history-label {margin:15px 0 7px;font-size:.65rem;font-weight:800;
    color:#7b879d;letter-spacing:1.6px;}
.ep-history {display:flex;flex-wrap:wrap;gap:6px;}
.ep-chip {background:#e7ecf7;color:#354b71;border-radius:7px;
    padding:5px 9px;font-size:.72rem;}
.ep-chip.newest {background:#dce7ff;color:#204fae;}
@keyframes ep-orbit {to {transform:rotate(360deg);}}
@keyframes ep-blink {to {opacity:.2;}}
@media(max-width:640px) {
    .stMainBlockContainer {padding-top:4.5rem;padding-left:1rem;padding-right:1rem;}
    .st-key-ep_stage {min-height:405px;}
}
@media(prefers-reduced-motion:reduce) {
    .ep-idle:before,.ep-dot,.st-key-ep_stage,.st-key-ep_stage img {
        animation:none!important;transition:none!important;}
}

/* The same card markup is used for every frame and for the final result. */
.ep-stage-body {display:flex;flex-direction:column;align-items:center;gap:12px;}
.ep-stage-media {height:224px;width:224px;display:flex;align-items:center;justify-content:center;}
.ep-stage-media img {display:block;width:224px;height:224px;object-fit:contain;}
.ep-stage-name {display:flex;align-items:center;justify-content:center;
    width:100%;height:58px;font-size:clamp(1.35rem,2.2vw,1.85rem);}
.ep-stage-meta {height:20px;line-height:20px;}
.ep-track {height:3px;width:78%;background:#21375e;border-radius:2px;overflow:hidden;}
.ep-track span {display:block;height:100%;background:#6f9aff;}
.ep-track.is-idle {visibility:hidden;}
.ep-status.is-final .ep-dot {background:#6f9aff;}
</style>
""")

logo = image_bytes("extra_point_logo.jpg")
if logo:
    st.logo(logo)

with st.container(key="ep_brand", horizontal_alignment="center"):
    banner = image_bytes("title.png")
    if banner:
        st.image(banner, width="stretch")
    else:
        st.html('<div class="ep-brand-fallback"><strong>EXTRA POINT</strong>'
                '<span>THE FOOTBALL PODCAST</span></div>')
    st.caption(
        "Independent football podcast. Not affiliated with, sponsored by, "
        "or endorsed by the NFL or any NFL team.", text_alignment="center"
    )

st.html('<div class="ep-heading"><h1>Random Team Generator</h1></div>')

def team_pool():
    return [t for t in teams if st.session_state.ep_conference == "All teams"
            or t["conference"] == st.session_state.ep_conference]


def available_teams(pool):
    return [t for t in pool if not st.session_state.ep_no_repeats
            or t["name"] not in st.session_state.ep_used]


def show_team(slot, team=None, progress=None):
    """Replace image, name and status together with one complete card update."""
    shuffling = progress is not None
    if team is None:
        status, status_class = "READY FOR KICKOFF", ""
        artwork = '<div class="ep-idle"><span>?</span></div>'
        name, detail = "Who’s up next?", "Your next talking point is one click away."
    else:
        status = "SHUFFLING THE FIELD" if shuffling else "THE PICK IS IN"
        status_class = "is-shuffling" if shuffling else "is-final"
        source = badge_source(team["logo"])
        artwork = (
            f'<img src="{source}" alt="{escape(team["name"], quote=True)} badge">'
            if source else f'<div class="ep-fallback">{escape(team["abbreviation"])}</div>'
        )
        name = team["name"]
        detail = f'{team["conference"]} · ' + (
            "Finding your next pick…" if shuffling else "Your latest pick"
        )
    track_class = "" if shuffling else " is-idle"
    percent = int(100 * progress) if shuffling else 0
    slot.html(
        '<div class="ep-stage-body">'
        f'<div class="ep-status {status_class}"><span class="ep-dot"></span>{status}</div>'
        f'<div class="ep-stage-media">{artwork}</div>'
        f'<div class="ep-stage-name">{escape(name)}</div>'
        f'<div class="ep-stage-meta">{escape(detail)}</div>'
        f'<div class="ep-track{track_class}" aria-hidden="true"><span style="width:{percent}%"></span></div>'
        '</div>'
    )


def render_controls(slot):
    # Render the normal controls once; they stay in place throughout the raffle.
    with slot.container():
        st.html('<div class="ep-eyebrow">SET THE FIELD</div>')
        st.radio("Team pool", ["All teams", "NFC", "AFC"], horizontal=True, key="ep_conference")
        st.toggle(
            "No repeats", key="ep_no_repeats",
            help="Skip teams already picked in this session. Reset picks starts a fresh round.",
        )
        st.toggle(
            "Raffle animation", key="ep_animate",
            help="A slowing shuffle before the final team. Turn off for an instant pick.",
        )
        pool = team_pool()
        eligible = available_teams(pool)
        st.html(
            '<div class="ep-stats">'
            f'<div class="ep-stat"><strong>{len(pool)}</strong><span>IN THE POOL</span></div>'
            f'<div class="ep-stat"><strong>{len(eligible)}</strong><span>AVAILABLE</span></div>'
            f'<div class="ep-stat"><strong>{st.session_state.ep_pick_count}</strong><span>PICKS MADE</span></div>'
            '</div>'
        )
        with st.container(key="ep_generate"):
            st.button(
                "Generate Team", key="ep_spin_button", type="primary", width="stretch",
                disabled=not eligible, on_click=request_draw,
            )
        with st.container(key="ep_reset"):
            st.button(
                "Reset picks", key="ep_reset_button", width="stretch", on_click=reset_picks,
                disabled=st.session_state.ep_pick_count == 0,
            )
        if not eligible:
            st.info("Every team in this pool has been picked. Reset picks, change the pool, or turn off No repeats.")
        history_slot = st.empty()
    return history_slot


def show_history(slot, history):
    if not history:
        slot.empty()
        return
    recent = list(reversed(history[-4:]))
    chips = "".join(
        f'<span class="ep-chip{" newest" if i == 0 else ""}">{escape(t["name"])}</span>'
        for i, t in enumerate(recent)
    )
    slot.html('<div class="ep-history-label">RECENT PICKS · NEWEST FIRST</div>'
              f'<div class="ep-history">{chips}</div>')


stage_column, control_column = st.columns([1.18, 1], gap="large")
with stage_column:
    with st.container(key="ep_stage"):
        stage_slot = st.empty()
with control_column:
    with st.container(key="ep_controls", gap="small"):
        controls_slot = st.empty()

pool = team_pool()
eligible = available_teams(pool)

previous_history = list(st.session_state.ep_history)
previous_team = st.session_state.ep_selected
winner = None
if draw_requested and eligible:
    shuffle_started = time.monotonic()
    # Store one result per explicit click. A settings rerun never replays the draw.
    winner = random.choice(eligible)
    st.session_state.ep_selected = winner.copy()
    st.session_state.ep_used.add(winner["name"])
    st.session_state.ep_history = (previous_history + [winner.copy()])[-50:]
    st.session_state.ep_pick_count += 1

# Keep the actual settings and buttons on screen, including during the shuffle.
# Counters and button availability already reflect the draw, but history waits
# until the reveal so it cannot give the winning team away early.
history_slot = render_controls(controls_slot)
show_history(history_slot, previous_history)
show_team(stage_slot, previous_team)

if winner is not None and st.session_state.ep_animate and len(eligible) > 1:
    frame_count = max(2, int(SHUFFLE_FRAMES))
    previous = None
    previews = []
    for frame in range(frame_count - 1):
        choices = [t for t in eligible if t["name"] != previous]
        preview = random.choice(choices)
        previews.append(preview)
        previous = preview["name"]
    # Prepare lightweight embedded images before the first animation frame.
    for team in previews + [winner]:
        badge_source(team["logo"])
    weights = [1 + 5 * (i / max(1, frame_count - 2)) ** 2
               for i in range(frame_count - 1)]
    total_weight = sum(weights)
    elapsed_weight = 0.0
    for frame, (preview, weight) in enumerate(zip(previews, weights)):
        show_team(stage_slot, preview, progress=(frame + 1) / frame_count)
        elapsed_weight += weight
        deadline = shuffle_started + max(0.0, SHUFFLE_SECONDS) * elapsed_weight / total_weight
        time.sleep(max(0.0, deadline - time.monotonic()))

# Publish the winner ONCE. Its image stays mounted after this call.
# No automatic rerun, clearing of image placeholders, or second final render.
if winner is not None:
    show_team(stage_slot, winner)
show_history(history_slot, st.session_state.ep_history)

missing_badges = [t["logo"] for t in teams if image_bytes(t["logo"]) is None]
if missing_badges:
    with st.expander(f"Image setup: {len(missing_badges)} files to check"):
        st.write("Put these PNGs beside app.py. Initials appear until the images are available.")
        st.code(", ".join(missing_badges), language=None)



