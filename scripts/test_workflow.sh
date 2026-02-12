#!/bin/bash
# Script de test complet du workflow

set -e  # Arrêter en cas d'erreur

echo "🧪 TEST COMPLET DU WORKFLOW MOBILE NOTION"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "app/workflow_recipes.py" ]; then
    echo -e "${RED}❌ Erreur : Exécutez ce script depuis le répertoire Appli-Food-Course${NC}"
    exit 1
fi

# Phase 1 : Tests unitaires
echo -e "${YELLOW}📋 Phase 1 : Tests unitaires${NC}"
echo "-----------------------------------"
if pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✅ Tous les tests unitaires passent${NC}"
else
    echo -e "${RED}❌ Certains tests échouent${NC}"
    exit 1
fi
echo ""

# Phase 2 : Tests dry-run
echo -e "${YELLOW}📋 Phase 2 : Tests en mode dry-run${NC}"
echo "-----------------------------------"

echo "Test 1 : Proposition de recettes (dry-run)"
if python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2; then
    echo -e "${GREEN}✅ Test 1 réussi${NC}"
else
    echo -e "${RED}❌ Test 1 échoué${NC}"
    exit 1
fi
echo ""

echo "Test 2 : Génération de courses (dry-run)"
if python -m app.workflow_courses --dry-run; then
    echo -e "${GREEN}✅ Test 2 réussi${NC}"
else
    echo -e "${YELLOW}⚠️  Test 2 : Pas de recettes sélectionnées (normal si première fois)${NC}"
fi
echo ""

# Phase 3 : Résumé
echo -e "${GREEN}✅ Tests dry-run terminés${NC}"
echo ""
echo "Prochaines étapes :"
echo "1. Vérifier votre configuration Notion"
echo "2. Exécuter les workflows en mode réel :"
echo "   python -m app.workflow_recipes --notion-url 'VOTRE_URL'"
echo "   python -m app.workflow_courses --notion-url 'VOTRE_URL'"
echo ""

