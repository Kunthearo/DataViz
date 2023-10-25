#! /bin/python
# -*- coding: utf-8 -*-
#
# DataVizProject.py
#
# Quelles sont les facteurs qui aggravent les accidents de vélo ?

__author__ = "Kevin OP"
__copyright__ = "Copyright 2023, DataVizProject 2023"
__credits__ = ["Kevin OP"]
__version__ = "0.0.1"
__maintainer__ = "Kevin OP"
__email__ = "kevin.op@efrei.net"
__status__ = "Research code"

import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np

def load_data():
    df = pd.read_csv('accidentsVelo.csv')
    return df

data = load_data()

st.title("Étude sur les accidents de vélo")

st.header("Quelles sont les facteurs qui aggravent les accidents de vélo ? :bike:", help="Données en France entre 2005 et 2021")

st.write("Avant de commencer notre étude de données pour savoir quelles sont les facteurs qui "
        "augmentent les risques d'accident à vélo, il serait intéressant de voir la "
        "répartition de ces accidents en France.")

data['lat'] = pd.to_numeric(data['lat'], errors='coerce')
data['long'] = pd.to_numeric(data['long'], errors='coerce')

center_latitude = 46.603354
center_longitude = 1.888334

unique_grav_values = data['grav'].unique()

color_mapping = {
    1: [255, 0, 0],
    2: [0, 255, 0],
    3: [0, 0, 255],
    4: [255, 255, 0]
}

data['color'] = data['grav'].map(color_mapping)

grav_mapping = {
    1: 'Indemne',
    2: 'Tué',
    3: 'Blessé hospitalisé',
    4: 'Blessé léger'
}

data['grav'] = data['grav'].map(grav_mapping)

sexe_mapping = {
    -1: 'Non renseigné',
    1: 'Masculin',
    2: 'Féminin'
}

data['sexe'] = data['sexe'].map(sexe_mapping)

grav_filter = st.multiselect("Sélectionne la gravité des blessés:", data['grav'].unique(), default=data['grav'].unique())
sexe_filter = st.multiselect("Sélectionne le sexe:", data['sexe'].unique(), default=data['sexe'].unique())

filtered_data = data[(data['grav'].isin(grav_filter)) & (data['sexe'].isin(sexe_filter))]

layer = pdk.Layer(
    'ScatterplotLayer',
    filtered_data,
    get_position='[long, lat]',
    get_radius=1000,
    get_color='color',
    pickable=True
)

view_state = pdk.ViewState(
    latitude=center_latitude,
    longitude=center_longitude,
    zoom=4.5
)

r = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
)

st.pydeck_chart(r, use_container_width=True)

st.write("La cartographie nous révèle sans surprises que la majorité des accidents sont provoqués "
         "autour des grandes métropoles, là où se concentrent de fortes densités de population "
         "et un trafic plus dense...")

st.write(" ")

st.write("Si la répartition géographique semble logique, qu'en est-t-il de la répartition temporelle ?")

reverse_grav_mapping = {v: k for k, v in grav_mapping.items()}
data['grav'] = data['grav'].map(reverse_grav_mapping)

fig, ax = plt.subplots(figsize=(14, 8))

cumulative_sums = []
grouped_data = 0
for i, grav_value in enumerate(unique_grav_values):
    grav_data = data[data['grav'] == grav_value]
    grouped_data = grav_data.groupby('an')['grav'].size()

    if i == 0:
        cumulative_sums.append(grouped_data)
    else:
        cumulative_sums.append(cumulative_sums[i - 1] + grouped_data)

for i, grav_value in enumerate(unique_grav_values):
    label = f'{grav_mapping[grav_value]}'
    sns.lineplot(x=grouped_data.index, y=cumulative_sums[i], label=label)

plt.xlabel("Année")
plt.ylabel('Nombre de personnes')
plt.title("Évolution du nombre de personnes accidentés")
st.pyplot(fig)

st.write("Ce graphique montre une certaine baisse d'accidents de vélo au cours de ces dernières années "
         "avec une chute significative des accidents en 2018, juste avant l'arrivée du Covid en France. "
         "Hormis pour l'année 2018, on peut remarquer que presque la moitié des accidents de vélo peut "
         "conduire à une hospitalisation ou même à la mort. ")

st.write(" ")

st.subheader("Quels sont donc les facteurs qui augmentent les risques ?")

st.subheader("CARACTERISTIQUES")

st.write("Lorsqu'on parle d'accidents de la route que ce soient des accidents de vélos ou de voitures, il est "
         "important de voir dans quels conditions l'accident a eu lieu pour vérifier s'il y a une quelconque "
         "corrélation entre les caractéristiques et les risques d'accident.")

st.write("Le graphique ci-dessous montre le nombre d'accidents en fonction des conditions métérologiques, "
         "de l'état de la surface (route) et de la luminosité")

selected_graph = st.selectbox("Choisis le type de données", ["Atmosphère", "Surface", "Luminosité"])

atm_mapping = {
    -1: 'Non renseigné',
    1: 'Normale',
    2: 'Pluie légère',
    3: 'Pluie forte',
    4: 'Neige - grêle',
    5: 'Brouillard - fumée',
    6: 'Vent fort - tempête',
    7: 'Temps éblouissant',
    8: 'Temps couvert',
    9: 'Autre',
}

surf_mapping = {
    -1: 'Non renseigné',
    1: 'Normale',
    2: 'Mouillée',
    3: 'Flaques',
    4: 'Inondée',
    5: 'Enneigée',
    6: 'Boue',
    7: 'Verglacée',
    8: 'Corps gras - huile',
    9: 'Autre'
}

lum_mapping = {
    1: 'Plein jour',
    2: 'Crépuscule ou aube',
    3: 'Nuit sans éclairage public',
    4: 'Nuit avec éclairage public non allumé',
    5: 'Nuit avec éclairage public allumé',
}

data['grav'] = data['grav'].map(grav_mapping)
data['atm'] = data['atm'].map(atm_mapping)
data['surf'] = data['surf'].map(atm_mapping)
data['lum'] = data['lum'].map(lum_mapping)

if selected_graph == 'Atmosphère':
    selected_atm_category = st.selectbox("Choisis une variable à étudier", data['atm'].unique())
    filtered_data = data[data['atm'] == selected_atm_category]

    for category in filtered_data['atm'].unique():
        grav_counts = filtered_data[filtered_data['atm'] == category]['grav'].value_counts().reset_index()
        grav_counts['log_count'] = np.log(grav_counts['count'])
        fig = px.bar(grav_counts, x='grav', y='log_count', title=f'Répartition de la gravité des blessures liée à la catégorie Atmosphère pour la variable {category}')
        fig.update_traces(text=grav_counts['count'], texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig)

        total_count = grav_counts['count'].sum()
        grav_counts['pourcentage'] = (grav_counts['count'] / total_count) * 100
        st.table(grav_counts[['grav', 'pourcentage']])

if selected_graph == 'Surface':
    selected_surf_category = st.selectbox("Choisis une variable à étudier", data['surf'].unique())
    filtered_data = data[data['surf'] == selected_surf_category]

    for category in filtered_data['surf'].unique():
        grav_counts = filtered_data[filtered_data['surf'] == category]['grav'].value_counts().reset_index()
        grav_counts['log_count'] = np.log(grav_counts['count'])
        fig = px.bar(grav_counts, x='grav', y='log_count', title=f'Répartition de la gravité des blessures liée à la catégorie Surface pour la variable {category}')
        fig.update_traces(text=grav_counts['count'], texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig)

        total_count = grav_counts['count'].sum()
        grav_counts['pourcentage'] = (grav_counts['count'] / total_count) * 100
        st.table(grav_counts[['grav', 'pourcentage']])

elif selected_graph == 'Luminosité':
    selected_lum_category = st.selectbox("Choisis une variable à étudier", data['lum'].unique())
    filtered_data = data[data['lum'] == selected_lum_category]

    for category in filtered_data['lum'].unique():
        grav_counts = filtered_data[filtered_data['lum'] == category]['grav'].value_counts().reset_index()
        grav_counts['log_count'] = np.log(grav_counts['count'])
        fig = px.bar(grav_counts, x='grav', y='log_count', title=f'Répartition de la gravité des blessures liée à la catégorie Luminosité pour la variable {category}')
        fig.update_traces(text=grav_counts['count'], texttemplate='%{text}', textposition='inside')
        st.plotly_chart(fig)

        total_count = grav_counts['count'].sum()
        grav_counts['pourcentage'] = (grav_counts['count'] / total_count) * 100
        st.table(grav_counts[['grav', 'pourcentage']])

st.write("Contrairement à ce que l'on pourrait penser au premier abord, la plupart des accidents surviennent "
         "dans des conditions assez normales. Même une petite pluie ne rajoute que très peu de risques d'accidents. "
         "En revanche, il est clair que plus les conditions sont mauvaises, plus les risques sont grands. "
         "On remarque aisément que la part de pourcentage des blessés 'seulement' légèrement diminuent lorsque "
         "les conditions sont mauvaises alors que la part des hospitalisés augmentent.")

st.write(" ")

st.subheader("VEHICULES")

catv_mapping = {
    '0': 'Indéterminable',
    '1': 'Bicyclette',
    '2': 'Cyclomoteur <50cm3',
    '3': 'Voiturette (Quadricycle à moteur carrossé)',
    '4': 'Référence inutilisée depuis 2006 (scooter immatriculé)',
    '5': 'Référence inutilisée depuis 2006 (motocyclette)',
    '6': 'Référence inutilisée depuis 2006 (side-car)',
    '7': 'VL seul',
    '8': 'Référence inutilisée depuis 2006 (VL + caravane)',
    '9': 'Référence inutilisée depuis 2006 (VL + remorque)',
    '10': 'VU seul 1,5T <= PTAC <= 3,5T avec ou sans remorque',
    '11': 'Référence inutilisée depuis 2006 (VU (10) + caravane)',
    '12': 'Référence inutilisée depuis 2006 (VU (10) + remorque)',
    '13': 'PL seul 3,5T <PTCA <= 7,5T',
    '14': 'PL seul > 7,5T',
    '15': 'PL > 3,5T + remorque',
    '16': 'Tracteur routier seul',
    '17': 'Tracteur routier + semi-remorque',
    '18': 'Référence inutilisée depuis 2006 (transport en commun)',
    '19': 'Référence inutilisée depuis 2006 (tramway)',
    '20': 'Engin spécial',
    '21': 'Tracteur agricole',
    '30': 'Scooter < 50 cm3',
    '31': 'Motocyclette > 50 cm3 et <= 125 cm3',
    '32': 'Scooter > 50 cm3 et <= 125 cm3',
    '33': 'Motocyclette > 125 cm3',
    '34': 'Scooter > 125 cm3',
    '35': 'Quad léger <= 50 cm3 (Quadricycle à moteur non carrossé)',
    '36': 'Quad lourd > 50 cm3 (Quadricycle à moteur non carrossé)',
    '37': 'Autobus',
    '38': 'Autocar',
    '39': 'Train',
    '40': 'Tramway',
    '41': '3RM <= 50 cm3',
    '42': '3RM > 50 cm3 <= 125 cm3',
    '43': '3RM > 125 cm3',
    '50': 'EDP à moteur',
    '60': 'EDP sans moteur',
    '80': 'VAE',
    '99': 'Autre véhicule',
}

col1, col2 = st.columns(2)

catv_counts = data['typevehicules'].value_counts().reset_index()
catv_counts.columns = ['typevehicules', 'count']

catv_counts = catv_counts.sort_values(by='count', ascending=False)

catv_counts['typevehicules'] = catv_counts['typevehicules'].map(catv_mapping)

first_catv = catv_counts.iloc[0]

first_catv_dict = {first_catv['typevehicules']: first_catv['count']}

with col1:
    st.write("Véhicule le plus dangereux")
    st.write("")
    st.bar_chart(first_catv_dict)

next_10_catv = catv_counts.iloc[1:11]

next_10_catv_dict = {row['typevehicules']: row['count'] for _, row in next_10_catv.iterrows()}

with col2:
    st.write("Top 10 des véhicules les plus dangereux (sans le Top 1 bien sûr :joy_cat:)")
    st.bar_chart(next_10_catv_dict)

st.write("Le cas le plus dangereux est sans contexte le cas du véhicule seul. ")

st.write(" ")

st.subheader("USAGERS")

st.write("Nous arrivons désormais à la dernière catégorie, celle des USAGERS. L'étude de cette catégorie est indispensable "
         "pour vérifier dans quelle contexte est-ce que les accidents ont lieu. Mais avant de regarder le contexte, qu'en "
         "est-il de la proportion homme/femme ?")

fig2, ax2 = plt.subplots(figsize=(12, 6))

sexe_counts = data['sexe'].value_counts().reset_index()
sexe_counts.columns = ['Sexe', 'Count']
sexe_counts = sexe_counts[sexe_counts['Sexe'] != 'Non renseigné']

plt.pie(sexe_counts['Count'], labels=sexe_counts['Sexe'], autopct='%1.1f%%', startangle=120, colors=sns.color_palette('pastel'))
plt.title('Répartition des accidents en fonction du sexe')
st.pyplot(fig2)

st.write("")

unique_trajet_values = [ 5, 4, 0, 3, 1, 2, 9]
unique_mois_values = data['mois'].unique()

counts = [len(data[data['trajet'] == trajet]) for trajet in unique_trajet_values]
unique_trajet_values = sorted(unique_trajet_values, key=lambda trajet: len(data[data['trajet'] == trajet]), reverse=True)

trajet_mapping = {
    0: 'Non renseigné',
    1: 'Domicile - Travail',
    2: 'Domicile - École',
    3: 'Courses - Achats',
    4: 'Utilisation professionnelle',
    5: 'Promenade - Loisirs',
    9: 'Autre'
}

fig3, ax3 = plt.subplots(figsize=(14, 8))

colors = sns.color_palette("bright", len(unique_trajet_values))

cumulative_sums = []
for i, trajet_value in enumerate(unique_trajet_values):
    trajet_data = data[data['trajet'] == trajet_value]
    grouped_data = trajet_data.groupby('mois')['trajet'].size()

    if i == 0:
        cumulative_sums.append(grouped_data)
    else:
        cumulative_sums.append(cumulative_sums[i - 1] + grouped_data)

for i, trajet_value in enumerate(unique_trajet_values):
    label = f'{trajet_mapping[trajet_value]}'
    sns.lineplot(x=grouped_data.index, y=cumulative_sums[i], label=label, color=colors[i])

plt.xlabel("Mois")
plt.ylabel('Nombre de personnes')
plt.title("Évolution du nombre de personnes accidentés en fonction du mois")
st.pyplot(fig3)

st.write("Nous pouvons constater un hausse d'accidents au début des vacances d'été et où le temps est propice "
         "à faire du vélo. À l'inverse, il y a une faible proportion de personnes en période de froid.")

st.write(" ")

st.subheader("Bibliographie")

st.write("Auteur du site: Kevin OP")
st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/kevin-op/)")

st.write("Dans le cadre d'un projet de EFREI Paris")
url = "https://www.cfa-afia.com/app/uploads/2022/01/logo-efrei-blanc-web.png"
st.image(url, use_column_width=True)
st.subheader("#datavz2023efrei")
