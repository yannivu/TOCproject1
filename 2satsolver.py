import csv
import time
import matplotlib.pyplot as plt

# Function to read the CNF file in 2-SAT format
def readCnf(filePath):
    # Dictionaries to store problems and answer keys
    problems = {} 
    answers = {} 

    with open(filePath, newline='', encoding='utf-8-sig') as file:
        csvFile = csv.reader(file)
        
        currProblem = None  # Variable to track the current problem number
        for line in csvFile:
            # Parse comment line
            if line[0] == 'c':  
                currProblem = int(line[1])  # Extract the current problem number
                problems[currProblem] = []  # Initialize a list of clauses for this problem
                if line[3] == 'S':
                    answers[currProblem] = 'SATISFIABLE'
                elif line[3] == 'U':
                    answers[currProblem] = 'UNSATISFIABLE'
                else:
                    answers[currProblem] = 'UNKNOWN'
                    
                continue
            
            # Ignore problem line
            elif line[0] == 'p':
                continue
            
            # Parse clause lines and add to the current problem
            else:
                clause = []
                for x in line:
                    if x == '0':  # '0' marks the end of a clause
                        break
                    if x:  # Skip empty strings to handle trailing commas in CSV
                        clause.append(int(x))  # Convert string to integer and add to clause
                
                if currProblem is not None:
                    problems[currProblem].append(clause)  # Add the clause to the current problem's clauses
    
    return problems, answers

# Class implementing the DPLL algorithm
class DPLL:
    def __init__(self, cnf):
        # Initialize CNF by removing duplicate clauses
        cnfList = list(cnf)
        self.cnf = []
        for item in cnfList:
            if item not in self.cnf:
                self.cnf.append(list(item))

        # Get all unique literals
        self.literals = set(abs(i) for clause in self.cnf for i in clause)

    def solve(self):
        # Call the DPLL algorithm with the CNF and literals
        return self.dpll(self.cnf, list(self.literals))

    def dpll(self, cnf, literals):
        # Unit propagation
        while True:
            unitClauses = [c for c in cnf if len(c) == 1]
            if not unitClauses:
                break
            for unit in unitClauses:
                cnf, literals = self.unitPropagation(cnf, literals, unit[0])

        # Empty clause exists, problem is unsatisfiable
        if [] in cnf:
            return False

        # No more clauses, problem is satisfiable
        if not cnf:
            return True

        # Pick the first literal
        chosenLiteral = literals.pop()

        # Try with positive and negative literal
        return (self.dpll(self.reduced(cnf, chosenLiteral), literals[:]) or
                self.dpll(self.reduced(cnf, -chosenLiteral), literals[:]))

    def unitPropagation(self, cnf, literals, unitLiteral):
        newCNF = []
        for clause in cnf:
            if unitLiteral in clause:
                continue  # Satisfiable
            if -unitLiteral in clause:
                newClause = [l for l in clause if l != -unitLiteral]
                newCNF.append(newClause)
            else:
                newCNF.append(clause)

        # Remove literal and its negation from the set of literals
        literals = [l for l in literals if l != abs(unitLiteral)]
        return newCNF, literals

    # Assign literal to true and reduce CNF
    def reduced(self, cnf, literal):
        newCNF = []
        for clause in cnf:
            if literal in clause:
                continue  # Satisfiable
            if -literal in clause:
                # Remove negation of literal from the clause
                newClause = [l for l in clause if l != -literal]
                newCNF.append(newClause)
            else:
                newCNF.append(clause)
        return newCNF

# Main function with timing and plotting
def main():
    fileName = input("Enter the CSV file name: ")
    problems, answers = readCnf(fileName)

    # Initialize lists for graphing
    sizes = []
    times = []
    results = []

    with open(f"{fileName}_solved.txt", "w") as resultFile:
        for problemId, clauses in problems.items():
            dpll = DPLL(clauses)
            
            # Start timer
            start_time = time.time()
            result = dpll.solve()
            elapsed_time = time.time() - start_time
            
            # Problem size and result recording
            problem_size = len(clauses)
            sizes.append(problem_size)
            times.append(elapsed_time)
            results.append(result)

            # Write result to file
            if result:
                resultFile.write(f"Problem {problemId}: SATISFIABLE ({elapsed_time} seconds)\n")
            else:
                resultFile.write(f"Problem {problemId}: UNSATISFIABLE ({elapsed_time} seconds)\n")
            resultFile.write(f"ANSWER KEY: {answers[problemId]}\n")
            resultFile.write("\n")
            
            print(f"Problem {problemId} solved in {elapsed_time:.4f} seconds.")

    # Plotting the results
    plt.figure(figsize=(10, 6))

    # Plot SATISFIABLE as blue circles and UNSATISFIABLE as red triangles
    for i in range(len(sizes)):
        if results[i]:  # SATISFIABLE
            plt.scatter(sizes[i], times[i], color='blue', label='SATISFIABLE' if i == 0 else "", marker='o')
        else:  # UNSATISFIABLE
            plt.scatter(sizes[i], times[i], color='red', label='UNSATISFIABLE' if i == 0 else "", marker='^')

    # Set labels and title
    plt.xlabel('Problem Size (Number of Clauses)')
    plt.ylabel('Execution Time (seconds)')
    plt.title('Execution Time vs. Problem Size for 2-SAT Solver')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()