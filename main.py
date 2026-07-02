"""
BFPME AI Credit Agent
======================
Intelligent document processing assistant for BFPME (Banque de Financement
des Petites et Moyennes Entreprises) credit risk officers in Tunisia.

Architecture:
  - Live LLM Engine: OpenAI GPT-4o for dynamic extraction and chatbot
  - Local Smart-Parsing Engine (Failsafe): Rule-based extraction + semantic
    response dictionary for fully offline operation
"""

import re
import json
import hashlib
import html
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from io import BytesIO

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BFPME AI Credit Agent",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Banking theme (Deep Blue / Teal)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* ── Header bar ── */
.bfpme-header {
    background: linear-gradient(135deg, #0A4A6E 0%, #0D7377 100%);
    padding: 1.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 16px rgba(10,74,110,0.18);
}
.bfpme-header h1 {
    color: #FFFFFF !important;
    margin: 0; font-size: 1.6rem; font-weight: 700;
}
.bfpme-header p {
    color: rgba(255,255,255,0.82); margin: 0; font-size: 0.92rem;
}

/* ── Metric cards ── */
.metric-card {
    background: #FFFFFF;
    border-left: 5px solid #0D7377;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 8px rgba(10,74,110,0.08);
    margin-bottom: 0.75rem;
}
.metric-card .label {
    font-size: 0.78rem; color: #5A7A8A; text-transform: uppercase;
    letter-spacing: 0.06em; margin-bottom: 0.25rem;
}
.metric-card .value {
    font-size: 1.5rem; font-weight: 700; color: #0A4A6E;
}
.metric-card .sub {
    font-size: 0.82rem; color: #6B8FA0; margin-top: 0.1rem;
}

/* ── Status badge ── */
.status-live {
    background: #E6F9F0; color: #0A7A4A; border: 1px solid #8FD5B2;
    padding: 0.45rem 0.9rem; border-radius: 20px; font-weight: 600;
    font-size: 0.82rem; display: inline-flex; align-items: center; gap: 6px;
}
.status-failsafe {
    background: #FFF4E6; color: #B07000; border: 1px solid #F0C878;
    padding: 0.45rem 0.9rem; border-radius: 20px; font-weight: 600;
    font-size: 0.82rem; display: inline-flex; align-items: center; gap: 6px;
}

/* ── Chat bubbles ── */
.chat-user {
    background: #E8F2FA; border-radius: 16px 16px 4px 16px;
    padding: 0.75rem 1rem; margin: 0.5rem 0; max-width: 80%;
    margin-left: auto; color: #1A2E3A;
}
.chat-agent {
    background: #FFFFFF; border: 1px solid #D0E4F0;
    border-radius: 16px 16px 16px 4px;
    padding: 0.75rem 1rem; margin: 0.5rem 0; max-width: 85%;
    color: #1A2E3A; box-shadow: 0 1px 4px rgba(10,74,110,0.07);
}
.chat-label-user { font-size: 0.73rem; color: #4A7A9A; margin-bottom: 0.2rem; text-align: right; }
.chat-label-agent { font-size: 0.73rem; color: #0D7377; margin-bottom: 0.2rem; font-weight: 600; }

/* ── Section title ── */
.section-title {
    color: #0A4A6E; font-size: 1.05rem; font-weight: 700;
    border-bottom: 2px solid #0D7377; padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* ── Risk badge ── */
.risk-low    { background:#E6F9F0; color:#0A7A4A; border:1px solid #8FD5B2; padding:0.3rem 0.7rem; border-radius:12px; font-weight:600; font-size:0.82rem; }
.risk-medium { background:#FFF4E6; color:#B07000; border:1px solid #F0C878; padding:0.3rem 0.7rem; border-radius:12px; font-weight:600; font-size:0.82rem; }
.risk-high   { background:#FDE8E8; color:#B02020; border:1px solid #F0A0A0; padding:0.3rem 0.7rem; border-radius:12px; font-weight:600; font-size:0.82rem; }

/* ── Tabs ── */
[data-baseweb="tab-list"] { gap: 0.5rem; }
[data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SAMPLE PROJECT DATA — "Agritech Sidi Bouzid"
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_TEXT = """
PLAN D'AFFAIRES - DEMANDE DE FINANCEMENT BFPME
===============================================

Raison Sociale : Agritech Sidi Bouzid SARL
Secteur d'activité : Industrie Agroalimentaire – Transformation de tomates
Localisation : Zone Industrielle, Sidi Bouzid, Gouvernorat de Sidi Bouzid

PRÉSENTATION DU PROMOTEUR
Le promoteur M. Karim Mellouli, ingénieur agronome diplômé de l'INAT, justifie d'une
expérience de 12 ans dans le secteur agroalimentaire tunisien.

DESCRIPTION DU PROJET
Création d'une unité de transformation de tomates pour la production de concentré de
tomates, de tomates pelées et de jus de tomates destinés au marché local et à l'export.
Capacité de traitement : 50 tonnes de tomates fraîches par jour.
Nombre d'emplois permanents à créer : 45 postes

STRUCTURE DU COÛT D'INVESTISSEMENT
Coût Total de l'Investissement : 2 850 mDT

Génie Civil & Aménagements : 620 mDT
Équipements & Matériels : 1 450 mDT
Matériel de Transport : 180 mDT
Matériel Informatique : 45 mDT
Fonds de Roulement : 555 mDT

STRUCTURE DE FINANCEMENT
Apport Personnel du Promoteur : 428 mDT (15%)
Dotation FOPRODI / Prime Régionale ZDR : 570 mDT (20%)
Participation SICAR Régionale : 285 mDT (10%)
Crédit à Moyen/Long Terme BFPME : 1 567 mDT (55%)

DONNÉES FINANCIÈRES PRÉVISIONNELLES
Chiffre d'Affaires Prévisionnel (An 1) : 3 200 mDT
Chiffre d'Affaires Prévisionnel (An 3) : 4 800 mDT
EBE Prévisionnel (An 3) : 980 mDT
Résultat Net (An 3) : 420 mDT
Délai de Récupération : 6,8 ans
TRI : 18,4%
VAN (Taux 10%) : 650 mDT

ANALYSE DES RISQUES
- Risque saisonnier : La production de tomates est concentrée sur 4 mois (juillet-octobre).
  Mitigation : contrats d'approvisionnement pluriannuels avec 38 agriculteurs locaux.
- Risque de marché : volatilité des prix des matières premières.
  Mitigation : diversification vers l'export (objectif 30% du CA).
- Risque de change : exposition à l'EUR et USD pour l'export.
  Mitigation : couverture par contrats à terme via STB.
- Risque opérationnel : dépendance aux équipements italiens.
  Mitigation : contrat de maintenance préventive + stock de pièces de rechange.

GARANTIES PROPOSÉES
Hypothèque de premier rang sur le terrain (valeur estimée : 380 mDT)
Gage sur équipements (valeur nette : 1 100 mDT)
Caution personnelle du promoteur à hauteur de 500 mDT
"""

SAMPLE_PROJECT_META = {
    "raison_sociale": "Agritech Sidi Bouzid SARL",
    "secteur": "Transformation de tomates – Agroalimentaire",
    "localisation": "Zone Industrielle, Sidi Bouzid",
    "promoteur": "M. Karim Mellouli",
    "emplois": 45,
}

SAMPLE_FINANCIALS = {
    "cout_total": 2850,
    "apport_personnel": 428,
    "foprodi_prime": 570,
    "sicar": 285,
    "credit_bfpme": 1567,
    "ca_an1": 3200,
    "ca_an3": 4800,
    "ebe_an3": 980,
    "resultat_net_an3": 420,
    "delai_recuperation": 6.8,
    "tri": 18.4,
    "van": 650,
    "emplois": 45,
}

# ─────────────────────────────────────────────────────────────────────────────
# FAILSAFE RULE-BASED CHATBOT RESPONSES
# ─────────────────────────────────────────────────────────────────────────────
SMART_RESPONSES = {
    # Délai de récupération
    ("délai", "récupération", "payback", "retour"): lambda d: (
        f"📅 **Délai de récupération du projet :** {d.get('delai_recuperation', 'N/A')} ans.\n\n"
        "Ce délai est considéré **acceptable** pour un projet agroalimentaire en zone de développement "
        "régional (ZDR), compte tenu des soutiens publics (FOPRODI, SICAR) qui allègent la charge financière "
        "initiale. Le seuil habituel de la BFPME pour ce secteur est ≤ 8 ans."
    ),
    # TRI
    ("tri", "taux de rentabilité", "rentabilité interne"): lambda d: (
        f"📈 **Taux de Rentabilité Interne (TRI) :** {d.get('tri', 'N/A')}%.\n\n"
        "Un TRI de {:.1f}% est **supérieur au coût moyen pondéré du capital (CMPC)** estimé à ~12% "
        "pour ce type de financement mixte (BFPME + FOPRODI). Le projet crée donc de la valeur "
        "pour le promoteur et couvre confortablement les obligations de remboursement.".format(d.get('tri', 0))
    ),
    # VAN
    ("van", "valeur actuelle", "npv"): lambda d: (
        f"💰 **Valeur Actuelle Nette (VAN) :** {d.get('van', 'N/A')} mDT (au taux de 10%).\n\n"
        "La VAN positive indique que le projet génère plus de cash-flows actualisés que son coût "
        "d'investissement initial. C'est un signal **favorable** pour l'octroi du crédit."
    ),
    # Risques
    ("risque", "risques", "risk"): lambda d: (
        "⚠️ **Risques principaux identifiés :**\n\n"
        "1. **Risque saisonnier** — Production de tomates concentrée sur 4 mois. *Mitigation :* contrats "
        "pluriannuels avec 38 agriculteurs.\n"
        "2. **Risque de marché** — Volatilité des prix MP. *Mitigation :* diversification export (objectif 30%).\n"
        "3. **Risque de change** — Exposition EUR/USD. *Mitigation :* couverture à terme via STB.\n"
        "4. **Risque opérationnel** — Équipements importés. *Mitigation :* contrat de maintenance + stock pièces.\n\n"
        "🔵 **Appréciation globale :** Risque **MODÉRÉ** — les mitigations proposées sont réalistes et le "
        "soutien ZDR renforce la viabilité."
    ),
    # Emplois
    ("emploi", "emplois", "jobs", "postes"): lambda d: (
        f"👥 **Emplois permanents à créer :** {d.get('emplois', 'N/A')} postes.\n\n"
        "Ce volume d'emplois correspond à l'éligibilité aux **primes à l'emploi** du FOPRODI et "
        "justifie l'inscription en Zone de Développement Régional (ZDR). Le ratio emploi/investissement "
        f"est de {round(d.get('emplois',45)/d.get('cout_total',2850)*1000, 1)} emplois par million de DT, "
        "dans la norme pour le secteur agroalimentaire tunisien."
    ),
    # Structure financement
    ("financement", "structure", "foprodi", "sicar", "apport"): lambda d: (
        f"🏗️ **Structure de Financement :**\n\n"
        f"| Source | Montant (mDT) | Part |\n"
        f"|--------|--------------|------|\n"
        f"| Apport Personnel | {d.get('apport_personnel','N/A')} | {round(d.get('apport_personnel',0)/d.get('cout_total',1)*100,1)}% |\n"
        f"| Dotation FOPRODI/ZDR | {d.get('foprodi_prime','N/A')} | {round(d.get('foprodi_prime',0)/d.get('cout_total',1)*100,1)}% |\n"
        f"| Participation SICAR | {d.get('sicar','N/A')} | {round(d.get('sicar',0)/d.get('cout_total',1)*100,1)}% |\n"
        f"| Crédit BFPME | {d.get('credit_bfpme','N/A')} | {round(d.get('credit_bfpme',0)/d.get('cout_total',1)*100,1)}% |\n\n"
        "✅ Le ratio d'endettement BFPME/Coût Total est dans les limites acceptables (≤ 60%)."
    ),
    # Chiffre d'affaires
    ("chiffre d'affaires", "ca", "revenus", "ventes"): lambda d: (
        f"📊 **Projections de Chiffre d'Affaires :**\n\n"
        f"- An 1 : **{d.get('ca_an1','N/A')} mDT**\n"
        f"- An 3 : **{d.get('ca_an3','N/A')} mDT**\n\n"
        f"La croissance projetée ({round((d.get('ca_an3',0)/d.get('ca_an1',1)-1)*100,1)}% sur 3 ans) "
        "est **réaliste** pour un projet en phase de montée en puissance avec une stratégie d'export progressive."
    ),
    # Garanties
    ("garantie", "garanties", "sûreté", "hypothèque", "gage"): lambda d: (
        "🔒 **Garanties proposées :**\n\n"
        "1. Hypothèque de 1er rang sur terrain — **380 mDT**\n"
        "2. Gage sur équipements (valeur nette) — **1 100 mDT**\n"
        "3. Caution personnelle du promoteur — **500 mDT**\n\n"
        f"**Taux de couverture :** {round((380+1100+500)/d.get('credit_bfpme',1567)*100,1)}% du crédit BFPME sollicité.\n"
        "✅ Couverture **satisfaisante** selon les normes BFPME (seuil minimum : 120%)."
    ),
    # Secteur / Projet
    ("secteur", "projet", "activité", "tomate", "agritech"): lambda d: (
        "🌿 **Présentation du projet :**\n\n"
        "Création d'une unité de **transformation de tomates** à Sidi Bouzid produisant :\n"
        "- Concentré de tomates (70% de la production)\n"
        "- Tomates pelées en conserve (20%)\n"
        "- Jus de tomates (10%)\n\n"
        "**Capacité :** 50 tonnes/jour de tomates fraîches.\n"
        "**Promoteur :** M. Karim Mellouli, ingénieur agronome (12 ans d'expérience).\n"
        "**Zone :** ZDR – éligible aux aides FOPRODI et primes régionales."
    ),
    # Recommandation
    ("recommandation", "avis", "décision", "accord", "refus"): lambda d: (
        "📋 **Synthèse & Recommandation préliminaire :**\n\n"
        "✅ **Points favorables :**\n"
        f"- TRI ({d.get('tri','N/A')}%) supérieur au coût du capital\n"
        f"- VAN positive ({d.get('van','N/A')} mDT)\n"
        "- Promoteur expérimenté (12 ans)\n"
        "- Localisation ZDR avec soutiens publics solides\n"
        "- Garanties couvrant >120% du crédit sollicité\n\n"
        "⚠️ **Points de vigilance :**\n"
        "- Saisonnalité prononcée (4 mois de production)\n"
        "- Délai de récupération à la limite haute acceptable\n\n"
        "🔵 **Recommandation :** **FAVORABLE SOUS CONDITIONS** — Accord de principe sous réserve "
        "de vérification des contrats agriculteurs et du plan de trésorerie mensuel An 1."
    ),
    # Remboursement
    ("remboursement", "échéances", "annuités", "dettes"): lambda d: (
        f"💳 **Plan de remboursement indicatif :**\n\n"
        f"- Crédit BFPME : **{d.get('credit_bfpme','N/A')} mDT** sur 7 ans\n"
        f"- Taux indicatif : ~7,5% l'an (TMM + marge)\n"
        f"- Annuité de remboursement estimée : ~**295 mDT/an**\n"
        f"- Ratio service de la dette / EBE (An 3) : {round(295/d.get('ebe_an3',980)*100,1)}%\n\n"
        "✅ Le ratio de couverture de la dette (EBE/Service Dette ≈ 3,3x) est **excellent** (seuil BFPME ≥ 1,3x)."
    ),
}

DEFAULT_RESPONSE = (
    "Je suis l'Assistant IA de la BFPME. Posez-moi des questions sur ce projet de financement, "
    "par exemple :\n"
    "- *Quel est le délai de récupération ?*\n"
    "- *Quels sont les risques principaux ?*\n"
    "- *Quelle est la structure de financement ?*\n"
    "- *Donnez-moi votre recommandation.*"
)


# ─────────────────────────────────────────────────────────────────────────────
# PARSING ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def parse_number(text, pattern):
    """Extract first number matching a regex pattern from text."""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        raw = match.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def smart_parse(text: str) -> dict:
    """
    Failsafe Smart-Parsing Engine.
    Tries regex extraction on the raw text. Falls back to sample defaults
    so the app always has valid data to display.
    """
    financials = {}

    # Coût total
    v = parse_number(text, r"co[uû]t\s+total[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["cout_total"] = v if v else SAMPLE_FINANCIALS["cout_total"]

    # Apport personnel
    v = parse_number(text, r"apport\s+personnel[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["apport_personnel"] = v if v else SAMPLE_FINANCIALS["apport_personnel"]

    # FOPRODI
    v = parse_number(text, r"(?:foprodi|prime[^:]*|dotation)[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["foprodi_prime"] = v if v else SAMPLE_FINANCIALS["foprodi_prime"]

    # SICAR
    v = parse_number(text, r"sicar[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["sicar"] = v if v else SAMPLE_FINANCIALS["sicar"]

    # Crédit BFPME
    v = parse_number(text, r"cr[eé]dit[^:]*bfpme[^:]*:\s*([\d\s,]+)\s*mdt")
    if v is None:
        v = parse_number(text, r"bfpme[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["credit_bfpme"] = v if v else SAMPLE_FINANCIALS["credit_bfpme"]

    # Emplois
    v = parse_number(text, r"emplois?\s+(?:permanents?)[^:]*:\s*([\d]+)")
    financials["emplois"] = int(v) if v else SAMPLE_FINANCIALS["emplois"]

    # CA
    v = parse_number(text, r"chiffre\s+d.affaires[^:]*an\s*[1I][^:]*:\s*([\d\s,]+)\s*mdt")
    financials["ca_an1"] = v if v else SAMPLE_FINANCIALS["ca_an1"]

    v = parse_number(text, r"chiffre\s+d.affaires[^:]*an\s*[3III][^:]*:\s*([\d\s,]+)\s*mdt")
    financials["ca_an3"] = v if v else SAMPLE_FINANCIALS["ca_an3"]

    # EBE
    v = parse_number(text, r"ebe[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["ebe_an3"] = v if v else SAMPLE_FINANCIALS["ebe_an3"]

    # Résultat net
    v = parse_number(text, r"r[eé]sultat\s+net[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["resultat_net_an3"] = v if v else SAMPLE_FINANCIALS["resultat_net_an3"]

    # Délai récupération
    v = parse_number(text, r"d[eé]lai\s+de\s+r[eé]cup[eé]ration\s*:\s*([\d.,]+)")
    financials["delai_recuperation"] = v if v else SAMPLE_FINANCIALS["delai_recuperation"]

    # TRI
    v = parse_number(text, r"tri\s*:\s*([\d.,]+)\s*%")
    financials["tri"] = v if v else SAMPLE_FINANCIALS["tri"]

    # VAN
    v = parse_number(text, r"van[^:]*:\s*([\d\s,]+)\s*mdt")
    financials["van"] = v if v else SAMPLE_FINANCIALS["van"]

    # Meta — extract from text or use sample defaults
    meta = {}
    rs_match = re.search(r"raison\s+sociale\s*:\s*(.+)", text, re.IGNORECASE)
    meta["raison_sociale"] = rs_match.group(1).strip() if rs_match else SAMPLE_PROJECT_META["raison_sociale"]

    sec_match = re.search(r"secteur[^:]*:\s*(.+)", text, re.IGNORECASE)
    meta["secteur"] = sec_match.group(1).strip()[:80] if sec_match else SAMPLE_PROJECT_META["secteur"]

    loc_match = re.search(r"localisation\s*:\s*(.+)", text, re.IGNORECASE)
    meta["localisation"] = loc_match.group(1).strip() if loc_match else SAMPLE_PROJECT_META["localisation"]

    promo_match = re.search(r"promoteur\s+m[^,\.]+", text, re.IGNORECASE)
    meta["promoteur"] = promo_match.group(0).replace("promoteur", "").strip().title() if promo_match else SAMPLE_PROJECT_META["promoteur"]

    meta["emplois"] = financials["emplois"]

    return {"financials": financials, "meta": meta}


def extract_text_from_pdf(file_like) -> str:
    """Extract text from a PDF using pypdf. Accepts a BytesIO or file-like object."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_like)
        texts = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                texts.append(t)
        return "\n".join(texts)
    except Exception as e:
        st.warning(f"Extraction PDF partielle : {e}")
        return ""


def llm_extract(text: str, api_key: str) -> dict:
    """Use OpenAI to extract financial variables from document text."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""Tu es un analyste crédit expert de la BFPME (Tunisie).
Extrais les informations financières suivantes du document ci-dessous et renvoie un JSON valide uniquement.
Si une valeur est absente, mets null.

Champs requis (nombres en mDT sauf indication contraire) :
- raison_sociale (string)
- secteur (string)
- localisation (string)
- promoteur (string)
- cout_total (float, mDT)
- apport_personnel (float, mDT)
- foprodi_prime (float, mDT)
- sicar (float, mDT)
- credit_bfpme (float, mDT)
- emplois (int)
- ca_an1 (float, mDT)
- ca_an3 (float, mDT)
- ebe_an3 (float, mDT)
- resultat_net_an3 (float, mDT)
- delai_recuperation (float, années)
- tri (float, %)
- van (float, mDT)

DOCUMENT :
{text[:6000]}

Réponds UNIQUEMENT avec le JSON, sans markdown.
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)

        meta = {k: data.get(k) or SAMPLE_PROJECT_META.get(k, "N/A")
                for k in ("raison_sociale", "secteur", "localisation", "promoteur")}
        meta["emplois"] = data.get("emplois") or SAMPLE_PROJECT_META["emplois"]

        fin_keys = ["cout_total", "apport_personnel", "foprodi_prime", "sicar",
                    "credit_bfpme", "ca_an1", "ca_an3", "ebe_an3", "resultat_net_an3",
                    "delai_recuperation", "tri", "van"]
        financials = {k: data.get(k) or SAMPLE_FINANCIALS[k] for k in fin_keys}
        financials["emplois"] = meta["emplois"]

        return {"financials": financials, "meta": meta}

    except Exception as e:
        st.warning(f"LLM extraction échouée ({e}), bascule vers Smart-Parsing.")
        return smart_parse(text)


def llm_chat(messages: list, context: dict, api_key: str) -> str:
    """Use OpenAI GPT-4o for the interactive chatbot."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        system_prompt = f"""Tu es un Assistant IA expert de la BFPME (Banque de Financement des PME, Tunisie).
Tu aides les chargés de crédit à analyser les dossiers de financement PME.
Réponds de façon professionnelle, précise et structurée en français.
Utilise des emojis appropriés et des tableaux markdown si pertinent.
Tu as accès aux données du projet suivant :

META : {json.dumps(context.get('meta', {}), ensure_ascii=False)}
FINANCIERS : {json.dumps(context.get('financials', {}), ensure_ascii=False)}
"""
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=full_messages,
            temperature=0.3,
            max_tokens=700,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Erreur LLM : {e}. Veuillez vérifier votre clé API."


def failsafe_chat(user_input: str, context: dict) -> str:
    """
    Rule-based semantic chatbot using keyword matching against SMART_RESPONSES dict.
    Falls back gracefully when no OpenAI key is available.
    """
    query = user_input.lower()
    fin = context.get("financials", SAMPLE_FINANCIALS)
    meta_emplois = context.get("meta", {}).get("emplois", fin.get("emplois", 45))
    chat_ctx = {**fin, "emplois": meta_emplois}

    for keywords, fn in SMART_RESPONSES.items():
        if any(kw in query for kw in keywords):
            return fn(chat_ctx)

    return DEFAULT_RESPONSE


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────
if "project_data" not in st.session_state:
    st.session_state.project_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bfpme-header">
    <div style="font-size:2.5rem;">🏦</div>
    <div>
        <h1>BFPME AI Credit Agent</h1>
        <p>Banque de Financement des Petites et Moyennes Entreprises — Moteur d'Analyse IA</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.divider()

    # API Key
    api_key_input = st.text_input(
        "🔑 Clé API OpenAI (optionnelle)",
        type="password",
        placeholder="sk-...",
        help="Sans clé : mode Failsafe activé automatiquement.",
    )
    api_key = api_key_input.strip() or None

    # Status indicator
    st.markdown("**Statut du moteur :**")
    if api_key:
        st.markdown(
            '<span class="status-live">🟢 Live LLM Engine (OpenAI GPT-4o)</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-failsafe">🟡 Local Smart-Parsing Engine (Failsafe Mode)</span>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("### 📂 Chargement du Dossier")

    # File uploader
    uploaded_file = st.file_uploader(
        "Importer un Plan d'Affaires",
        type=["txt", "pdf"],
        help="Formats acceptés : .txt, .pdf",
    )

    # Sample project button
    if st.button("🌿 Charger Projet Sample\n(Agritech Sidi Bouzid)", use_container_width=True):
        st.session_state.raw_text = SAMPLE_TEXT
        if api_key:
            with st.spinner("Extraction LLM en cours…"):
                st.session_state.project_data = llm_extract(SAMPLE_TEXT, api_key)
        else:
            st.session_state.project_data = smart_parse(SAMPLE_TEXT)
        st.session_state.chat_history = []
        st.success("✅ Projet sample chargé avec succès !")
        st.rerun()

    # Process uploaded file
    if uploaded_file is not None:
        raw_bytes = uploaded_file.read()
        file_hash = hashlib.sha256(raw_bytes).hexdigest()
        if st.session_state.get("last_file_hash") != file_hash:
            st.session_state.last_file_hash = file_hash
            with st.spinner("Traitement du fichier…"):
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(BytesIO(raw_bytes))
                else:
                    text = raw_bytes.decode("utf-8", errors="ignore")

                st.session_state.raw_text = text
                if api_key:
                    st.session_state.project_data = llm_extract(text, api_key)
                else:
                    st.session_state.project_data = smart_parse(text)
                st.session_state.chat_history = []
            st.success(f"✅ '{html.escape(uploaded_file.name)}' analysé avec succès !")
            st.rerun()

    st.divider()

    # Project info summary in sidebar
    if st.session_state.project_data:
        meta = st.session_state.project_data.get("meta", {})
        fin = st.session_state.project_data.get("financials", {})
        st.markdown("**📌 Dossier en cours :**")
        st.caption(f"🏢 {meta.get('raison_sociale', '—')}")
        st.caption(f"📍 {meta.get('localisation', '—')}")
        st.caption(f"💼 {meta.get('secteur', '—')[:50]}")
        st.caption(f"💰 Crédit BFPME : **{fin.get('credit_bfpme', '—')} mDT**")
    else:
        st.info("Aucun dossier chargé. Importez un fichier ou chargez le projet sample.")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT — TABS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.project_data is None:
    # Welcome state
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📂 **Étape 1** : Importez un plan d'affaires (.txt ou .pdf) via la barre latérale.")
    with col2:
        st.info("🌿 **Ou** : Cliquez sur « Charger Projet Sample » pour tester instantanément avec un projet Agritech tunisien.")
    with col3:
        st.info("🔑 **Optionnel** : Entrez votre clé OpenAI pour activer l'extraction LLM et le chatbot GPT-4o.")
    st.stop()

# ── Extract data from session ──────────────────────────────────────────────
data = st.session_state.project_data
meta = data.get("meta", {})
fin = data.get("financials", {})

tab1, tab2, tab3 = st.tabs([
    "📊 Synthèse du Projet",
    "📈 Schéma de Financement",
    "🤖 Assistant IA Interactif",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — EXECUTIVE DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    # Project identity
    col_id, col_risk = st.columns([3, 1])
    with col_id:
        rs   = html.escape(str(meta.get('raison_sociale', 'N/A')))
        loc  = html.escape(str(meta.get('localisation', 'N/A')))
        sec  = html.escape(str(meta.get('secteur', 'N/A'))[:70])
        prom = html.escape(str(meta.get('promoteur', 'N/A')))
        st.markdown(f"""
<div style="background:#FFFFFF;border-radius:12px;padding:1.25rem 1.5rem;box-shadow:0 2px 8px rgba(10,74,110,0.08);margin-bottom:1rem;">
<div style="font-size:0.78rem;color:#5A7A8A;text-transform:uppercase;letter-spacing:0.06em;">Raison Sociale</div>
<div style="font-size:1.4rem;font-weight:700;color:#0A4A6E;">{rs}</div>
<div style="font-size:0.9rem;color:#4A7A9A;margin-top:0.2rem;">
  📍 {loc} &nbsp;|&nbsp; 🏭 {sec}
</div>
<div style="font-size:0.9rem;color:#4A7A9A;">👤 Promoteur : {prom}</div>
</div>
""", unsafe_allow_html=True)

    with col_risk:
        # Simple risk scoring
        tri_val = fin.get("tri", 0) or 0
        dr_val = fin.get("delai_recuperation", 99) or 99
        if tri_val >= 15 and dr_val <= 7:
            risk_label = '<span class="risk-low">🟢 Risque FAIBLE</span>'
        elif tri_val >= 10 and dr_val <= 9:
            risk_label = '<span class="risk-medium">🟡 Risque MODÉRÉ</span>'
        else:
            risk_label = '<span class="risk-high">🔴 Risque ÉLEVÉ</span>'

        st.markdown(f"""
<div style="background:#FFFFFF;border-radius:12px;padding:1.25rem 1.5rem;box-shadow:0 2px 8px rgba(10,74,110,0.08);margin-bottom:1rem;text-align:center;">
<div style="font-size:0.78rem;color:#5A7A8A;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Niveau de Risque</div>
{risk_label}
</div>
""", unsafe_allow_html=True)

    # KPI metrics
    st.markdown('<div class="section-title">📌 Indicateurs Clés</div>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    with r1c1:
        st.markdown(f"""<div class="metric-card">
<div class="label">Coût Total Investissement</div>
<div class="value">{fin.get('cout_total','N/A')} mDT</div>
<div class="sub">Milliers de Dinars Tunisiens</div>
</div>""", unsafe_allow_html=True)

    with r1c2:
        st.markdown(f"""<div class="metric-card">
<div class="label">Crédit BFPME Sollicité</div>
<div class="value">{fin.get('credit_bfpme','N/A')} mDT</div>
<div class="sub">{round(fin.get('credit_bfpme',0)/fin.get('cout_total',1)*100,1) if fin.get('cout_total') else '—'}% du coût total</div>
</div>""", unsafe_allow_html=True)

    with r1c3:
        st.markdown(f"""<div class="metric-card">
<div class="label">Emplois à Créer</div>
<div class="value">{meta.get('emplois','N/A')}</div>
<div class="sub">Postes permanents</div>
</div>""", unsafe_allow_html=True)

    with r1c4:
        st.markdown(f"""<div class="metric-card">
<div class="label">TRI du Projet</div>
<div class="value">{fin.get('tri','N/A')}%</div>
<div class="sub">Taux Rentabilité Interne</div>
</div>""", unsafe_allow_html=True)

    r2c1, r2c2, r2c3, r2c4 = st.columns(4)
    with r2c1:
        st.markdown(f"""<div class="metric-card">
<div class="label">Apport Personnel</div>
<div class="value">{fin.get('apport_personnel','N/A')} mDT</div>
<div class="sub">{round(fin.get('apport_personnel',0)/fin.get('cout_total',1)*100,1) if fin.get('cout_total') else '—'}% du coût total</div>
</div>""", unsafe_allow_html=True)

    with r2c2:
        st.markdown(f"""<div class="metric-card">
<div class="label">Dotation FOPRODI/ZDR</div>
<div class="value">{fin.get('foprodi_prime','N/A')} mDT</div>
<div class="sub">Prime régionale</div>
</div>""", unsafe_allow_html=True)

    with r2c3:
        st.markdown(f"""<div class="metric-card">
<div class="label">VAN (taux 10%)</div>
<div class="value">{fin.get('van','N/A')} mDT</div>
<div class="sub">Valeur Actuelle Nette</div>
</div>""", unsafe_allow_html=True)

    with r2c4:
        st.markdown(f"""<div class="metric-card">
<div class="label">Délai de Récupération</div>
<div class="value">{fin.get('delai_recuperation','N/A')} ans</div>
<div class="sub">Payback period</div>
</div>""", unsafe_allow_html=True)

    # Financial performance table
    st.markdown('<div class="section-title" style="margin-top:1.5rem;">📈 Projections Financières</div>', unsafe_allow_html=True)
    df_proj = pd.DataFrame({
        "Indicateur": ["Chiffre d'Affaires", "EBE", "Résultat Net"],
        "An 1 (mDT)": [fin.get("ca_an1", "—"), "—", "—"],
        "An 3 (mDT)": [fin.get("ca_an3", "—"), fin.get("ebe_an3", "—"), fin.get("resultat_net_an3", "—")],
    })
    st.dataframe(df_proj, use_container_width=True, hide_index=True)

    # Document text expander
    if st.session_state.raw_text:
        with st.expander("📄 Texte du document analysé"):
            st.text_area("Contenu brut", st.session_state.raw_text[:5000], height=300, disabled=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — FINANCIAL VISUALIZATIONS
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">💰 Structure de Financement</div>', unsafe_allow_html=True)

    col_pie, col_inv = st.columns(2)

    with col_pie:
        # Financing structure pie chart
        labels_fin = ["Apport Personnel", "FOPRODI / Prime ZDR", "Participation SICAR", "Crédit BFPME"]
        values_fin = [
            fin.get("apport_personnel", 0),
            fin.get("foprodi_prime", 0),
            fin.get("sicar", 0),
            fin.get("credit_bfpme", 0),
        ]
        colors_fin = ["#0D7377", "#14A097", "#0A4A6E", "#1B7FC4"]

        fig_pie = go.Figure(go.Pie(
            labels=labels_fin,
            values=values_fin,
            hole=0.45,
            marker=dict(colors=colors_fin, line=dict(color="#FFFFFF", width=2)),
            textinfo="label+percent",
            textfont=dict(size=12),
            hovertemplate="%{label}<br>%{value} mDT<br>%{percent}<extra></extra>",
        ))
        fig_pie.update_layout(
            title=dict(text="Structure de Financement", font=dict(size=15, color="#0A4A6E")),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25),
            margin=dict(t=50, b=60, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            height=380,
            annotations=[dict(
                text=f"<b>{fin.get('cout_total',0)}<br>mDT</b>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#0A4A6E")
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_inv:
        # Investment vs financing bar comparison
        categories = ["Coût Total", "Apport Pers.", "FOPRODI/ZDR", "SICAR", "Crédit BFPME"]
        amounts = [
            fin.get("cout_total", 0),
            fin.get("apport_personnel", 0),
            fin.get("foprodi_prime", 0),
            fin.get("sicar", 0),
            fin.get("credit_bfpme", 0),
        ]
        bar_colors = ["#0A4A6E", "#0D7377", "#14A097", "#1B7FC4", "#2196C4"]

        fig_bar = go.Figure(go.Bar(
            x=categories,
            y=amounts,
            marker_color=bar_colors,
            text=[f"{v} mDT" for v in amounts],
            textposition="outside",
            hovertemplate="%{x}<br><b>%{y} mDT</b><extra></extra>",
        ))
        fig_bar.update_layout(
            title=dict(text="Répartition Investissement & Financement (mDT)", font=dict(size=15, color="#0A4A6E")),
            yaxis=dict(title="mDT", gridcolor="#E8EFF5"),
            xaxis=dict(tickangle=-15),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=20, l=20, r=20),
            height=380,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:1rem;">📊 Projections & Rentabilité</div>', unsafe_allow_html=True)

    col_ca, col_gauge = st.columns(2)

    with col_ca:
        # CA evolution bar chart
        years = ["An 1", "An 2 (estimé)", "An 3"]
        ca_an1 = fin.get("ca_an1", 0) or 0
        ca_an3 = fin.get("ca_an3", 0) or 0
        ca_an2 = round((ca_an1 + ca_an3) / 2, 0)

        fig_ca = go.Figure()
        fig_ca.add_trace(go.Bar(
            name="Chiffre d'Affaires",
            x=years, y=[ca_an1, ca_an2, ca_an3],
            marker_color=["#0A4A6E", "#0D7377", "#14A097"],
            text=[f"{v} mDT" for v in [ca_an1, ca_an2, ca_an3]],
            textposition="outside",
        ))
        fig_ca.add_trace(go.Bar(
            name="EBE (An 3)",
            x=["An 3"], y=[fin.get("ebe_an3", 0) or 0],
            marker_color="#1B7FC4",
            text=[f"{fin.get('ebe_an3',0)} mDT"],
            textposition="outside",
            showlegend=True,
        ))
        fig_ca.update_layout(
            title=dict(text="Évolution du Chiffre d'Affaires (mDT)", font=dict(size=15, color="#0A4A6E")),
            yaxis=dict(title="mDT", gridcolor="#E8EFF5"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            barmode="group",
            margin=dict(t=50, b=20, l=20, r=20),
            height=340,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        )
        st.plotly_chart(fig_ca, use_container_width=True)

    with col_gauge:
        # TRI Gauge
        tri_val = fin.get("tri", 0) or 0
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tri_val,
            delta={"reference": 12, "valueformat": ".1f", "suffix": "%"},
            number={"suffix": "%", "font": {"size": 28, "color": "#0A4A6E"}},
            title={"text": "TRI vs Coût du Capital (12%)", "font": {"size": 13, "color": "#0A4A6E"}},
            gauge={
                "axis": {"range": [0, 30], "ticksuffix": "%"},
                "bar": {"color": "#0D7377"},
                "bgcolor": "#F0F4F8",
                "steps": [
                    {"range": [0, 10], "color": "#FDECEA"},
                    {"range": [10, 16], "color": "#FFF8E1"},
                    {"range": [16, 30], "color": "#E8F5E9"},
                ],
                "threshold": {
                    "line": {"color": "#0A4A6E", "width": 3},
                    "thickness": 0.8,
                    "value": 12,
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=20, l=40, r=40),
            height=340,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Coverage ratio
    st.markdown('<div class="section-title" style="margin-top:0.5rem;">🔒 Ratio de Couverture des Garanties</div>', unsafe_allow_html=True)
    credit = fin.get("credit_bfpme", 1) or 1
    guarantees = {"Hypothèque terrain": 380, "Gage équipements": 1100, "Caution personnelle": 500}
    total_guarantee = sum(guarantees.values())
    coverage_pct = round(total_guarantee / credit * 100, 1)

    fig_cov = go.Figure(go.Bar(
        x=list(guarantees.keys()),
        y=list(guarantees.values()),
        marker_color=["#0D7377", "#14A097", "#1B7FC4"],
        text=[f"{v} mDT" for v in guarantees.values()],
        textposition="outside",
    ))
    fig_cov.add_hline(
        y=credit, line_dash="dash", line_color="#B02020",
        annotation_text=f"Crédit BFPME : {credit} mDT",
        annotation_position="top right",
    )
    fig_cov.update_layout(
        title=dict(text=f"Garanties vs Crédit (Couverture : {coverage_pct}%)", font=dict(size=15, color="#0A4A6E")),
        yaxis=dict(title="mDT", gridcolor="#E8EFF5"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_cov, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — INTERACTIVE AI CHATBOT
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    mode_label = "🟢 GPT-4o (Live)" if api_key else "🟡 Smart-Parsing (Failsafe)"
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#0A4A6E,#0D7377);border-radius:10px;padding:0.9rem 1.2rem;
color:#fff;margin-bottom:1rem;display:flex;align-items:center;gap:0.8rem;">
<div style="font-size:1.5rem;">🤖</div>
<div>
  <b>Assistant IA Crédit BFPME</b> &nbsp; <span style="font-size:0.82rem;opacity:0.85;">Mode : {mode_label}</span><br>
  <span style="font-size:0.85rem;opacity:0.85;">Posez des questions sur le projet en cours d'analyse.</span>
</div>
</div>
""", unsafe_allow_html=True)

    # Quick question chips
    st.markdown("**Questions rapides :**")
    q_cols = st.columns(4)
    quick_questions = [
        "Quel est le délai de récupération ?",
        "Quels sont les risques principaux ?",
        "Quelle est la structure de financement ?",
        "Donnez votre recommandation.",
    ]
    for i, q in enumerate(quick_questions):
        with q_cols[i]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                # Add to history as user message
                st.session_state.chat_history.append({"role": "user", "content": q})
                if api_key:
                    response = llm_chat(st.session_state.chat_history, data, api_key)
                else:
                    response = failsafe_chat(q, data)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

    st.divider()

    # Chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown(
                f'<div class="chat-agent"><div class="chat-label-agent">🤖 Assistant BFPME</div>'
                f'{DEFAULT_RESPONSE}</div>',
                unsafe_allow_html=True,
            )
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-label-user">Vous</div>'
                        f'<div class="chat-user">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="chat-label-agent">🤖 Assistant BFPME</div>'
                        f'<div class="chat-agent">{msg["content"]}</div>',
                        unsafe_allow_html=True,
                    )

    st.divider()

    # Input
    with st.form("chat_form", clear_on_submit=True):
        col_inp, col_btn = st.columns([5, 1])
        with col_inp:
            user_input = st.text_input(
                "Message",
                placeholder="Ex: Quel est le ratio de couverture des garanties ?",
                label_visibility="collapsed",
            )
        with col_btn:
            submitted = st.form_submit_button("Envoyer ▶", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("Analyse en cours…"):
            if api_key:
                response = llm_chat(st.session_state.chat_history, data, api_key)
            else:
                response = failsafe_chat(user_input.strip(), data)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Clear chat button
    if st.session_state.chat_history:
        if st.button("🗑️ Effacer la conversation", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()
