# 🏘️ AVEC - Application Villageoise d'Épargne et de Crédit

Une application web moderne pour digitaliser et simplifier le processus des associations villageoises d'épargne et de crédit (AVEC) tout en préservant leurs principes fondamentaux d'autonomie et d'autogestion.

## 🎯 **Objectifs**

L'application AVEC sert de plateforme centrale pour :
- ✅ **Formation** : Modules de formation numérisés
- ✅ **Gestion des groupes** : Création et suivi des groupes AVEC
- ✅ **Transactions** : Suivi des épargnes, prêts et remboursements
- ✅ **Transparence** : Validation multi-membres et carnets individuels
- ✅ **Supervision** : Tableaux de bord et rapports automatiques

## 👥 **Publics Cibles**

### **Animateur/Animatrice (Administrateur)**
- Interface optimisée pour la gestion de multiples groupes
- Supervision et collecte de données
- Accès complet aux fonctionnalités de gestion

### **Membre AVEC (Utilisateur)**
- Interface simple et intuitive
- Accès limité aux activités de leur groupe
- Conçu pour des niveaux d'alphabétisation variés

## 🏗️ **Architecture - Trois Phases**

### **Phase Préparatoire (Animateur uniquement)**
- Évaluation et sélection de la communauté
- Création de nouveaux groupes AVEC
- Configuration des paramètres (valeur des parts, taux d'intérêt)

### **Phase Intensive (Animateur et Membres)**
- **7 modules de formation** numérisés
- **Gestion des transactions** (parts, prêts, solidarité)
- **Transparence** avec validation multi-membres
- **Carnets individuels** numériques

### **Phase de Supervision (Animateur)**
- Tableaux de bord de suivi
- Rapports automatiques
- Évaluations numériques de changement de phase

## 🛠️ **Technologies Utilisées**

- **Backend** : Flask (Python)
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : Bootstrap 5, Chart.js
- **Authentification** : Flask-Login
- **ORM** : SQLAlchemy

## 🚀 **Installation et Démarrage**

### **Prérequis**
- Python 3.8+
- pip

### **Installation**

1. **Cloner le repository**
```bash
git clone https://github.com/votre-username/avec-app.git
cd avec-app
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
```

3. **Activer l'environnement virtuel**
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. **Installer les dépendances**
```bash
pip install -r requirements_stable.txt
```

5. **Lancer l'application**
```bash
python app_simple.py
```

6. **Accéder à l'application**
```
http://localhost:5000
```

### **Compte par défaut**
- **Email** : admin@avec.com
- **Mot de passe** : admin123

## 📊 **Fonctionnalités Principales**

### **Gestion des Groupes**
- Création et configuration de groupes AVEC
- Gestion des membres
- Suivi des épargnes et prêts
- Configuration des paramètres (parts, taux d'intérêt)

### **Transactions AVEC**
- Achat de parts
- Demandes et octroi de prêts
- Remboursements avec intérêts
- Caisse de solidarité
- Validation multi-membres

### **Formation Numérisée**
- 7 modules de formation interactifs
- Suivi de progression
- Évaluations numériques

### **Carnets Individuels**
- Historique personnel des transactions
- Suivi des épargnes et prêts
- Calcul automatique des intérêts

### **Supervision**
- Tableaux de bord de suivi
- Rapports automatiques
- Évaluations de changement de phase

## 🔐 **Système de Permissions**

### **Membres AVEC**
- ✅ Lecture seule des informations de groupe
- ✅ Accès aux transactions de leur groupe
- ✅ Carnet personnel
- ❌ Pas de modification des groupes

### **Animateurs**
- ✅ Création et modification de groupes
- ✅ Gestion des membres
- ✅ Supervision complète

### **Administrateurs**
- ✅ Toutes les permissions
- ✅ Suppression de groupes
- ✅ Gestion complète de la plateforme

## 💰 **Spécificités Financières**

- **Devise** : FCFA (Franc CFA)
- **Parts** : Valeur configurable par groupe
- **Intérêts** : Calcul automatique
- **Solidarité** : Caisse d'urgence
- **Transparence** : Toutes transactions en présence

## 📱 **Interface Utilisateur**

- **Design moderne** avec Bootstrap 5
- **Interface responsive** pour mobile et desktop
- **Icônes intuitives** pour utilisateurs peu alphabétisés
- **Navigation simple** et claire
- **Messages d'aide** contextuels

## 🔧 **Configuration**

### **Variables d'environnement**
```bash
SECRET_KEY=votre-clé-secrète
DATABASE_URL=sqlite:///avec.db
FLASK_ENV=development
```

### **Base de données**
L'application utilise SQLite par défaut. Pour la production, configurez PostgreSQL :
```bash
DATABASE_URL=postgresql://user:password@localhost/avec_db
```

## 📈 **Roadmap**

- [ ] Application mobile offline
- [ ] Synchronisation des données
- [ ] Notifications push
- [ ] Rapports avancés
- [ ] Intégration SMS
- [ ] Multi-langues

## 🤝 **Contribution**

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 **Licence**

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 **Support**

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

---

**AVEC** - Simplifiant l'épargne collective pour un avenir financier inclusif 🌍 