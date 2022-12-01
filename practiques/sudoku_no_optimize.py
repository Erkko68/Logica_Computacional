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
    
    #values: generate lists with required values ​​based on the size of the sudoku.
    #the lists rows, columns and values are the same and could be used just one, but for readability I chose to do it this way.
    
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
    #Functionality: This function generates amo functions for each subgroup.
    #It uses the variables i and j to define wich one of the subgroup restriction clauses are being generated.
    
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

    #

    #This part of the code generates a set of clauses based on the source cell. 
    #Each cell within horse movement distance of the origin cell cannot contain the same value.
    #if there is a knight position with respect to the cell of origin and it is inside the board, it will be added to the list of clauses.
    
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
            
            #Origin cell
            
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
            
            #1st horse position
            
                if (int(row-2) >= 0) and (int(column-1) >= 0):
                    lit = Bool('Cell_{}_{}_{}'.format(row-2,column-1,value))
                    lits.append(lit)
                    
            #2nd horse position    
             
                if (int(row-2) >= 0) and (int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                    lit = Bool('Cell_{}_{}_{}'.format(row-2,column+1,value))
                    lits.append(lit)
                    
            #3rd horse position
            
                if (int(row-1) >= 0) and (int(column-2) >= 0):
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column-2,value))
                    lits.append(lit)
                  
            #4rth horse position
               
                if (int(row-1) >= 0) and (int(column+2) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column+2,value))
                    lits.append(lit)
                   
            #5th horse position
               
                if (int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column-2) >= 0):
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column-2,value))
                    lits.append(lit)
            
            #6th horse position
               
                if (int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column+2) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column+2,value))
                    lits.append(lit)
         
            #7th horse position
               
                if (int(row+2) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column-1) >= 0):
                    lit = Bool('Cell_{}_{}_{}'.format(row+2,column-1,value))
                    lits.append(lit)
         
            #8th horse position
               
                if (int(row+2) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)) and (int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT)):
                    lit = Bool('Cell_{}_{}_{}'.format(row+2,column+1,value))
                    lits.append(lit)
                    
            #create clauses and reset list
            
                cnf.add_clauses(selfish_amo(lits))
                lits = []  
     
    # Cells reachable with a king move can not contain same value
    #
    
    for value in values:
        lits = []
        for row in rows:
            for column in columns:
                
                #generate origin cell
                
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
                #Cells top
                
                if int(row-1) >= 0 and int(column-1) >=0:
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column-1,value))
                    lits.append(lit)
                    
                if int(row-1) >= 0 and int(column) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column,value))
                    lits.append(lit)

                if int(row-1) >= 0 and int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column+1,value))
                    lits.append(lit)
                
                #Cells Mid
                
                if int(row) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(column-1) >= 0:
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row,column-1,value))
                    lits.append(lit)
                
                if int(row) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row,column+1,value))
                    lits.append(lit)
                
                #Cells bot
                
                if int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(column-1) >= 0:
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column-1,value))
                    lits.append(lit)
                    
                if int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(column) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column,value))
                    lits.append(lit)

                if int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                  
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column+1,value))
                    lits.append(lit)
                    
                #create clauses and reset list
                
                cnf.add_clauses(selfish_amo(lits))
                lits = []  
    
    # Cells reachable with a king move (without diagonal one) can not contain a consecutive value
    
    for value in values:
        for row in rows:
            for column in columns:
            
            	#generate origin cell
                
                lit = Bool('Cell_{}_{}_{}'.format(row,column,value))
                lits.append(lit)
                
                #top
                
                if int(row-1) >= 0 and int(value+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column,value+1))
                    lits.append(lit)
                    
                if int(row-1) >= 0 and int(value-1) >= 0:
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row-1,column,value-1))
                    lits.append(lit)
                
                #bot
                
                if int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(value+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column,value+1))
                    lits.append(lit)
                    
                if int(row+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(value-1) >= 0:
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row+1,column,value-1))
                    lits.append(lit)
                    
                #left
                    
                if int(column-1) >= 0 and int(value+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row,column-1,value+1))
                    lits.append(lit)
                    
                if int(column-1) >= 0 and int(value-1) >= 0:
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row,column-1,value-1))
                    lits.append(lit)
                    
                #right
                
                if int(column+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT) and int(value+1) < (SUBGROUP_LENGTH*SUBGROUP_HEIGHT):
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row,column+1,value+1))
                    lits.append(lit)
                
                if int(column+1) >= 0 and int(value-1) >= 0:
                                     
                    lit = Bool('Cell_{}_{}_{}'.format(row,column+1,value-1))
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
