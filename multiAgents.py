# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random

import util
from game import Agent, Directions  # noqa
from util import manhattanDistance  # noqa


class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        foodPos = newFood.asList()
        foodCount = len(foodPos)
        ghostCount = len(newGhostStates)
        distance = float('inf')
        ghostPos = successorGameState.getGhostPositions()

        if foodCount == 0:
          distance = 0
        else:
          for foods in foodPos:
            distance = min(distance, manhattanDistance(foods,newPos))
        score = -(distance + foodCount*50)

        for i in range(ghostCount):
          exactPos = ghostPos[i]
          if manhattanDistance(newPos, exactPos) <= 1 :
            score = -float('inf')

        return score
        


def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn="scoreEvaluationFunction", depth="2"):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game
        """
        "*** YOUR CODE HERE ***"
        numAgent = gameState.getNumAgents()
        allStatesSaved = []
        someMoreSavedStuff = []

        def miniMaxer(gS, curDepth, agentID):
          if agentID >= numAgent:
            agentID = 0
            curDepth += 1

          #reached the bottom od the tree
          if gS.isWin() or gS.isLose() or curDepth >= self.depth:
            return self.evaluationFunction(gS)

          #maximizer aka pacman
          if agentID == 0:
            result = -float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = max(result, miniMaxer(succs, curDepth, agentID+1))
              if curDepth == 0 and agentID == 0:
                allStatesSaved.append(result)
                someMoreSavedStuff.append(moves)
            return result

          #minimizer aka ghosts
          else:
            result = float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = min(result, miniMaxer(succs, curDepth, agentID+1))
            return result

        finalAns = miniMaxer(gameState, 0, 0)
        return someMoreSavedStuff[allStatesSaved.index(max(allStatesSaved))]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        numAgent = gameState.getNumAgents()
        allStatesSaved = []
        someMoreSavedStuff = []
        smallestSeen = float('inf')
        largestSeen = -float('inf')

        def alphaGo(gS, curDepth, agentID, smallestSeen, largestSeen):
          if agentID >= numAgent:
            agentID = 0
            curDepth += 1

          #reached the bottom od the tree
          if gS.isWin() or gS.isLose() or curDepth >= self.depth:
            return self.evaluationFunction(gS)

          #maximizer aka pacman
          if agentID == 0:
            result = -float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = max(result, alphaGo(succs, curDepth, agentID+1, smallestSeen, largestSeen))
              largestSeen = max(result, largestSeen)
              if curDepth == 0 and agentID == 0:
                allStatesSaved.append(result)
                someMoreSavedStuff.append(moves)
              if largestSeen >= smallestSeen:
                break
            return result

          #minimizer aka ghosts
          else:
            result = float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = min(result, alphaGo(succs, curDepth, agentID+1, smallestSeen, largestSeen))
              smallestSeen = min(result, smallestSeen)
              if smallestSeen <= largestSeen:
                break
            return result

        finalAns = alphaGo(gameState, 0, 0, smallestSeen, largestSeen)
        return someMoreSavedStuff[allStatesSaved.index(max(allStatesSaved))]


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        numAgent = gameState.getNumAgents()
        allStatesSaved = []
        someMoreSavedStuff = []

        def expectiMaxer(gS, curDepth, agentID):
          if agentID >= numAgent:
            agentID = 0
            curDepth += 1

          #reached the bottom od the tree
          if gS.isWin() or gS.isLose() or curDepth >= self.depth:
            return self.evaluationFunction(gS)

          #maximizer aka pacman
          if agentID == 0:
            result = -float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = max(result, expectiMaxer(succs, curDepth, agentID+1))
              if curDepth == 0 and agentID == 0:
                allStatesSaved.append(result)
                someMoreSavedStuff.append(moves)
            return result

          #minimizer aka ghosts
          else:
            avger = []
            result = float('inf')
            validMoves = gS.getLegalActions(agentID)
            for moves in validMoves:
              succs = gS.generateSuccessor(agentID, moves)
              result = expectiMaxer(succs, curDepth, agentID+1)
              avger.append(result)
            return sum(avger)/len(avger)

        finalAns = expectiMaxer(gameState, 0, 0)
        return someMoreSavedStuff[allStatesSaved.index(max(allStatesSaved))]


def betterEvaluationFunction(currentGameState):



  newPos = currentGameState.getPacmanPosition()
  newFood = currentGameState.getFood()
  currScore = currentGameState.getScore()
  foodPos = newFood.asList()
  distance = []
  capsuleScores = []
  ghostPos = currentGameState.getGhostPositions()
  ghostCount = len(ghostPos)
  foodCount = len(foodPos)
  ghostStates = currentGameState.getGhostStates()
  capsulLocs = currentGameState.getCapsules()

  
  for foods in foodPos:
    distance.append(1/(manhattanDistance(foods,newPos)))

  if not distance:
    distance.append(0)
  score = max(distance)
  
  for capsule in capsulLocs:
    capsuleScores.append(40/manhattanDistance(newPos, capsule))

  if not capsuleScores:
    capsuleScores.append(0)
  score += max(capsuleScores)


  for i in range(ghostCount):
    exactPos = ghostPos[i]
    ghostDist = manhattanDistance(newPos, exactPos)
    if ghostStates[i].scaredTimer > 0:
      testerVar = 8-ghostDist
      if testerVar >= 0:
        score += pow(testerVar, 2)
    else:
      testerVar = 7-ghostDist
      if testerVar >= 0:
        score -= pow(testerVar, 2)




  finalAns = currScore + score
  
  return finalAns



# Abbreviation
better = betterEvaluationFunction
