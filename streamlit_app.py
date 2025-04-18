import streamlit as st
import pandas as pd

k1 = st.secrets["magic"]["k1"]
k2 = st.secrets["magic"]["k2"]
k3 = st.secrets["magic"]["k3"]

st.set_page_config(
    page_title="Abyssus - Aide à la chasse",
    layout="wide"
)

st.markdown("""
    <style>
    body {
        background: linear-gradient(#000000, #010547);
        height: 100vh;
    }
    .stApp {
        background: transparent;
    }
    </style>
""", unsafe_allow_html=True)

# DATAFRAMES

unites_stats = pd.DataFrame({
    "Unité" : ["Petite Roussette", "Roussette", "Requin Blanc"],
    "Attaque" : [60, 100, 1100],
    "Défense" : [40, 60, 1],
    "Vie" : [70, 100, 600]
})
unites_stats.set_index("Unité", inplace=True)

def calcul_fdf_par_chasse():
    fdf_totale = 0
    for unite_nom, row in unites_joueur.iterrows():
        nombre = row["Nombre"]
        if unite_nom in unites_stats.index:
            attaque = unites_stats.loc[unite_nom, "Attaque"]
            fdf_totale += nombre * (attaque + attaque * 0.1 * morsure)
    return fdf_totale / instinct_chasse



# SIDEBAR
spacer, col1 , spacer, col2, spacer = st.columns([0.3, 1, 0.3, 1, 0.3])

with col1:
    st.title("Champs à remplir")

    sous_col1, spacer, sous_col2 = st.columns([1, 0.5, 1])

    with sous_col1:
        nb_petite_roussette = st.number_input("Nombre de Petites Roussettes", min_value=0, step=1, value=0)
        nb_roussette = st.number_input("Nombre de Roussettes", min_value=0, step=1, value=0)
        nb_requin_blanc = st.number_input("Nombre de Requins Blancs", min_value=0, step=1, value=0)

        unites_joueur = pd.DataFrame({
            "Unité": ["Petite Roussette", "Roussette", "Requin Blanc"],
            "Nombre": [nb_petite_roussette, nb_roussette, nb_requin_blanc]
        }).set_index("Unité")

    with sous_col2:
        morsure = st.number_input("Niveau de morsure", min_value=1)
        instinct_chasse = st.number_input("Niveau d'instinct de chasse", min_value=1)
        tm_arrivee = st.number_input("TM à l'arrivée de la chasse (en Millions)", min_value=1, max_value=100, placeholder='Écris "5" pour 5M')

coef_magique = (k1 / (float(tm_arrivee) ** k2)) * (1 / (k3 ** float(tm_arrivee)))
tm_chasse = int(coef_magique * calcul_fdf_par_chasse())

# RESULTATS
with col2:
    st.title("Données calculées")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(label="Nombre de chasses", value=instinct_chasse)
        st.metric(label="TM par chasse", value=tm_chasse)

    with col2:
        st.metric(label="Petites Roussettes à envoyer", value=int(nb_petite_roussette / instinct_chasse))
        st.metric(label="Roussettes à envoyer", value=int(nb_roussette / instinct_chasse))
        st.metric(label="Requins Blancs à envoyer", value=int(nb_requin_blanc / instinct_chasse))


st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        color: white;
        font-size: 0.9em;
    }
    </style>

    <div class="footer">
        Créé avec ❤️ par Samutus / Shapzen
    </div>
""", unsafe_allow_html=True)
