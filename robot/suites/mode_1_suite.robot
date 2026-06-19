*** Settings ***
Metadata    generated_by    bdd-to-robot-pipeline
Metadata    source_feature    bdd/features/mode_1.feature

Library     Collections
Resource    robot/resources/keywords/generated/mode_1_keywords.resource


*** Variables ***
${AURAL_MESSAGE}    ${EMPTY}    # TODO: set value
${HEIGHT}           ${EMPTY}    # TODO: set value
${RATEOFDESCENT}    ${EMPTY}    # TODO: set value


*** Test Cases ***
Mode Arming/Disarming
    [Tags]    mops_268    generated
    Ensure Plane Is Flying
    Verify Mode 1 Is Armed

Must Alert — 1560
    [Tags]    mops_269    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1560
    Set Height Above Terrain    100
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 2200
    [Tags]    mops_269    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2200
    Set Height Above Terrain    630
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 5700
    [Tags]    mops_269    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    5700
    Set Height Above Terrain    2200
    Verify Mode 1 Caution Alert Is Emitted

Must Not Alert When Not Armed
    [Tags]    mops_270    generated
    Disarm Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert When Inhibited
    [Tags]    mops_270    generated
    Inhibit Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert — 964
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    964
    Set Height Above Terrain    10
    Verify No Mode 1 Caution Alert

Must Not Alert — 2300
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1550
    Verify No Mode 1 Caution Alert

Must Not Alert — 4400
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2900
    Verify No Mode 1 Caution Alert

Must Not Alert — 5000
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    5000
    Set Height Above Terrain    3200
    Verify No Mode 1 Caution Alert

Must Not Alert — 8000
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    4600
    Verify No Mode 1 Caution Alert

Must Not Alert — 12000
    [Tags]    mops_270    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    6467
    Verify No Mode 1 Caution Alert

Must Alert — 1798
    [Tags]    mops_271    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    1798
    Set Height Above Terrain    150
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 1944
    [Tags]    mops_271    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    1944
    Set Height Above Terrain    300
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 3233
    [Tags]    mops_271    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    3233
    Set Height Above Terrain    1078
    Verify Mode 1 Caution Alert Is Emitted

Must Alert — 6225
    [Tags]    mops_271    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    6225
    Set Height Above Terrain    2075
    Verify Mode 1 Caution Alert Is Emitted

Must Not Alert When Not Armed
    [Tags]    mops_272    generated
    Disarm Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert When Inhibited
    [Tags]    mops_272    generated
    Inhibit Mode 1
    Verify No Mode 1 Caution Alert

Must Not Alert — 964
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    964
    Set Height Above Terrain    10
    Verify No Mode 1 Caution Alert

Must Not Alert — 2300
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1550
    Verify No Mode 1 Caution Alert

Must Not Alert — 4400
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2900
    Verify No Mode 1 Caution Alert

Must Not Alert — 5000
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    5000
    Set Height Above Terrain    3200
    Verify No Mode 1 Caution Alert

Must Not Alert — 8000
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    4600
    Verify No Mode 1 Caution Alert

Must Not Alert — 12000
    [Tags]    mops_272    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    6467
    Verify No Mode 1 Caution Alert

Must Alert — 1600
    [Tags]    mops_273    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1600
    Set Height Above Terrain    100
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 1850
    [Tags]    mops_273    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1850
    Set Height Above Terrain    300
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 10100
    [Tags]    mops_273    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    10100
    Set Height Above Terrain    1958
    Verify Mode 1 Warning Alert Is Emitted

Must Not Alert When Not Armed
    [Tags]    mops_274    generated
    Disarm Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert When Inhibited
    [Tags]    mops_274    generated
    Inhibit Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert — 1217
    [Tags]    mops_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    1217
    Set Height Above Terrain    10
    Verify No Mode 1 Warning Alert

Must Not Alert — 2300
    [Tags]    mops_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1300
    Verify No Mode 1 Warning Alert

Must Not Alert — 4400
    [Tags]    mops_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2500
    Verify No Mode 1 Warning Alert

Must Not Alert — 8000
    [Tags]    mops_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    3500
    Verify No Mode 1 Warning Alert

Must Not Alert — 12000
    [Tags]    mops_274    generated
    Ensure Steep Approach Is Not Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    4611
    Verify No Mode 1 Warning Alert

Must Alert — 1908
    [Tags]    mops_275    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    1908
    Set Height Above Terrain    150
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 2050
    [Tags]    mops_275    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    2050
    Set Height Above Terrain    300
    Verify Mode 1 Warning Alert Is Emitted

Must Alert — 10300
    [Tags]    mops_275    generated
    Arm Mode 1
    Ensure Mode 1 Is Not Inhibited
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    10300
    Set Height Above Terrain    1958
    Verify Mode 1 Warning Alert Is Emitted

Must Not Alert When Not Armed
    [Tags]    mops_276    generated
    Disarm Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert When Inhibited
    [Tags]    mops_276    generated
    Inhibit Mode 1
    Verify No Mode 1 Warning Alert

Must Not Alert — 1217
    [Tags]    mops_276    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    1217
    Set Height Above Terrain    10
    Verify No Mode 1 Warning Alert

Must Not Alert — 2300
    [Tags]    mops_276    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    2300
    Set Height Above Terrain    1300
    Verify No Mode 1 Warning Alert

Must Not Alert — 4400
    [Tags]    mops_276    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    4400
    Set Height Above Terrain    2500
    Verify No Mode 1 Warning Alert

Must Not Alert — 8000
    [Tags]    mops_276    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    8000
    Set Height Above Terrain    3500
    Verify No Mode 1 Warning Alert

Must Not Alert — 12000
    [Tags]    mops_276    generated
    Ensure Steep Approach Is Selected
    Set Rate Of Descent    12000
    Set Height Above Terrain    4611
    Verify No Mode 1 Warning Alert

Caution Alert
    [Tags]    mops_277    generated
    Trigger Caution Level Mode 1 Alert
    Verify Aural Message Is Emitted    ${AURAL_MESSAGE}

Warning Alert
    [Tags]    mops_278    generated
    Trigger Warning Level Mode 1 Alert
    Verify Aural Message Is Emitted    ${AURAL_MESSAGE}

Repeating Warning Alert
    [Tags]    mops_279    generated
    Maintain Warning Level Mode 1 Alert Condition
    Confirm Alert Is Not Silenced
    Ensure No Higher Priority Alert
    Verify Aural Message Is Repeated Periodically

Caution
    [Tags]    mops_281    generated
    Activate Mode 1 Caution Alert
    Verify TAWS Yellow Or Amber Indicator

Warning
    [Tags]    mops_282    generated
    Activate Mode 1 Warning Alert
    Verify TAWS Red Indicator
