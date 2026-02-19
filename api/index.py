import sys
from pathlib import Path

# 1. On donne à Python le chemin vers ton dossier "src" 
# pour que tes imports (ex: "from backend.main import app") fonctionnent.
# Path(__file__) = TEAM-Z/api/index.py
# .parent.parent = TEAM-Z/
src_path = Path(__file__).resolve().parent.parent / "backend" / "src"
sys.path.insert(0, str(src_path))

# 2. On importe directement ton application FastAPI
from backend.main import app

# Vercel n'a besoin que de cette variable 'app' pour générer ton API !