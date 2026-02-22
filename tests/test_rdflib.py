from rdflib import Graph, URIRef, Literal, Namespace
g2 = Graph()
# src = '''
# @prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
# @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
# [ a rdf:Statement ;
#    rdf:subject <http://rdflib.net/store#ConjunctiveGraph>;
#    rdf:predicate rdfs:label;
#    rdf:object "Conjunctive Graph" ] .
#  '''
src= '''@prefix : <http://localhost:3000/david/aventures/ilots/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:ile_python rdf:type :Ilot ;
    rdfs:label "Ile Python" ;
    :description "Un îlot mystérieux entouré de forêts enchantées où la langue Python règne en maîtresse." ;
    :theme "Programmation, Logique, Communauté" ;
    :difficulte "Moyenne" ;
    :objectif "Résoudre des énigmes logiques pour débloquer des portes dans des temples codés." ;
    :recompense "Un artefact magique : le 'Bâton des Boucles', qui permet de répéter les actions avec magic." ;
    :degats "Aucun, mais évite les 'Serpents de SyntaxError' qui apparaissent la nuit." ;
    :accessibleVia "Un pont de code flottant sur le 'Lac de la Documentation' situé à l'est des 'Montagnes des Erreurs'." ;
    :historique "La légende raconte que les premiers chercheurs en informatique ont posé le pied ici après avoir résolu un problème de récursivité infinie." ;
    :piège "Attention aux 'Pièges de Typage' disséminés dans les sentiers, ils changent le type des objets sans prévenir."
    ;
    :elementsClés [
        a :ListeEléments ;
        :élément1 "Comprendre les concepts de base de Python (variables, boucles, conditions)" ;
        :élément2 "Résoudre des énigmes basées sur des algorithmes simples" ;
        :élément3 "Collaborer avec d'autres aventuriers pour coder des solutions collectives"
    ] .'''
g2 = g2.parse(data=src, format='n3')
print(len(g2))
