from optilog.modelling import *
from optilog.formulas import CNF
from optilog.solvers.sat import Glucose41
from sudoku_base import read_sudoku, var, visualize
import sys
from sys import exit

    



def alo(lits):
    return [lits[:]]

def amo(lits):
    clauses = []
    for i in range(len(lits)-1):
        for j in range(i+1,len(lits)):
            lit1 = lits[i]
            lit2 = lits[j]
            clauses.append([~lit1,~lit2])
    return clauses
    


def solve(path):
    cnf = CNF()
    sudoku = read_sudoku(path)
    SUBGROUP_LENGTH = sudoku.subgroup_length
    SUBGROUP_HEIGHT = sudoku.subgroup_height
    VALUES = (SUBGROUP_HEIGHT *  SUBGROUP_LENGTH)

    # Fixed
    for j in range(VALUES):
        for i in range(VALUES):
            v = sudoku.cells[i][j]
            if v is not None:
                cnf.add_clause([var(i, j, v)])

    # Debug clauses:

    # print('---------')

    #for clause in cnf.clauses:
    #      print(cnf.decode_dimacs(clause))

    # print('---------')
    
    #values: Generate the amount of values needed in function of the size
    
    lst = []
    val = 0
    while(val<SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
        lst.append(val)
        val += 1
    rows = lst.copy()
    columns = lst.copy()
    values = lst.copy()
    
    # Cells: Create a set of clauses with each possible value
    
    for row in rows:
        lits = []
        for column in columns:
            for value in values:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(alo(lits))
            cnf.add_clauses(amo(lits))
            
            #reset list to create next clause
            
            lits = [] 

    # Row
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(amo(lits))
            
            #reset list to create next clause
            
            lits = [] 

    # Column
    
    for value in values:
        lits = []
        for column in columns:
            for row in rows:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(amo(lits))
            
            #reset list to create next clause
            
            lits = [] 
   
    # Subgroup
    #Functionality: This functions generates amo functions for each subgroup.
    #It uses the variables i and j to define wich one of the subgroups clauses are being generated.
    
    for i in range(SUBGROUP_LENGTH):
    
        for j in range(SUBGROUP_HEIGHT):
        
            for value in values:
                lits = []
                for row in rows:
              
                    if int(row) >= (SUBGROUP_HEIGHT*i)-SUBGROUP_HEIGHT and int(row) < SUBGROUP_HEIGHT*i:            
                        for column in columns:
                            if int(column) >= (SUBGROUP_LENGTH*j)-SUBGROUP_LENGTH and int(column) < SUBGROUP_LENGTH*j:
                            
                                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                                lits.append(lit)
                                
                cnf.add_clauses(amo(lits))      
                lits = []
        
        
    #debug only
    
    #Clauses = 0
    #for clause in cnf.clauses:
    #        Clauses += 1
    #print("Total Clauses:",Clauses)
    
    # Miracle Sudoku
    
    # Cells reachable with a knight move can not contain same value
    # - YOUR CODE HERE -
    
    # Cells reachable with a king move can not contain same value
    # - YOUR CODE HERE -

    # Cells reachable with a king move (without diagonal one) can not contain a consecutive value
    # - YOUR CODE HERE -
    
    s = Glucose41()
    s.add_clauses(cnf.clauses)
    has_solution = s.solve()
    print('Has solution?', has_solution)

    if has_solution:
        interp = s.model()
        visualize(cnf.decode_dimacs(interp), sudoku)

if __name__ == '__main__':
    solve(sys.argv[1])
