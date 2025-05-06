```rapid
MODULE Module1
    CONST robtarget Target_10:=[[425,25,308],[0,-0.707106781,0.707106781,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_20:=[[425,325,308],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_30:=[[25,325,308],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_40:=[[25,25,308],[0,-0.707106781,0.707106781,0],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    PERS tooldata UISpenholder:=[TRUE,[[0,0,110],[1,0,0,0]],[1,[0,0,1],[1,0,0,0],0,0,0]];
    TASK PERS wobjdata wobjTable:=[FALSE,TRUE,"",[[300,-175,1],[1,0,0,0]],[[0,0,0],[1,0,0,0]]];
    CONST robtarget Target_50:=[[125,50,323],[0,-0.707106781,0.707106781,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_60:=[[325,50,323],[0,-0.707106781,0.707106781,0],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_70:=[[325,300,323],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_80:=[[125,300,323],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_90:=[[150,75,349],[0,-0.707106781,0.707106781,0],[0,0,0,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_100:=[[300,75,349],[0,-0.707106781,0.707106781,0],[-1,0,-2,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_110:=[[300,275,349],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];
    CONST robtarget Target_120:=[[150,275,349],[0,-0.707106781,0.707106781,0],[0,0,-1,0],[9E+09,9E+09,9E+09,9E+09,9E+09,9E+09]];

    PROC main()
        Path_10;
        Path_20;
        Path_30;
        Path_40;
    ENDPROC
    PROC Path_10()
        MoveL Target_10,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_20,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_30,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_40,v1000,z5,UISpenholder\WObj:=wobjTable;
    ENDPROC
    PROC Path_20()
        MoveL Target_50,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_60,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_70,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_80,v1000,z5,UISpenholder\WObj:=wobjTable;
    ENDPROC
    PROC Path_30()
        MoveL Target_90,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_100,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_110,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Target_120,v1000,z5,UISpenholder\WObj:=wobjTable;
    ENDPROC
    PROC Path_40()
        MoveL Target_90,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Offs(Target_90, 0, 0, -12), v1000, z5, UISpenholder\WObj:=wobjTable;
        MoveL Target_100,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Offs(Target_100, 0, 0, -12), v1000, z5, UISpenholder\WObj:=wobjTable;
        MoveL Target_110,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Offs(Target_110, 0, 0, -12), v1000, z5, UISpenholder\WObj:=wobjTable;
        MoveL Target_120,v1000,z5,UISpenholder\WObj:=wobjTable;
        MoveL Offs(Target_120, 0, 0, -12), v1000, z5, UISpenholder\WObj:=wobjTable;

    ENDPROC
ENDMODULE
```