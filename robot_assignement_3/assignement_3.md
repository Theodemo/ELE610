# Faculty of Science and Technology

## ELE610 Applied Robot Technology, V-2025

### ABB Robot Assignment 3

**Instructor:** Karl Skretting, Department of Electrical Engineering and Computer Science (IDE), University of Stavanger (UiS)  
**Location:** Stavanger, January 13, 2025  

---

## Assignment Overview
In this assignment, you will develop a simple program for the ABB IRB 140 robot, named **Norbert**, to pick and place pucks on a desk. You are expected to use the **RAPID documentation** extensively and regularly save your work, including RAPID code and module files.

### Submission and Approval
- Demonstrate the robot program to the teacher.
- Submit a report including the RAPID code on **Canvas** (as a `.txt` file, not a `.mod` file).
- Optionally, include comments or questions in a **PDF file**.
- Ensure RAPID code is clearly marked (e.g., using **Courier font**).

---

## 3 Pick and Place Program for Norbert

### 3.1 Open Pack-and-Go File
Download and open the **Pack and Go** file `UiS_E458_nov18.rspag`. Follow the instructions from **RS2, section 2.1**.

### 3.2 Clean Up
- Retain **Norbert, the table, the puck, and the gripper**.
- Delete unnecessary components and verify that simulation works.
- If puck release issues arise, check the **RobotWare version** (version 6.13 should work).
- If issues persist, replace faulty pucks with working copies and modify colors.
- Run a simulation to ensure the pick-and-place mechanism is functional.

### 3.3 Add More Positions
- Analyze the station and **RAPID code**.
- Define at least **7 target positions** in an array.
- Remove unused targets (K1, K2) from both the **code** and **station**.
- Synchronize the changes and modify the `movePuck` function.

#### Example Position Array
```rapid
VAR robtarget targets {7} := [
  [[0,-200,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[200,-200,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[0,0,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[200,0,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[-200,200,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[0,200,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]],
  [[200,200,0],[0,1,0,0],[0,0,0,0],[9E9,9E9,9E9,9E9,9E9,9E9]]
];
VAR num currentPos := 1;
```

### 3.4 More Pucks
- Create **5 new pucks** (`Solid -> Cylinder` in **Modeling** tab).
- Modify the program to move **5 pucks from `targets[1]` to `targets[4]` and back**.
- **Synchronize and test the simulation.**

### 3.5 Move One Puck
Implement the function:
```rapid
PROC movePuck(num fromPosNo, num toPosNo)
```
#### Considerations:
- Ensure **smooth and efficient movement**.
- Use **fast movement**, except for precise puck placement.
- Update **nOnPos** and **lastPosNo**.
- Lift gripper **2x puck height** after placement.
- Avoid collisions by **moving sideways before gripping**.

### 3.6 Move a Stack
Create a function to move an entire stack:
```rapid
PROC moveStack(num fromPosNo, num toPosNo)
```
- Use `movePuck(..)` for each puck in `fromPosNo`.
- Implement `moveStackTwice(..)` for extra flexibility.

### 3.7 Flip a Stack
Implement:
```rapid
PROC flipStack(num fromPosNo)
```
- Reverse puck order efficiently.
- Use `movePuck(..)` to redistribute and recollect the stack.

### 3.8 Interface on FlexPendant
#### Requirements:
- Display current state using `TPWrite`:
  ```rapid
  TPWrite("Number of pucks in pos. 1-7: 5,0,0,0,0,0,0");
  ```
- Menu options:
  - Move a puck.
  - Move a stack.
  - Flip a stack.
  - Collect all pucks to stack 1.
  - Quit.
- Use `TPReadFK`, `TPReadNum`, and `TPWrite`.

### 3.9 Move Pucks Using Norbert
- **Load the final program** onto Norbert (`152.94.160.198`).
- Adjust **I/O signals** for real vs. simulated gripper (`AirValve1` and `AirValve2`).
- Store the final program (`RSprog39`, `mainModule39.mod`).
- Demonstrate **puck movement via FlexPendant instructions**.
- Submit a **brief report with RAPID code** on **Canvas**.

---

## Final Notes
- Save and back up your work.
- Test thoroughly in **simulation** before moving to the **real robot**.
- Ask questions if any issues arise.

---

End of Assignment.