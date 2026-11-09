#!/usr/bin/env python3
"""Régénère tout le site (pages HTML, sitemap, llms.txt, .htaccess, versions Markdown).
Usage : python3 scripts/generateur/build_all.py   (nécessite Python 3 et Pillow)."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ["build_site", "build_pages", "build_misc", "build_rejoindre", "build_comparatif",
         "build_mylotier", "build_agents", "build_services", "build_about", "build_markdown"]
for name in ORDER:
    print("→", name)
    subprocess.run([sys.executable, os.path.join(HERE, name + ".py")], cwd=HERE, check=True)
print("→ audit SEO (data/seo-report.json)")
subprocess.run([sys.executable, os.path.join(HERE, "..", "seo_audit.py")], check=True)
print("→ audit visibilité IA (data/ai-visibility-report.json)")
subprocess.run([sys.executable, os.path.join(HERE, "..", "ai_visibility_audit.py")], check=True)
print("Terminé.")
