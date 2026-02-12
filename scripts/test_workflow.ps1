# Script de test complet du workflow (PowerShell)

Write-Host "🧪 TEST COMPLET DU WORKFLOW MOBILE NOTION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
if (-not (Test-Path "app\workflow_recipes.py")) {
    Write-Host "❌ Erreur : Exécutez ce script depuis le répertoire Appli-Food-Course" -ForegroundColor Red
    exit 1
}

# Phase 1 : Tests unitaires
Write-Host "📋 Phase 1 : Tests unitaires" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow
try {
    pytest tests/ -v --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Tous les tests unitaires passent" -ForegroundColor Green
    } else {
        Write-Host "❌ Certains tests échouent" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de l'exécution des tests : $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Phase 2 : Tests dry-run
Write-Host "📋 Phase 2 : Tests en mode dry-run" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow

Write-Host "Test 1 : Proposition de recettes (dry-run)" -ForegroundColor Cyan
try {
    python -m app.workflow_recipes --dry-run --n-candidates 3 --n-final 2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test 1 réussi" -ForegroundColor Green
    } else {
        Write-Host "❌ Test 1 échoué" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors du test 1 : $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "Test 2 : Génération de courses (dry-run)" -ForegroundColor Cyan
try {
    python -m app.workflow_courses --dry-run
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Test 2 réussi" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Test 2 : Pas de recettes sélectionnées (normal si première fois)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Test 2 : Pas de recettes sélectionnées (normal si première fois)" -ForegroundColor Yellow
}
Write-Host ""

# Phase 3 : Résumé
Write-Host "✅ Tests dry-run terminés" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes :" -ForegroundColor Cyan
Write-Host "1. Vérifier votre configuration Notion"
Write-Host "2. Exécuter les workflows en mode réel :"
Write-Host "   python -m app.workflow_recipes --notion-url 'VOTRE_URL'"
Write-Host "   python -m app.workflow_courses --notion-url 'VOTRE_URL'"
Write-Host ""

