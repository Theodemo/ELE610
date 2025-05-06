MODULE MODULE1
	! Communication variables
	VAR num WPW              := 0;   !What Python Wants
	VAR num WRD              := 0;   ! What RAPID Does
    VAR num height           := 250;   ! Height specified by Python
    VAR num puckHeight := 30;
    VAR robtarget puckPos; 
    VAR robtarget fromPnt    := target_K0;
    VAR robtarget toPnt      := target_K4;
       
    ! Variables for Task04
    VAR num nPuck;
    CONST num arraysize := 5;
    VAR robtarget pucksPos{arraysize};
    
    VAR robtarget Task04_0 := [[0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    VAR robtarget Task04_1 := [[0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    VAR robtarget Task04_2 := [[0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    VAR robtarget Task04_3 := [[0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    VAR robtarget Task04_4 := [[0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
       
	TASK PERS wobjdata wobjTableN:=[FALSE,TRUE,"",[[150,-500,8],[0.707106781,0,0,-0.707106781]],[[0,0,0],[1,0,0,0]]];       
	VAR speeddata robotSpeed := v400;

	! Target points 
	CONST robtarget target_K0 := [[0,0,0],[0,1,0,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
	CONST robtarget target_K1 := [[0, -100, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
	CONST robtarget target_K2 := [[100, -100, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K3 := [[-100, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K4 := [[100, 100, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K5 := [[200, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K6 := [[200, 200, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K7 := [[-100, -100, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    CONST robtarget target_K8 := [[-100, 100, 0], [0, 1, 0, 0], [0, 0, 0, 0], [9E9, 9E9, 9E9, 9E9, 9E9, 9E9]];
    
    CONST robtarget targets{8} := [target_K1, target_K2, target_K3, target_K4, target_K5, target_K6, target_K7, target_K8]; 

    PERS tooldata tGripper:=[TRUE,[[0,0,114.25],[0,0,0,1]],[1,[-0.095984607,0.082520613,38.69176324],[1,0,0,0],0,0,0]];
    
	!------------------------------
    ! Main program
    PROC main()
        CloseGripper(FALSE);
        !helpPuck; ! just to place pucks in nine different position to compute T
        displayPuckCount;
        MainLoop;
        collectPuck;
    ENDPROC

	!------------------------------
	! MainLoop - listen to Python
	PROC MainLoop()
                
		TPWrite "MainLoop starting";
        
		WHILE TRUE DO
            MoveL Offs(target_K0, 0, 0, 500),v500,z10,tGripper\WObj:=wobjTableN;
			WRD := 0;
			IF WPW = 0 THEN
				TPWrite "Waiting for WPW from Python.";
			ENDIF

			WaitUntil WPW <> 0;
			TPWrite "Python ask fot task WPW = "\Num:=WPW;

			WRD := WPW;
			WPW := 0;

			TEST WRD
				CASE -1:
					RETURN;
				CASE 0:
					TPWrite "WRD = 0. Do nothing.";
				CASE 1:
					Task01;
				CASE 2:
					Task02;
                CASE 3: 
                    Task03;
                CASE 4:
                    Task04;
                
                    
			ENDTEST
		ENDWHILE
	ENDPROC
    
    !------------------------------
	! Task01 - Move puck from one known position and place it in another.
    !-------------------------------
    
	PROC Task01()
        MoveL Offs(target_K0, 0, 0, 250),v500,z10,tGripper\WObj:=wobjTableN;
        TPWrite "Task01: Starting...";
        MovePuck fromPnt, toPnt;
        
		MoveJ Offs(target_K0,0,0,500), robotSpeed, z10, tGripper\WObj:=wobjTableN;
		WaitTime 0.1;
        
	ENDPROC
    
    !-------------------------------
    ! Task02 - Move to a given position at a given height
    !-------------------------------
    PROC Task02()
        TPWrite"Task02: Starting...";
        puckPos := fromPnt;
        MoveJ Offs(puckPos,0,0,height), robotSpeed,z10, tGripper\WObj:=wobjTableN;
    ENDPROC
    
    !-------------------------------
    ! Task03 - Move a puck from a unknown position to a reference position like target_K0
    !-------------------------------
    PROC Task03()
        VAR robtarget puckPos;
        puckPos := fromPnt;
        TPWrite"Task03: Starting...";
        
        MovePuck puckPos, target_K0;         
    ENDPROC
    
    !-------------------------------
    ! Task04 - Collect pucks from unknown positions to a reference position
    !-------------------------------
    PROC Task04()
        VAR num puckHeight := 50;
        
        TPWrite "Task04: Starting...";
        TPWrite "Task04: Number of pucks to stack:"\Num:=nPuck;
        
        pucksPos := [Task04_0, Task04_1, Task04_2, Task04_3, Task04_4];
        
        ! Loop tostack pucks
        FOR i FROM 1 TO nPuck DO
            MovePuck pucksPos{i}, Offs(target_K0, 0, 0, (i-1) * puckHeight);
            !MoveJ Offs(pucksPos{i}, 0, 0, 100), robotSpeed, z10, tGripper\WObj:=wobjTableN;
            WaitTime 0.1;
        ENDFOR
        
        TPWrite "Task04: Completed, all pucks stacked.";
    ENDPROC
    
	!------------------------------
	! MovePuck  to robtargets
    PROC MovePuck(robtarget fromPos, robtarget toPos)
        
        VAR robtarget gripPnt;
        VAR robtarget placePnt;
        VAR num sideOffset := -30; ! Offset distance to approach from the side
        VAR num puck        := 0;
        

        ! Move above the puck
        MoveJ Offs(fromPos, 0, 0, 100), robotSpeed, z10, tGripper\WObj:=wobjTableN;

        ! Approach from the side
        MoveL Offs(fromPos, sideOffset, 0, 10), robotSpeed, fine, tGripper\WObj:=wobjTableN;
        MoveL Offs(fromPos, 0, 0, 10), v10, fine, tGripper\WObj:=wobjTableN;

        ! Pick the puck 
        WaitTime 0.5;
        CloseGripper(TRUE);

        ! Pick the puck up 
        MoveL Offs(fromPos, sideOffset, 0, 100), robotSpeed, z10, tGripper\WObj:=wobjTableN;

        ! Move above the target
        MoveJ Offs(toPos, 0, 0, 200), robotSpeed, z10, tGripper\WObj:=wobjTableN;
        MoveL Offs(toPos,0,0,10), robotSpeed, fine, tGripper\WObj:=wobjTableN; ! Edited part

        ! Release the puck
        CloseGripper(FALSE);
        WaitTime 0.5;

        ! Move up 300 mm above table
        MoveL Offs(toPos, 0, 0, 300), robotSpeed, z10, tGripper\WObj:=wobjTableN;

    ENDPROC
    
    PROC helpPuck()

        FOR i FROM 1 TO 8 DO
            puckPos := Offs(target_K0, 0, 0, (8-i) * puckHeight);
            MovePuck puckPos, targets{i};
            !MoveJ Offs(targets{i}, 0, 0, 100), robotSpeed, z10, tGripper\WObj:=wobjTableN;
        ENDFOR
    ENDPROC
    PROC collectPucks()

    ENDPROC
    PROC displayPuckCount()

    ENDPROC
    PROC collectPuck()

    ENDPROC

ENDMODULE