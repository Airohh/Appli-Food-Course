"""Tests pour le module workflow_recipes."""

from unittest.mock import Mock, patch, MagicMock
import pytest

from app.workflow_recipes import (
    archive_old_recipes,
    transfer_purchased_to_stock,
    propose_recipes_to_notion,
)


@pytest.fixture
def mock_client():
    """Mock du client Notion."""
    client = Mock()
    return client


@pytest.fixture
def mock_pages():
    """Pages mockées pour les tests."""
    return [
        {
            "id": "page1",
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Name": "Recette 1",
        },
        {
            "id": "page2",
            "Semaine": {"select": {"name": "Semaine 45 – 2025"}},
            "Name": "Recette 2",
        },
        {
            "id": "page3",
            "Semaine": "Semaine 46 – 2025",
            "Name": "Recette 3",
        },
    ]


@patch('app.workflow_recipes.get_client')
@patch('app.workflow_recipes.export_database')
@patch('app.workflow_recipes.get_database_properties')
@patch('app.workflow_recipes.normalize_id')
def test_archive_old_recipes(
    mock_normalize_id,
    mock_get_schema,
    mock_export,
    mock_get_client,
    mock_client,
    mock_pages,
):
    """Test archivage des anciennes recettes."""
    mock_normalize_id.return_value = "db_id"
    mock_get_client.return_value = mock_client
    mock_export.return_value = mock_pages
    mock_get_schema.return_value = {
        "Archivée": {"type": "checkbox"},
        "Name": {"type": "title"},
    }
    
    result = archive_old_recipes("Semaine 46 – 2025", dry_run=False)
    
    # page2 devrait être archivée (semaine différente)
    assert result == 1
    mock_client.pages.update.assert_called()


@patch('app.workflow_recipes.get_client')
@patch('app.workflow_recipes.export_database')
@patch('app.workflow_recipes.normalize_id')
def test_archive_old_recipes_dry_run(
    mock_normalize_id,
    mock_export,
    mock_get_client,
    mock_client,
    mock_pages,
):
    """Test archivage en mode dry_run."""
    mock_normalize_id.return_value = "db_id"
    mock_get_client.return_value = mock_client
    mock_export.return_value = mock_pages
    
    result = archive_old_recipes("Semaine 46 – 2025", dry_run=True)
    
    # Devrait compter sans archiver
    assert result == 1
    mock_client.pages.update.assert_not_called()


@patch('app.workflow_recipes.get_client')
@patch('app.workflow_recipes.export_database')
@patch('app.workflow_recipes.normalize_id')
@patch('app.workflow_recipes.week_label')
def test_transfer_purchased_to_stock(
    mock_week_label,
    mock_normalize_id,
    mock_export,
    mock_get_client,
    mock_client,
):
    """Test transfert des courses achetées vers le stock."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_normalize_id.side_effect = lambda x: "db_id" if x else None
    mock_get_client.return_value = mock_client
    
    pages = [
        {
            "id": "grocery1",
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Acheté": {"checkbox": True},
            "Aliment": "Poulet",
            "Quantité": 500,
            "Unité": "g",
            "Catégorie": "Viande",
        },
        {
            "id": "grocery2",
            "Semaine": {"select": {"name": "Semaine 46 – 2025"}},
            "Acheté": {"checkbox": False},
            "Aliment": "Tomates",
        },
    ]
    mock_export.return_value = pages
    
    with patch('app.workflow_recipes.upsert_page') as mock_upsert, \
         patch('app.workflow_recipes.get_database_properties') as mock_schema, \
         patch('app.workflow_recipes.grocery_to_notion_properties') as mock_map:
        mock_schema.return_value = {"Aliment": {"type": "title"}}
        mock_map.return_value = {}
        
        result = transfer_purchased_to_stock(dry_run=False)
        
        # Seulement grocery1 devrait être transféré
        assert result == 1
        mock_upsert.assert_called_once()


@patch('app.workflow_recipes.get_candidate_recipes')
@patch('app.workflow_recipes.push_recipes_to_notion')
@patch('app.workflow_recipes.archive_old_recipes')
@patch('app.workflow_recipes.transfer_purchased_to_stock')
@patch('app.workflow_recipes.week_label')
@patch('app.workflow_recipes.notify_ntfy')
@patch('app.workflow_recipes.DATA_DIR')
def test_propose_recipes_to_notion(
    mock_data_dir,
    mock_notify,
    mock_week_label,
    mock_transfer,
    mock_archive,
    mock_push,
    mock_get_candidates,
    tmp_path,
):
    """Test proposition de recettes."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_archive.return_value = 2
    mock_transfer.return_value = 1
    mock_push.return_value = {"n_created": 6, "n_updated": 0, "n_errors": 0}
    
    candidates = [
        {"title": f"Recette {i}", "id": i, "sourceUrl": f"https://spoonacular.com/recipes/{i}"}
        for i in range(9)
    ]
    mock_get_candidates.return_value = candidates
    
    # Mock DATA_DIR
    mock_data_dir.__truediv__ = lambda self, other: tmp_path / other
    mock_data_dir.mkdir = Mock()
    
    result = propose_recipes_to_notion(
        n_candidates=9,
        n_final=6,
        dry_run=False,
        notion_recipes_url="https://notion.so/test",
    )
    
    assert result["n_candidates"] == 9
    assert result["n_final"] == 6
    assert result["archived_recipes"] == 2
    assert result["transferred_to_stock"] == 1
    mock_notify.assert_called_once()


@patch('app.workflow_recipes.get_candidate_recipes')
@patch('app.workflow_recipes.push_recipes_to_notion')
@patch('app.workflow_recipes.archive_old_recipes')
@patch('app.workflow_recipes.transfer_purchased_to_stock')
@patch('app.workflow_recipes.week_label')
@patch('app.workflow_recipes.notify_ntfy')
def test_propose_recipes_to_notion_dry_run(
    mock_notify,
    mock_week_label,
    mock_transfer,
    mock_archive,
    mock_push,
    mock_get_candidates,
):
    """Test proposition de recettes en mode dry_run."""
    mock_week_label.return_value = "Semaine 46 – 2025"
    mock_archive.return_value = 0
    mock_transfer.return_value = 0
    mock_push.return_value = {"n_created": 0, "n_updated": 0, "n_errors": 0}
    mock_get_candidates.return_value = []
    
    result = propose_recipes_to_notion(dry_run=True)
    
    # Ne doit pas envoyer de notification en dry_run
    mock_notify.assert_not_called()
    assert result["n_candidates"] == 0

