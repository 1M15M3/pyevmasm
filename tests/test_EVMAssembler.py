import unittest

import pyevmasm as EVMAsm


# noinspection PyPep8Naming
class EVMTest_Assembler(unittest.TestCase):
    _multiprocess_can_split_ = True
    maxDiff = None

    def test_ADD_1(self):
        instruction = EVMAsm.disassemble_one(b'\x60\x10')
        self.assertEqual(EVMAsm.Instruction(0x60, 'PUSH', 1, 0, 1, 3, 'Place 1 byte item on stack.', 16, 0),
                         instruction)

        instruction = EVMAsm.assemble_one('PUSH1 0x10')
        self.assertEqual(instruction, EVMAsm.Instruction(0x60, 'PUSH', 1, 0, 1, 3, 'Place 1 byte item on stack.', 16, 0))

        instructions1 = EVMAsm.disassemble_all(b'\x30\x31')
        instructions2 = EVMAsm.assemble_all('ADDRESS\nBALANCE')
        self.assertTrue(all(a == b for a, b in zip(instructions1, instructions2)))

        # High level simple assembler/disassembler

        bytecode = EVMAsm.assemble_hex(
            """PUSH1 0x80
               BLOCKHASH
               MSTORE
               PUSH1 0x2
               PUSH2 0x100
            """
        )
        self.assertEqual(bytecode, '0x608040526002610100')

        asmcode = EVMAsm.disassemble_hex('0x608040526002610100')
        self.assertEqual(asmcode, '''PUSH1 0x80\nBLOCKHASH\nMSTORE\nPUSH1 0x2\nPUSH2 0x100''')

    def test_STOP(self):
        insn = EVMAsm.disassemble_one(b'\x00')
        self.assertTrue(insn.mnemonic == 'STOP')

    def test_JUMPI(self):
        insn = EVMAsm.disassemble_one(b'\x57')
        self.assertTrue(insn.mnemonic == 'JUMPI')
        self.assertTrue(insn.is_branch)

    def test_pre_byzantium(self):
        insn = EVMAsm.disassemble_one(b'\x57', fork='pre-byzantium')
        self.assertTrue(insn.mnemonic == 'JUMPI')
        self.assertTrue(insn.is_branch)
        insn = EVMAsm.disassemble_one(b'\xfa', fork='pre-byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # STATICCALL added in byzantium
        insn = EVMAsm.disassemble_one(b'\xfd', fork='pre-byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # REVERT added in byzantium

    def test_byzantium_fork(self):
        insn = EVMAsm.disassemble_one(b'\x57', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'JUMPI')
        self.assertTrue(insn.is_branch)
        insn = EVMAsm.disassemble_one(b'\x1b', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # SHL added in constantinople
        insn = EVMAsm.disassemble_one(b'\x1c', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # SHR added in constantinople
        insn = EVMAsm.disassemble_one(b'\x1d', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # SAR added in constantinople
        insn = EVMAsm.disassemble_one(b'\x3f', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # EXTCODEHASH added in constantinople
        insn = EVMAsm.disassemble_one(b'\xf5', fork='byzantium')
        self.assertTrue(insn.mnemonic == 'INVALID')  # CREATE2 added in constantinople

    def test_constantinople_fork(self):
        insn = EVMAsm.disassemble_one(b'\x1b', fork='constantinople')
        self.assertTrue(insn.mnemonic == 'SHL')
        self.assertTrue(insn.is_arithmetic)
        insn = EVMAsm.disassemble_one(b'\x1c', fork='constantinople')
        self.assertTrue(insn.mnemonic == 'SHR')
        self.assertTrue(insn.is_arithmetic)
        insn = EVMAsm.disassemble_one(b'\x1d', fork='constantinople')
        self.assertTrue(insn.mnemonic == 'SAR')
        self.assertTrue(insn.is_arithmetic)
        insn = EVMAsm.disassemble_one(b'\x3f', fork='constantinople')
        self.assertTrue(insn.mnemonic == 'EXTCODEHASH')
        insn = EVMAsm.disassemble_one(b'\xf5', fork='constantinople')
        self.assertTrue(insn.mnemonic == 'CREATE2')

if __name__ == '__main__':
    unittest.main()
