python3 -m pip install --upgrade pip
pip install -r requirements.txt
rm -rf dist/ || true
python3 -m build
