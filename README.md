# 🎓 Hub d'Organisation du Tutorat - HELMo CEI

Application web construite avec Streamlit pour automatiser et faciliter le matching, l'ajustement manuel et la mise en relation par e-mail entre étudiants de Bloc 1 (tutorés) et de Blocs 2/3 (tuteurs).

## 🚀 Fonctionnalités principales

- **Appariement automatique** : Pré-matching basé sur la section d'étude et la capacité maximale de chaque tuteur.
- **Ajustement manuel** : Interface permettant de réattribuer facilement les tuteurs ou de gérer les cas particuliers.
- **Génération automatique de `mailto:`** : Boutons d'envoi d'e-mails pré-remplis avec toutes les consignes et détails de contact pour chaque binôme.
- **Suivi de la charge** : Visualisation en temps réel de la disponibilité et du nombre d'étudiants assignés par tuteur.
- **Analyse des pénuries** : Détection automatique des tutorés sans tuteur.
- **Export Excel** : Téléchargement récapitulatif des binômes formés au format `.xlsx`.

## 🛠️ Installation et Lancement

### Prérequis

- Python 3.10 ou supérieur
- Git

### 1. Cloner le dépôt

```bash
git clone [https://github.com/cei-helmo/cei-tutorat-app.git](https://github.com/cei-helmo/cei-tutorat-app.git)
cd cei-tutorat-app
```

### 2. Créer un environnement virtuel

```bash
# Sur Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Sur Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt

```

### 4. Configuration des données (Anonymisation)

Afin d'éviter tout leak de données sensibles (adresses e-mail de responsables, nom de la structure, etc.), créez un fichier `config.json` à partir du fichier modèle :

```bash
cp config.example.json config.json

```

Modifiez ensuite `config.json` selon vos besoins :

```json
{
  "academic_year": "2026-2027",
  "organization_name": "Cercle Étudiant HELMo CEI",
  "email_subject_prefix": "[CEI] Tutorat",
  "responsible": {
    "name": "Responsable Tutorat",
    "email": "votre.email@student.helmo.be"
  }
}

```

> **Note :** Le fichier `config.json` est ignoré par Git (via `.gitignore`) pour protéger vos données confidentielles.

### 5. Lancer l'application

```bash
streamlit run app.py

```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse : `http://localhost:8501`.


## 📂 Format du Fichier d'Entrée (Forms / Excel / CSV)

Le fichier importé via la barre latérale doit idéalement comporter les colonnes suivantes :

| Colonne requis / optionnel | Nom attendu dans le fichier |
| --- | --- |
| **Identifiant** | `Id` ou première colonne |
| **Nom / Prénom** | `Nom` |
| **Adresse e-mail** | `Adresse de messagerie` |
| **Rôle** | `Que souhaitez-vous ?` *(Contenant "aide" pour les tutorés et "aider" pour les tuteurs)* |
| **Section** | `Quel est ta section` |
| **Moyens de contact** *(Optionnel)* | Doit contenir `"moyens de contact"` |
| **Info / Tag Discord** *(Optionnel)* | Doit contenir `"informations de contact"` ou `"tag discord"` |
| **Remarques** *(Optionnel)* | Doit contenir `"autre(s) information(s)"` |

## 🔒 Sécurité & Confidentialité

* **Aucune donnée sensible stockée à distance** : Tout le traitement s'effectue en mémoire locale lors de la session.
* **`.gitignore` inclus** : Bloque automatiquement l'envoi de `config.json` ainsi que de tout fichier `.xlsx` ou `.csv` déposé dans le projet.

## 📄 Licence
Ce projet est distribué sous licence Open-Source. Utilisation libre pour les cercles étudiants et institutions académiques.