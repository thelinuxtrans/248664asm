import shutil

class VirtualMachine:
    def __init__(self):
        self.memory = [0] * 65536    # 64KiB memory (0000 - FFFF)
        self.registers = [0] * 10    # 10 Registers R0 to R9
        self.stack = []              # Stack (for push/pop)
        self.pc = 0                  # Program Counter
        self.sp = 0                  # Stack Pointer (could use len(self.stack))
        self.running = True          # VM running state

    def reset(self):
        """ Resets the VM state. """
        self.pc = 0
        self.sp = 0
        self.registers = [0] * 10
        self.memory = [0] * 65536
        self.stack.clear()
        self.running = True

    def load_program(self, program):
        """ Loads a program into memory (as lines of assembly). """
        for i, line in enumerate(program):
            self.memory[i] = line.strip()  # Store the line as a string
        print(f"Loaded {len(program)} instructions into memory.")

    def fetch(self):
        """ Fetch the next instruction. """
        instruction = self.memory[self.pc]
        print(f"Fetching instruction at {self.pc:04X}: {instruction}")  # Debug line
        self.pc += 1
        return instruction

    def execute(self, instruction):
        """ Executes a single instruction. """
        print(f"Executing: {instruction}")  # Debug line
        tokens = instruction.split(maxsplit=1)
        op = tokens[0]

        if op == "JMP":
            addr = int(tokens[1].replace('%', ''), 16)
            self.pc = addr

        elif op == "STR":
            self.memory[self.pc] = self.pc

        elif op == "PUSH":
            self.stack.append(self.pc)

        elif op == "MOV":
            args = tokens[1].split()
            if args[0].startswith("R"):
                reg = int(args[0][1])
                addr = int(args[1], 16)
                self.registers[reg] = self.memory[addr]
            else:
                addr = int(args[0].replace('%', ''), 16)
                self.memory[addr] = self.pc

        elif op == "CMP":
            args = tokens[1].split()
            addr = int(args[0], 16)
            if self.memory[addr] == self.stack[-1]:
                print(f"Memory {addr:04X} matches stack.")

        elif op == "ADD":
            args = tokens[1].split(',')
            reg = int(args[0][1])
            addr = int(args[1], 16)
            self.registers[reg] += self.memory[addr]

        elif op == "NULL":
            target = tokens[1]
            if target.startswith("R"):
                reg = int(target[1])
                self.registers[reg] = 0
            elif target == "%STCK%":
                self.stack = []
            else:
                addr = int(target, 16)
                self.memory[addr] = 0

        elif op == "HLT":
            print("Halting VM.")
            self.running = False

        elif op == "PRN":
            content = tokens[1].strip()
            if content.startswith("{") and content.endswith("}"):
                print(content[1:-1])
            elif content.startswith("R"):
                reg = int(content[1])
                print(f"R{reg}: {self.registers[reg]}")
            else:
                addr = int(content, 16)
                print(f"Memory[{addr:04X}]: {self.memory[addr]}")

    def run_program(self):
        """ Runs the program loaded into memory. """
        while self.running and self.pc < len(self.memory):
            instruction = self.fetch()
            if instruction and instruction != 0:
                self.execute(instruction)


class VMCLI:
    def __init__(self):
        self.vm = VirtualMachine()

    def clear(self):
        """ Clears the screen by printing enough blank lines. """
        _, terminal_height = shutil.get_terminal_size(fallback=(80, 24))  # Default to 80x24
        print("\n" * (terminal_height + 1))  # Add one extra line for good measure

    def load_program(self, filename):
        """ Loads a program from an assembly file, ignoring comments. """
        try:
            with open(filename, 'r') as file:
                program = []
                for line in file:
                    line = line.split(';')[0].strip()  # Remove comments and strip whitespace
                    if line:  # Skip empty lines
                        program.append(line)
                self.vm.load_program(program)
                print(f"Program '{filename}' loaded into memory.")
        except FileNotFoundError:
            print(f"File '{filename}' not found.")

    def run_program(self):
        """ Starts the VM and runs the loaded program. """
        print("Running program...")
        self.vm.run_program()

    def reset_vm(self):
        """ Resets the VM to initial state. """
        self.vm.reset()
        print("VM reset.")

    def start_cli(self):
        """ Starts the CLI to interact with the VM. """
        print("Welcome to the VM CLI. Type 'help' for commands.")
        while True:
            command = input("> ").strip().split()
            if len(command) == 0:
                continue

            cmd = command[0]

            if cmd == "clear":
                self.clear()  # Call the clear function

            elif cmd == "load":
                if len(command) < 2:
                    print("Usage: load <filename>")
                else:
                    self.load_program(command[1])

            elif cmd == "run":
                self.run_program()

            elif cmd == "reset":
                self.reset_vm()

            elif cmd == "exit":
                print("Exiting...")
                break

            elif cmd == "help":
                print("""
Available commands:
  clear             - Clear the screen.
  load <filename>   - Load an assembly program into memory.
  run               - Run the loaded program.
  reset             - Reset the VM to its initial state.
  exit              - Exit the CLI.
  help              - Show this help message.
                """)
            else:
                print(f"Unknown command: {cmd}. Type 'help' for a list of commands.")


if __name__ == "__main__":
    cli = VMCLI()
    cli.start_cli()
