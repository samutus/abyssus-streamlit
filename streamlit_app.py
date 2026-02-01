import streamlit as st
import pandas as pd
import numpy as np

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
    "Unité": ["Petite Roussette", "Roussette", "Requin Blanc"],
    "Attaque": [60, 100, 1100],
    "Défense": [40, 60, 1],
    "Vie": [70, 100, 600]
})
unites_stats.set_index("Unité", inplace=True)

# TABLE DE RÉFÉRENCE POUR L'INTERPOLATION Tc(Ta)
FDF_REF = 252_000_000_000

TABLE_REF = pd.DataFrame({
    "Ta": [
        1_000_000,
        2_500_000,
        5_000_000,
        10_000_000,
        25_000_000,
        50_000_000,
        100_000_000,
        250_000_000,
        500_000_000,
        1_000_000_000,
        3_000_000_000,
        5_000_000_000,
        10_000_000_000,
    ],
    "Tc": [
        2_128_000_000,
        1_816_000_000,
        1_617_000_000,
        1_437_000_000,
        1_228_000_000,
        1_090_000_000,
        968_000_000,
        829_000_000,
        731_000_000,
        646_000_000,
        509_000_000,
        450_500_000,
        342_800_000,
    ]
})


def interpolation_log_log(ta: float, fdf: float) -> float:
    """
    Interpolation log-log de Tc en fonction de Ta,
    puis scaling linéaire par FDF / FDF_REF.
    
    Reproduit exactement la formule Google Sheets :
    =LET(
      vTa, ...,
      vFdf, ...,
      vFdfRef, $B$4,
      rngTaList, $D$5:$D$17,
      rngTcList, $F$5:$F$17,
      nPts, ROWS(rngTaList),
      idxSeg, IF(vTa<=INDEX(rngTaList,1), 1, IF(vTa>=INDEX(rngTaList,nPts), nPts-1, MATCH(vTa, rngTaList, 1))),
      vTaLo, INDEX(rngTaList, idxSeg),
      vTaHi, INDEX(rngTaList, idxSeg+1),
      vTcLo, INDEX(rngTcList, idxSeg),
      vTcHi, INDEX(rngTcList, idxSeg+1),
      vTcRef, EXP(LN(vTcLo) + (LN(vTa)-LN(vTaLo)) * (LN(vTcHi)-LN(vTcLo)) / (LN(vTaHi)-LN(vTaLo))),
      vTcRef * (vFdf / vFdfRef)
    )
    """
    ta_list = TABLE_REF["Ta"].values
    tc_list = TABLE_REF["Tc"].values
    n = len(ta_list)
    
    # Trouver le segment (équivalent du IF/MATCH)
    if ta <= ta_list[0]:
        idx = 0
    elif ta >= ta_list[-1]:
        idx = n - 2
    else:
        # MATCH(..., 1) en Excel = recherche la plus grande valeur <= ta
        idx = np.searchsorted(ta_list, ta, side='right') - 1
        idx = max(0, min(idx, n - 2))
    
    ta_lo = ta_list[idx]
    ta_hi = ta_list[idx + 1]
    tc_lo = tc_list[idx]
    tc_hi = tc_list[idx + 1]
    
    # Interpolation log-log
    ln_tc = np.log(tc_lo) + (np.log(ta) - np.log(ta_lo)) * (np.log(tc_hi) - np.log(tc_lo)) / (np.log(ta_hi) - np.log(ta_lo))
    tc_ref = np.exp(ln_tc)
    
    # Scaling par FDF
    tc_final = tc_ref * (fdf / FDF_REF)
    
    return tc_final


def calcul_fdf(unites_joueur, morsure):
    """Calcule la FDF totale de l'armée."""
    fdf_totale = 0
    for unite_nom, row in unites_joueur.iterrows():
        nombre = row["Nombre"]
        if unite_nom in unites_stats.index:
            attaque = unites_stats.loc[unite_nom, "Attaque"]
            fdf_totale += nombre * attaque * (1 + 0.1 * morsure)
    return fdf_totale


def calcul_fdf_par_chasse(unites_joueur, morsure, instinct_chasse):
    """Calcule la FDF envoyée par chasse."""
    fdf_totale = calcul_fdf(unites_joueur, morsure)
    if instinct_chasse > 0:
        return fdf_totale / instinct_chasse
    return 0


# SIDEBAR / INPUTS
spacer, col1, spacer2, col2, spacer3 = st.columns([0.3, 1, 0.3, 1, 0.3])

with col1:
    st.title("Champs à remplir")

    sous_col1, spacer_in, sous_col2 = st.columns([1, 0.5, 1])

    with sous_col1:
        nb_petite_roussette = st.number_input("Nombre de Petites Roussettes", min_value=0, step=1, value=0)
        nb_roussette = st.number_input("Nombre de Roussettes", min_value=0, step=1, value=0)
        nb_requin_blanc = st.number_input("Nombre de Requins Blancs", min_value=0, step=1, value=0)

    with sous_col2:
        morsure = st.number_input("Niveau de morsure", min_value=1, value=1)
        instinct_chasse = st.number_input("Niveau d'instinct de chasse", min_value=1, value=1)
        ta_input_millions = st.number_input(
            "TM avant arrivée (en millions)",
            min_value=1,
            max_value=10_000,
            value=50,
            step=1
        )
        ta_input = ta_input_millions * 1_000_000

# Création du DataFrame APRÈS les inputs
unites_joueur = pd.DataFrame({
    "Unité": ["Petite Roussette", "Roussette", "Requin Blanc"],
    "Nombre": [nb_petite_roussette, nb_roussette, nb_requin_blanc]
}).set_index("Unité")

# --- COEUR DU CALCUL ---

fdf_totale = calcul_fdf(unites_joueur, morsure)
fdf_par_chasse = calcul_fdf_par_chasse(unites_joueur, morsure, instinct_chasse)

# Calcul du Tc optimal via interpolation log-log
tc_optimal = interpolation_log_log(ta=ta_input, fdf=fdf_par_chasse)

# -----------------------------------------

# RESULTATS
with col2:
    st.title("Données calculées")

    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.metric(label="Nombre de chasses", value=instinct_chasse)
        st.metric(label="FDF totale", value=f"{int(fdf_totale):,}".replace(",", " "))
        st.metric(label="FDF / chasse", value=f"{int(fdf_par_chasse):,}".replace(",", " "))

    with res_col2:
        st.metric(label="TM maximal / chasse", value=f"{int(tc_optimal):,}".replace(",", " "))
        st.metric(label="Petites Roussettes / chasse", value=int(nb_petite_roussette / instinct_chasse) if instinct_chasse > 0 else 0)
        st.metric(label="Roussettes / chasse", value=int(nb_roussette / instinct_chasse) if instinct_chasse > 0 else 0)
        st.metric(label="Requins Blancs / chasse", value=int(nb_requin_blanc / instinct_chasse) if instinct_chasse > 0 else 0)

    # Alerte si TM maximal / chasse trop faible
    if tc_optimal < 5_000_000:
        st.warning("⚠️ Attention, le TM / chasse est très faible. Descends le TM d'arrivée pour mieux t'adapter à ton armée.")

# SECTION EXPLICATIONS
st.divider()

with st.expander("Explications - Comment utiliser le simulateur ?", expanded=False):
    
    st.markdown("""
    Ce simulateur calcule le TM maximal que tu peux chasser en fonction de ta FDF.

    Plus tu fixes un TM élevé à l'arrivée, plus tu réduis le TM / chasse.

    Cependant, ne soit pas trop gourmand! Tant que le TM / chasse ne monte pas très haut, c'est inutile et dangereux d'augmenter le TM à l'arrivée.

    Exemples :
    - 5G de FDF totale -> 50M de TM d'arrivée
    - 50G de FDF totale -> 250M de TM d'arrivée
    - 250G de FDF totale -> 1G de TM d'arrivée
    - Plus de 1T de FDF totale -> 5G de TM d'arrivée


    /!\ Si ton armée dépasse 1T de FDF totale, le TM maximal / chasse sera bien trop élevé.
    Tu peux donc viser un TM d'arrivée très haut et choisir le TM / chasse que tu souhaites. L'idée est de pexer beaucoup sans lancer des chasses de 1 mois. 

    """)
    
st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        width: 100%;
        text-align: center;
        color: white;
        font-size: 0.9em;
        opacity: 0.7;
    }
    </style>

    <div class="footer">
        Créé avec ❤️ par Samutus - Version 1.1.0
    </div>
""", unsafe_allow_html=True)
