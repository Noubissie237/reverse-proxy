# Tests - Apache Virtual Host Manager

## 🧪 Suite de Tests

Cette suite de tests garantit la qualité et la fiabilité du gestionnaire de Virtual Hosts Apache.

## 📋 Structure

```
tests/
├── __init__.py              # Package tests
├── conftest.py              # Fixtures pytest
├── test_validation.py       # Tests des validations (email, port, domaine)
├── test_config.py           # Tests de gestion de configuration
└── test_monitoring.py       # Tests des fonctionnalités de monitoring
```

## 🚀 Exécuter les Tests

### Tests simples
```bash
pytest tests/
```

### Tests avec détails
```bash
pytest tests/ -v
```

### Tests avec couverture
```bash
pytest tests/ --cov=vhost_manager --cov-report=term-missing
```

### Tests spécifiques
```bash
# Un fichier
pytest tests/test_validation.py

# Une classe
pytest tests/test_validation.py::TestEmailValidation

# Un test spécifique
pytest tests/test_validation.py::TestEmailValidation::test_valid_emails
```

## 📊 Statistiques

- **Total de tests** : 27
- **Couverture** : ~19%
- **Temps d'exécution** : < 1 seconde

### Répartition des tests

- **test_validation.py** : 7 tests
  - Validation email (2 tests)
  - Validation port (3 tests)
  - Validation domaine (3 tests)

- **test_config.py** : 7 tests
  - Gestion configuration (4 tests)
  - Opérations sur les sites (3 tests)

- **test_monitoring.py** : 13 tests
  - Vérification statut (2 tests)
  - Statistiques (4 tests)
  - Statut des sites (3 tests)
  - Liste des sites (3 tests)

## 🔧 Configuration

### pytest.ini
Configuration principale de pytest avec :
- Chemins de tests
- Options par défaut
- Marqueurs personnalisés

### conftest.py
Fixtures réutilisables :
- `mock_manager` : Instance de VHostManager sans initialisation
- `sample_site_config` : Configuration de site exemple

## ✅ Tests Couverts

### Validation
- ✅ Emails valides et invalides
- ✅ Ports valides et invalides (1-65535)
- ✅ Domaines valides et invalides
- ✅ Longueur des domaines

### Configuration
- ✅ Chargement de configuration vide
- ✅ Sauvegarde et chargement
- ✅ Format JSON valide
- ✅ Gestion de plusieurs sites

### Monitoring
- ✅ Vérification de ports
- ✅ Calcul de statistiques
- ✅ Comptage SSL
- ✅ Distribution des ports
- ✅ Statut des sites

## 🎯 Prochaines Améliorations

- [ ] Tests d'intégration avec Apache
- [ ] Tests de création de certificats SSL
- [ ] Tests de commandes CLI
- [ ] Augmenter la couverture à >80%
- [ ] Tests de performance

## 🐛 Debugging

### Voir les logs détaillés
```bash
pytest tests/ -v -s
```

### Arrêter au premier échec
```bash
pytest tests/ -x
```

### Voir les variables locales en cas d'échec
```bash
pytest tests/ -l
```

### Mode debug
```bash
pytest tests/ --pdb
```

## 📝 Écrire de Nouveaux Tests

### Template de test
```python
import pytest

class TestMyFeature:
    """Test my feature"""
    
    def test_something(self, mock_manager):
        """Test that something works"""
        # Arrange
        expected = "value"
        
        # Act
        result = mock_manager.some_method()
        
        # Assert
        assert result == expected
```

### Bonnes pratiques
1. Un test = une fonctionnalité
2. Noms descriptifs
3. Arrange-Act-Assert
4. Tests indépendants
5. Utiliser les fixtures

## 🔄 CI/CD

Les tests s'exécutent automatiquement via GitHub Actions sur :
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

Voir `.github/workflows/tests.yml` pour la configuration.
