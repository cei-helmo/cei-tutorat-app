import io
import json
import os
import urllib.parse
import pandas as pd
import streamlit as st

# =============================================================================
# 0. CHARGEMENT DE LA CONFIGURATION MASQUÉE / ANONYMISÉE
# =============================================================================
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "academic_year": "2026-2027",
    "organization_name": "Cercle Étudiant HELMo CEI",
    "email_subject_prefix": "[CEI] Tutorat",
    "responsible": {
        "name": "Responsable Tutorat CEI",
        "email": "tutorat@example.com"
    }
}

def load_config():
    """Charge le fichier JSON de configuration s'il existe, sinon utilise les valeurs par défaut."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Impossible de lire {CONFIG_FILE}, utilisation de la configuration par défaut. Erreur : {e}")
    return DEFAULT_CONFIG

CONFIG = load_config()

# =============================================================================
# 1. CONFIGURATION DE LA PAGE & STYLES CSS
# =============================================================================
st.set_page_config(
    page_title=f"Tutorat {CONFIG['organization_name']} | Centre d'Organisation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Spacing global */
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; }

    /* Badges de section */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-devapps { background-color: #e0e7ff; color: #3730a3; }
    .badge-cyber   { background-color: #d1fae5; color: #065f46; }
    .badge-ia      { background-color: #fef3c7; color: #92400e; }
    .badge-default { background-color: #f3f4f6; color: #374151; }

    /* Indicateurs d'état */
    .status-ok      { color: #10b981; font-weight: 600; }
    .status-warning { color: #f59e0b; font-weight: 600; }
    .status-alert   { color: #ef4444; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. FONCTIONS UTILITAIRES & GENERATEUR DE MAILTO
# =============================================================================
def get_badge_html(section: str) -> str:
    """Génère le tag HTML stylisé selon la section de l'étudiant."""
    sec_lower = str(section).lower()
    if 'dev' in sec_lower:
        cls = 'badge-devapps'
    elif 'cyber' in sec_lower:
        cls = 'badge-cyber'
    elif 'ia' in sec_lower or 'intelligence' in sec_lower:
        cls = 'badge-ia'
    else:
        cls = 'badge-default'
    return f'<span class="badge {cls}">{section}</span>'


def clean_val(val, default_text: str = "Non renseigné") -> str:
    """Nettoie les chaînes de caractères et gère les valeurs manquantes/NaN."""
    if pd.isna(val) or str(val).strip() in ['', 'nan', 'NaN', 'None', 'null']:
        return default_text
    return str(val).strip()


def build_mailto_link(
        mail_tutore: str,
        mail_tuteur: str,
        nom_tutore: str,
        nom_tuteur: str,
        section: str,
        moyen_tutore,
        info_tutore,
        autre_tutore,
        moyen_tuteur,
        info_tuteur
) -> str | None:
    """Génère une URL mailto et structurée pour le client e-mail."""
    if not mail_tuteur or mail_tuteur == "Aucun":
        return None

    academic_year = CONFIG.get("academic_year", "2026-2027")
    prefix = CONFIG.get("email_subject_prefix", "[CEI] Tutorat")
    org_name = CONFIG.get("organization_name", "Cercle Étudiant HELMo CEI")
    resp_email = CONFIG["responsible"].get("email", "")

    subject = f"{prefix} {academic_year} : Coordination {section}"

    m_tutore = clean_val(moyen_tutore, "Non spécifié")
    i_tutore = clean_val(info_tutore, "Non renseigné")
    a_tutore = clean_val(autre_tutore, "Aucune précision particulière")

    m_tuteur = clean_val(moyen_tuteur, "Non spécifié")
    i_tuteur = clean_val(info_tuteur, "Non renseigné")

    body = (
        f"Bonjour {nom_tutore} et {nom_tuteur},\n\n"
        f"Au nom du {org_name}, nous avons le plaisir de vous confirmer votre mise en relation dans le cadre du programme de tutorat pour l'année académique {academic_year}.\n\n"
        f"FICHES DE CONTACT ET PREFERENCES\n\n"
        f"• Tutoré(e) (B1) : {nom_tutore} ({section})\n"
        f"  Courriel : {mail_tutore}\n"
        f"  Canal souhaité : {m_tutore}\n"
        f"  Identifiant / Contact : {i_tutore}\n"
        f"  Besoins spécifiques : {a_tutore}\n\n"
        f"• Tuteur / Tutrice (B2/B3) : {nom_tuteur} ({section})\n"
        f"  Courriel : {mail_tuteur}\n"
        f"  Canal souhaité : {m_tuteur}\n"
        f"  Identifiant / Contact : {i_tuteur}\n\n"
        f"MODALITES DE CONTACT\n\n"
        f"Nous invitons {nom_tuteur} à initier le premier échange avec {nom_tutore} afin de définir ensemble la fréquence et les modalités de vos séances de travail (sur le campus, via Discord ou par téléphone).\n\n"
        f"CADRE ET ENGAGEMENTS DU TUTORAT\n\n"
        f"1. Engagement mutuel : Le tuteur réalise cet accompagnement de manière bénévole en parallèle de sa propre formation. Veillez à respecter les horaires et engagements convenus.\n"
        f"2. Préparation des séances : Pour garantir un suivi efficace, le tutoré est invité à préparer ses questions et points de blocage en amont de chaque rencontre.\n"
        f"3. Suivi du binôme : Pour toute question ou ajustement nécessaire en cours d'année, merci de contacter votre responsable tutorat ({resp_email}).\n\n"
        f"Nous vous souhaitons une excellente collaboration ainsi qu'une très belle réussite académique.\n\n"
        f"Excellente Journée,\n\n"
        f"Le {org_name}\n"
        f"Responsable Tutorat : {resp_email}"
    )

    params = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    return f"mailto:{mail_tutore},{mail_tuteur}?{params}"


# =============================================================================
# 3. INITIALISATION DU STATE & ENTÊTE
# =============================================================================
if 'assignments' not in st.session_state:
    st.session_state.assignments = {}

st.title(f"🎓 Hub d'Organisation du Tutorat - {CONFIG.get('organization_name', 'HELMo CEI')}")
st.caption("Plateforme d'appariement, de régulation manuelle et de mise en relation B1 ↔ B2/B3")

# Barre latérale
st.sidebar.header("⚙️ Configuration")
uploaded_file = st.sidebar.file_uploader("Fichier Forms / Excel (CSV ou XLSX)", type=["csv", "xlsx"])
max_capacity = st.sidebar.slider("Capacité max par tuteur", min_value=1, max_value=5, value=2)

# =============================================================================
# 4. TRAITEMENT DU FICHIER & LOGIQUE PRINCIPALE
# =============================================================================
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
            if len(df.columns) <= 1:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=',', encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()

    df.columns = df.columns.str.strip()

    col_id = 'Id' if 'Id' in df.columns else df.columns[0]
    col_nom = 'Nom'
    col_email = 'Adresse de messagerie'
    col_role = 'Que souhaitez-vous ?'
    col_section = 'Quel est ta section'

    col_moyen = next((c for c in df.columns if 'moyens de contact' in c.lower()), None)
    col_info = next((c for c in df.columns if 'informations de contact' in c.lower() or 'tag discord' in c.lower()),
                    None)
    col_autre = next((c for c in df.columns if 'autre(s) information(s)' in c.lower()), None)

    mask_tutore = (
            df[col_role].astype(str).str.contains("aide", case=False, na=False) &
            ~df[col_role].astype(str).str.contains("aider", case=False, na=False)
    )
    mask_tuteur = df[col_role].astype(str).str.contains("aider", case=False, na=False)

    df_tutores = df[mask_tutore].copy()
    df_tuteurs = df[mask_tuteur].copy()

    if not st.session_state.assignments:
        tuteur_load = {row[col_email]: 0 for _, row in df_tuteurs.iterrows()}
        for _, tutore in df_tutores.iterrows():
            tut_id = tutore[col_id]
            tut_sec = tutore[col_section]

            tuteurs_compatibles = df_tuteurs[df_tuteurs[col_section] == tut_sec]
            assigned = None
            for _, tut_row in tuteurs_compatibles.iterrows():
                t_mail = tut_row[col_email]
                if tuteur_load[t_mail] < max_capacity:
                    assigned = t_mail
                    tuteur_load[t_mail] += 1
                    break
            st.session_state.assignments[tut_id] = assigned if assigned else "Aucun"

    if st.sidebar.button("🔄 Réinitialiser le matching auto"):
        st.session_state.assignments = {}
        st.rerun()

    sections_dispo = ["Toutes"] + sorted(list(df[col_section].dropna().unique()))
    selected_section = st.sidebar.selectbox("Filtrer par Section", sections_dispo)

    if selected_section != "Toutes":
        df_tutores_filtered = df_tutores[df_tutores[col_section] == selected_section]
        df_tuteurs_filtered = df_tuteurs[df_tuteurs[col_section] == selected_section]
    else:
        df_tutores_filtered = df_tutores
        df_tuteurs_filtered = df_tuteurs

    # =========================================================================
    # 5. TABLEAU DE BORD & METRIQUES
    # =========================================================================
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    total_tutores = len(df_tutores_filtered)
    total_tuteurs = len(df_tuteurs_filtered)

    assigned_count = sum(
        1 for tid in df_tutores_filtered[col_id]
        if st.session_state.assignments.get(tid) and st.session_state.assignments.get(tid) != "Aucun"
    )
    unassigned_count = total_tutores - assigned_count

    col_m1.metric("Demandes Tutorés (B1)", total_tutores)
    col_m2.metric("Offres Tuteurs (B2/B3)", total_tuteurs)
    col_m3.metric("Binômes Formés", assigned_count, delta=f"{assigned_count}/{total_tutores}")
    col_m4.metric(
        "Non Assignés (En attente)",
        unassigned_count,
        delta_color="inverse" if unassigned_count > 0 else "normal"
    )

    st.divider()

    # =========================================================================
    # 6. ONGLETS D'ORGANISATION
    # =========================================================================
    tab_organisation, tab_tuteurs, tab_unassigned, tab_export = st.tabs([
        "🔀 Organisation des Binômes",
        "👥 Charge & Capacité Tuteurs",
        "⚠️ Analyse des Pénuries",
        "📥 Exporter & Sauvegarder"
    ])

    with tab_organisation:
        st.subheader("Ajustement & Validation des Binômes")
        st.caption("Sélectionnez ou modifiez le tuteur de chaque étudiant B1.")

        tuteur_options_dict = {"Aucun": "⚠️ Aucun (Non assigné)"}
        for _, t_row in df_tuteurs.iterrows():
            tuteur_options_dict[t_row[col_email]] = f"{t_row[col_nom]} ({t_row[col_section]})"

        for _, tutore in df_tutores_filtered.iterrows():
            tut_id = tutore[col_id]
            tut_nom = tutore[col_nom]
            tut_mail = tutore[col_email]
            tut_sec = tutore[col_section]

            tut_moyen = tutore[col_moyen] if col_moyen else ""
            tut_info = tutore[col_info] if col_info else ""
            tut_autre = tutore[col_autre] if col_autre else ""

            current_tuteur_mail = st.session_state.assignments.get(tut_id, "Aucun")

            with st.container():
                c1, c2, c3, c4 = st.columns([2.5, 2.5, 1.2, 1.8])

                with c1:
                    st.markdown(f"**{tut_nom}** {get_badge_html(tut_sec)}", unsafe_allow_html=True)
                    st.caption(f"📧 {tut_mail}")

                with c2:
                    options_keys = list(tuteur_options_dict.keys())
                    default_index = options_keys.index(current_tuteur_mail) if current_tuteur_mail in options_keys else 0

                    new_tuteur = st.selectbox(
                        f"Tuteur pour {tut_nom}",
                        options=options_keys,
                        format_func=lambda x: tuteur_options_dict[x],
                        index=default_index,
                        key=f"select_{tut_id}",
                        label_visibility="collapsed"
                    )

                    if new_tuteur != current_tuteur_mail:
                        st.session_state.assignments[tut_id] = new_tuteur
                        st.rerun()

                with c3:
                    if new_tuteur != "Aucun":
                        st.markdown("<span class='status-ok'>✓ Assigné</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='status-alert'>✗ En attente</span>", unsafe_allow_html=True)

                with c4:
                    if new_tuteur != "Aucun":
                        t_match = df_tuteurs[df_tuteurs[col_email] == new_tuteur]
                        if not t_match.empty:
                            t_row = t_match.iloc[0]
                            t_nom = t_row[col_nom]
                            t_moyen = t_row[col_moyen] if col_moyen else ""
                            t_info = t_row[col_info] if col_info else ""

                            mailto = build_mailto_link(
                                tut_mail, new_tuteur,
                                tut_nom, t_nom,
                                tut_sec,
                                tut_moyen, tut_info, tut_autre,
                                t_moyen, t_info
                            )
                            if mailto:
                                st.link_button("📧 Envoyer Mailto", mailto)
                    else:
                        st.button("En attente", key=f"btn_warn_{tut_id}", disabled=True)

                with st.expander(f"🔍 Détails contact & besoins de {tut_nom}"):
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        st.markdown(f"**Préférence contact :** {clean_val(tut_moyen)}")
                        st.markdown(f"**Tag / Téléphone :** `{clean_val(tut_info)}`")
                    with dc2:
                        st.markdown(f"**Remarque / Demande spécifique :** {clean_val(tut_autre)}")

                st.divider()

    with tab_tuteurs:
        st.subheader("Disponibilité & Étudiants pris en charge par Tuteur")

        tuteur_assigned_list = {t_mail: [] for t_mail in df_tuteurs_filtered[col_email]}

        for tut_id, t_mail in st.session_state.assignments.items():
            if t_mail in tuteur_assigned_list:
                tut_row = df_tutores[df_tutores[col_id] == tut_id]
                if not tut_row.empty:
                    tuteur_assigned_list[t_mail].append(tut_row.iloc[0][col_nom])

        for _, t_row in df_tuteurs_filtered.iterrows():
            t_mail = t_row[col_email]
            t_nom = t_row[col_nom]
            t_sec = t_row[col_section]
            t_moyen = t_row[col_moyen] if col_moyen else ""
            t_info = t_row[col_info] if col_info else ""

            assigned_students = tuteur_assigned_list.get(t_mail, [])
            count = len(assigned_students)

            col_t1, col_t2, col_t3 = st.columns([3, 2, 3])

            with col_t1:
                st.markdown(f"**{t_nom}** {get_badge_html(t_sec)}", unsafe_allow_html=True)
                st.caption(f"📧 {t_mail} | `{clean_val(t_info)}` ({clean_val(t_moyen)})")

            with col_t2:
                if count >= max_capacity:
                    st.markdown(f"<span class='status-warning'>🟡 Complet ({count}/{max_capacity})</span>", unsafe_allow_html=True)
                elif count > 0:
                    st.markdown(f"<span class='status-ok'>🟢 Actif ({count}/{max_capacity})</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='status-alert'>⚪ Disponible (0/{max_capacity})</span>", unsafe_allow_html=True)

            with col_t3:
                if assigned_students:
                    st.markdown("**Élèves pris en charge :** " + ", ".join(assigned_students))
                else:
                    st.caption("Aucun étudiant assigné pour le moment.")

            st.divider()

    with tab_unassigned:
        st.subheader("Détail des étudiants non assignés")

        unassigned_df = []
        for _, tutore in df_tutores.iterrows():
            tut_id = tutore[col_id]
            if st.session_state.assignments.get(tut_id) in ["Aucun", None]:
                unassigned_df.append({
                    "Nom Tutoré": tutore[col_nom],
                    "Email": tutore[col_email],
                    "Section": tutore[col_section],
                    "Contact Souhaité": clean_val(tutore[col_moyen] if col_moyen else ""),
                    "Précisions / Demande": clean_val(tutore[col_autre] if col_autre else "")
                })

        if unassigned_df:
            st.warning(f"Il y a actuellement **{len(unassigned_df)} tutoré(s)** en attente d'un tuteur.")
            st.dataframe(pd.DataFrame(unassigned_df), use_container_width=True)
        else:
            st.success("🎉 Tous les tutorés B1 ont un tuteur assigné !")

    with tab_export:
        st.subheader("Exporter l'Assemblée Générée")
        st.write("Téléchargez le fichier récapitulatif final au format Excel pour vos archives ou le comité.")

        export_data = []
        for _, tutore in df_tutores.iterrows():
            tut_id = tutore[col_id]
            t_mail = st.session_state.assignments.get(tut_id, "Aucun")

            t_nom = "Non assigné"
            if t_mail != "Aucun":
                t_match = df_tuteurs[df_tuteurs[col_email] == t_mail]
                if not t_match.empty:
                    t_nom = t_match.iloc[0][col_nom]

            export_data.append({
                "ID Tutoré": tut_id,
                "Nom Tutoré": tutore[col_nom],
                "Email Tutoré": tutore[col_email],
                "Section": tutore[col_section],
                "Contact Tutoré": clean_val(tutore[col_moyen] if col_moyen else ""),
                "Info Contact Tutoré": clean_val(tutore[col_info] if col_info else ""),
                "Remarques Tutoré": clean_val(tutore[col_autre] if col_autre else ""),
                "Nom Tuteur Assigné": t_nom,
                "Email Tuteur Assigné": t_mail
            })

        df_export = pd.DataFrame(export_data)
        st.dataframe(df_export, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Binomes_Tutorat')

        st.download_button(
            label="📊 Télécharger au format Excel (.xlsx)",
            data=buffer.getvalue(),
            file_name="Matching_Tutorat_HELMo_CEI.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("👈 Veuillez importer votre fichier Forms (CSV ou Excel) dans la barre latérale pour activer la plateforme.")