# AVEC - Application Python Flask

## Description

AVEC (Appui à la Vulnérabilité et l'Épargne Collective) est une application web développée avec Python Flask pour gérer les groupes d'épargne et de crédit collectif.

## Fonctionnalités

### 🔐 Authentification
- Inscription et connexion des utilisateurs
- Gestion des rôles (admin, supervisor, animator, member)
- Sécurité avec bcrypt pour le hachage des mots de passe

### 📅 Gestion des Cycles
- Création et gestion des cycles d'épargne
- Phases : préparation, formation, supervision, terminé
- Suivi de la progression et des objectifs

### 👥 Gestion des Groupes
- Création et gestion des groupes d'épargne
- Ajout/retrait de membres
- Suivi des contributions et prêts

### 💰 Gestion des Transactions
- Enregistrement des épargnes, prêts, remboursements
- Approbation et rejet des transactions
- Calcul automatique des intérêts

### 📊 Tableau de Bord
- Statistiques en temps réel
- Vue d'ensemble des cycles et groupes
- Actions rapides

## Structure du Projet

```
avec-python/
├── app.py                 # Application Flask principale
├── config.py              # Configuration
├── requirements.txt       # Dépendances Python
├── models/                # Modèles SQLAlchemy
│   └── __init__.py       # User, Cycle, Group, Transaction
├── routes/                # Routes Flask
│   ├── auth.py           # Authentification
│   ├── cycles.py         # Gestion des cycles
│   ├── groups.py         # Gestion des groupes
│   └── transactions.py   # Gestion des transactions
├── templates/             # Templates HTML
│   ├── base.html         # Template de base
│   ├── index.html        # Page d'accueil
│   ├── dashboard.html    # Tableau de bord
│   └── auth/             # Pages d'authentification
└── static/               # CSS, JS, images
```

## Installation

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Configuration
1. Copier le fichier `.env.example` vers `.env`
2. Modifier les variables d'environnement selon votre configuration

### Lancement
```bash
python app.py
```

L'application sera accessible à l'adresse : http://localhost:5000

## Compte de démonstration

- **Email** : admin@avec.com
- **Mot de passe** : admin123

## Technologies utilisées

- **Backend** : Flask, SQLAlchemy
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Authentification** : Flask-Login, bcrypt
- **Frontend** : Bootstrap 5, HTML/CSS/JavaScript
- **Validation** : WTForms, email-validator

## Fonctionnalités principales

### 1. Gestion des Cycles
- Création de cycles d'épargne avec objectifs
- Suivi des phases (préparation → formation → supervision → terminé)
- Calcul automatique de la progression

### 2. Gestion des Groupes
- Création de groupes avec limites de membres
- Gestion des membres (ajout/retrait)
- Suivi des contributions et prêts

### 3. Gestion des Transactions
- Enregistrement des épargnes et prêts
- Système d'approbation des transactions
- Calcul automatique des intérêts

### 4. Tableau de Bord
- Statistiques en temps réel
- Vue d'ensemble des activités
- Actions rapides

## Sécurité

- Hachage des mots de passe avec bcrypt
- Gestion des sessions avec Flask-Login
- Validation des données avec WTForms
- Protection CSRF

## Développement

### Structure des modèles

#### User
- Informations personnelles (nom, email, téléphone)
- Rôles et permissions
- Historique de connexion

#### Cycle
- Nom, description, dates
- Phases et statut
- Objectifs financiers

#### Group
- Nom, description, membres
- Limites et règles
- Statistiques financières

#### Transaction
- Type (épargne, prêt, remboursement)
- Montants et intérêts
- Statut et approbation

## Prochaines étapes

1. **Templates supplémentaires** : Pages pour cycles, groupes, transactions
2. **API REST** : Pour intégration mobile
3. **Rapports** : Génération de rapports PDF
4. **Notifications** : Système de notifications
5. **Tests** : Tests unitaires et d'intégration

## Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Créer une Pull Request

## Licence

MIT License - voir le fichier LICENSE pour plus de détails. 