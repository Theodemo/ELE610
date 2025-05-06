# Main Robot Assignment 4

```rapid

MODULE MainModule

    PERS tooldata TatemTool1:=[TRUE,[[0,-48.3,153.5],[0,0,-0.5,0.866025404]],[0.3,[0,0,1],[1,0,0,0],0,0,0]];
    
    TASK PERS wobjdata wobjTableR:=[FALSE,TRUE,"",[[150,500,8],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    TASK PERS wobjdata wobjTestBoardOnTable := [FALSE,TRUE,"",[[0,544,146],[0.965928085,0.258810616,0,0]],[[0,0,0],[1,0,0,0]]];
    TASK PERS wobjdata wobjTestBoardOnBelt  := [FALSE,TRUE,"",[[599.763,-318.75,282.622],[0.265084,0.0713605,-0.252646,-0.927797]],[[0,0,0],[1,0,0,0]]];
    TASK PERS wobjdata wobjTestBoard :=        [FALSE,TRUE,"",[[599.763,-318.75,282.622],[0.265084,0.0713605,-0.252646,-0.927797]],[[0,0,0],[1,0,0,0]]];
    
    CONST speeddata vVeryFast  := [5000,500,5000,1000];
    CONST speeddata vFast      := [1000,500,5000,1000];
    CONST speeddata vSlow      := [ 200,500,5000,1000];
    CONST speeddata vVerySlow  := [ 100,500,5000,1000];
    
    VAR NUM tA         := 0.1;          
    VAR NUM tAdelay    := 0.06;         
    VAR NUM tAdiff     := 0.04;        
    VAR NUM tOp        := 0.3;       
    VAR NUM tOpdelay   := 0.1;       
    VAR NUM tR         := 0.1;       
    VAR NUM tRdelay    := 0.05;        
    VAR num tWait      := 0.59;

    CONST robtarget AboveTestBoard:= [[90,90,100],[0,1,0,0],[1,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Peg00:=[[0,0,0],[0,1,0,0],[1,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Peg03:=[[0,180,0],[0,1,0,0],[1,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Peg30:=[[180,0,0],[0,1,0,0],[0,-1,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Peg33:=[[180,180,0],[0,1,0,0],[0,-1,0,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    VAR intnum igun_on;   
    VAR triggdata PGunOn;
    CONST jointtarget jCalibPosL:=[[60,30,0,0,-10,90],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST jointtarget jCalibPos0:=[[0,0,0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST jointtarget jCalibPosR:=[[-15,15,0,0,-10,90],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    VAR jointtarget jCalibPos;
    
    VAR bool doSlow := TRUE;
    VAR bool useFlexPendant := FALSE;
    VAR bool useBoardOnTable := TRUE;

    PROC main()
        
        IF useBoardOnTable THEN 
            wobjTestBoard := wobjTestBoardOnTable;
            jCalibPos := jCalibPosL;

        ELSE
            wobjTestBoard := wobjTestBoardOnBelt;
            jCalibPos := jCalibPosR;
        ENDIF
        
        IF useFlexPendant THEN 
            TPErase;
            reg1 := 0;
        ELSE
            reg1 := 2;
        ENDIF
        
        WHILE reg1 < 5 DO 
            TEST reg1
            CASE 1:
                testPeg00;
            CASE 2:
                test4corners;
            CASE 3:
                test7pegs;
            DEFAULT:
                WaitTime 0.1;
            ENDTEST
            IF useFlexPendant THEN 
                TPReadFK reg1, "Select task", "testPeg00", "test4corners", "test7pegs", "unused", "Quit";
            ELSE
                reg1 := 5;
            ENDIF
        ENDWHILE
    ENDPROC
    
    PROC testPeg00()   
        VAR num pegNum;
        VAR num dx;
        VAR num dy;
        VAR num rotation;
        VAR num numTime := 0;
        VAR bool isValid;
        
        WHILE TRUE DO
        TPReadNum pegNum, "Enter peg number (1-16) or invalid to quit:";
        isValid := TRUE;
        IF pegNum = 1 THEN
            dx := 0;   dy := 0;
        ELSEIF pegNum = 2 THEN
            dx := 0;   dy := 60;
        ELSEIF pegNum = 3 THEN
            dx := 0;   dy := 120;
        ELSEIF pegNum = 4 THEN
            dx := 0;   dy := 180;
        ELSEIF pegNum = 5 THEN
            dx := 60;  dy := 0;
        ELSEIF pegNum = 6 THEN
            dx := 60;  dy := 60;
        ELSEIF pegNum = 7 THEN
            dx := 60;  dy := 120;
        ELSEIF pegNum = 8 THEN
            dx := 60;  dy := 180;
        ELSEIF pegNum = 9 THEN
            dx := 120; dy := 0;
        ELSEIF pegNum = 10 THEN
            dx := 120; dy := 60;
        ELSEIF pegNum = 11 THEN
            dx := 120; dy := 120;
        ELSEIF pegNum = 12 THEN
            dx := 120; dy := 180;
        ELSEIF pegNum = 13 THEN
            dx := 180; dy := 0;
        ELSEIF pegNum = 14 THEN
            dx := 180; dy := 60;
        ELSEIF pegNum = 15 THEN
            dx := 180; dy := 120;
        ELSEIF pegNum = 16 THEN
            dx := 180; dy := 180;
        ELSE
            TPWrite "Invalid peg number! Exiting...";
            EXIT;
        ENDIF

        TPReadNum rotation, "Enter rotation (-180 to 180, steps of 45):";
        
        IF (rotation MOD 45 <> 0) OR (rotation < -180) OR (rotation > 180) THEN
            TPWrite "Invalid rotation! Try again.";
            isValid := FALSE;
        ENDIF

        IF isValid THEN
            isValid := isReachable(dx, dy, rotation);
            IF NOT isValid THEN
                TPWrite "Target point is not reachable! Choose another.";
            ENDIF
        ENDIF

        IF isValid THEN          
            MoveAbsJ jCalibPos,vFast,z10,tool0;
            ClkReset clock1;  
            ClkStart clock1;

            initTatemTool;
            doPeg00 dx, dy, rotation;

            MoveAbsJ jCalibPos,vFast,z10,tool0;
            numTime := ClkRead(clock1);
            TPWrite "Time used on testPeg00() [s] = " \Num:=numTime;
        ENDIF
    ENDWHILE
ENDPROC

    FUNC bool isReachable(num dx, num dy, num rotation)
        VAR bool reachable;

        CONST num X_MIN := -200;
        CONST num X_MAX := 200;
        CONST num Y_MIN := -200;
        CONST num Y_MAX := 200;
        CONST num ROT_MIN := -180;
        CONST num ROT_MAX := 180;
    
        reachable := (dx >= X_MIN) AND (dx <= X_MAX) AND 
                     (dy >= Y_MIN) AND (dy <= Y_MAX);
    
        reachable := reachable AND (rotation MOD 45 = 0) AND
                     (rotation >= ROT_MIN) AND (rotation <= ROT_MAX);
                     
        RETURN reachable;
    ENDFUNC

    PROC test4corners()  
        VAR num numTime := 0;
        
        IF useFlexPendant THEN 
            TPWrite "test4corners() started";
        ENDIF
        MoveAbsJ jCalibPos,vFast,z10,tool0;     
        ClkReset clock1;  
        ClkStart clock1;
        
        initTatemTool;
        doPeg00 0, 0, 0;
        doPeg00 180, 0, -90;
        doPeg00 180, 180, 0;
        doPeg00 0, 180, -90;
        
        MoveAbsJ jCalibPos,vFast,z10,tool0;     
        numTime := ClkRead(clock1);
        IF useFlexPendant THEN 
            TPWrite "Time used on test4corners() [s] = " \Num:=numTime;
        ENDIF
    ENDPROC
    
    PROC test7pegs()  
        VAR num numTime := 0;
        
        IF useFlexPendant THEN 
            TPWrite "test7pegs() started";
        ENDIF
        
        MoveAbsJ jCalibPos,vFast,z10,tool0;     
        ClkReset clock1;  
        ClkStart clock1;
        
        initTatemTool;
        doPeg00 0, 180, 90; !1
        doPeg00 0, 0, 0;
        doPeg00 180, 0, 90;
        doPeg00 60, 180, -45;
        doPeg00 60, 60, 45;
        doPeg00 120, 120, 0;
        doPeg00 180, 120, -45;
        
        MoveAbsJ jCalibPos,vFast,z10,tool0;     
        numTime := ClkRead(clock1);
            
        IF useFlexPendant THEN 
            TPWrite "Time used on test7pegs() [s] = " \Num:=numTime;
        ENDIF
    ENDPROC

    PROC doPeg00(num dx, num dy, num rotz)

        VAR num t1 := 0.025;
        VAR num t2 := 0.450;
        VAR num t3 := 0.125;

        IF doSlow THEN
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast, z5,   TatemTool1\WObj:=wobjTestBoard;
            MoveL RelTool(Peg00, dx, -dy,   0, \Rz:= -rotz), vSlow, fine, TatemTool1\WObj:=wobjTestBoard;
            WaitTime t1;
            SetDO AirValve, 1;
            WaitTime t2;
            SetDO AirValve, 0;
            WaitTime t3;
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vSlow, z5,  TatemTool1\WObj:=wobjTestBoard;
        ELSE
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast,         z10, TatemTool1\WObj:=wobjTestBoard;
            TriggL RelTool(Peg00, dx, -dy,  0, \Rz:= -rotz),  vSlow, PGunOn, fine, TatemTool1\WObj:=wobjTestBoard; 
            WaitTime tWait;
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast,         z10, TatemTool1\WObj:=wobjTestBoard;
        ENDIF
    ENDPROC
    
    PROC initTatemTool()   
        IF NOT doSlow THEN
            TriggIO PGunOn, tAdelay\Time \DOp:=AirValve, 1;   
            IDelete igun_on;
            CONNECT igun_on WITH resetSignal;
            ISignalDO AirValve, 1, igun_on;
       ENDIF
    ENDPROC
    
    TRAP resetSignal
        TEST INTNO    
        CASE igun_on:
            ISleep igun_on;
            SetDO \SDelay:=tA+tOp+tOpdelay, AirValve, 0;
            IWatch igun_on;
        ENDTEST
    ENDTRAP
    
ENDMODULE

```
