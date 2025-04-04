# ELE610 Applied Robot Technology, V-2025

## ABB Robot Assignment 2

### 1. Introduction
Dans ce projet, vous devez créer un programme de dessin simple pour le robot ABB IRB 140 (Rudolf). Vous devez utiliser la documentation RAPID pour vous aider dans votre travail.

L'approbation de l'assignation se fait en démontrant le programme à l'enseignant, puis en soumettant le code RAPID sous forme de fichier texte (.txt) ou PDF.

---

### 2. Préparation de l'environnement

#### 2.1 Téléchargement et ouverture du fichier Pack and Go
1. Télécharger le fichier `UiS_E458_nov18.rspag%`.
2. Ouvrir **RobotStudio**.
3. Aller dans l'onglet `File` > `Open` > `Pack and Go` et sélectionner le fichier téléchargé.
4. Sélectionner un dossier cible (`R:\Projects\RS2`).
5. Choisir d'utiliser les fichiers locaux pour les doublons.
6. Sélectionner `RobotWare 6.14.01.00` pour les contrôleurs virtuels.
7. Vérifier les options sélectionnées et cliquer sur `Finish`.
8. Fermer l'assistant et activer l'onglet `Home`.

#### 2.2 Nettoyage de la scène
1. Supprimer tous les éléments inutiles, sauf Rudolf, la table adjacente et le stylo.
2. Vérifier que la simulation fonctionne toujours.
3. Supprimer le chemin prédéfini de Rudolf et ne conserver qu'un point à 30 mm au-dessus du centre de la table.
4. Modifier `main()` pour ne contenir qu'un déplacement vers ce point.

#### 2.3 Ajout d'une feuille A4
1. Aller dans `Modeling` > `Surface` > `Surface Rectangle`.
2. Définir une surface de 297 mm × 210 mm, couleur blanche, nommée `A4sheet`.
3. Placer la feuille à **0.1 mm au-dessus du centre de la table**.
4. Copier `wobjTableR` en `wobjA4` et ajuster la hauteur.
5. Synchroniser le code RAPID et vérifier la position du stylo.

---

### 3. Programmation du dessin

#### 3.1 Dessiner un rectangle
1. Définir 4 points cibles pour un rectangle de **70 mm × 50 mm**.
2. Ajouter les déplacements dans `main()`.
3. Activer `TCP Trace` pour visualiser le chemin.

#### 3.2 Fonction paramétrique pour dessiner un rectangle
1. Créer une procédure prenant un point de référence et les dimensions du rectangle.
2. Ajouter des déplacements pour dessiner des rectangles imbriqués :
   - 70 mm × 50 mm
   - 80 mm × 60 mm
   - 90 mm × 70 mm
3. Synchroniser et tester la simulation.

#### 3.3 Dessiner des triangles et des cercles
1. Créer `drawTriangle()` pour dessiner un **triangle équilatéral centré sur un point donné**.
2. Créer `drawCircle()` utilisant `MoveC` pour dessiner un **cercle centré sur un point donné**.
3. Modifier `main()` pour dessiner :
   - Un carré de **100 mm × 100 mm**
   - Un triangle et un cercle à chaque coin du carré
4. Synchroniser et tester la simulation.

#### 3.4 Contrôle du programme
1. Utiliser les boucles `FOR`, `WHILE`, et les instructions `IF`, `GOTO` pour créer `drawShapes()`.
2. La fonction doit dessiner un nombre défini de carrés et de cercles imbriqués.
3. Vérifier que chaque objet s'inscrit dans le précédent.
4. Synchroniser et tester la simulation.

#### 3.5 Interaction utilisateur
1. Utiliser `TEST`, `TPWrite`, `TPReadFK` et `TPReadNum` pour ajouter un menu interactif via le **FlexPendant virtuel**.
2. Permettre à l'utilisateur de sélectionner la section du programme à exécuter.
3. Vérifier que le programme fonctionne correctement.

---

### 4. Exécution sur le robot physique

#### 4.1 Sécurité
1. Effectuer une initiation à la sécurité avec un enseignant.
2. Vérifier que le bon outil est monté sur Rudolf.
3. S'entraîner à **manipuler le robot avec le FlexPendant**.

#### 4.2 Connexion au robot physique
1. Se connecter au **réseau sans fil du robot** (`NorbertRudolf`).
2. Ouvrir **RobotStudio** sans charger de station.
3. Aller dans `Controller` > `Add Controller`.
4. Entrer l'adresse IP de Rudolf : **152.94.160.197**.
5. Demander un accès en écriture (`Request Write Access`).
6. Supprimer le programme existant (`Delete`).
7. Charger le programme depuis votre PC (`Load`).

#### 4.3 Exécution du programme
1. Activer le programme via l'onglet `RAPID` (`Ctrl + S`, puis `Ctrl + Shift + S`).
2. Exécuter pas à pas avec le FlexPendant (`⏯` bouton `Step`).
3. Vérifier que la position du stylo correspond bien à celle de la simulation.
4. Ajuster `wobjA4` si nécessaire.
5. Exécuter le programme en continu (`⏯` bouton `Play`).
6. Montrer le résultat à l'enseignant.

---

### 5. Extensions optionnelles

#### 5.1 Stylo triple
1. Remplacer le stylo simple par `TriplePen.rslib` et `TriplePen.mod`.
2. Dessiner les mêmes formes avec le triple stylo.
3. Ajouter une option pour sélectionner la couleur du stylo.

#### 5.2 Formes avancées
1. Ajouter de nouvelles formes géométriques.
2. Expérimenter avec des motifs artistiques.

---

### 6. Soumission
- **Démonstration obligatoire** du programme à l'enseignant.
- **Soumission du code RAPID** en fichier `.txt` sur Canvas.
- (Optionnel) Ajouter des commentaires ou questions dans un fichier PDF.

---

### 7. Conclusion
Cette assignation vous permet d'explorer la programmation de robots ABB avec **RAPID** et **RobotStudio** en créant un programme de dessin interactif.
