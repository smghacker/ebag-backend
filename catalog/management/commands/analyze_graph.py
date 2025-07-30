from pprint import pprint

from django.core.management.base import BaseCommand

from catalog.graph_analysis import export_graph_analysis_to_json


class Command(BaseCommand):
    help = "Analyze the similarity graph and output the longest rabbit hole and all rabbit islands."

    def handle(self, *args, **kwargs):
        path, data = export_graph_analysis_to_json()
        self.stdout.write(self.style.SUCCESS(f"\n✅ Graph analysis saved to: {path}\n"))
        pprint(data)
