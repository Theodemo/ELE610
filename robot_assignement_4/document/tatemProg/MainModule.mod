MODULE MainModule
    ! made by KS November 2023
    ! (based on how RWS and JAMR adapted template program from ABB spring 2023)
    ! 
    ! main module for simulation using TATEM tool and a test board with pegs attached
    
    ! position of tool point is relative to tool0, translated so the Tool Center Point (TCP) is
    ! between the two fingers at level of the gap for the front LED, it is rotated -60 degrees around x-axis to make z-axis
    ! point 'forward' from the tool, the 180 degrees around the z-axis so y-axis points into the widest finger, 
    ! and x-axis points to the 'right'.
    ! PERS tooldata TatemTool1:=[TRUE,[[0,-48.3,153.5],[0,0,-0.5,0.866025404]],[0.3,[0,0,1],[1,0,0,0],0,0,0]];
    PERS tooldata TatemTool1:=[TRUE,[[0,-48.3,153.5],[0,0,-0.5,0.866025404]],[0.3,[0,0,1],[1,0,0,0],0,0,0]];
    
    ! the center of the table (not used), relative to robot coordinate system (not world)
    TASK PERS wobjdata wobjTableR:=[FALSE,TRUE,"",[[150,500,8],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    
    ! the work object used with test board on table                 x      y      z
    TASK PERS wobjdata wobjTestBoardOnTable := [FALSE,TRUE,"",[[0,544,145],[0.965928085,0.258810616,0,0]],[[0,0,0],[1,0,0,0]]];
    ! the one used with test board on conveyer belt         x      y      z
    TASK PERS wobjdata wobjTestBoardOnBelt  := [FALSE,TRUE,"",[[599.763,-318.75,282.622],[0.265084,0.0713605,-0.252646,-0.927797]],[[0,0,0],[1,0,0,0]]];
    ! the work object to use or used last time
    TASK PERS wobjdata wobjTestBoard :=        [FALSE,TRUE,"",[[0,544,145],[0.965928,0.258811,0,0]],[[0,0,0],[1,0,0,0]]];
    
    ! speeddata that are fixed
    CONST speeddata vVeryFast  := [5000,500,5000,1000];
    CONST speeddata vFast      := [1000,500,5000,1000];
    CONST speeddata vSlow      := [ 200,500,5000,1000];
    CONST speeddata vVerySlow  := [ 100,500,5000,1000];
    
    VAR NUM tA         := 0.1;          ! The time it takes to activate the tool
    VAR NUM tAdelay    := 0.06;         ! The amount of time before entering the point that the DO signal will be turned on (should be less than tA)
    VAR NUM tAdiff     := 0.04;         ! Amount of time the robot will stand still in its position before executing the spotwelding (MUST be tA-tA_Delay)
    ! note that tO is a reserved word, i.e. TO as used in FOR-loops, and gives error when used otherwise    
    ! RAPID identifieres (names) are case-insensitive, see Rapid Overview (on Help) Basic RAPID programming - Program structure - Basic elements 
    VAR NUM tOp        := 0.3;          ! The execution time of the task
    VAR NUM tOpdelay   := 0.1;          ! Extra time to make sure the task is finished before retracting the tool
    VAR NUM tR         := 0.1;          ! The time it takes to retract the tool
    VAR NUM tRdelay    := 0.05;         ! Extra time to make sure that the tool has been retracted before exiting the point
    VAR num tWait      := 0.59;         ! tWait, == (tAdiff + tO + tOpdelay + tR + tRdelay)

    CONST robtarget AboveTestBoard:= [[90,90,100],[0,1,0,0],[1,0,-1,1],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    ! pegs at the 4 corners of the test board
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
    VAR bool useFlexPendant := TRUE;
    VAR bool useBoardOnTable := TRUE;

    PROC main()         
        ! MoveAbsJ jCalibPos0,v1000,z10,tool0;   
        
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
                reg1 := 5;  ! Quit if no FlexPendant is used
            ENDIF
        ENDWHILE
         
        MoveAbsJ jCalibPos0,v1000,z10,tool0;     
    ENDPROC
    
    PROC testPeg00()   
        VAR num pegNum;
        VAR num dx;
        VAR num dy;
        VAR num rotation;
        VAR num numTime := 0;
        VAR bool isValid;
        
        WHILE TRUE DO
        ! Ask for peg number
        TPReadNum pegNum, "Enter peg number (1-16) or invalid to quit:";
        
        ! Convert peg number to (dx, dy)
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

        ! Ask for rotation
        TPReadNum rotation, "Enter rotation (-180 to 180, steps of 45):";
        
        IF (rotation MOD 45 <> 0) OR (rotation < -180) OR (rotation > 180) THEN
            TPWrite "Invalid rotation! Try again.";
            isValid := FALSE;
        ENDIF

        ! Check reachability
        IF isValid THEN
            isValid := isReachable(dx, dy, rotation);
            IF NOT isValid THEN
                TPWrite "Target point is not reachable! Choose another.";
            ENDIF
        ENDIF

        ! Execute peg test if valid
        IF isValid THEN
            !TPWrite "Testing peg at (" \Num:=dx, ", " \Num:=dy, "), Rotation: " \Num:=rotation;
            
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
    
        ! Check if dx, dy are within reachable limits
        reachable := (dx >= X_MIN) AND (dx <= X_MAX) AND 
                     (dy >= Y_MIN) AND (dy <= Y_MAX);
    
        ! Check if rotation is valid
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
        ! arguments here should be given relative to work object
        ! but RelTool adjust position reltive to tool coordinate system 
        ! Below sign of dx is kept, sign of dy (and dz) and rotation around z-axis are reversed,
        ! this will, for the cases here, make arguments dx, dy, and rotz as if they were 
        ! related to the work object. 
        ! 
        VAR num t1 := 0.025;   ! at peg wait t1 and the activate tool
        VAR num t2 := 0.450;   ! then wait t2, staying calm on peg 
        VAR num t3 := 0.125;   ! deactivate tool, and wait t3 until moving from peg
        !
        IF doSlow THEN
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast, z5,   TatemTool1\WObj:=wobjTestBoard;
            MoveL RelTool(Peg00, dx, -dy,   0, \Rz:= -rotz), vSlow, fine, TatemTool1\WObj:=wobjTestBoard;
            WaitTime t1;
            SetDO AirValve, 1;  ! activate tool
            WaitTime t2;
            SetDO AirValve, 0;  ! deactivate tool
            WaitTime t3;
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vSlow, z5,  TatemTool1\WObj:=wobjTestBoard;
        ELSE
            ! here try to do a faster 'weld simulation', using TriggL
            ! Moving to above wanted position (dx, dy) from Peg00 and tool rotated rotz degrees clockwise
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast,         z10, TatemTool1\WObj:=wobjTestBoard;
            ! the signal is turned on tAdelay second before (=above) the target point 
            TriggL RelTool(Peg00, dx, -dy,  0, \Rz:= -rotz),  vSlow, PGunOn, fine, TatemTool1\WObj:=wobjTestBoard; 
            WaitTime tWait;   ! should be the minimum time to wait
            ! move up again
            MoveL RelTool(Peg00, dx, -dy, -50, \Rz:= -rotz), vFast,         z10, TatemTool1\WObj:=wobjTestBoard;
        ENDIF
    ENDPROC
    
    ! The last two functions for using trigger to activate and and interrupt to deactivate tool
    PROC initTatemTool()   
        ! just return IF doSlow
        IF NOT doSlow THEN
            ! initialize the TATEM tool, for using trigger and interrupt
            ! Connect the triggdata variable PGunOn to the DO signal AirValve
            ! and set the startup time of the tool as tA_dalay seconds before reaching the point
            ! the last argument, 1, is the value to assign to the DO signal when triggered.
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
            SetDO \SDelay:=tA+tOp+tOpdelay, AirValve, 0; ! Triggering DO off
            IWatch igun_on;
        ENDTEST
    ENDTRAP
    
ENDMODULE