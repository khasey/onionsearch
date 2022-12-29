import argparse
import sys
import re

# Ouvrez le fichier en mode lecture
with open(sys.argv[1], 'r') as f:
    # Parcourez chaque ligne du fichier
    for ligne in f:
        # Utilisez une expression régulière pour trouver les URL dans la ligne
        resultats = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', ligne)
        # Affichez chaque URL trouvée
        for url in resultats:
            site = url.split('/', 2)
            with open('onionSite.txt', 'a') as f:
                for item in resultats:
                    f.write("%s\n" % site[2])
