# Custom Instructions for project MovingLive

Every time you choose to apply a rule(s), explicitly state the rule(s) in the output. You can abbreviate the rule description to a single word or phrase.

## Project Context

FastApi backend with Vue.js frontend for a sport online compagny. The company offers online courses and training sessions.
The platform allows :

- participant to register for session (live) or replay thanks to zoom integration
- coaches to create and manage sessions, replays, and packages.

## Code Style and Structure

- Write concise, technical TypeScript and Python code with accurate examples
- Use functional and declarative programming patterns; avoid classes
- Prefer iteration and modularization over code duplication
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError)
- Structure repository files as follows:

```bash
Workspace
├── .github # Contient les configurations GitHub
│ ├── copilot # Instructions pour GitHub Copilot
│ ├── workflows # Workflows CI/CD
│ ├── copilot-instructions.md
├── alembic # Gestion des migrations de base de données
│ ├── versions # Contient les fichiers de migration
│ ├── env.py
│ ├── script.py.mako
│ └── run_migrations.py
├── app # Contient le code source du backend
│ ├── main.py # Point d'entrée de l'application
│ ├── api # Routes de l'API
│ ├── certs # Certificats SSL/TLS
│ ├── cli # Outils en ligne de commande
│ ├── core # Fonctionnalités principales
│ ├── courriels # Templates d'emails
│ ├── models # Contient les modèles de données
│ ├── schemas # Contient les schémas de validation
│ ├── services # Contient la logique métier
│ └── db # Gestion de la base de données
├── frontend # Contient le code source du frontend Vue.js
│ ├── src
│ │ ├── components # Composants Vue.js
│ │ ├── content # Articles et contenus statiques
│ │ ├── locales # Fichiers de traduction
│ │ ├── router # Configuration du routeur
│ │ ├── services # Services d'API
│ │ ├── stores # Stores Pinia
│ │ └── views # Composants de pages
│ └── public # Fichiers statiques publics
├── logs # Fichiers de journalisation
├── tests # Tests unitaires et d'intégration
├── .env.development # Variables d'environnement de développement
├── .env.production # Variables d'environnement de production
├── alembic.ini # Configuration Alembic
├── pyproject.toml # Dépendances Python avec Poetry
├── pytest.ini # Configuration des tests
└── README.md # Documentation du projet
```

## Tech Stack

- Vue js 3 with Composition API
- Pinia
- Vite js
- Vitest
- TypeScript
- Bootstrap 5.3
- Python 3.12
- Fast API
- Pydantic V2
- SQLAlchemy V2
- PostgreSQL
- PyUnit
- GitHub Action

## Naming Conventions

- Use lowercase with dashes for directories (e.g., components/form-wizard)
- Use snake_case for functions and variables
- Favor named exports for components and utilities
- Use PascalCase for component files (e.g., VisaForm.tsx)
- Use camelCase for utility files (e.g., formValidator.ts)

## TypeScript Usage

- Use TypeScript for all code; prefer interfaces over types
- Avoid enums; use const objects with 'as const' assertion
- Use functional components with TypeScript interfaces
- Define strict types for message passing between different parts of the extension
- Use absolute imports for all files @/...
- Avoid try/catch blocks unless there's good reason to translate or handle error in that abstraction
- Use explicit return types for all functions
- Use interfaces to define code contracts.
- Use enumeration types for constant values.
- Use union types for parameters that can have multiple types.
- Use generic types for reusable functions and classes.
- Use `any` types sparingly and as a last resort.
- Use `unknown` types for values with unknown types.
- Use `never` types for functions that never return a value.
- Use `void` types for functions that return no value.

## Vue js Usage

- Add setup in the script tag. Example: ``

## Python Usage

- Use `now(timezone.utc)` instead of `utcnow` method

## FastAPI Usage

- Use lifespan event handlers instead of on_event `Method`

## Pydantic Usage

- Use `model_config = ConfigDict(from_attributes=True)` for mapping object to database
- Use `@field_validator` and `@classmethod` for personalized validation

Exemple:

```python
from pydantic import BaseModel, ConfigDict, field_validator
@field_validator("name", mode="before")
@classmethod
def validate_name(cls, v):
if not v:
raise ValueError("name cannot be empty")
return v
```

## Syntax and Formatting

### Front-end: Vue.js with TypeScript

- Components: Use PascalCase for component names, ensuring each component name is multi-word to prevent conflicts with existing and future HTML elements. For example, MyComponent.
- Component Files: Name component files in PascalCase or kebab-case, depending on your project's conventions. For example, MyComponent.vue or my-component.vue.
- Variables and Functions: Use camelCase. For example, myVariable or myFunction().
- Constants: Use SCREAMING_SNAKE_CASE for constants. For example, MY_CONSTANT.
- Classes: Use PascalCase for class names. For example, MyClass.

### Back-end: Python

- Variables and Functions: Use snake_case, which means lowercase letters with underscores separating words. For example, my_variable or my_function().
- Constants: Use UPPER_CASE_WITH_UNDERSCORES for constants. For example, MY_CONSTANT.
- Classes: Use PascalCase, where each word starts with an uppercase letter without separators. For example, MyClass.

## UI and Styling

- Implement Bootstrap 5 for styling
- Follow Material Design guidelines
Accessibility WCAG 2.1
- Responsive Design
- Performance - Lighthouse Score > 90
- SEO
- Security - CSS, CSRF protection
- User friendly with good experience

## Error Handling

- Implement proper error boundaries
- Log errors appropriately for debugging
- Provide user-friendly error messages
- Handle network failures gracefully

## Testing

Requis pour de bons tests unitaires:

- regarder les schémas pydantics attendus des endpoints pour s'assurer d'envoyer l'ensemble des information attendues
- utiliser les factory situées dans `app/tests/mock_generators` pour générer des données de tests
- utiliser les mocks pour simuler des appels à des services externes
- utiliser les fixtures pour partager des données entre les tests
- utiliser les paramétrages pour tester des cas de bords

## Security

- Implement Content Security Policy
- Sanitize user inputs
- Handle sensitive data properly
- Implement proper CORS handling

## Documentation

- Maintain clear README with setup instructions
- Document API interactions and data flows
- Keep manifest.json well-documented
- Don't include comments unless it's for complex logic
- Document permission requirements
