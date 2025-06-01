import streamlit as st
import random
import pandas as pd

def generate_validators(num_validators, max_stake_per_validator):
    # Générer des stakes initiaux aléatoires (supposés gros ou petits)
    validators = []
    for i in range(1, num_validators + 1):
        # Stake random avant plafonnement, ex entre 50 et 500 tokens
        raw_stake = random.randint(50, 500)
        # Appliquer le plafond max stake
        stake = min(raw_stake, max_stake_per_validator)
        validators.append({"id": f"Validator_{i}", "stake": stake})
    return validators

def select_validators(validators, num_selected, seed):
    random.seed(seed)
    total_stake = sum(v["stake"] for v in validators)
    # Probabilité pondérée par stake
    weighted_validators = []
    for v in validators:
        # pondération : stake / total_stake
        weight = v["stake"] / total_stake if total_stake > 0 else 0
        weighted_validators.append((v, weight))
    
    selected = []
    # Tirage sans remise pondéré (approximation par random.choices)
    # Comme random.choices permet tirage avec remise, on fait une boucle en vérifiant d'avoir pas de doublons
    candidates = validators.copy()
    weights = [v["stake"] for v in candidates]
    while len(selected) < min(num_selected, len(validators)):
        choice = random.choices(candidates, weights=weights, k=1)[0]
        if choice not in selected:
            selected.append(choice)
    return selected

# Streamlit UI

st.title("Simulation de la sélection des validateurs PoS avec plafonnement et rotation")

# Paramètres utilisateur
num_validators = st.sidebar.slider("Nombre de validateurs", min_value=5, max_value=50, value=20)
max_stake_per_validator = st.sidebar.slider("Plafond max stake par validateur", min_value=50, max_value=500, value=200)
num_selected = st.sidebar.slider("Nombre de validateurs sélectionnés par round", min_value=1, max_value=10, value=5)
seed = st.sidebar.number_input("Seed pour rotation / randomisation", min_value=0, max_value=10000, value=42)

# Génération des validateurs
validators = generate_validators(num_validators, max_stake_per_validator)

# Affichage des validateurs
df_validators = pd.DataFrame(validators)
df_validators = df_validators.sort_values(by="stake", ascending=False).reset_index(drop=True)
st.subheader("Liste des validateurs (triés par stake)")
st.dataframe(df_validators)

# Simulation sélection validateurs pour un round
selected = select_validators(validators, num_selected, seed)

# Affichage sélectionnés
st.subheader(f"Validateurs sélectionnés pour le round (seed={seed})")

df_selected = pd.DataFrame(selected)
total_selected_stake = sum(v["stake"] for v in selected)
df_selected["stake_share (%)"] = df_selected["stake"] / total_selected_stake * 100

st.dataframe(df_selected)

# Visualisation graphique
st.subheader("Répartition du stake parmi les validateurs sélectionnés")

st.bar_chart(df_selected.set_index("id")["stake_share (%)"])

st.markdown("""
---
### Explications :

- Chaque validateur a un stake plafonné à la valeur définie.
- La sélection des validateurs pour valider un round est pondérée par leur stake, mais la rotation est introduite via la seed.
- Ce système limite la centralisation en plafonnant le stake et en changeant les validateurs sélectionnés à chaque round.
""")
