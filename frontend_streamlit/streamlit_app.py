from __future__ import annotations

import html
import io
import random
import struct
import textwrap
import wave
from typing import Any

import requests
import streamlit as st

st.set_page_config(
    page_title="Portfolio Livre Interactif",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_DEFAULT = "http://localhost:8000"


@st.cache_data(ttl=60)
def fetch_data(base_url: str, endpoint: str) -> Any:
    url = f"{base_url.rstrip('/')}{endpoint}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


def build_page_flip_audio() -> bytes:
    sample_rate = 16000
    duration_seconds = 0.32
    frame_count = int(sample_rate * duration_seconds)
    buf = io.BytesIO()

    with wave.open(buf, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(frame_count):
            envelope = 1.0 - (i / frame_count)
            noise = random.uniform(-1.0, 1.0)
            sample = int(7000 * envelope * noise)
            wav_file.writeframesraw(struct.pack("<h", sample))

    return buf.getvalue()


def inject_css() -> None:
    st.markdown(
        """
        <style>
            #MainMenu, header, footer {visibility: hidden;}
            section[data-testid="stSidebar"] {display: none !important;}
            .block-container {padding-top: 1rem; max-width: 1220px;}

            .book-wrap {
                perspective: 1800px;
                margin: 0.8rem auto 0;
                position: relative;
            }

            .book-open {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
                min-height: 690px;
                border-radius: 10px;
                overflow: hidden;
                box-shadow:
                    0 35px 60px rgba(35, 20, 10, 0.27),
                    0 6px 18px rgba(45, 25, 12, 0.18);
                transform: rotateX(2deg);
                animation: spreadIn 380ms ease;
                background: #ead5b1;
                border: 1px solid rgba(113, 78, 42, 0.45);
            }

            @keyframes spreadIn {
                from {transform: rotateX(2deg) scale(0.987); opacity: 0.85;}
                to {transform: rotateX(2deg) scale(1); opacity: 1;}
            }

            .leaf {
                background: #fdf6e3;
                padding: 2.2rem 2.1rem;
                min-height: 690px;
                line-height: 1.52;
                color: #3f2c1b;
                overflow: hidden;
                position: relative;
            }

            .leaf-left {
                border-right: 1px solid rgba(113, 78, 42, 0.22);
                box-shadow: inset -18px 0 24px -22px rgba(34, 21, 11, 0.35);
            }

            .leaf-right {
                box-shadow: inset 18px 0 24px -22px rgba(34, 21, 11, 0.35);
            }

            .spine {
                position: absolute;
                left: 50%;
                top: 0;
                width: 28px;
                height: 100%;
                transform: translateX(-50%);
                background: radial-gradient(circle, rgba(70,40,20,0.24) 0%, rgba(70,40,20,0.03) 70%);
                pointer-events: none;
            }

            .cover {
                background: linear-gradient(145deg, #1f2840, #2f1d13);
                color: #f8e7b8;
            }

            .cover h1, .cover h2 {
                color: #f2cf85;
                text-shadow: 0 1px 0 rgba(0,0,0,0.5);
                letter-spacing: 0.06em;
            }

            .page-title {
                margin: 0 0 1rem;
                font-size: 2rem;
                color: #4f3722;
            }

            .small-muted {color: #6e5233; font-size: 0.93rem;}
            .timeline-item {margin-bottom: 0.9rem; padding-left: 0.8rem; border-left: 3px solid #c89b5a;}
            .chip {display:inline-block; margin:0.16rem 0.25rem 0.16rem 0; padding:0.22rem 0.58rem; border-radius:18px; border:1px solid rgba(176,141,87,0.35); background:rgba(176,141,87,0.14); font-size:0.85rem;}
            .book-list {margin: 0; padding-left: 1.2rem;}
            .book-list li {margin-bottom: 0.45rem;}
            .project-card {margin-bottom: 0.8rem; padding: 0.7rem; border: 1px solid rgba(120,84,46,0.22); border-radius: 8px; background: rgba(255,252,245,0.65);}

            .st-key-book_prev,
            .st-key-book_next {
                margin-top: -690px;
                position: relative;
                z-index: 6;
            }

            .st-key-book_prev button,
            .st-key-book_next button {
                width: 100%;
                height: 690px;
                opacity: 0;
                border: none;
                box-shadow: none;
                background: transparent !important;
                cursor: pointer;
            }

            .st-key-book_prev button:hover,
            .st-key-book_next button:hover {
                opacity: 0.07;
                background: rgba(100, 60, 25, 0.28) !important;
            }

            .nav-hint {
                text-align: center;
                color: #6c5235;
                margin-top: 0.55rem;
                font-size: 0.95rem;
            }

            .sommaire-btns {margin-top: 0.8rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_types() -> list[str]:
    return [
        "cover_left",
        "cover_right",
        "sommaire",
        "projects",
        "experiences",
        "graph",
        "contact",
        "back_cover",
    ]


def spreads() -> list[tuple[str, str]]:
    pages = page_types()
    return [(pages[i], pages[i + 1]) for i in range(0, len(pages), 2)]


def set_spread(index: int) -> None:
    max_index = len(spreads()) - 1
    st.session_state.spread_index = max(0, min(index, max_index))
    st.session_state.play_flip_sound = True


def get_base_url() -> str:
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = API_DEFAULT

    left, right = st.columns([4, 1])
    with left:
        st.session_state.api_base_url = st.text_input(
            "URL API FastAPI",
            value=st.session_state.api_base_url,
            label_visibility="collapsed",
            placeholder="http://localhost:8000",
        )
    with right:
        if st.button("Tester API"):
            try:
                health = fetch_data(st.session_state.api_base_url, "/health")
                st.success(f"API OK · v{health.get('version', 'n/a')}")
            except Exception as exc:
                st.error(f"API KO: {exc}")

    return st.session_state.api_base_url


def load_all_data(base_url: str) -> dict[str, Any]:
    data: dict[str, Any] = {
        "global": {},
        "projects": [],
        "experiences": [],
        "skills": [],
        "technologies": [],
        "educations": [],
        "hobbies": [],
    }

    data["global"] = fetch_data(base_url, "/profile/global")
    data["projects"] = fetch_data(base_url, "/projects")
    data["experiences"] = fetch_data(base_url, "/experiences")
    data["skills"] = fetch_data(base_url, "/skills")
    data["technologies"] = fetch_data(base_url, "/technologies")
    data["educations"] = fetch_data(base_url, "/profile/education")
    data["hobbies"] = fetch_data(base_url, "/profile/hobbies")
    return data


def _safe_text(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return html.escape(text) if text else fallback


def _project_lines(projects: list[dict[str, Any]], limit: int = 4) -> str:
    blocks = []
    for item in projects[:limit]:
        title = _safe_text(item.get("nom"), "Projet")
        status = _safe_text(item.get("status"), "n/a")
        desc = _safe_text(item.get("description"), "")[:200]
        blocks.append(
            f"<div class='project-card'><strong>{title}</strong><br/><span class='small-muted'>{status}</span><br/>{desc}</div>"
        )
    return "".join(blocks) if blocks else "<p class='small-muted'>Aucun projet disponible.</p>"


def render_page(page_type: str, data: dict[str, Any]) -> str:
    global_data = data.get("global", {})
    infos = global_data.get("infos_personnels", [])
    person = infos[0] if infos else {}

    projects = data.get("projects", [])
    experiences = data.get("experiences", [])
    skills = data.get("skills", [])
    technologies = data.get("technologies", [])
    educations = data.get("educations", [])
    hobbies = data.get("hobbies", [])
    hobby_items = "".join(f"<li>{_safe_text(h.get('nom'), 'n/a')}</li>" for h in hobbies[:6]) or "<li>n/a</li>"

    full_name = _safe_text(f"{person.get('prenom', 'Portfolio')} {person.get('nom', '')}".strip(), "Portfolio")

    if page_type == "cover_left":
        return f"""
            <div class='leaf leaf-left cover'>
                <h1 style='font-size:2.65rem;margin:0;'>Le Livre</h1>
                <h1 style='font-size:2.65rem;margin:0.1rem 0 1rem;'>du Portfolio</h1>
                <h2 style='margin:0.5rem 0 0.4rem'>{full_name}</h2>
                <p style='max-width:460px'>
                    Journal interactif des projets, expériences et compétences
                    alimenté par FastAPI, MongoDB et Neo4j.
                </p>
                <p class='small-muted' style='margin-top:2.2rem;color:#ead3a1'>Clique à droite du livre pour ouvrir.</p>
            </div>
        """

    if page_type == "cover_right":
        mail = _safe_text(person.get("contact", {}).get("mail"), "n/a") if isinstance(person, dict) else "n/a"
        return f"""
            <div class='leaf leaf-right cover'>
                <h2 style='font-size:2rem;margin-top:0;'>Édition Data-Driven</h2>
                <p>Ce livre présente une lecture en double-page réaliste.</p>
                <ul class='book-list'>
                    <li>MongoDB pour les documents</li>
                    <li>Neo4j pour les relations</li>
                    <li>Streamlit pour l'expérience interactive</li>
                </ul>
                <p style='margin-top:2rem'>Contact principal: <strong>{mail}</strong></p>
            </div>
        """

    if page_type == "sommaire":
        return """
            <div class='leaf leaf-left'>
                <h2 class='page-title'>Sommaire</h2>
                <ol class='book-list'>
                    <li>Projets</li>
                    <li>Expériences & parcours</li>
                    <li>Graph intelligent</li>
                    <li>Contact & hobbies</li>
                </ol>
                <p class='small-muted'>Utilise les flèches du livre ou clique les boutons de section.</p>
            </div>
        """

    if page_type == "projects":
        return f"""
            <div class='leaf leaf-right'>
                <h2 class='page-title'>Projets</h2>
                {_project_lines(projects, limit=5)}
            </div>
        """

    if page_type == "experiences":
        timeline = ""
        for exp in experiences[:6]:
            timeline += (
                "<div class='timeline-item'>"
                f"<strong>{_safe_text(exp.get('nom'), 'Expérience')}</strong><br/>"
                f"{_safe_text(exp.get('company'), '')} — {_safe_text(exp.get('role'), '')}<br/>"
                f"<span class='small-muted'>{_safe_text(exp.get('date_debut'), 'n/a')} → {_safe_text(exp.get('date_fin'), 'n/a')}</span>"
                "</div>"
            )
        if not timeline:
            timeline = "<p class='small-muted'>Aucune expérience disponible.</p>"

        return f"""
            <div class='leaf leaf-left'>
                <h2 class='page-title'>Expériences</h2>
                {timeline}
            </div>
        """

    if page_type == "graph":
        skills_html = "".join(
            f"<span class='chip'>{_safe_text(s.get('nom'), 'n/a')}</span>" for s in skills[:20]
        ) or "<p class='small-muted'>Aucune compétence.</p>"
        tech_html = "".join(
            f"<span class='chip'>{_safe_text(t.get('nom'), 'n/a')}</span>" for t in technologies[:20]
        ) or "<p class='small-muted'>Aucune technologie.</p>"

        return f"""
            <div class='leaf leaf-right'>
                <h2 class='page-title'>Graph Intelligent</h2>
                <h4 style='margin-bottom:0.35rem'>Skills</h4>
                <div>{skills_html}</div>
                <h4 style='margin:1rem 0 0.35rem'>Technologies</h4>
                <div>{tech_html}</div>
                <p class='small-muted' style='margin-top:1rem'>Les liens projet↔skill sont exploités depuis Neo4j.</p>
            </div>
        """

    if page_type == "contact":
        contact = person.get("contact", {}) if isinstance(person, dict) else {}
        edu_items = "".join(
            f"<li>{_safe_text(e.get('school_name'), 'n/a')} · {_safe_text(e.get('degree'), 'n/a')}</li>" for e in educations[:4]
        ) or "<li>n/a</li>"

        return f"""
            <div class='leaf leaf-left'>
                <h2 class='page-title'>Contact</h2>
                <ul class='book-list'>
                    <li><strong>Mail:</strong> {_safe_text(contact.get('mail'), 'n/a')}</li>
                    <li><strong>Téléphone:</strong> {_safe_text(contact.get('tel'), 'n/a')}</li>
                    <li><strong>LinkedIn:</strong> {_safe_text(contact.get('linkedin'), 'n/a')}</li>
                </ul>
                <h4>Parcours</h4>
                <ul class='book-list'>{edu_items}</ul>
            </div>
        """

    if page_type == "back_cover":
        return f"""
            <div class='leaf leaf-right cover'>
                <h2 style='margin-top:0'>Fin du chapitre</h2>
                <p>Merci pour la lecture.</p>
                <h4>Hobbies</h4>
                <ul class='book-list'>{hobby_items}</ul>
                <p class='small-muted' style='margin-top:2rem;color:#ead3a1'>Clique à gauche pour revenir en arrière.</p>
            </div>
        """

    return "<div class='leaf leaf-right'><p>Page vide.</p></div>"


def render_book(spread_index: int, data: dict[str, Any]) -> None:
    left_page, right_page = spreads()[spread_index]
    left_html = textwrap.dedent(render_page(left_page, data)).strip()
    right_html = textwrap.dedent(render_page(right_page, data)).strip()

    st.markdown(
        textwrap.dedent(
            f"""
        <div class='book-wrap'>
            <div class='book-open'>
                {left_html}
                {right_html}
            </div>
            <div class='spine'></div>
        </div>
        """
        ).strip(),
        unsafe_allow_html=True,
    )


def render_book_click_zones(spread_index: int) -> None:
    total = len(spreads())
    left, right = st.columns(2, gap="small")
    with left:
        if st.button("", key="book_prev", disabled=spread_index <= 0):
            set_spread(spread_index - 1)
            st.rerun()
    with right:
        if st.button("", key="book_next", disabled=spread_index >= total - 1):
            set_spread(spread_index + 1)
            st.rerun()


def render_extra_controls(spread_index: int) -> None:
    st.markdown(
        f"<div class='nav-hint'>Spread {spread_index + 1} / {len(spreads())} · Clique la page gauche/droite pour tourner</div>",
        unsafe_allow_html=True,
    )

    if spread_index == 1:
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("Section Projets"):
            set_spread(1)
            st.rerun()
        if c2.button("Section Expériences"):
            set_spread(2)
            st.rerun()
        if c3.button("Section Graphe"):
            set_spread(2)
            st.rerun()
        if c4.button("Section Contact"):
            set_spread(3)
            st.rerun()

    if spread_index == 2:
        skills = st.session_state.get("cached_data", {}).get("skills", [])
        skill_names = [s.get("nom") for s in skills if s.get("nom")]
        if skill_names:
            selected = st.selectbox("Explorer Skill → Projets", sorted(skill_names), key="skill_lookup")
            try:
                related = fetch_data(st.session_state.api_base_url, f"/skills/{selected}/projects")
                if related:
                    st.caption("Projets liés")
                    for project in related:
                        st.markdown(f"- **{project.get('nom', 'Projet')}**")
                else:
                    st.warning("Aucun projet lié pour cette compétence.")
            except Exception as exc:
                st.error(f"Erreur Neo4j/Mongo: {exc}")


def play_flip_sound_if_needed() -> None:
    if st.session_state.get("play_flip_sound", False):
        audio_bytes = build_page_flip_audio()
        try:
            st.audio(audio_bytes, format="audio/wav", autoplay=True)
        except TypeError:
            st.audio(audio_bytes, format="audio/wav")
        st.session_state.play_flip_sound = False


def main() -> None:
    if "spread_index" not in st.session_state:
        st.session_state.spread_index = 0
    if "play_flip_sound" not in st.session_state:
        st.session_state.play_flip_sound = False

    inject_css()
    st.title("📖 Portfolio — Livre Interactif")
    base_url = get_base_url()

    try:
        data = load_all_data(base_url)
        st.session_state.cached_data = data
    except requests.RequestException as exc:
        st.error(f"Connexion API impossible: {exc}")
        st.info("Lance l'API FastAPI puis recharge la page.")
        return
    except Exception as exc:
        st.error(f"Erreur chargement des données: {exc}")
        return

    spread_index = st.session_state.spread_index
    render_book(spread_index, data)
    render_book_click_zones(spread_index)
    render_extra_controls(spread_index)
    play_flip_sound_if_needed()


if __name__ == "__main__":
    main()
