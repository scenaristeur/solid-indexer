python solid_rag_query_crud_function_calling_retrieve.py
2026-02-19 16:34:06,505 - INFO - ****\*\***** Loading indexer
2026-02-19 16:34:06,507 - INFO - [MAIN] - ********************\*\*********************NEW SESSION******************\*\*******************
2026-02-19 16:34:06,517 - INFO - Anonymized telemetry enabled. See https://docs.trychroma.com/telemetry for more information.
2026-02-19 16:34:06,812 - INFO - CRUD Store initialisé avec base: http://localhost:3000/david/notes/
Assistant prêt. Tapez votre question (ou 'quit' pour quitter), ':commande [params]' pour les commandes internes, '/commande [params]' pour les commandes llm

Vous: combien d'oeufs dans le gateau ?
2026-02-19 16:34:24,595 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 16:34:24,601 - INFO - [TOOL CALL]: 1
2026-02-19 16:34:24,601 - INFO - Appel fonction retrieve avec args {'query': "nombre d'œufs dans le gâteau"}
2026-02-19 16:34:24,926 - INFO - Résultat 1: http://localhost:3000/david/notes/recettes.ttl (dist=0.5244) - extrait: Entité: http://localhost:3000/david/notes/recettes...
2026-02-19 16:34:24,926 - INFO - Résultat 2: http://localhost:3000/david/notes/recettes_des_trois_petits_cochons.ttl (dist=0.6264) - extrait: Entité: http://localhost:3000/david/notes/recettes...
2026-02-19 16:34:24,926 - INFO - Résultat 3: http://localhost:3000/david/notes/hello-bonjour.ttl (dist=0.6513) - extrait: Entité: http://localhost:3000/david/notes/hello-bo...
2026-02-19 16:34:24,926 - INFO - Résultat 4: http://localhost:3000/david/notes/porc_roti_au_romarin_pour_le_cochon_lene.ttl (dist=0.6664) - extrait: Entité: http://localhost:3000/david/notes/porc_rot...
2026-02-19 16:34:24,926 - INFO - Résultat 5: http://localhost:3000/david/notes/recette-canele.ttl (dist=0.6693) - extrait: Entité: http://localhost:3000/david/notes/recette-...
2026-02-19 16:34:24,926 - INFO - result Document (source: http://localhost:3000/david/notes/recettes.ttl):
Entité: http://localhost:3000/david/notes/recettes.ttl
type: http://example.org/ns#Note
content: ## Liste des recettes référencées

### 1. [Recettes des Trois Petits Cochons](http://localhost:3000/david/notes/recettes_des_trois_petits_cochons.ttl)

### 2. [Gâteau Jaune Blanc (Émile)](http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl)

### 3. [Canelés](http://localhost:3000/david/notes/recette-canele.ttl)

### 4. [Pancakes au Lait de la Écureuil (Maison du Cochon Gourmand)](http://localhost:3000/david/notes/pancakes_au_lait_de_laecure_maison_du_cochon_gourmand.ttl)

### 5. [Quiche à la Salsepareille](http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl)

### 6. [Porc Roti au Romarin (pour Léne)](http://localhost:3000/david/notes/porc_roti_au_romarin_pour_le_cochon_lene.ttl)

modified: 2026-02-19 15:03:23.519696+00:00

---

Document (source: http://localhost:3000/david/notes/recettes_des_trois_petits_cochons.ttl):
Entité: http://localhost:3000/david/notes/recettes_des_trois_petits_cochons.ttl
type: http://example.org/ns#Note
content: **Recette 1 : soupe aux herbes, maison des cochons sages**

_Une recette réconfortante pour les cochons qui ont construit avec sagesse._

Ingrédients :

- 1 litre d’eau
- 1 oignon
- 2 carottes
- 2 pommes de terre
- 1 bouquet de persil frais
- 1 bouquet de thym
- 1 c. à café de sel
- 1 c. à café de poivre
- 2 c. à soupe d’huile d’olive

Étapes :

1. Épluchez et coupez l’oignon, les carottes, et les pommes de terre en dés.
2. Dans une cocotte, faites revenir l’oignon dans l’huile d’olive.
3. Ajoutez les légumes coupés, couvrez avec l’eau, puis ajoutez les herbes, le sel et le poivre.
4. Laissez mijoter à feu doux pendant environ 30-40 minutes.
5. Servez chaud avec une tranche de pain de campagne.

_Idéal pour une journée d’hiver après une longue journée de construction._
tags: recette,soupe,maison_sage
created: 2026-02-19 13:52:00.347820+00:00

---

Document (source: http://localhost:3000/david/notes/hello-bonjour.ttl):
Entité: http://localhost:3000/david/notes/hello-bonjour.ttl
type: http://example.org/ns#Note
content: Hello, pour dire bonjour tout le monde !
tags:
created: 2026-02-19 11:02:38.384839+00:00

---

Document (source: http://localhost:3000/david/notes/porc_roti_au_romarin_pour_le_cochon_lene.ttl):
Entité: http://localhost:3000/david/notes/porc_roti_au_romarin_pour_le_cochon_lene.ttl
type: http://example.org/ns#Note
content: **Recette 2 : Porc rôti au romarin, maison du cochon paresseux**

\*Un plat festif pour le cochon qui préférait rester au chaud plutôt que de travailler.

Ingrédients :

- 1 morceau de porc (environ 1 kg)
- 4 gousses d’ail hachées
- 2 c. à soupe d’huile d’olive
- 1 branche de romarin
- 1 feuille de laurier
- 1 citron (jus et zeste)
- Sel et poivre
- 2 c. à soupe de miel

Étapes :

1. Préchauffez le four à 180°C.
2. Dans un saladier, mélangez l’huile d’olive, l’ail, le romarin, le laurier, le jus et le zeste de citron, le sel et le poivre.
3. Enveloppez le morceau de porc dans du film alimentaire et massez-le avec ce mélange.
4. Ajoutez le miel sur le porc et placez-le dans un plat.
5. Enfournez pendant 3-4 heures à basse température ou 1h30 à plus haute température.
6. Servez avec des légumes rôtis ou une purée de patates douces.

_Un repas royal pour célébrer les moments de repos bien mérité._
tags: recette,porc,rôti,maison_paresseuse
created: 2026-02-19 13:52:02.227867+00:00

---

Document (source: http://localhost:3000/david/notes/recette-canele.ttl):
Entité: http://localhost:3000/david/notes/recette-canele.ttl
type: http://example.org/ns#Note
content: ### Recette des canelés

**Ingrédients** (pour un moule à canelés de 6 compartiments) :

- 100 g de farine
- 100 g de sucre
- 1 œuf
- 80 ml de lait
- 30 g de beurre fondu
- 1 pincée de sel
- 1 sachet de sucre vanillé (ou 1 c. à café d’extrait de vanille)
- Zeste d’1/2 citron (optionnel)

**Ustensiles** :

- Un moule à canelés bien beurré et fariné
- Un fouet
- Une cuillère à soupe

**Étapes** :

1. **Préchauffez** le four à 180°C (th. 6). Beurrez et farinez généreusement le moule à canelés.
2. **Mélangez** la farine, le sucre et le sel dans un saladier.
3. **Ajoutez** l’œuf, le sucre vanillé, le zeste de citron (si utilisé) et le beurre fondu. Fouettez jusqu’à obtenir une pâte lisse et homogène.
4. **Incorporez** le lait petit à petit en fouettant pour éviter les grumeaux. La pâte doit être assez liquide pour couler dans le moule.
5. **Remplissez** le moule à ras bord avec la pâte en évitant les bulles d’air.
6. **Enfournez** pour **12 à 15 minutes** : les canelés doivent être dorés et gonflés, mais pas brûlés. Vérifiez qu’ils sont bien cuits en plantant la pointe d’un couteau dans un canelé (il doit ressortir sec).
7. **Sortez** du four et laissez refroidir **2 minutes** avant de démouler. Servez tiède.

**Astuce** : Pour des canelés encore plus moelleux, ajoutez 1 c. à soupe de rhum ou d’eau de fleur d’oranger à la pâte.

**Variante** : Vous pouvez ajouter une touche de cannelle ou de noix de muscade pour parfumer.

Bon appétit ! 🍮✨
tags:
created: 2026-02-19 13:41:55.344366+00:00
2026-02-19 16:34:25,352 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Pour la recette des **canelés**, il faut **1 œuf**.

Pour les autres recettes, il n'y a pas d'indication sur le nombre d'œufs dans un gâteau spécifique (comme le _"Gâteau Jaune Blanc (Émile)"_).
Si tu cherches une autre recette précise, dis-le-moi ! 😊

Vous: où est-il question de javascript ?
2026-02-19 16:35:14,979 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 16:35:14,980 - INFO - [TOOL CALL]: 1
2026-02-19 16:35:14,985 - INFO - Appel fonction retrieve avec args {'query': 'javascript'}
2026-02-19 16:35:15,230 - INFO - Résultat 1: http://localhost:3000/david/notes/tech-javascript-python-paul.ttl (dist=0.6959) - extrait: Entité: http://localhost:3000/david/notes/tech-jav...
2026-02-19 16:35:15,230 - INFO - Résultat 2: http://localhost:3000/david/notes/hello-trevor.ttl (dist=0.7643) - extrait: Entité: http://localhost:3000/david/notes/hello-tr...
2026-02-19 16:35:15,230 - INFO - Résultat 3: http://localhost:3000/david/notes/outils.ttl (dist=0.8187) - extrait: Entité: http://localhost:3000/david/notes/outils.t...
2026-02-19 16:35:15,230 - INFO - Résultat 4: http://localhost:3000/david/notes/RomansTop.ttl (dist=0.8495) - extrait: Entité: http://localhost:3000/david/notes/RomansTo...
2026-02-19 16:35:15,230 - INFO - Résultat 5: http://localhost:3000/david/notes/swing.ttl (dist=0.8754) - extrait: Entité: http://localhost:3000/david/notes/swing.tt...
2026-02-19 16:35:15,230 - INFO - result Document (source: http://localhost:3000/david/notes/tech-javascript-python-paul.ttl):
Entité: http://localhost:3000/david/notes/tech-javascript-python-paul.ttl
type: http://example.org/ns#Note
content: Langages : JavaScript et Python
Auteur de référence : Paul (à préciser selon contexte)
tags: tech,javascript,python,auteur
created: 2026-02-19 10:54:53.083737+00:00

---

Document (source: http://localhost:3000/david/notes/hello-trevor.ttl):
Entité: http://localhost:3000/david/notes/hello-trevor.ttl
type: http://example.org/ns#Note
content: Bonjour Trevor ! 👋
Trevor, tu es un développeur JS talentueux qui travaille sur Solid. J’espère que tu vas bien et que ton travail avance super ! Si tu as besoin de quelque chose ou si tu veux échanger, n’hésite pas.
À très vite !
tags: bonjour,developpeur,work,js,solid
created: 2026-02-19 13:38:57.350701+00:00

---

Document (source: http://localhost:3000/david/notes/outils.ttl):
Entité: http://localhost:3000/david/notes/outils.ttl
type: http://example.org/ns#Note
content: "type": "function",
"function": {
"name": "create_note",
"description": "Crée une nouvelle note avec un titre et un contenu",
"parameters": {
"type": "object",
"properties": {
modified: 2026-02-19 07:38:48.853335+00:00

---

Document (source: http://localhost:3000/david/notes/RomansTop.ttl):
Entité: http://localhost:3000/david/notes/RomansTop.ttl
type: http://example.org/ns#Note
content: Fondation
Auteur : Asimov, Isaac
modified: 2026-02-19 15:03:21.704523+00:00

---

Document (source: http://localhost:3000/david/notes/swing.ttl):
Entité: http://localhost:3000/david/notes/swing.ttl
type: http://example.org/ns#Note
content: Swing est un style musical né à New York au début du 20e siècle, issus des traditions musicales africaines et européennes. Il est souvent associé à des rythmes entraînants, des improvisations et des orchestrations riches.
tags: musique,jazz,styles
created: 2026-02-19 12:26:29.254391+00:00
2026-02-19 16:35:15,972 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Voici les mentions de **JavaScript** dans tes notes :

1. **Note sur les langages techniques** :
   - [JavaScript et Python](http://localhost:3000/david/notes/tech-javascript-python-paul.ttl) (mentionne JavaScript aux côtés de Python).

2. **Message à Trevor (développeur JS)** :
   - [Trevor, développeur JS talentueux](http://localhost:3000/david/notes/hello-trevor.ttl) (lié à Solid et mention explicite de JavaScript).
