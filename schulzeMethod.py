from condorcet import CondorcetSystem
from pygraph.classes.digraph import digraph
from pygraph.algorithms.accessibility import accessibility, mutual_accessibility
class SchulzeMethod(CondorcetSystem):
    
    @staticmethod
    def calculateWinner(ballots):
        result = CondorcetSystem.calculateWinner(ballots)
        
        # If there's a Condorcet winner, return it
        if "winners" in result:
            return result
        
        # Initialize the candidate graph
        candidateGraph = digraph()
        candidateGraph.add_nodes(list(result["candidates"]))
        for pair in result["strongPairs"].keys():
            candidateGraph.add_edge(pair[0], pair[1], result["strongPairs"][pair])
        
        # Iterate through using the Schwartz set heuristic
        result["actions"] = []
        candidates = result["candidates"].copy()
        while len(candidateGraph.edges()) > 0:
            
            # Remove nodes at the end of non-cycle paths
            access = accessibility(candidateGraph)
            mutualAccess = mutual_accessibility(candidateGraph)
            candidatesToRemove = set()
            for candidate in candidates:
                candidatesToRemove = candidatesToRemove | (set(access[candidate]) - set(mutualAccess[candidate]))
            if len(candidatesToRemove) > 0:
                result["actions"].append(['nodes', candidatesToRemove])
                for candidate in candidatesToRemove:
                    candidateGraph.del_node(candidate)
                    candidates.remove(candidate)

            # If none exist, remove the weakest edges
            else:
                lightestEdges = set([candidateGraph.edges()[0]])
                weight = candidateGraph.edge_weight(candidateGraph.edges()[0][0], candidateGraph.edges()[0][1])
                for edge in candidateGraph.edges():
                    if candidateGraph.edge_weight(edge[0], edge[1]) < weight:
                        weight = candidateGraph.edge_weight(edge[0], edge[1])
                        lightestEdges = set([edge])
                    elif candidateGraph.edge_weight(edge[0], edge[1]) == weight:
                        lightestEdges.add(edge)
                result["actions"].append(['edges', lightestEdges])
                for edge in lightestEdges:
                    candidateGraph.del_edge(edge[0], edge[1])
        
        # Mark the winner
        if len(candidateGraph.nodes()) == 1:
            result["winners"] = candidateGraph.nodes()[0]
        else:
            result["tiedWinners"] = set(candidateGraph.nodes())
            result["tieBreaker"] = SchulzeMethod.generateTieBreaker(result["candidates"])
            result["winners"] = set([SchulzeMethod.breakWinnerTie(candidateGraph.nodes(), result["tieBreaker"])])
        
        # Return the final result
        return result