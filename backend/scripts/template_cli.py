"""  python scripts/template_cli.py write OUT.xlsx          blank template from the default rubric
     python scripts/template_cli.py preview IN.xlsx        parse + validate an upload (compares with the default rubric)"""
import json, sys
sys.path.insert(0, ".")
from app.fit import DEFAULT_RUBRIC
from app.template_xlsx import preview, write_template

if sys.argv[1] == "write":
    write_template(sys.argv[2], DEFAULT_RUBRIC); print("wrote", sys.argv[2])
else:
    print(json.dumps(preview(sys.argv[2], DEFAULT_RUBRIC), indent=1, default=str))
