import re
import sys
import os

def parse_log(logfile, filtre_uri=None):
    """
    Analyse le fichier de log du sniffeur HTTP et affiche les informations
    sur les requêtes GET et les réponses associées.

    - logfile : chemin du fichier log
    - filtre_uri : sous-chaîne à rechercher dans l'URI (facultatif)
    """
    if not os.path.exists(logfile):
        print(f"Fichier log introuvable : {logfile}")
        return

    print(f"\n=== Analyse du log : {logfile} ===")
    if filtre_uri:
        print(f"Filtre appliqué sur l'URI contenant : '{filtre_uri}'")
    print()

    # Expressions régulières pour extraire les infos
    # compile() pour optimiser les recherches répétées
    reg_req = re.compile(r"CLIENT\s+([\d\.]+):(\d+)\s+→\s+GET\s+(\S+)")
    reg_rep = re.compile(r"SERVEUR\s+→\s+([\d\.]+):(\d+).*HTTP/\d\.\d\s+(\d+)\s+([A-Za-z ]+?)+\s+\|\s+taille=(\d+)")
    reg_blocked_req = re.compile(r"CLIENT\s+([\d\.]+):(\d+)\s+→\s+GET\s+(\S+)\s+→\s+BLOQUÉ\s+(\S+)")

    with open(logfile, "r", encoding="utf-8") as f:
        lignes = f.readlines()

    # On stocke les infos sous forme de dictionnaires
    requetes = []
    reponses = []
    blocked_requests = []

    for ligne in lignes:
        req_match = reg_req.search(ligne) # recherche une requête GET
        rep_match = reg_rep.search(ligne) # recherche une réponse serveur
        block_match = reg_blocked_req.search(ligne) # recherche une requête bloquée
        if req_match:
            ip, port, uri = req_match.groups()
            if not filtre_uri or filtre_uri in uri:
                requetes.append({"ip": ip, "port": port, "uri": uri})

        if rep_match:
            ip, port, code, msg, taille = rep_match.groups()
            if not filtre_uri:
                reponses.append({"ip": ip, "port": port, "code": code, "message" : msg.strip() , "taille": taille})
        if block_match:
            ip, port, uri, blocked_uri = block_match.groups()
            if not filtre_uri or filtre_uri in uri:
                blocked_requests.append({"ip": ip, "port": port, "uri": uri, "blocked_uri": blocked_uri})

    # Affichage des résultats
    if not requetes:
        print("Aucune requête correspondante trouvée.")
        return

    print("Requêtes GET enregistrées :")
    for r in requetes:
        print(f"  - Client {r['ip']}:{r['port']} → {r['uri']}")

    if reponses:
        print("\n Réponses serveur enregistrées :")
        for r in reponses:
            print(f"  - Vers {r['ip']}:{r['port']} | Code {r['code']} | Taille {r['taille']} octets")

    if blocked_requests:
        print("\n Requêtes BLOQUÉES enregistrées :")
        for r in blocked_requests:
            print(f"  - Client {r['ip']}:{r['port']} → {r['uri']} (BLOQUÉE)")
    print("\n Analyse terminée.\n")


if __name__ == "__main__":

    # logfile = sys.argv[1]
    logfile = os.path.abspath("./MiniProjet1/Exercice2/QST2") + "/http_sniffer.log"
    filtre_uri = sys.argv[1] if len(sys.argv) >= 2 else None

    parse_log(logfile, filtre_uri)
