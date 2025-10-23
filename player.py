import board
import random
import math

WINSCORE = 9999 #defines the score for winning
LOSEPENALTY = -9999 #defines the score penalty for losing
DRAWPENALTY = -5000 #defines the score penalty for drawing
MOVEPENALTY = -1 #defines the score penalty per move

class opponentNode: #this is a class to store the information about an instance of the board when the opponent was the last to play
	def __init__(self, score):
		self.score = score #the score of this node, based on the score of the best move the player can make from this position
		self.bestChild = None # the child which is the best for the player
		self.lastMove = None # the play to get this node

class playerNode: #this is a class to store the information about an instance of the board when the player was the last to play
	def __init__(self, score):
		self.score = score # the score from the node which is the best for the opponent (minimal score from the child list)
		self.children = list() # the list of the children of this node (of type opponentNode)
		self.lastMove = None # the play to get this node


class Player:
	
	def __init__(self, name):
		self.name = name
		self.numExpanded = 0 # Use this to track the number of nodes you expand
		self.numPruned = 0 # Use this to track the number of times you prune 
		self.lastState = None # Variable to store the state of the game after the player last played
		if name == 'X': #checks what the name of the player is
			#if the player's name is 'X' then the opponent will be 'O'
			self.opponentName = 'O'
		else:
			#if the player's name is 'O' then the opponent will be 'X'
			self.opponentName = 'X'


	def evaluatePlayerMove(self, currBoard):
		"""
		This function iterates through all possible moves that the opponent could make from the current state. If this is a 
		terminating node (a win or draw), a score for that terminating state is assigned otherwise, the information about 
		these moves of the player are returned as opponentNodes from the evaluateOpponentMove() function. All necessary 
		information is gathered and then stored within a playerNode object.

		Args:
			self (Player): The player which this function has been called from
			currBoard (Board): The current state of the board which we need to analyse 
		
		Returns:
			node (playerNode): A player node containing the score for this node, a list of all of the child opponentNodes
							   based on the moves that the opponent could make next and the move that was last played to reach
							   this node.
		"""
		node = playerNode(0) #creates a player node, with score initially 0
		node.lastMove = currBoard.lastPlay #stores the move required to get to this state as lastMove

		if currBoard.checkWin() == True: #checks whether the move just made has resulted in a win
			#if the current state is a win, the player was the last player and hence the player has won
			node.score += WINSCORE #adds the score for winning the game

		elif currBoard.checkFull() == True: #checks whether the move filled the board
			#if the board is full then there can be no subsequent moves, hence a draw
			node.score += DRAWPENALTY #adds the penalty for drawing the game

		else: #if the game will have another move afterwards
			currChildren = list() #the list of children nodes of this player node
			node.score = math.inf #sets the node score to infinity to compare with the worst child node

			for col in range(0, currBoard.numColumns): #iterates over all columns
				if currBoard.colFills[col] != currBoard.numRows: #checks whether the column is full or not
						
						currBoard.addPiece(col, self.opponentName) #adds a piece to the column as if the opponent had played
						moveState = self.evaluateOpponentMove(currBoard) #gets the information about that state
						currBoard.removePiece(col) #removes the piece from the board

						currChildren.append(moveState) #adds the new state to the list of children
			
		
			for i in range(len(currChildren)): # iterates all of the children of the node
				# in minimax we assume that the opponent will pick the worst option for us 
				# so the score of the node is the lowest score of the children
				node.score = min(node.score, currChildren[i].score) #updates the score of the node to be the worst node for the player

			node.children = currChildren #the list of the children of the node
		
		node.score += MOVEPENALTY # takes away the move penalty to encourage the shortest game path
		self.numExpanded += 1 #increments the number of nodes expanded by 1
		return node #returns the node

	


	def evaluateOpponentMove(self, currBoard):
		"""
		This function iterates through all possible moves that the player could make from the current state. If this is a terminating
		node (a win or draw, a score for that terminating state is assigned) otherwise, the information about these moves
		of the player are returned as playerNodes from the evaluatePlayerMove() function. All necessary information is 
		gathered and then stored within a opponentNode object.

		Args:
			self (Player): The player which this function has been called from
			currBoard (Board): The current state of the board which we need to analyse 
		
		Returns:
			node (opponentNode): An opponent node containing the score for this node, the last move played to get to this node
								 and the optimal playerNode for the player to reach after this node.
		"""
		node = opponentNode(0) #creates an opponent node with a starting score of 0
		node.lastMove = currBoard.lastPlay #stores the last play of this current board

		bestChildScore = -math.inf #sets the best score of a child node as -infinity
		
		if currBoard.checkWin() == True: 
			#The opponent was the last player, hence if there is a winning state then it would have been performed by the
			#opponent, as such a losing penalty should be applied.
			node.score += LOSEPENALTY #sets the node score to the losing penalty
		elif currBoard.checkFull() == True:
			#if the board is full, then no more moves can be played and it is a draw
			node.score += DRAWPENALTY #sets the node score to the draw penalty
		else:
			for col in range(0, currBoard.numColumns): #iterates over the number of columns
				if currBoard.colFills[col] != currBoard.numRows: #checks whether the column is full or not
					#if the column is not full, then a move can be made there
						
					currBoard.addPiece(col, self.name) #adds a piece to the column
					moveState = self.evaluatePlayerMove(currBoard) #gets the value of that move
					currBoard.removePiece(col) #removes the piece from the board

					if moveState.score > bestChildScore: #checks whether this move is better than the best move currently stored
						bestChildScore = moveState.score #sets the best score so far, as the score just returned
						node.bestChild = moveState #sets the state that was the best to the new state within the node

			#the next move from this node would be of the maximizing player, so the node's score is the best child of it
			node.score = node.bestChild.score #sets the score of the node as the best move that the player can make from this node

		self.numExpanded += 1 #increments the number of nodes expanded by 1
		return node #returns the node
	


	def getMove(self, gameBoard):
		"""
		This function either performs the creation of the minimax tree and then returns the best move or explores the already
		created tree to get the next best move. Each potential move is rotated through and then the move is passed onto 
		evaluatePlayerMove() to get the playerNode for that move.

		Args:
			self (Player): The player making the move
			gameBoard (Board): The current board state of the game

		Returns:
			bestMove (int): The best column to play for the player
		"""
		bestMoveScore = -math.inf #initialises the score for the best move as -infinity
		bestMove = -1 #initialises the best column to move in as -1
		bestState = None #a variable to store the best next state so far

		if self.lastState == None: #if this is the first move of the player
			for col in range (0, gameBoard.numColumns): #iterates over the number of columns
				if gameBoard.colFills[col] != gameBoard.numRows: #checks whether the column is full or not
					#if the column is not full, then a move can be made there
					
					gameBoard.addPiece(col, self.name) #adds a piece to the column
					moveState = self.evaluatePlayerMove(gameBoard) #gets the value of that move
					gameBoard.removePiece(col) #removes the piece from the board

					if moveState.score > bestMoveScore: #checks whether this move is better than the best move currently stored
						bestMoveScore = moveState.score #sets the best score so far, as the score just returned
						bestMove = col #sets the best column to move in as the column we've evaluated
						bestState = moveState #sets the best state to be current move state
			
			self.lastState = bestState # sets the last state node the player has as the node for the state it has chosen


		#if the player has made a move before (we already have explored all possibilities and simply need to find the next best score)
		else:
			#The lastState stores all of the possible moves the opponent could've made since the player last played
			for child in range(0, len(self.lastState.children)): # iterates over all of the possible children given the last move that the player made
				columnCheck = self.lastState.children[child].lastMove[1] # gets the column of where the opponent played to get this child
				rowCheck = self.lastState.children[child].lastMove[0] # gets the row of where the opponent played to get this child
				
				#we analyse the children of the lastMove to see what move the opponent made
				if str(gameBoard.checkSpace(rowCheck, columnCheck)) == self.opponentName: #checks whether there is a piece now in that spot from the opponent
					#if there is a piece in that spot, then we know the opponent moved there
					nextState = self.lastState.children[child].bestChild #defines the next state that the player should player as the best child of the current state
					self.lastState = nextState #the last state stored by the player is set to the next state we're going to move to
					bestMove = nextState.lastMove[1] # sets the column to move in as the move that would lead to nextState
					break #end the for loop
		
		return bestMove # returns the column of the next best move










	
	def evaluatePlayerMoveAB(self, currBoard, alpha, beta):
		"""
		This function intakes the current board after a play by the player has just been made. The function returns a 
		score depending on whether this new board has provided a winning or draw state, or calls evaluateOpponentMoveAB()
		to recursively return a score depending on the moves after this board state.

		Args:
			self (Player): The player that we're running the algorithm from
			currBoard (Board): The board representing the current state of the game, the player was the last player
			alpha (int): The alpha value to be used for Alpha-Beta pruning
			beta (int): The beta value to be used for Alpha-Beta pruning
		
		Returns:
			nodeScore (int): The score of the currBoard state for our player
		"""
		nodeScore = 0 #initialises the score for the node as 0

		if currBoard.checkWin() == True: #checks whether the move just made has resulted in a win
			nodeScore += WINSCORE #adds the score for winning the game

		elif currBoard.checkFull() == True: #checks whether the move filled the board
			nodeScore += DRAWPENALTY #adds the penalty for drawing the game

		else: #if the game will have another move afterwards
			nodeScore = math.inf #sets the node score to infinity to compare with the worst child node

			for col in range(0, currBoard.numColumns): #iterates over all columns
				if currBoard.colFills[col] != currBoard.numRows: #checks whether the column is full or not
					#if the column isn't full, then a move could be played there
						
					currBoard.addPiece(col, self.opponentName) #adds a piece to the column as if the opponent had played
					moveScore = self.evaluateOpponentMoveAB(currBoard, alpha, beta) #gets the information about that state
					currBoard.removePiece(col) #removes the piece from the board
			
					#the minimum score out of this new node and the current worst node since we want to check what value
					#picked by the minimizing player would be
					nodeScore = min(nodeScore, moveScore)  #updates the node score to the minimum of the children

					beta = min(beta, nodeScore)  #updates the beta value to be the worst node score considering our new node

					#if our beta value is worse than our alpha value, then this branch will never be selected and therefore can be pruned
					if alpha >= beta:  #checks whether this should be pruned 
						self.numPruned += 1 #increments the pruned counter
						break #breaks the loop if it needs to be pruned
		
		nodeScore += MOVEPENALTY # takes away the move penalty to encourage the shortest game path
		self.numExpanded += 1 #increments the number of nodes expanded by 1
		return nodeScore

	

	def evaluateOpponentMoveAB(self, currBoard, alpha, beta):
		"""
		This function intakes the current board after a play by the opponent has just been made. The function returns a score 
		depending on whether this new board has provided a winning or draw state, or calls evaluatePlayerMoveAB() to 
		recursively return a score depending on the moves after this board state.

		Args:
			self (Player): The player that we're running the algorithm from
			currBoard (Board): The board representing the current state of the game, the opponent was the last player
			alpha (int): The alpha value to be used for Alpha-Beta pruning
			beta (int): The beta value to be used for Alpha-Beta pruning
		
		Returns:
			nodeScore (int): The score of the currBoard state for our player
		"""
		nodeScore = 0 #initialises the node score as 0
		bestChildScore = -math.inf #sets the best score of a child node as -infinity
		
		if currBoard.checkWin() == True: #checks whether this board is a win state
			nodeScore += LOSEPENALTY #sets the node score to the losing penalty (the win has occurred from the opponents move)
		elif currBoard.checkFull() == True: #checks whether this board is full and hence a draw
			nodeScore += DRAWPENALTY #sets the node score to the draw penalty
		else:
			for col in range(0, currBoard.numColumns): #iterates over the number of columns
				if currBoard.colFills[col] != currBoard.numRows: #checks whether the column is full or not
					#if the column isn't full, a move could be played there
						
					currBoard.addPiece(col, self.name) # adds a piece to the column, as if from the player
					moveScore = self.evaluatePlayerMoveAB(currBoard, alpha, beta) #gets the value of that move
					currBoard.removePiece(col) #removes the piece from the board

					#the player will select the best next move
					bestChildScore = max(bestChildScore, moveScore) # updates bestChildScore to be the best 

					#updates alpha to be the optimal next move
					alpha = max(alpha, bestChildScore) #updates alpha to be the highest possible next move (what we want our player to pick)

					#if alpha is greater than beta then the minimizing player won't pick this branch
					if alpha >= beta:  #checks if alpha is greater than beta
						self.numPruned += 1 #increments the pruned counter
						break #breaks the exploration
			
			nodeScore = bestChildScore #sets the score to be the best child score

		self.numExpanded += 1 #increments the number of nodes expanded by 1
		return nodeScore #returns the score
	


	def getMoveAlphaBeta(self, gameBoard):
		"""
		This function is called to get the column where the next player should move. It iterates through all possible moves
		and passes them into evaluatePlayerMoveAB() to get a score for the best move that the player should make.

		Args:
			self (Player): The player that we are getting the next move for
			gameBoard (Board): The current state of the board
		
		Returns:
			bestMove (int): The integer value of the column where the player should move
		"""
		bestMoveScore = -math.inf #initialises the score for the best move as -infinity
		bestMove = -1 #initialises the best column to move in as -1
		alpha = -math.inf  #initialises the alpha value as negative infinity
		beta = math.inf  #initialises the beta value as infinity

		for col in range (0, gameBoard.numColumns): #iterates over the number of columns
			if gameBoard.colFills[col] != gameBoard.numRows: #checks whether the column is full or not
				#if the column is not full then it is valid to play there
					
				gameBoard.addPiece(col, self.name) #adds a piece to the column
				moveScore = self.evaluatePlayerMoveAB(gameBoard, alpha, beta) #gets the value of that move
				gameBoard.removePiece(col) #removes the piece from the board

				if moveScore > bestMoveScore: #checks whether this move is better than the best move currently stored
					bestMoveScore = moveScore #sets the best score so far, as the score just returned
					bestMove = col #sets the best column to move in as the column we've evaluated
		
				alpha = max(alpha, bestMoveScore) #updates the alpha value to be the score of the best move so far

		return bestMove #returns the column of the next best move
