def test_project_contract():
    from pathlib import Path
    root=Path(__file__).parents[1]
    assert (root/'backend/app/main.py').exists()
    assert (root/'frontend/src/main.jsx').exists()
    assert (root/'.env.example').exists()
