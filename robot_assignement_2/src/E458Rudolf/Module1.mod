MODULE Module1
    PERS tooldata tSimplePen:=[TRUE,[[0,0,110],[1,0,0,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    TASK PERS wobjdata wobjA4:=[FALSE,TRUE,"",[[5.873368922,412.148225486,9.1],[0,0.707106781,0.707106781,0]],[[0,0,0],[1,0,0,0]]];
    
    CONST robtarget Target_10:=[[105,148.5,-29.9],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    
PROC Path_10()
    MoveL Target_10,v1000,z100,tSimplePen\WObj:=wobjA4;
ENDPROC
    
PROC DrawRectangle(robtarget refPoint, num width, num height)
    VAR robtarget P1;
    VAR robtarget P2;
    VAR robtarget P3;
    VAR robtarget P4;

    
    P1 := refPoint;
    P2 := P1;
    P2.trans.x := P1.trans.x + width;
    P3 := P2;
    P3.trans.y := P2.trans.y + height;
    P4 := P3;
    P4.trans.x := P1.trans.x;

    
    MoveL P1, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P2, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P3, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P4, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P1, v200, z5, tSimplePen\WObj:=wobjA4; 
ENDPROC
    
PROC DrawTriangle(robtarget refPoint, num sideLength)
    VAR robtarget P1;
    VAR robtarget P2;
    VAR robtarget P3;
    VAR num height;

    
    height := (sideLength * sqrt(3)) / 2;

    
    P1 := refPoint;
    P1.trans.y := refPoint.trans.y + (height / 3) * 2; 

    P2 := refPoint;
    P2.trans.x := refPoint.trans.x - (sideLength / 2);
    P2.trans.y := refPoint.trans.y - (height / 3);

    P3 := refPoint;
    P3.trans.x := refPoint.trans.x + (sideLength / 2);
    P3.trans.y := refPoint.trans.y - (height / 3);

    
    MoveL P1, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P2, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P3, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveL P1, v200, z5, tSimplePen\WObj:=wobjA4;
ENDPROC
     

PROC DrawCircle(robtarget refPoint, num radius)
    VAR robtarget P1;
    VAR robtarget P2;
    VAR robtarget P3;
    VAR robtarget P4;

    P1 := refPoint;
    P1.trans.x := refPoint.trans.x - radius;

    P2 := refPoint;
    P2.trans.y := refPoint.trans.y - radius;

    P3 := refPoint;
    P3.trans.x := refPoint.trans.x + radius;
    
    P4 := refPoint;
    P4.trans.y := refPoint.trans.y + radius;
    
    MoveL P1, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveC P2, P3, v200, z5, tSimplePen\WObj:=wobjA4;
    MoveC P4, P1, v200, z5, tSimplePen\WObj:=wobjA4;
ENDPROC

PROC DrawShapes(robtarget refPoint, num startSize, num j, num numShapes)
    VAR num i;
    VAR num size;
    VAR num radius;

    FOR i FROM 0 TO numShapes-1 DO
        size := startSize + (i * j);
        DrawRectangle refPoint, size, size ;
    ENDFOR

    radius := startSize / 2;  
    i := 0;

    WHILE i < numShapes DO
        IF radius > 0 THEN
            DrawCircle refPoint, radius;
            radius := radius + j / 2;
        ELSE
            GOTO EndLoop;
        ENDIF
        i := i + 1;
    ENDWHILE

    EndLoop:
        RETURN;
ENDPROC

PROC ShowMenu()
    VAR num choice;
    VAR num validChoice;
    VAR num userInput;
    VAR robtarget refPoint := [[105, 148.5, 0], [1, 0, 0, 0], [0, 0, 0, 0], [9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    
    WHILE TRUE DO
        ! Afficher le menu
        TPWrite "=== Menu Interactif ===";
        TPWrite "1 - Dessiner un rectangle";
        TPWrite "2 - Dessiner un cercle";
        TPWrite "3 - Dessiner formes imbriquées";
        TPWrite "4 - Quitter";
        
        ! Lire le choix utilisateur
        TPReadNum userInput,"";
        
        ! Vérification du choix
        validChoice := 0;  ! Reset validation

        TEST userInput
        CASE 1:
            TPWrite "Taille du rectangle (ex: 80) ?";
            TPReadNum choice,"";
            DrawRectangle refPoint, choice, choice;
            validChoice := 1;
        CASE 2:
            TPWrite "Rayon du cercle (ex: 50) ?";
            TPReadNum choice,"";
            DrawCircle refPoint, choice;
            validChoice := 1;
        CASE 3:
            TPWrite "Nombre de formes imbriquées (ex: 3) ?";
            TPReadNum choice,"";
            DrawShapes refPoint, 50, 10, choice;
            validChoice := 1;
        CASE 4:
            TPWrite "Fin du programme.";
            RETURN;
        DEFAULT:
            TPWrite "Choix invalide, veuillez entrer un nombre entre 1 et 4.";
        ENDTEST

        ! Attendre une action valide avant de réafficher le menu
        IF validChoice = 1 THEN
            TPWrite "Dessin terminé. Retour au menu.";
        ELSE
            TPWrite "Veuillez réessayer.";
        ENDIF
    ENDWHILE
ENDPROC

    PROC main()
        VAR robtarget refPoint:=[[105,148.5,0],[1,0,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

        Path_10;
        !DrawRectangle refPoint, 70, 50;
        !DrawRectangle refPoint, 80, 60;
        !DrawRectangle refPoint, 90, 70;
        !DrawRectangle refPoint, 100, 100;
        !DrawTriangle refPoint, 100;
        !DrawCircle refPoint,100;
        !DrawShapes refPoint, 50, 10, 5;
        ShowMenu;
        Path_10;
    ENDPROC 
ENDMODULE