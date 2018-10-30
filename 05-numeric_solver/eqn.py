import numpy as np
import re
import sys

def solve_eqs(file):
    right_sides = []
    equations = []
    variable_reg = re.compile(r"(\d*)([a-z])")
    operand = None

    if file is not None:
        for line in file:
            left_side = {}
            is_right_side = False
            for item in line.split(" "):
                #item is some kind of operand
                if item == '=':
                    is_right_side = True
                elif item == '-':
                    operand = '-'
                elif item == '+':
                    operand = '+'
                #item is a variable/number
                else :
                    if is_right_side:
                        right_sides.append(int(item))
                    else:
                        match = variable_reg.match(item)
                        if match:
                            if match.group(1):
                                multiple = int(match.group(1))
                            else:
                                multiple = 1
                            if operand and operand == '-':
                                multiple = - multiple
                            variable = match.group(2)
                            left_side[variable] = int(multiple)
            equations.append(left_side)

    all_variables = set().union(*(d.keys() for d in equations))
    sorted_variables_list = sorted(list(all_variables))
    arrays = []
    for eq in equations:
        list_var = []
        for variable in sorted_variables_list:
            if variable in eq.keys():
                list_var.append(eq[variable])
            else:
                list_var.append(0)
        arrays.append(list_var)

    variables_count = len(sorted_variables_list)
    multiplies = np.array(arrays)
    results = np.array(right_sides)
    equations_matrix = np.array(np.c_[multiplies, results])
    multiplies_rank = np.linalg.matrix_rank(multiplies)
    results_rank = np.array(np.linalg.matrix_rank(results))
    equations_matrix_rank = np.array(np.linalg.matrix_rank(equations_matrix))

    if multiplies_rank != equations_matrix_rank:
        print("no solution")
    else:
        if multiplies_rank < variables_count:
            print("solution space dimension: " + str(variables_count - multiplies_rank))
        else:
            result = np.linalg.solve(multiplies, results)
            print('solution: ', end='')
            index = 0
            for key in sorted_variables_list:
                print(key, ' = ', result[index], end='', flush=True)
                if index < len(sorted_variables_list) - 1:
                    print(end=', ')
                index += 1
            print()


f = open(sys.argv[1], 'r')
solve_eqs(f)
