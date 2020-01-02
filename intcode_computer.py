import copy
import itertools
import numpy as np

op_code_num_params = {1: 3,  # add next two numbers, store according to 3rd param
                        2: 3,  # multiply next two numbers, store according to 3rd param
                        3: 1,  # takes integer and stores it at address given by only parameter (1 param)
                        4: 1,  # outputs the value at the address of its only parameter (1 param)
                        5: 2,  # jump-if-true: if the first parameter is non-zero, it sets the instruction pointer to the value from the second parameter.
                        6: 2,  # jump-if-false:
                        7: 3,  # less than: if the first parameter is less than the second parameter, it stores 1 in the position given by the third parameter. Otherwise, it stores 0.
                        8: 3,  # equals: if the first parameter is equal to the second parameter, it stores 1 in the position given by the third parameter. Otherwise, it stores 0.
                        9: 1,  # adjust relative base by the paramter value (+=)
                        99: 0} # ends program immediately (0 params)
    
param_modes = {0, # position mode - look at memory location
               1, # immediate mode - take value as written
               2} # relative mode - take memory position from relative_base

def get_param_values(param_modes, params, program, relative_base):
    param_values = []
    for i, (mode, param) in enumerate(zip(param_modes, params)):
        if mode == '0':
            param_values.append(program[param])
        elif mode == '1':
            param_values.append(param)
        elif mode == '2':
            params[i] = relative_base+param
            param_values.append(program[relative_base+param])
    return param_values

class Computer(object):

    
    

    
    
    def __init__(self, name, program, input_queue=None, output_queue=None, extra_memory=0, copy_program=True):
        self.name = name
        
        program = [int(i) for i in program.split(',')]
        if copy_program:
            self.program = copy.copy(program) + [0]*extra_memory
        else:
            self.program = program + [0]*extra_memory
        
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.instr_ptr = 0
        self.stopped = False
        self.relative_base = 0
        
    def run_until_inputop_and_empty_input_queue_or_end_of_program(self):
        continue_ = True
        next_opcode, _ = self.get_next_opcode_and_instr_modes()
        while not (next_opcode == 3 and len(self.input_queue) == 0):
            op_code = self.run_single_instruction()
            if op_code == 99:
                print('end of program')
                return -1
            next_opcode, _ = self.get_next_opcode_and_instr_modes()
        return
            
    
    def get_next_opcode_and_instr_modes(self):
        mode_and_op_code = int(self.program[self.instr_ptr])
    
        # logger.info('reading op_code')
        op_code = mode_and_op_code % 100
        # logger.info(f'op_code={op_code}')
        
        # logger.info('getting param_modes')
        param_modes = str(mode_and_op_code // 100).zfill(op_code_num_params[op_code])[::-1] # left to right now
        # logger.info(f'exited param_modes, param_modes = {param_modes}')
        return op_code, param_modes

        
    def run_single_instruction(self):
        # logger.info(f'self.name:{self.name}')
        # logger.info(f'program-state:{self.program}')
        # logger.info(f'self.instr_ptr:{self.instr_ptr}')
        # logger.info(f'relative_base:{self.relative_base}')
        op_code, param_modes = self.get_next_opcode_and_instr_modes()
        
        # logger.info('getting params')
        n_params = op_code_num_params[op_code]
        params = self.program[self.instr_ptr+1:self.instr_ptr+1+n_params]
        self.instr_ptr += n_params+1
        # logger.info(f'done getting params, params={params}')

        # logger.info('entering get_param_values')
        param_values = get_param_values(param_modes, params, self.program, self.relative_base)
        # logger.info(f'exited get_param_values, param_values={param_values}')

        # param_values are not necessarilly accurate except for op_code 1 and 2,
        # the logic was adjusted below to correct for this
        if op_code == 1:
            self.program[params[2]] = param_values[0] + param_values[1]
        elif op_code == 2:
            self.program[params[2]] = param_values[0] * param_values[1]
        elif op_code == 3:
#             if param_modes == '2':
#                 self.program[self.relative_base+params[0]] = self.input_queue.pop(0)
#             else:
#                 print(param_modes)
            self.program[params[0]] = self.input_queue.pop(0)
        elif op_code == 4:
            self.output_queue.append(param_values[0])
        elif op_code == 5:
            if param_values[0] != 0:
                self.instr_ptr = param_values[1]
        elif op_code == 6:
            if param_values[0] == 0:
                self.instr_ptr = param_values[1]
        elif op_code == 7:
            if param_values[0] < param_values[1]:
                self.program[params[2]] = 1
            else:
                self.program[params[2]] = 0
        elif op_code == 8:
            if param_values[0] == param_values[1]:
                self.program[params[2]] = 1
            else:
                self.program[params[2]] = 0
        elif op_code == 9:
            self.relative_base += param_values[0]
        elif op_code == 99:
            self.stopped = True
            
        # logger.info(f'post_op program-state:{self.program}')
        # logger.info(f'self.instr_ptr:{self.instr_ptr}')
        # logger.info(f'self.output_queue:{self.output_queue}')
        # logger.info('\n')
        return op_code