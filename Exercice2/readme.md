# Mini Projet 1 – Relais HTTP

## 📘 Introduction

Ce projet met en œuvre un ensemble de **relais HTTP** programés en Python et simulant différentes fonctions réseau.  
Les échanges entre le **client** et le **serveur** transitent à travers ces relais en utilisant le **protocole HTTP**.  
Le client est représenté par un navigateur web, tandis que le serveur est un serveur HTTP basique.

Chaque entité du système a un rôle bien défini (les rôles, comportements et commandes de lancement seront détaillés dans les sections suivantes) :

- **Relai Cache HTTP** : met en cache les réponses du serveur pour optimiser les performances.
- **Relai Censeur HTTP** : bloque l’accès à certaines ressources web configurées dans une *blacklist*.
- **Relai Sniffer HTTP** : enregistre les requêtes et réponses HTTP dans un fichier journal à des fins d’analyse.
- **Serveur HTTP** : fournit les fichiers demandés par les clients.
- **AuditHTTP** : outil d’analyse des journaux HTTP (logs) produits par les relais.

---

## ⚙️ Architecture générale

### 🔁 Chaînage des relais 

CLIENT (Navigateur Web) -> Relai Cache HTTP (port 5000) -> Relai Censeur HTTP (port 6000) -> Relai Sniffer HTTP (port 7000) -> SERVEUR HTTP (port 8000)

Le client envoie une requête HTTP au relai cache.  
Celui-ci, s’il ne trouve pas la réponse dans son cache, transmet la requête au relai censeur, puis au sniffer, et enfin au serveur HTTP.

Les réponses suivent le chemin inverse :
Serveur → Sniffer → Censeur → Cache → Client.

> 💡 **Remarque :**  
> Avec cet ordre d’enchaînement, le **Relai Cache HTTP** ne stockera jamais une page dont l’accès est interdit par le **Relai Censeur HTTP**.

---

##  Composants du projet

> 💡 **Remarque :**  
> Les commandes de lancement ici concernent les tests en local. Pour des test sur des machines différentes remplacez l'adresse Loopback `127.0.0.1` par l'adresse IP de la machine sur laquelle vous exécutez le programme. 


### 🖥️ Serveur HTTP
**Fichier :** `serveurHTTP.py`  
**Rôle :**
- Sert les fichiers présents dans le répertoire `DOCUMENT_ROOT`. Exemple : `index.html`
- Retourne un message d’erreur `404 Not Found` si le fichier n’existe pas.
- Envoie les en-têtes HTTP complets (`Date`, `Content-Type`, `Content-Length`, etc.).

**Commandes de lancement :**
```bash
python serveurHTTP.py 127.0.0.1 8000 
# Arguments : <@IP_serveurHTTP> <port_serveurHTTP>
``` 

### 🧠 Relai Sniffer HTTP

**Fichier :** `relaiSnifferHTTP.py`

**Rôle :**
- Intercepte et consigne (log) les **requêtes** et **réponses** HTTP dans le fichier `http_sniffer.log`.
- Fonctionne comme un relais intermédiaire entre un client (ou un autre relais) et le serveur HTTP.
- Peut être inséré n’importe où dans la chaîne de relais (avant ou après d’autres relais) pour observer et journaliser le trafic.

**Commande de lancement :**
```bash
python relaiSnifferHTTP.py 127.0.0.1 8000
# Arguments : <IP_serveur_HTTP> <port_serveur_HTTP>
``` 

### 🚫 Relai Censeur HTTP

**Fichier :** relaiCenseurHTTP.py
**Rôle :**

- Intercepte les requêtes HTTP et bloque celles dont les URI figurent dans une blacklist (utilisation du fichier de configation `ùri_blacklist.conf`).

- Retourne une réponse :
```css
HTTP/1.1 403 Forbidden
<h1>Acces confidentiel mon ami</h1>
```

- Les requêtes bloquées sont également journalisées dans le même fichier log que le sniffer.

**Commandes de lancement :**
```bash
python relaiCenseurHTTP.py 127.0.0.1 7000
# Arguments : <IP_serveur_Sniffer> <port_serveur_Sniffer>
``` 
### 🗃️ Relai Cache HTTP

**Fichier :** relaiCacheHTTP.py
**Rôle :**

- Intercepte les requêtes HTTP et stocke les réponses valides (200 OK) dans un cache mémoire (dict Python).
- Si une URI est déjà présente dans le cache, la réponse est renvoyée directement au client sans interroger le serveur.
- Permet de réduire la charge et le temps de réponse.

**Comportement :**

- Si la réponse n’est pas en cache → transmet la requête au relais suivant (Censeur).
- Si la réponse est en cache → renvoie directement la réponse au client.
- Seules les réponses avec code ``200 OK` sont enregistrées.
- Les erreurs (`403`,`404`)  ne sont pas mises en cache. 

**Commandes de lancement :**
```bash
python relaiCacheHTTP.py 127.0.0.1 6000
# Arguments : <IP_serveur_Censeur> <port_serveur_Censeur>
``` 

### 📜 Outil d’audit HTTP

**Fichier :** `AuditHTTP.py`
**Rôle :**

Analyse le fichier de log http_sniffer.log pour extraire :
- Les requêtes GET observées.

- Les réponses serveur (code HTTP et taille).

- Les requêtes bloquées par le censeur.

Peut filtrer par URI spécifique.

**Utilisation :** 
```bash
Python AuditHTTP.py [mot_cle_URI]
```

**Exemple de sortie :**
```text
=== Analyse du log : http_sniffer.log ===
Requêtes GET enregistrées :
  - Client 127.0.0.1:54393 → /index.html

Réponses serveur enregistrées :
  - Vers 127.0.0.1:54393 | Code 200 | Taille 343 octets

Requêtes BLOQUÉES enregistrées :
  - Client 127.0.0.1:54396 → /admin.html (BLOQUÉE)
```


## Tests 

> 💡 **Remarque :**  
>  Si le relai Cache HTTP s'exécute sur une machine appartenant au réseau du client alors remplacez `127.0.0.1` par l'adresse IP de la machine sur laquelle vous exécutez le relai.  


### Test 1: Requête autorisée 

Depuis la barre de recherche d'un navigateur web, tapez : `http://127.0.0.1:5000/index.html`

**Résultat attendu :**
Si la page demandée est non présente dans le cache, alors le cache cherchera a contacter le serveur HTTP, et puis :
- La page index.html est servie.
- Le sniffer logge la requête et la réponse (200 OK).
- Le cache mémorise la réponse.

### Test 2: Requête bloquée

Depuis la barre de recherche d'un navigateur web, tapez : `http://127.0.0.1:5000/admin.html`

**Résultat attendu :**

- Le censeur renvoie 403 Forbidden.
- Message affiché : “Accès confidentiel mon ami”.
- Le log contient la ligne :

```text
CLIENT 127.0.0.1:54393 → GET /admin.html → BLOQUÉ /admin.html
```

### Test 3: Requête enchaînée

Exécutez un chainage comme ceci : 
`Client->Cache(5000)->Censeur(6000)->Sniffer(7000)->Serveur(8000)`

Depuis la barre de recherche d'un navigateur web, tapez : `http://127.0.0.1:5000/admin.html`

**Résulat attendu et comportement :**
- Cache : recherche la ressource. Si elle n'est pas présente -> joindre le serveur HTTP en transmettant la requête au relai suivant.
- Censeur : vérifie la blacklist. Si la ressource n'est pas censurée -> requête transmise au relai suivant.
- Sniffer : enregistre la requête (et puis la transmet au serveur) et la réponse (après réponse du serveur HTTP).
- Serveur : renvoi la ressource demandée.   


---

## 🧾 Journalisation (Logging)

Pour des raisons de simplification, les relais Censeur et Sniffer partagent le même fichie : `MiniProjet1/Exercice2/QST2/http_sniffer.log`
L’exécution de la chaîne de relais et du serveur en local ne devrait pas poser de problème.
Néanmoins, une limitation apparaît lorsqu’on exécute les scripts séparément sur différentes machines du réseau :
les scripts Censeur et Sniffer, ainsi que les fichiers http_sniffer.log et uri_blacklist.conf, doivent être présents sur la même machine, en adaptant les chemins d’accès aux fichiers en conséquence.

**Exemple de contenu :**

```text
[2025-10-16 16:32:52] CLIENT 127.0.0.1:54393 → GET /index.html
[2025-10-16 16:32:52] SERVEUR → 127.0.0.1:54393 | HTTP/1.1 200 OK | taille=343
Réponse (décodée) :
HTTP/1.1 200 OK

Date: Thu, 16 Oct 2025 14:32:52 GMT

Server: SimplePythonHTTPServer/1.0

Content-Length: 186

Content-Type: text/html

Connection: close



<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <title>Hello World Page</title>

</head>

<body>

    <h1>Hello World! This is your page</h1>

</body>

</html>

[2025-10-16 16:33:36] CLIENT 127.0.0.1:54396 → GET /admin.html → BLOQUÉ /admin.html
[2025-10-16 17:21:08] CLIENT 127.0.0.1:61247 → GET /admin.html → BLOQUÉ /admin.html

```
---

## 🧩 Améliorations possibles

- Ajout d’un timeout configurable sur les sockets.
- Gestion du cache persistant (fichiers locaux).
- Support d’autres méthodes HTTP (POST, HEAD).
- Permettre l'exécution des scripts Censeur et Sniffer dans des machines différentes : trouver une meilleure approche qu'un fichier partagé ou bien permettre d'écrire sur ce fichier en utilisant les Sockets.   
- Interface web pour consulter les logs.
- Statistiques sur les requêtes bloquées et servies depuis le cache.

---

## Auteurs 

**Riad Kouache**
**Bendouha Abderezak** 
Master 1 RES : Internet, Cybersécurité, Cloud et Automatisation
Mini Projet 1 – Relais TCP, HTTP et audit de trafic
Sorbonne Université – 2025/2026