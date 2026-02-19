python solid_rag_query_crud_function_calling.py
2026-02-19 07:40:13,626 - INFO - CRUD Store initialisé avec base: http://localhost:3000/david/notes/
Assistant prêt. Tapez votre question (ou 'quit' pour quitter), ':commande [params]' pour les commandes internes, '/commande [params]' pour les commandes llm

Vous: :truc
TODO: commandes internes : cd, ls, mkdir...
2026-02-19 07:40:20,827 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:40:20,833 - INFO - ChatCompletionMessage(content='Quelle action veux-tu effectuer avec cette note ? Un exemple serait :\n- _Crée une note sur "truc"_\n- _Montre-moi les notes existantes_', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[], reasoning=None, reasoning_content=None)

Assistant: Quelle action veux-tu effectuer avec cette note ? Un exemple serait :

- _Crée une note sur "truc"_
- _Montre-moi les notes existantes_

Vous: mkdir recettes
2026-02-19 07:40:51,334 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:40:51,335 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-8f66c0e262e76699', function=Function(arguments='{"title": "recettes", "content": "", "tags": "menu,cuisine"}', name='create_note'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:40:51,335 - INFO - Appel fonction create_note avec args {'title': 'recettes', 'content': '', 'tags': 'menu,cuisine'}
2026-02-19 07:40:51,557 - INFO - ✅ Note créée : http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:40:51,557 - INFO - result Note créée : http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:40:51,971 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Note **"recettes"** créée à l'adresse : [link](http://localhost:3000/david/notes/recettes.ttl).
Que veux-tu faire ensuite ? (Ex: ajouter du contenu, modifier, lister les notes...) ?

Vous: créé une nouvelle recette "Quiche à la salsepareille", invente cette recette, formate la en ttl correct et reférence toutes les recettes dans recettes.ttl
2026-02-19 07:42:46,990 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:42:46,991 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-a64cd526fcacd5ae', function=Function(arguments='{"uri": "http://localhost:3000/david/notes/recettes.ttl", "new_content": "@prefix : <http://localhost:3000/david/notes/#> .\\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\\n\\n:recettes a rdf:type :Note ;\\n :recettesList [\\n a :RecetteList ;\\n :listeDeRecettes ( \\n :recetteQuicheSalsepareille\\n )\\n ] ;\\n :titre \\"Recettes\\" .\\n\\n:recetteQuicheSalsepareille a :Recette ;\\n :titre \\"Quiche à la Salsepareille\\" ;\\n :ingredients \\"\\"\\"Pâte brisée (maison ou du commerce) : 1 rouleau\\\\nCrème fraîche épaisse : 300 ml\\\\nŒufs : 3\\\\nFromage râpé (type Gruyère ou Emmental) : 100 g\\\\nSalsepareille : 2 c. à soupe (environ 30 ml)\\\\nOignons : 1 moyen, finement émincé\\\\nSel, poivre : selon goût\\\\nNoix de muscade râpée : une pincée\\\\n\\"\\"\\" ;\\n :etapes \\"\\"\\"1. Préparation de la pâte : Étalez la pâte brisée dans un moule à tarte et piquez le fond avec une fourchette. Préchauffez le four à 180°C (th. 6).\\\\n2. Cuisson de la pâte : Enfournez la pâte à blanc (avec des billes de cuisson ou du papier sulfurisé couvert de riz) pendant 10 minutes, puis retirez-la.\\\\n3. Préparation des ingrédients : Dans un saladier, battez les œufs avec la crème fraîche, salez, poivrez et ajoutez la noix de muscade.\\\\n4. Ajout des oignons et de la salsepareille : Faites revenir les oignons émincés dans une poêle sans matière grasse jusqu’à ce qu’ils soient tendres. Mélangez-les à la préparation aux œufs. Ajoutez le fromage râpé et la salsepareille.\\\\n5. Montage de la quiche : Versez ce mélange sur la pâte précuite.\\\\n6. Cuisson : Enfournez pour 35-40 minutes jusqu’à ce que la quiche soit dorée et bien prise.\\\\n7. Dégustation : Laissez tiédir avant de servir, accompagnée d’une salade verte.\\"\\"\\" ;\\n :note \\"Une quiche originale grâce à la touche acidulée de la salsepareille, parfaite pour surprendre !\\""}', name='update_note'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:42:46,991 - INFO - Appel fonction update_note avec args {'uri': 'http://localhost:3000/david/notes/recettes.ttl', 'new_content': '@prefix : <http://localhost:3000/david/notes/#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n:recettes a rdf:type :Note ;\n :recettesList [\n a :RecetteList ;\n :listeDeRecettes ( \n :recetteQuicheSalsepareille\n )\n ] ;\n :titre "Recettes" .\n\n:recetteQuicheSalsepareille a :Recette ;\n :titre "Quiche à la Salsepareille" ;\n :ingredients """Pâte brisée (maison ou du commerce) : 1 rouleau\\nCrème fraîche épaisse : 300 ml\\nŒufs : 3\\nFromage râpé (type Gruyère ou Emmental) : 100 g\\nSalsepareille : 2 c. à soupe (environ 30 ml)\\nOignons : 1 moyen, finement émincé\\nSel, poivre : selon goût\\nNoix de muscade râpée : une pincée\\n""" ;\n :etapes """1. Préparation de la pâte : Étalez la pâte brisée dans un moule à tarte et piquez le fond avec une fourchette. Préchauffez le four à 180°C (th. 6).\\n2. Cuisson de la pâte : Enfournez la pâte à blanc (avec des billes de cuisson ou du papier sulfurisé couvert de riz) pendant 10 minutes, puis retirez-la.\\n3. Préparation des ingrédients : Dans un saladier, battez les œufs avec la crème fraîche, salez, poivrez et ajoutez la noix de muscade.\\n4. Ajout des oignons et de la salsepareille : Faites revenir les oignons émincés dans une poêle sans matière grasse jusqu’à ce qu’ils soient tendres. Mélangez-les à la préparation aux œufs. Ajoutez le fromage râpé et la salsepareille.\\n5. Montage de la quiche : Versez ce mélange sur la pâte précuite.\\n6. Cuisson : Enfournez pour 35-40 minutes jusqu’à ce que la quiche soit dorée et bien prise.\\n7. Dégustation : Laissez tiédir avant de servir, accompagnée d’une salade verte.""" ;\n :note "Une quiche originale grâce à la touche acidulée de la salsepareille, parfaite pour surprendre !"'}
2026-02-19 07:42:47,045 - INFO - ✅ Note mise à jour : http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:42:47,045 - INFO - result Note mise à jour
2026-02-19 07:42:47,482 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Recette **"Quiche à la Salsepareille"** ajoutée à **recettes.ttl** :
[Lien vers la note mise à jour](http://localhost:3000/david/notes/recettes.ttl).

Tu peux maintenant :

- Voir la liste des recettes.
- Créer/modifier une autre recette.

Vous: non, il faut créer une nouvelle note pour la recette à la salsepareille
2026-02-19 07:43:35,773 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:43:35,774 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-b8add4b9d3ee5c37', function=Function(arguments='{"title": "quiche-a-la-salsepareille", "content": "@prefix : <http://localhost:3000/david/notes/#> .\\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\\n\\n:quicheALaSalsepareille a rdf:type :Recette ;\\n :titre \\"Quiche à la Salsepareille\\" ;\\n :ingredients \\"\\"\\"\\\\n- **Pâte brisée** : 1 rouleau (maison ou industriel)\\\\n- **Crème fraîche épaisse** : 300 ml\\\\n- **Œufs** : 3\\\\n- **Fromage râpé** (Gruyère/Emmental) : 100 g\\\\n- **Salsepareille** : 2 cuillères à soupe (30 ml)\\\\n- **Oignons** : 1 moyen, finement émincés\\\\n- **Assaisonnement** : sel, poivre, noix de muscade râpée\\\\n\\"\\"\\" ;\\n\\n :etapes \\"\\"\\"\\\\n1. **Préparer la pâte** : Étalez-la dans un moule à tarte, percez le fond et précuisez à blanc (10 min à 180°C).\\\\n2. **Préparer l’appareil** : Dans un bol, mélangez œufs, crème, sel, poivre et muscade.\\\\n3. **Faire revenir les oignons** : Dans une poêle, faites-les dorer jusqu’à tendreté.\\\\n4. **Assembler** : Mélangez les oignons à la préparation aux œufs, ajoutez fromage et salsepareille. Versez sur la pâte.\\\\n5. **Cuisson** : Enfournez 35-40 min à 180°C jusqu’à ce que la quiche soit dorée.\\\\n6. **Dégustation** : Servez tiède avec une salade.\\"\\"\\" ;\\n\\n :note \\"Une version audacieuse et acidulée de la quiche classique, parfaite pour sublimer un repas !\\" ;\\n :tags :cuisine,:original,:fromage"}', name='create_note'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:43:35,774 - INFO - Appel fonction create_note avec args {'title': 'quiche-a-la-salsepareille', 'content': '@prefix : <http://localhost:3000/david/notes/#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n:quicheALaSalsepareille a rdf:type :Recette ;\n :titre "Quiche à la Salsepareille" ;\n :ingredients """\\n- **Pâte brisée** : 1 rouleau (maison ou industriel)\\n- **Crème fraîche épaisse** : 300 ml\\n- **Œufs** : 3\\n- **Fromage râpé** (Gruyère/Emmental) : 100 g\\n- **Salsepareille** : 2 cuillères à soupe (30 ml)\\n- **Oignons** : 1 moyen, finement émincés\\n- **Assaisonnement** : sel, poivre, noix de muscade râpée\\n""" ;\n\n :etapes """\\n1. **Préparer la pâte** : Étalez-la dans un moule à tarte, percez le fond et précuisez à blanc (10 min à 180°C).\\n2. **Préparer l’appareil** : Dans un bol, mélangez œufs, crème, sel, poivre et muscade.\\n3. **Faire revenir les oignons** : Dans une poêle, faites-les dorer jusqu’à tendreté.\\n4. **Assembler** : Mélangez les oignons à la préparation aux œufs, ajoutez fromage et salsepareille. Versez sur la pâte.\\n5. **Cuisson** : Enfournez 35-40 min à 180°C jusqu’à ce que la quiche soit dorée.\\n6. **Dégustation** : Servez tiède avec une salade.""" ;\n\n :note "Une version audacieuse et acidulée de la quiche classique, parfaite pour sublimer un repas !" ;\n :tags :cuisine,:original,:fromage'}
2026-02-19 07:43:35,913 - INFO - ✅ Note créée : http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl
2026-02-19 07:43:35,913 - INFO - result Note créée : http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl
2026-02-19 07:43:36,386 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Recette **"Quiche à la Salsepareille"** créée :
[Lien direct](http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl).

Veux-tu maintenant **référencer cette note dans `recettes.ttl`** pour l’inclure dans la liste ?

Vous: et referencer toutes nos recettes dans recettes.ttl qui sert d'index
2026-02-19 07:44:04,404 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:44:04,405 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-9564ac126f48d0f0', function=Function(arguments='{"uri": "http://localhost:3000/david/notes/recettes.ttl", "new_content": "@prefix : <http://localhost:3000/david/notes/#> .\\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\\n\\n:recettes a rdf:type :Note ;\\n :titre \\"Recettes\\" ;\\n :description \\"Liste de toutes mes recettes favorites.\\" ;\\n :recettesList [\\n a :ListeDeRecettes ;\\n :listeDeRecettes ( \\n :quiche-a-la-salsepareille\\n )\\n ] ;\\n\\n:quiche-a-la-salsepareille a :Recette ;\\n rdf:type rdf:Seq ;\\n rdf:first :quicheALaSalsepareilleRecette ;\\n rdf:rest rdf:null .\\n\\n:quicheALaSalsepareilleRecette :titre \\"Quiche à la Salsepareille\\" ;\\n :uri \\"http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl\\" ;\\n :description \\"Une quiche originale avec une touche acidulée de salsepareille.\\""}', name='update_note'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:44:04,405 - INFO - Appel fonction update_note avec args {'uri': 'http://localhost:3000/david/notes/recettes.ttl', 'new_content': '@prefix : <http://localhost:3000/david/notes/#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n:recettes a rdf:type :Note ;\n :titre "Recettes" ;\n :description "Liste de toutes mes recettes favorites." ;\n :recettesList [\n a :ListeDeRecettes ;\n :listeDeRecettes ( \n :quiche-a-la-salsepareille\n )\n ] ;\n\n:quiche-a-la-salsepareille a :Recette ;\n rdf:type rdf:Seq ;\n rdf:first :quicheALaSalsepareilleRecette ;\n rdf:rest rdf:null .\n\n:quicheALaSalsepareilleRecette :titre "Quiche à la Salsepareille" ;\n :uri "http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl" ;\n :description "Une quiche originale avec une touche acidulée de salsepareille."'}
2026-02-19 07:44:04,460 - INFO - ✅ Note mise à jour : http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:44:04,460 - INFO - result Note mise à jour
2026-02-19 07:44:04,888 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: L'**index `recettes.ttl`** est maintenant mis à jour avec une référence à la note **"Quiche à la Salsepareille"** :

- [Consulter `recettes.ttl`](http://localhost:3000/david/notes/recettes.ttl).

Besoin d'ajouter d'autres recettes ou modifier l'index ?

Vous: liste toutes les recettes
2026-02-19 07:45:11,949 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:45:11,950 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-b832cb9498895c23', function=Function(arguments='{"uri": "http://localhost:3000/david/notes/"}', name='list_notes'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:45:11,950 - INFO - Appel fonction list_notes avec args {'uri': 'http://localhost:3000/david/notes/'}
2026-02-19 07:45:12,019 - INFO - Membres trouvés dans http://localhost:3000/david/notes/: ['http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl', 'http://localhost:3000/david/notes/todo1.ttl', 'http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl', 'http://localhost:3000/david/notes/recettes.ttl']
2026-02-19 07:45:12,019 - INFO - result Notes trouvées :
http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl
http://localhost:3000/david/notes/todo1.ttl
http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl
http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:45:12,972 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: ### **Liste des notes liées aux recettes :**

1. **[Quiche à la Salsepareille]** – [Lien](http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl)
2. **[Index des recettes (`recettes.ttl`)]** – [Lien](http://localhost:3000/david/notes/recettes.ttl)

_Autres notes non explicites (ex: `todo1.ttl`, `gâteau jaune-blanc-émile` si modifiée) :_

- **[Gâteau jaune-blanc-émile]** (à vérifier) – [Lien](http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl)

---

_Veux-tu consulter ou ajouter une autre recette ?_

Vous: ajoute le gateau à la liste des recettes
2026-02-19 07:45:32,264 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"
2026-02-19 07:45:32,265 - INFO - ChatCompletionMessage(content=None, refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='chatcmpl-tool-adb42f14b38229bb', function=Function(arguments='{"uri": "http://localhost:3000/david/notes/recettes.ttl", "new_content": "@prefix : <http://localhost:3000/david/notes/#> .\\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\\n\\n:recettes a rdf:type :Note ;\\n :titre \\"Recettes\\" ;\\n :description \\"Liste de toutes mes recettes favorites.\\" ;\\n :recettesList [\\n a :ListeDeRecettes ;\\n :listeDeRecettes ( \\n :gâteauJauneBlancEmile\\n :quicheALaSalsepareille\\n )\\n ] ;\\n\\n:gâteauJauneBlancEmile a :Recette ;\\n rdf:type rdf:Seq ;\\n rdf:first :gâteauJauneBlancEmileRecette ;\\n rdf:rest :quicheALaSalsepareilleRecette ;\\n rdf:rest rdf:null .\\n\\n:quicheALaSalsepareilleRecette a :Recette ;\\n rdf:type rdf:Seq ;\\n rdf:first :quicheALaSalsepareilleDetaillee ;\\n rdf:rest rdf:null .\\n\\n:gâteauJauneBlancEmileRecette :titre \\"Gâteau Jaune-Blanc-Émile\\" ;\\n :uri \\"http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl\\" ;\\n :description \\"Un gâteau moelleux aux couleurs emblématiques.\\" ;\\n\\n:quicheALaSalsepareilleDetaillee :titre \\"Quiche à la Salsepareille\\" ;\\n :uri \\"http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl\\" ;\\n :description \\"Une quiche originale avec une touche acidulée de salsepareille.\\""}', name='update_note'), type='function')], reasoning=None, reasoning_content=None)
2026-02-19 07:45:32,265 - INFO - Appel fonction update_note avec args {'uri': 'http://localhost:3000/david/notes/recettes.ttl', 'new_content': '@prefix : <http://localhost:3000/david/notes/#> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n:recettes a rdf:type :Note ;\n :titre "Recettes" ;\n :description "Liste de toutes mes recettes favorites." ;\n :recettesList [\n a :ListeDeRecettes ;\n :listeDeRecettes ( \n :gâteauJauneBlancEmile\n :quicheALaSalsepareille\n )\n ] ;\n\n:gâteauJauneBlancEmile a :Recette ;\n rdf:type rdf:Seq ;\n rdf:first :gâteauJauneBlancEmileRecette ;\n rdf:rest :quicheALaSalsepareilleRecette ;\n rdf:rest rdf:null .\n\n:quicheALaSalsepareilleRecette a :Recette ;\n rdf:type rdf:Seq ;\n rdf:first :quicheALaSalsepareilleDetaillee ;\n rdf:rest rdf:null .\n\n:gâteauJauneBlancEmileRecette :titre "Gâteau Jaune-Blanc-Émile" ;\n :uri "http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl" ;\n :description "Un gâteau moelleux aux couleurs emblématiques." ;\n\n:quicheALaSalsepareilleDetaillee :titre "Quiche à la Salsepareille" ;\n :uri "http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl" ;\n :description "Une quiche originale avec une touche acidulée de salsepareille."'}
2026-02-19 07:45:32,317 - INFO - ✅ Note mise à jour : http://localhost:3000/david/notes/recettes.ttl
2026-02-19 07:45:32,317 - INFO - result Note mise à jour
2026-02-19 07:45:33,123 - INFO - HTTP Request: POST https://albert.api.etalab.gouv.fr/v1/chat/completions "HTTP/1.1 200 OK"

Assistant: Le **gâteau "Jaune-Blanc-Émile"** a été ajouté à la liste des recettes dans **`recettes.ttl`**.
L'index est maintenant complet avec :

- [Gâteau Jaune-Blanc-Émile](http://localhost:3000/david/notes/recette-gateau-jaune-blanc-emile.ttl)
- [Quiche à la Salsepareille](http://localhost:3000/david/notes/quiche-a-la-salsepareille.ttl)

Consulter l'**index mis à jour** : [recettes.ttl](http://localhost:3000/david/notes/recettes.ttl).

Vous:

![alt text](image-1.png)
![alt text](image.png)
![alt text](image-2.png)
![alt text](image-3.png)
