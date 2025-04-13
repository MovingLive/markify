# Markify

Markify est une application permettant d'extraire le contenu de la documentation web et de le convertir en fichiers Markdown. Ce projet combine un backend FastAPI en Python et un frontend Vue.js en TypeScript pour fournir une solution complète de scraping de documentation.

## Fonctionnalités

- **Scraping de documentation** : Extraction et conversion du contenu d'une page web en Markdown.
- **Téléchargement automatique** : Possibilité de télécharger le résultat en fichier unique ou en archive ZIP (structure hiérarchique ou plate).
- **Interface conviviale** : Permet de lancer le scraping via un formulaire et de suivre la progression en temps réel.
- **API RESTful** : Ensemble d'endpoints FastAPI pour démarrer le scraping, suivre sa progression et récupérer les résultats.

## Structure du Projet

```bash
Workspace
├── .github/          # Configurations GitHub et workflows CI/CD
├── app/              # Backend FastAPI
│   ├── main.py       # Point d'entrée de l'application
│   ├── api/          # Endpoints de l'API
│   ├── services/     # Logique métier (scraping, traitement)
│   └── schemas/      # Schémas Pydantic pour validation
├── frontend/         # Frontend Vue.js
│   ├── src/          # Code source du frontend
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── locales/
│   │   ├── services/
│   │   ├── stores/
│   │   └── views/
│   └── public/       # Fichiers statiques
├── scripts/          # Scripts utilitaires en Python
├── pyproject.toml    # Dépendances et configuration du backend avec Poetry
└── README.md         # Documentation du projet
```

## Prérequis

- **Python 3.12** (ou version spécifiée dans `pyproject.toml`)
- **Node.js** (version recommandée 18 ou supérieure)
- **Poetry** pour la gestion des dépendances Python

## Installation Locale

### Backend

1. **Cloner le repository**

   ```sh
   git clone <URL_DU_REPOSITORY>
   cd markify
   ```

2. **Installer les dépendances Python avec Poetry**

   ```sh
   pip install poetry
   poetry install
   ```

3. **Lancer l'application FastAPI en locale dans VsCode**

    S'assurer que python interpreter est bien configuré sur le bon environnement virtuel (venv) de Poetry.
    Lancer le serveur à l'aide du laucnher VsCode
    Le backend sera disponible sur [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend

1. **Accéder au dossier du frontend**

   ```sh
   cd frontend
   ```

2. **Installer les dépendances Node.js**

   ```sh
   npm ci
   ```

3. **Lancer l'application Vue.js**

   ```sh
   npm run dev
   ```

   Le frontend sera accessible via l'URL indiquée (généralement [http://localhost:5173/](http://localhost:5173/)).

## Utilisation

- **Via l'interface** : Entrez l'URL de la documentation à scraper, choisissez le format d'exportation et lancez le scraping. La progression sera affichée et le fichier sera téléchargé automatiquement une fois le processus terminé.
- **Via l'API** : Utilisez les endpoints `/api/scrape`, `/api/progress/{task_id}` et `/api/result/{task_id}` pour intégrer le scraping dans d'autres applications.

## Tests & Intégration Continue

- **Tests** : Le projet utilise `pytest` pour les tests unitaires et d'intégration.
- **CI/CD** : Des workflows GitHub Actions sont configurés dans le dossier `.github/workflows` pour automatiser les tests, le linting et les déploiements conditionnels.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une pull request pour améliorer ou étendre les fonctionnalités de Markify.

---
