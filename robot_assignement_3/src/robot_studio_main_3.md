```rapid
MODULE MODULE1

    TASK PERS wobjdata wobjTableN:=[FALSE,TRUE,"",[[150,-500,8],[0.707106781,0,0,-0.707106781]],[[0,0,0],[1,0,0,0]]];
    
    CONST robtarget target_K0:=[[0,0,0],[0,1,0,0],[-1,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST speeddata vSlow := v100;
    CONST speeddata vFast := v1000;
    CONST num puckHeight := 30;
    CONST num safeHeight := 240;
    CONST num nPos := 7;
    VAR num choice;
    VAR num fromPos;
    VAR num toPos;
    VAR num lastPosNo := 0;
    VAR num nOnPos {nPos} := [5, 0, 0, 0, 0, 0, 0];
    
    VAR robtarget targets{nPos} :=[
        [[0,-200,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[200,-200,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[0,0,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[200,0,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[-200,200,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[0,200,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
        [[200,200,0],[0,1,0,0] ,[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]
        ];
    VAR num currentPos := 1;
    PERS tooldata tGripper:=[TRUE,[[0,0,114.25],[0,0,0,1]],[1,[-0.095984607,0.082520613,38.69176324],[1,0,0,0],0,0,0]];
    
	PROC main()
        TPReadFK reg1, "Choose what to do:", "Move puck ", "Move stack ", "Flip stack", "Collect pucks to position 1", "To implement";
        
        TEST reg1
        CASE 1 :
            TPReadNum reg2, "From which position?";
            TPReadNum reg3, "To which position";
            TPReadNum reg4, "How many pucks to move?";
            FOR i FROM 1 TO reg4 DO
                IF reg2 <= 7 AND reg3 <= 7 THEN
                    
                    movePuck reg2,reg3;
                ELSE
                    TPWrite "Invalid position! choose again:";
                    EXIT;
                ENDIF
            ENDFOR
    
        CASE 2 :
            TPReadNum reg2, "From which position?";
            TPReadNum reg3, "To which position";
            moveStack reg2,reg3;
    
        CASE 3:
            TPReadNum reg2, "From which position?";
            flipStack reg2;
           
        CASE 4:
            collectPuck;
           
        CASE 5:
            
        ENDTEST
    ENDPROC    
       
    PROC getPuck(robtarget pos)
        MoveJ Offs(pos, 40, 0, 200),v500,z50,tGripper\WObj:=wobjTableN;
        MoveJ Offs(pos, 40, 0, 50),v200,z10,tGripper\WObj:=wobjTableN;
	    MoveL Offs(pos, 40, 0, 10),v50,fine,tGripper\WObj:=wobjTableN;   
        MoveL Offs(pos, 0, 0, 10),v10,fine,tGripper\WObj:=wobjTableN;
        closeGripper(TRUE);        
	    MoveL Offs(pos, 0, 0, 50),v50,z10,tGripper\WObj:=wobjTableN;
        MoveJ Offs(pos, 0, 0, 200),v200,z50,tGripper\WObj:=wobjTableN;
    ENDPROC

    PROC putPuck(robtarget pos)
        MoveJ Offs(pos, 0, 0, 200),v500,z50,tGripper\WObj:=wobjTableN;
        MoveJ Offs(pos, 0, 0, 50),v200,z10,tGripper\WObj:=wobjTableN;
	    MoveL Offs(pos, 0, 0, 10),v50,fine,tGripper\WObj:=wobjTableN;
        closeGripper(FALSE);        
	    MoveL Offs(pos, 0, 0, 50),v50,z10,tGripper\WObj:=wobjTableN;
        MoveJ Offs(pos, 0, 0, 200),v200,z50,tGripper\WObj:=wobjTableN;
    ENDPROC
    

PROC flipStack (num fromPosNo)
        VAR num i;
        VAR num tempPos1; 
        VAR num tempPos2;
        FOR i FROM 1 TO 7 DO
            IF nOnPos{i}=0 AND nOnPos{i+1}=0 THEN
                tempPos1 := nOnPos{i};      
                tempPos2 := nOnPos{i+1};    
                EXIT;                   
            ENDIF
        ENDFOR
        
        moveStack fromPosNo, tempPos1;
        moveStack tempPos1, tempPos2;
        moveStack tempPos2, fromPosNo;
        
ENDPROC


PROC displayPuckCount()
        TPWrite "Number of pucks in each position:";
        
        TPWrite "Pos 1: ", \Num:=nOnPos{1};
        TPWrite "Pos 2: ", \Num:=nOnPos{2};
        TPWrite "Pos 3: ", \Num:=nOnPos{3};
        TPWrite "Pos 4: ", \Num:=nOnPos{4};
        TPWrite "Pos 5: ", \Num:=nOnPos{5};
        TPWrite "Pos 6: ", \Num:=nOnPos{6};
        TPWrite "Pos 7: ", \Num:=nOnPos{7};
ENDPROC
    
PROC collectPuck()
        WHILE nOnPos<>[5,0,0,0,0,0,0] DO
            IF nOnPos{2}>0 THEN
                movePuck 2,1;
            ENDIF
            
            IF nOnPos{3}>0 THEN
                movePuck 3,1;
            ENDIF
            
            IF nOnPos{4}>0 THEN
                movePuck 4,1;
            ENDIF
            
            IF nOnPos{5}>0 THEN
                movePuck 5,1;
            ENDIF
            IF nOnPos{6}>0 THEN
                movePuck 6,1;
            ENDIF
            IF nOnPos{7}>0 THEN
                movePuck 7,1;
            ENDIF   
        ENDWHILE
ENDPROC
    
     
PROC movePuck(num fromPos, num toPos)
         VAR robtarget fromTarget;
         VAR robtarget toTarget;
         VAR num i;
         fromTarget := targets{fromPos};
         toTarget := targets{toPos};
         
             nOnPos{fromPos} := nOnPos{fromPos} - 1;
             MoveJ Offs(fromTarget, 0, 0, safeHeight), vFast, z10, tGripper\WObj := wobjTableN;
             getPuck(Offs(fromTarget, 0, 0, puckHeight * (nOnPos{fromPos})));
             MoveJ Offs(toTarget, 0, 0, safeHeight), vFast, z10, tGripper\WObj := wobjTableN;
             putPuck(Offs(toTarget, 0, 0, puckHeight * nOnPos{toPos}));          
             ! Update puck counts at each position
             nOnPos{toPos} := nOnPos{toPos} + 1;
     
             MoveL Offs(target_K0, 0, 0, 200),v500,z10,tGripper\WObj:=wobjTableN;
               
ENDPROC    

PROC moveStack(num fromPos, num toPos)
    VAR num puckLevel;
    VAR robtarget fromTarget;
    VAR robtarget toTarget;
        
    fromTarget := targets{fromPos};
    toTarget := targets{toPos};
    FOR puckLevel FROM 1 TO nOnPos{fromPos} DO
        nOnPos{fromPos} := nOnPos{fromPos} - 1;
        MoveJ Offs(fromTarget, 0, 0, safeHeight), vFast, z10, tGripper\WObj := wobjTableN;
        getPuck(Offs(fromTarget, 0, 0, puckHeight * (nOnPos{fromPos})));
        MoveJ Offs(toTarget, 0, 0, safeHeight), vFast, z10, tGripper\WObj := wobjTableN;
        putPuck(Offs(toTarget, 0, 0, puckHeight * nOnPos{toPos}));           
        nOnPos{toPos} := nOnPos{toPos} + 1;
    ENDFOR
ENDPROC

ENDMODULE
```