
import streamlit as st
import pandas as pd
import json
from io import BytesIO

# Chargement des utilisateurs
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def authenticate(username, password, users):
    return username in users and users[username]["password"] == password

def get_role(username, users):
    return users[username]["role"]

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

users = load_users()

st.title("📦 Gestion de Stock - Multi-utilisateur")

if "user" not in st.session_state:
    st.session_state.user = None

# Connexion
if not st.session_state.user:
    st.subheader("🔐 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if authenticate(username, password, users):
            st.session_state.user = username
            st.success(f"Bienvenue, {username} !")
        else:
            st.error("Identifiants incorrects.")

# Si connecté
if st.session_state.user:
    user_role = get_role(st.session_state.user, users)
    st.sidebar.success(f"Connecté en tant que : {st.session_state.user} ({user_role})")

    # Zone admin
    if user_role == "admin":
        st.sidebar.subheader("🛠️ Gestion des utilisateurs")
        with st.sidebar.expander("➕ Créer un utilisateur"):
            new_user = st.text_input("Nom nouvel utilisateur")
            new_pass = st.text_input("Mot de passe", type="password", key="newpass")
            role = st.selectbox("Rôle", ["utilisateur", "admin"])
            if st.button("Créer"):
                if new_user in users:
                    st.warning("Utilisateur déjà existant.")
                else:
                    users[new_user] = {"password": new_pass, "role": role}
                    save_users(users)
                    st.success("Utilisateur créé.")

        with st.sidebar.expander("🗑️ Supprimer un utilisateur"):
            to_delete = st.selectbox("Sélectionner", list(users.keys()))
            if st.button("Supprimer"):
                if to_delete == "admin":
                    st.warning("Impossible de supprimer l'administrateur.")
                else:
                    users.pop(to_delete)
                    save_users(users)
                    st.success("Utilisateur supprimé.")

    # Zone principale (saisie de stock)
    st.header("📋 Saisie du stock journalier")
    produits = ["Guinness", "Doppel", "Beaufort", "Malta"]
    data = []
    for prod in produits:
        cols = st.columns(6)
        init = cols[0].number_input(f"{prod} - Stock initial", key=f"i_{prod}")
        entree = cols[1].number_input(f"{prod} - Entrée", key=f"e_{prod}")
        sortie = cols[2].number_input(f"{prod} - Vente", key=f"s_{prod}")
        prix = cols[3].number_input(f"{prod} - Prix", key=f"p_{prod}")
        wave = cols[4].number_input(f"{prod} - Wave", key=f"w_{prod}")
        credit = cols[5].number_input(f"{prod} - Crédit", key=f"c_{prod}")
        final = init + entree - sortie
        total = sortie * prix
        data.append([prod, init, entree, sortie, final, prix, total, wave, credit])

    if st.button("📥 Générer rapport"):
        df = pd.DataFrame(data, columns=[
            "Produit", "Stock initial", "Entrée", "Vente", "Stock final",
            "Prix", "Montant vente", "Wave", "Crédit"
        ])
        st.dataframe(df)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Stock", index=False)
        output.seek(0)
        st.download_button("📄 Télécharger rapport", data=output, file_name=f"rapport_{st.session_state.user}.xlsx")

    if st.button("🚪 Se déconnecter"):
        st.session_state.user = None
        st.rerun()
