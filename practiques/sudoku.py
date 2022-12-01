from optilog.modelling import *
from optilog.formulas import CNF
from optilog.solvers.sat import Glucose41
from sudoku_base import read_sudoku, var, visualize
import sys
from sys import exit

#generate at least one (alo) clauses function

def alo(lits):
    return [lits[:]]
    
#generate at most one (amo) clauses function

def amo(lits):
    clauses = []
    for i in range(len(lits)-1):
        for j in range(i+1,len(lits)):
            lit1 = lits[i]
            lit2 = lits[j]
            clauses.append([~lit1,~lit2])
    return clauses

#variation of the amo function but taking only the first clause of the list as a reference for pairwise combinations (function only used in miracle sudoku)
    
def selfish_amo(lits):
    clauses = []
    for i in range(len(lits)):
        if i != 0:
            clauses.append([~lits[0],~lits[i]])
    return clauses

#main function

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
    
    #values: generate lists of required values ​​based on the size of the sudoku.
    #the lists rows, columns and values are the same and could be used just one, but for readability i chose to do it this way.
    
    lst = []
    val = 0
    while(val<SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
        lst.append(val)
        val += 1
    rows = lst.copy()
    columns = lst.copy()
    values = lst.copy()
    
    # Cells: Create a set of clauses with each possible value of each cell.
    
    for row in rows:
        lits = []
        for column in columns:
            for value in values:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(alo(lits))
            cnf.add_clauses(amo(lits))
            
            #reset list
            
            lits = [] 

    # Row: Create restrictions for each row.
    
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(amo(lits))
            
            #reset list
            
            lits = [] 

    # Column: Create restrictions for each column
    
    for value in values:
        lits = []
        for column in columns:
            for row in rows:
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
            # add ALO clauses
            
            cnf.add_clauses(amo(lits))
            
            #reset list
            
            lits = [] 
   
    # Subgroup
    #This function generates amo functions for each subgroup.
    #It uses the variables i and j to define wich one of the subgroup restriction clauses are being generated based on the subgroup lenght and height.
    
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
    
    # Miracle Sudoku

    '''
    
    Each cell within horse movement distance of the origin cell cannot contain the same value.

    Since I've optimized this section maybe too much not to repeat the code, it's a bit confusing, so I've decided to write a little explanation of what's going on here.
    
    Let's consider the "X" as the possible positions of the knight and the "O" as the Knight:
    
    - - - - - - -
    - - X - X - -
    - X - - - X -
    - - - O - - -
    - X - - - X -
    - - X - X - -
    - - - - - - -
    
    What this code does is take the original "0" position and see if the other "X" positions are available on the board, to do this it uses the range of values ​​in i and j to determine the cell position, if the cell position cell is within the size of the board, it adds a new clause to the list. The order to determine each cell is like this:
    
    - - - - - - -
    - - 1 - 2 - -
    - 5 - - - 6 -
    - - - O - - -
    - 7 - - - 8 -
    - - 3 - 4 - -
    - - - - - - -
    
    Positions 1,2,3,4 correspond to the first if i,j and positions 5,6,7,8 to the second if j,i. I hope It helped a bit.
    
    '''
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
                for i in range(-2,3,4):
                    for j in range(-1,2,2):
            
                        #Origin cell
            
                        lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                        lits.append(lit)
            
                        #Knight position
            
                        if (int(row+i) >= 0) and (int(column+j) >= 0) and (int(row+i) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column+j) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                        
                            lit = Bool('Cell_{}_{}_{}'.format(row+i,column+j,value))
                            lits.append(lit)         
            
                        if (int(row+j) >= 0) and (int(column+i) >= 0) and (int(row+j) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column+i) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                        
                            lit = Bool('Cell_{}_{}_{}'.format(row+j,column+i,value))
                            lits.append(lit)
                    
                        #create clauses and reset list
            
                        cnf.add_clauses(selfish_amo(lits))
                        lits = []  
     
    # Cells reachable with a king move can not contain same value
    
    '''
    - - - - - - -       - - - - - - -
    - - - - - - -       - - - - - - -
    - - X X X - -       - - 1 2 3 - -
    - - X O X - -  -->  - - 4 O 5 - -
    - - X X X - -       - - 6 7 8 - -
    - - - - - - -       - - - - - - -
    - - - - - - -       - - - - - - -
    
    '''
    
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
                for i in range(-1,2,2):
                    for j in range(-1,2,2):
                
                        #generate origin cell
                
                        lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                        lits.append(lit)
                
                        #Cells
                
                        if ((int(row+i) >= 0) and (int(column+j) >=0)) and ((int(row+i) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column+j) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT))):
                  
                            lit = Bool('Cell_{}_{}_{}'.format(row+i,column+j,value))
                            lits.append(lit)
 
                        #create clauses and reset list
                
                        cnf.add_clauses(selfish_amo(lits))
                        lits = []  

    # Cells reachable with a king move (without diagonal one) can not contain a consecutive value
    
    '''
    - - - - - - -       - - - - - - -
    - - - - - - -       - - - - - - -
    - - - X - - -       - - - 1 - - -
    - - X O X - -  -->  - - 3 O 4 - -
    - - - X - - -       - - - 2 - - -
    - - - - - - -       - - - - - - -
    - - - - - - -       - - - - - - -
    
    '''
    
    for value in values:
        for row in rows:
            for column in columns:
                for i in range(-1,2,2):
                    for j in range(-1,2,2):
            
            	#generate origin cell
                
                            lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                            lits.append(lit)
                
                            #top and bot
                        
                            if (int(row+i) >= 0 and int(value+j) >=0) and int(row+i) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(value+j) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                        
                                lit = Bool('Cell_{}_{}_{}'.format(row+i,column,value+j))
                                lits.append(lit)
                            
                    
                            #left and right
                        
                            if (int(column+i) >= 0 and int(value+j) >=0) and int(column+i) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(value+j) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):

                                lit = Bool('Cell_{}_{}_{}'.format(row,column+i,value+j))
                                lits.append(lit)
                
                            #create clauses and reset list
                
                            cnf.add_clauses(selfish_amo(lits))
                            lits = [] 
    
    #debug only, count clauses
    
    '''
    Clauses = 0
    for clause in cnf.clauses:
            Clauses += 1
    print("Total Clauses:",Clauses)
    '''
    
    s = Glucose41()
    s.add_clauses(cnf.clauses)
    has_solution = s.solve()
    print('Has solution?', has_solution)

    if has_solution:
        interp = s.model()
        visualize(cnf.decode_dimacs(interp), sudoku)

if __name__ == '__main__':
    solve(sys.argv[1])
