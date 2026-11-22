// Box.asm for K = 77
// Draws a 32-pixel wide (2 words), 20-row tall black box starting at row 77 (SCREEN + 2464)
// while any key is pressed; clears it when no key is pressed.

(LOOP)
    // Check keyboard state
    @KBD
    D=M
    @SET_WHITE
    D;JEQ           // If KBD == 0, set color = 0 (white)

    @color
    M=-1            // Key pressed: set color = -1 (1111111111111111 = black)
    @START_DRAW
    0;JMP

(SET_WHITE)
    @color
    M=0             // No key pressed: set color = 0 (white)

(START_DRAW)
    // Start address = SCREEN (16384) + 32 * 77 (2464) = 18848
    @18848
    D=A
    @addr
    M=D             // addr = 18848 (row 77, word 0)

    @20
    D=A
    @rows
    M=D             // rows = 20 remaining

(ROW_LOOP)
    @rows
    D=M
    @LOOP
    D;JEQ           // If rows == 0, return to main keyboard poll loop

    // Draw Word 0 (pixels 0..15 of current row)
    @color
    D=M
    @addr
    A=M
    M=D

    // Draw Word 1 (pixels 16..31 of current row)
    @color
    D=M
    @addr
    A=M+1
    M=D

    // Advance addr by 32 words to reach the same column in the next row
    @32
    D=A
    @addr
    M=D+M

    // Decrement row counter
    @rows
    M=M-1

    @ROW_LOOP
    0;JMP