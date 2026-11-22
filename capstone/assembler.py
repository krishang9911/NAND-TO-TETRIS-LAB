import sys
import os

DEST_TABLE = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011", "DM":  "011",
    "A":   "100",
    "AM":  "101", "MA":  "101",
    "AD":  "110", "DA":  "110",
    "AMD": "111", "ADM": "111", "DAM": "111", "DMA": "111", "MAD": "111", "MDA": "111"
}

JUMP_TABLE = {
    "": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"
}

COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "A+D": "0000010",
    "D+M": "1000010", "M+D": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "A&D": "0000000",
    "D&M": "1000000", "M&D": "1000000",
    "D|A": "0010101", "A|D": "0010101",
    "D|M": "1010101", "M|D": "1010101"
}

def init_symbols():
    symbols = {
        "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576
    }
    for i in range(16):
        symbols[f"R{i}"] = i
    return symbols

def clean_line(raw_line):
    # Remove inline comments and surrounding whitespace
    no_comment = raw_line.split("//")[0]
    return no_comment.strip()

def assemble(asm_path):
    with open(asm_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    symbols = init_symbols()
    declared_labels = set()
    instructions = []

    # FIRST PASS: Strip comments/blanks and record (LABEL) ROM addresses
    rom_address = 0
    for line_num, raw_line in enumerate(raw_lines, start=1):
        line = clean_line(raw_line)
        if not line:
            continue

        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1].strip()
            # Extra Feature (K=77 -> 77 mod 3 = 2): Warn on duplicate label
            if label in declared_labels:
                print(f"Warning (Line {line_num}): Duplicate label '({label})' ignored; keeping original address {symbols[label]}.")
            else:
                symbols[label] = rom_address
                declared_labels.add(label)
        else:
            instructions.append(line)
            rom_address += 1

    # SECOND PASS: Translate A-instructions and C-instructions into 16-bit binary
    next_ram_addr = 16
    machine_code = []

    for inst in instructions:
        if inst.startswith("@"):
            symbol = inst[1:].strip()
            if symbol.isdigit():
                addr = int(symbol)
            else:
                if symbol not in symbols:
                    symbols[symbol] = next_ram_addr
                    next_ram_addr += 1
                addr = symbols[symbol]
            machine_code.append(f"0{addr:015b}")
        else:
            # Parse C-instruction: [dest=]comp[;jump]
            dest_part, jump_part = "", ""
            comp_part = inst

            if "=" in comp_part:
                dest_part, comp_part = comp_part.split("=", 1)
            if ";" in comp_part:
                comp_part, jump_part = comp_part.split(";", 1)

            dest_bits = DEST_TABLE[dest_part.strip()]
            comp_bits = COMP_TABLE[comp_part.strip()]
            jump_bits = JUMP_TABLE[jump_part.strip()]

            machine_code.append(f"111{comp_bits}{dest_bits}{jump_bits}")

    hack_path = os.path.splitext(asm_path)[0] + ".hack"
    with open(hack_path, "w", encoding="utf-8") as f:
        for code in machine_code:
            f.write(code + "\n")

    print(f"Assembled {asm_path} -> {hack_path} ({len(machine_code)} instructions)")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <filename.asm>")
        sys.exit(1)
    assemble(sys.argv[1])