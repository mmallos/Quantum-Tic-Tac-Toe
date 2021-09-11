# -*- coding: utf-8 -*-
"""
*by Matthew Mallos*

*Student ID: [13255587](mailto:13255587@student.uts.edu.au)*

Submitted: 2nd June, 2021
"""

import qiskit

# Import Packages
from termcolor import colored, cprint #For printing in colour
import json #For printing the board in readable format

# Building and Printing the Board


def resetBoard(): #Reset board sets all dictionary values to 0 and ''
  return {'1': [' ', 0] , '2': [' ', 0], '3': [' ', 0],
          '4': [' ', 0], '5': [' ', 0], '6': [' ', 0],
          '7': [' ', 0], '8': [' ', 0], '9': [' ', 0]}

##Print the Board
def printBoard(board):
  print()
  colour = 0 #Variable to record colour to print
  for i in range (1,10):
    if board[str(i)][1] == 0:
      cprint(board[str(i)][0], end='')
    else:
      if (colour == 0 or colour == 1): #First quantum move = red
        cprint(board[str(i)][0], 'red', end='')
        colour = colour + 1
      elif (colour == 2 or colour == 3): #Second quantum move = green
        cprint(board[str(i)][0], 'green', end='')
        colour = colour + 1
      elif (colour == 4 or colour == 5): #Second quantum move = blue
        cprint(board[str(i)][0], 'blue', end='')
        colour = colour + 1
      elif (colour == 6 or colour == 7): #Second quantum move = yellow
        cprint(board[str(i)][0], 'yellow', end='')
        colour = colour + 1

    if i % 3 == 0: #Prints the boards gridlines
      print()
      if i != 9: 
        print('-+-+-')
    else:
      cprint('|', end='')

# Moves

## Classical Moves

def make_classic_move(theBoard, turn, count, circuit):

  valid_move = False
  valid_moves = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
  
  while (not valid_move):
    print()
    print("Which location? (1-9) ", end='')
    location = input()

    if location in valid_moves:
        
      if theBoard[location][0] == ' ':
        valid_move = True #Certifies move is valid
        theBoard[location][0] = turn #set the location's marker
        count += 1 #increment counter (total markers on board) 
        #when count = 9, collapse/measure the board 
        theBoard[location][1] = 0 #set marker's state (classical)

        # set qubit[location] to ON, 100% = 1
        circuit.x(int(location)-1) # one pauli X gate

        print(circuit.draw())
      else: 
        print()
        print("That place is already filled.")
    else:
      print("Please select a square from 1-9")

  return theBoard, turn, count, circuit

## Quantum Moves
def make_quantum_move(theBoard, count, circuit, turn):

  valid_move = False
  valid_moves = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

  while (not valid_move):
    location1 = input("Which location for Q1? (1-9) ")
    location2 = input("Which location for Q2? (1-9) ")

    if location1 != location2 and location1 in valid_moves and location2 in valid_moves and theBoard[location1][0] == ' ' and theBoard[location2][0] == ' ':
        valid_move = True
        # set the location's marker
        theBoard[location1][0] = turn
        theBoard[location2][0] = turn
        
        count += 2 #increment counter (total markers on board) 
        #when this = 9, collapse/measure the board
        
        # set marker's state (classical or quantum)
        theBoard[location1][1] = 1 # quantum (coloured on screen)
        theBoard[location2][1] = 1 # quantum (coloured on screen)

        # set qubit[location1], qubit[location2] to superposition/entangled
        circuit.h(int(location1)-1) #hadamard gates
        circuit.x(int(location2)-1) #x gate
        circuit.cx(int(location1)-1,int(location2)-1) #cnot gate

        print(circuit.draw())

    else:
        print()
        print("You have selected an invalid position/s")
    
  return theBoard, count, circuit, turn

##Special Ability: Collapse

#To add strategy to the game, allows a user to collapse the board once per game. 

#Measuring

def measure(circuit, theBoard, count):
  # trigger collapse
  printBoard(theBoard)
  print()
  print("Trigger collapse.")
  print()

  # Use Aer's qasm_simulator
  simulator = qiskit.Aer.get_backend('qasm_simulator')

  circuit.measure(0,0)
  circuit.measure(1,1)
  circuit.measure(2,2)
  circuit.measure(3,3)
  circuit.measure(4,4)
  circuit.measure(5,5)
  circuit.measure(6,6)
  circuit.measure(7,7)
  circuit.measure(8,8)

  print(circuit.draw())

  # Execute the circuit on the qasm simulator
  job = qiskit.execute(circuit, simulator, shots=1)

  # Grab results from the job
  result = job.result()

  out = json.dumps(result.get_counts()) #Converts the result.get_counts() into a string
  string = out[2:11] #Removes unnecessary data from string, leaving us with board

  # update board
  for i in range(9):
      if string[i] == '1':
          # cement value in the board
          theBoard[str(9-i)][1] = 0
      else:
          # make square empty
          theBoard[str(9-i)][1] = 0
          theBoard[str(9-i)][0] = ' '

  # update count (total number of markers on the board)
  count = 0
  for i in range(9):
      theBoard[str(i+1)][1] = 0
      if theBoard[str(i+1)][0] != ' ':
          count += 1

  # reset qubits
  circuit.reset(0)
  circuit.reset(1)
  circuit.reset(2)
  circuit.reset(3)
  circuit.reset(4)
  circuit.reset(5)
  circuit.reset(6)
  circuit.reset(7)
  circuit.reset(8)

  for i in range(9):
      if string[8-i] == '1':
          # add pauli x gate
          circuit.x(i)

  return circuit, string, theBoard, count

# Checking for a Victory

def check_win(theBoard, turn):
  win = [[1,2,3], [4,5,6], [7,8,9], [1,4,7], [2,5,8], [3,6,9], [1,5,9], [3,5,7]]

  for moves in win:
    if theBoard[str(moves[0])][0] == theBoard[str(moves[1])][0] == theBoard[str(moves[2])][0] != ' ': #win condition to check
        if theBoard[str(moves[0])][1] == theBoard[str(moves[1])][1] == theBoard[str(moves[2])][1] == 0: #counts only cemented markers
            printBoard(theBoard)
            print("\nGame Over.\n")                
            print(" **** " + turn + " won ****")
            print() 
            return True

# Start Menu

def start_menu():
    start_menu = """
Start Menu:
    1. Start Game
    2. How to Play
    3. Quit
    """ 
    
    print("""
###########################
### Quantum Tic-Tac-Toe ###
###########################
    """)
    print(start_menu)
    choice = 0
    while (choice != '1'):
      choice = input("What would you like to do? (1-3) ")

      if (choice != '1' and choice != '2'):
        print("Please select a valid option")

      if (choice == '2'):
        print( """ 
In Quantum Tic-Tac-Toe, each square starts empty and your goal is to create a line of three of your naughts/crosses. 
Playing a classical move will result in setting a square permanently as your piece.
Playing a quantum move will create a superposition between two squares of your choosing. You may only complete a quantum move in two empty squares.
The board will collapse when the board is full. At collapse, each superposition is viewed and only 1 piece of the superposition will remain. 
Each superposition will place pieces of the same colour.
*Powerup* Each player can decide to collapse the board prematurely, they may do this once per game each.
        """ )

      if (choice == '3'):
        print("Goodbye")
        break
      
    return choice

# The Main Game Function
#Implementation of Two Player Tic-Tac-Toe game in Python.
# Now we'll write the main function which has all the gameplay functionality.

def game():

    turn = 'X'
    count = 0
    win = False
    x_collapse = 1
    y_collapse = 1

    # initialise quantum circuit with 9 qubits (all on OFF = 0)
    circuit = qiskit.QuantumCircuit(9, 9)

    while (not win):

        # ============================= ROUND START ============================ 
        global theBoard
        printBoard(theBoard)

        print()
        
        valid_moves = ["1", "2", "3", "4"]
        valid_move = False

        while (not valid_move):
          print("It's your turn " + turn + """. Please select:
    1. Make classical move 
    2. Make quantum move
    3. Collapse
    4. Quit""")
          move = input()
          if move in valid_moves:
            valid_move = True
          else:
            print("please select a valid move")

        # ============================= CLASSIC MOVE ===========================

        if int(move) == 1:
            theBoard, turn, count, circuit = make_classic_move(theBoard, turn, count, circuit)
            madeMove = True

        # ============================= QUANTUM MOVE ===========================

        elif int(move) == 2 and count > 8:
          # cant do a quantum move if there's only 1 empty square left
          print()
          print("There aren't enough empty spaces for that!")

        elif int(move) == 2 and count < 8:
          theBoard, count, circuit, turn = make_quantum_move(theBoard, count, circuit, turn)
          madeMove = True
        
        # ============================= COLLAPSE/MEASURE =======================

        elif int(move) == 3:
            if (count > 0):
              if (turn == 'X' and x_collapse== 1 ):
                circuit, string, theBoard, count = measure(circuit, theBoard, count)
                x_collapse = 0
              elif (turn == 'O' and y_collapse == 1):
                circuit, string, theBoard, count = measure(circuit, theBoard, count)
                y_collapse = 0
              else:
                print("You have already used your collapse this game!")
            else:
                print("There are no pieces on the board yet")
                madeMove = False

        # ============================= QUIT ===================================

        elif int(move) == 4:
            break
        
        # ============================= CHECK FOR WIN ==========================

        # Now we will check if player X or O has won,for every move  
        if count >= 5:
          win = check_win(theBoard, turn)
          if (win):
            break

        # If neither X nor O wins and the board is full, we'll declare the result as 'tie'.
        if count == 9:
          circuit, string, theBoard, count = measure(circuit, theBoard, count)
          win = check_win(theBoard, turn)
          if count == 9:
            print("\nGame Over.\n")                
            print("It's a Tie !")
            print()
            win = True

        # Now we have to change the player after every move.
        if  (madeMove):  
          madeMove = False
          if turn =='X':
              turn = 'O'
          else:
              turn = 'X'        

    # Now we will ask if player wants to restart the game or not.
    restart = input("Play Again?(y/n) ")
    if restart == "y" or restart == "Y":
        theBoard = resetBoard()
        game()
    else:
      print("Goodbye")

# Play the Game

#Reset the board at start
theBoard = resetBoard()

#Set no moves made yet
if (start_menu() == '1'):  
  madeMove = False
  game()
