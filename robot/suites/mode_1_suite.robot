*** Settings ***
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/mode_1.feature

Library     BuiltIn
Resource    robot/resources/keywords/generated/mode_1_keywords.resource


*** Variables ***


*** Test Cases ***
Mode Arming Disarming
    [Tags]    MOPS_268    generated
    Check Mode 1 Is Armed
    Verify Mode 1 Is Armed

Must Alert — 1560
    [Tags]    MOPS_269    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1560
    Set Height Above Terrain    100
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 2200
    [Tags]    MOPS_269    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2200
    Set Height Above Terrain    630
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 5700
    [Tags]    MOPS_269    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    5700
    Set Height Above Terrain    2200
    Verify Mode 1 Caution Alert Is Emitted

Must Not Alert When Not Armed — Mops_270
    [Tags]    MOPS_270    generated
    Set Mode 1 Not Armed
    Verify No Mode 1 Caution Alert

Must Not Alert When Inhibited — Mops_270
    [Tags]    MOPS_270    generated
    Inhibit Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert — 964
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    964
    Set Height Above Terrain    10
    Verify No Mode 1 Caution Alert

Must Not Alert — 2300
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1550
    Verify No Mode 1 Caution Alert

Must Not Alert — 4400
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2900
    Verify No Mode 1 Caution Alert

Must Not Alert — 5000
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    5000
    Set Height Above Terrain    3200
    Verify No Mode 1 Caution Alert

Must Not Alert — 8000
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    4600
    Verify No Mode 1 Caution Alert

Must Not Alert — 12000
    [Tags]    MOPS_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    6467
    Verify No Mode 1 Caution Alert

Must Alert — 1798
    [Tags]    MOPS_271    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    1798
    Set Height Above Terrain    150
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 1944
    [Tags]    MOPS_271    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    1944
    Set Height Above Terrain    300
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 3233
    [Tags]    MOPS_271    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    3233
    Set Height Above Terrain    1078
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 6225
    [Tags]    MOPS_271    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    6225
    Set Height Above Terrain    2075
    Verify Mode 1 Caution Alert Is Emitted

Must Not Alert When Not Armed — Mops_272
    [Tags]    MOPS_272    generated
    Set Mode 1 Not Armed
    Verify No Mode 1 Caution Alert

Must Not Alert When Inhibited — Mops_272
    [Tags]    MOPS_272    generated
    Inhibit Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert — 964
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    964
    Set Height Above Terrain    10
    Verify No Mode 1 Caution Alert

Must Not Alert — 2300
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    2300
    Set Height Above Terrain    1550
    Verify No Mode 1 Caution Alert

Must Not Alert — 4400
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    4400
    Set Height Above Terrain    2900
    Verify No Mode 1 Caution Alert

Must Not Alert — 5000
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    5000
    Set Height Above Terrain    3200
    Verify No Mode 1 Caution Alert

Must Not Alert — 8000
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    8000
    Set Height Above Terrain    4600
    Verify No Mode 1 Caution Alert

Must Not Alert — 12000
    [Tags]    MOPS_272    generated
    Select Steep Approach
    Set Rate Of Descent    12000
    Set Height Above Terrain    6467
    Verify No Mode 1 Caution Alert

Must Alert — 1600
    [Tags]    MOPS_273    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1600
    Set Height Above Terrain    100
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 1850
    [Tags]    MOPS_273    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1850
    Set Height Above Terrain    300
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 10100
    [Tags]    MOPS_273    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    10100
    Set Height Above Terrain    1958
    Verify Mode 1 Warning Alert Is Emitted

Must Not Alert When Not Armed — Mops_274
    [Tags]    MOPS_274    generated
    Set Mode 1 Not Armed
    Verify No Mode 1 Warning Alert

Must Not Alert When Inhibited — Mops_274
    [Tags]    MOPS_274    generated
    Inhibit Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert — 1217
    [Tags]    MOPS_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1217
    Set Height Above Terrain    10
    Verify No Mode 1 Warning Alert

Must Not Alert — 2300
    [Tags]    MOPS_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1300
    Verify No Mode 1 Warning Alert

Must Not Alert — 4400
    [Tags]    MOPS_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2500
    Verify No Mode 1 Warning Alert

Must Not Alert — 8000
    [Tags]    MOPS_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    3500
    Verify No Mode 1 Warning Alert

Must Not Alert — 12000
    [Tags]    MOPS_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    4611
    Verify No Mode 1 Warning Alert

Must Alert — 1908
    [Tags]    MOPS_275    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    1908
    Set Height Above Terrain    150
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 2050
    [Tags]    MOPS_275    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    2050
    Set Height Above Terrain    300
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 10300
    [Tags]    MOPS_275    generated
    Set Mode 1 Armed
    Ensure Mode 1 Is Not Inhibited
    Select Steep Approach
    Set Rate Of Descent    10300
    Set Height Above Terrain    1958
    Verify Mode 1 Warning Alert Is Emitted

Must Not Alert When Not Armed — Mops_276
    [Tags]    MOPS_276    generated
    Set Mode 1 Not Armed
    Verify No Mode 1 Warning Alert

Must Not Alert When Inhibited — Mops_276
    [Tags]    MOPS_276    generated
    Inhibit Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert — 1217
    [Tags]    MOPS_276    generated
    Select Steep Approach
    Set Rate Of Descent    1217
    Set Height Above Terrain    10
    Verify No Mode 1 Warning Alert

Must Not Alert — 2300
    [Tags]    MOPS_276    generated
    Select Steep Approach
    Set Rate Of Descent    2300
    Set Height Above Terrain    1300
    Verify No Mode 1 Warning Alert

Must Not Alert — 4400
    [Tags]    MOPS_276    generated
    Select Steep Approach
    Set Rate Of Descent    4400
    Set Height Above Terrain    2500
    Verify No Mode 1 Warning Alert

Must Not Alert — 8000
    [Tags]    MOPS_276    generated
    Select Steep Approach
    Set Rate Of Descent    8000
    Set Height Above Terrain    3500
    Verify No Mode 1 Warning Alert

Must Not Alert — 12000
    [Tags]    MOPS_276    generated
    Select Steep Approach
    Set Rate Of Descent    12000
    Set Height Above Terrain    4611
    Verify No Mode 1 Warning Alert

Caution Alert
    [Tags]    MOPS_277    generated
    Trigger Mode 1 Caution Alert
    Verify Aural Message Is Emitted    Sink Rate

Warning Alert
    [Tags]    MOPS_278    generated
    Trigger Mode 1 Warning Alert
    Verify Aural Message Is Emitted    Pull Up

Repeating Warning Alert
    [Tags]    MOPS_279    generated
    Ensure Warning Alert Condition Persists
    Ensure Alert Is Not Silenced
    Ensure No Higher Priority Alert
    Verify Aural Message Is Repeated Periodically

Caution
    [Tags]    MOPS_281    generated
    Trigger Mode 1 Caution Alert
    Verify TAWS Visual Alert Is Yellow Or Amber

Warning
    [Tags]    MOPS_282    generated
    Trigger Mode 1 Warning Alert
    Verify TAWS Visual Alert Is Red
