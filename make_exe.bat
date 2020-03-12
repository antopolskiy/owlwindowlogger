rm -r distr
CALL pyinstaller --onefile --distpath "distr" --clean -w logger.py
rm -r build
rm -r __pycache__
rm logger.spec
PAUSE