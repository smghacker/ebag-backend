import os
import django
from pprint import pprint

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ebag_backend.settings")
django.setup()

from catalog.graph_analysis import export_graph_analysis_to_json

def main():
    path, data = export_graph_analysis_to_json()
    print(f"\n✅ Graph analysis saved to: {path}\n")
    pprint(data)

if __name__ == "__main__":
    main()
