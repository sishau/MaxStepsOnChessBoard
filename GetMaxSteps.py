import random
from lib.libChess import ChessBoard

chess_countr = {"A": 10, "B": 10, "C": 8}

class Individual:
    def __init__(self, start_pos, start_angle, chess_seq, flip_seq):
        self.start_pos = start_pos  # (x, y)
        self.start_angle = start_angle  # 0-7
        self.chess_seq = chess_seq  # list of chess types
        self.flip_seq = flip_seq  # list of booleans
        self.fitness = 0

    def calculate_fitness(self, chessboard_size):
        # Create a new chessboard for each fitness calculation
        self.board = ChessBoard(size=chessboard_size)
        steps = self.board.count_steps(self.start_pos, self.start_angle, self.chess_seq.copy(), self.flip_seq.copy())
        self.fitness = steps
        return steps

def generate_population(population_size, chessboard_size):
    population = []
    base_chess = ["A"] * chess_countr["A"] + ["B"] * chess_countr["B"] + ["C"] * chess_countr["C"]
    max_x, max_y = chessboard_size
    for _ in range(population_size):
        # Random start position
        x = random.randint(0, max_x - 1)
        y = random.randint(0, max_y - 1)
        start_pos = (x, y)
        # Random start angle
        start_angle = random.randint(0, 7)
        # Randomly shuffled chess sequence
        chess_seq = base_chess.copy()
        random.shuffle(chess_seq)
        # Random flip sequence
        flip_seq = [random.getrandbits(1) for _ in range(len(base_chess))]
        # Create individual
        population.append(Individual(start_pos, start_angle, chess_seq, flip_seq))
    return population

def selection(population, num_parents):
    # Tournament selection
    parents = []
    for _ in range(num_parents):
        candidates = random.sample(population, 5)  # Tournament size 5
        parents.append(max(candidates, key=lambda x: x.fitness))
    return parents

def repair_chess_seq(chess_seq, flip_seq):
    actual_A = chess_seq.count("A")
    actual_B = chess_seq.count("B")
    actual_C = chess_seq.count("C")

    num_A_to_remove = actual_A - chess_countr["A"] if actual_A > chess_countr["A"] else 0
    num_B_to_remove = actual_B - chess_countr["B"] if actual_B > chess_countr["B"] else 0
    num_C_to_remove = actual_C - chess_countr["C"] if actual_C > chess_countr["C"] else 0

    for idx in reversed(range(len(chess_seq))):
        if chess_seq[idx] == "A" and num_A_to_remove > 0:
            chess_seq.pop(idx)
            flip_seq.pop(idx)
            num_A_to_remove -= 1
        elif chess_seq[idx] == "B" and num_B_to_remove > 0:
            chess_seq.pop(idx)
            flip_seq.pop(idx)
            num_B_to_remove -= 1
        elif chess_seq[idx] == "C" and num_C_to_remove > 0:
            chess_seq.pop(idx)
            flip_seq.pop(idx)
            num_C_to_remove -= 1
        if num_A_to_remove == 0 and num_B_to_remove == 0 and num_C_to_remove == 0:
            break

    replacements = []
    actual_A = chess_seq.count("A")
    actual_B = chess_seq.count("B")
    actual_C = chess_seq.count("C")
    if actual_A < chess_countr["A"]:
        replacements.extend(["A"] * ( chess_countr["A"] - actual_A))
    if actual_B < chess_countr["B"]:
        replacements.extend(["B"] * ( chess_countr["B"] - actual_B))
    if actual_C < chess_countr["C"]:
        replacements.extend(["C"] * ( chess_countr["C"] - actual_C))

    random.shuffle(replacements)
    chess_seq.extend(replacements)
    flip_seq.extend([random.getrandbits(1) for _ in range(len(replacements))])
    return chess_seq, flip_seq

def crossover(parent1, parent2):
    # Crossover start position and angle
    child_start_pos = (
        random.choice([parent1.start_pos[0], parent2.start_pos[0]]),
        random.choice([parent1.start_pos[1], parent2.start_pos[1]])
    )
    child_start_angle = random.choice([parent1.start_angle, parent2.start_angle])

    # Partial chess sequence crossover (swap middle section)
    # Ensure chess sequence constraints are maintained
    parent1_valid_length = min(parent1.fitness, len(parent1.chess_seq))
    parent2_valid_length = min(parent2.fitness, len(parent2.chess_seq))
    cross_point1 = random.randint(0, parent1_valid_length)
    cross_point2 = random.randint(0, parent2_valid_length)
    child_chess_seq = parent1.chess_seq[:cross_point1] + parent2.chess_seq[:cross_point2]
    child_flip_seq = parent1.flip_seq[:cross_point1] + parent2.flip_seq[:cross_point2]

    # Repair the chess sequence to maintain counts (this is a placeholder for actual repair logic)
    child_chess_seq, child_flip_seq = repair_chess_seq(child_chess_seq, child_flip_seq)
    return Individual(child_start_pos, child_start_angle, child_chess_seq, child_flip_seq)

def mutate(individual, mutation_rate):
    # Mutate start position
    if random.random() < mutation_rate:
        individual.start_pos = (random.randint(0, 5), individual.start_pos[1])
    if random.random() < mutation_rate:
        individual.start_pos = (individual.start_pos[0], random.randint(0, 5))
    # Mutate start angle
    if random.random() < mutation_rate * 2:
        individual.start_angle = random.randint(0, 7)
    # Mutate chess sequence by swapping two random elements
    if random.random() < mutation_rate * 2:
        i, j = random.sample(range(len(individual.chess_seq)), 2)
        individual.chess_seq[i], individual.chess_seq[j] = individual.chess_seq[j], individual.chess_seq[i]
    # Mutate flip sequence
    for i in range(len(individual.flip_seq)):
        if random.random() < mutation_rate * 2:
            individual.flip_seq[i] = not individual.flip_seq[i]

def genetic_algorithm(population_size=100, max_generations=100):
    chessboard_size = (6, 6)
    mutation_rate = 0.4
    elite_size = population_size // 10  # Number of elite individuals to carry over
    best_fitness = 0
    best_Gen =  0

    # Initialize population
    population = generate_population(population_size, chessboard_size)
    for individual in population:
        individual.calculate_fitness(chessboard_size)

    for generation in range(max_generations):
        # print(f"Generation {generation + 1}")
        # Select parents
        parents = selection(population, population_size - elite_size)
        # Create next generation
        new_population = []
        # Elite individuals
        sorted_population = sorted(population, key=lambda x: x.fitness, reverse=True)
        elites = sorted_population[:elite_size]
        new_population.extend(elites)

        # Generate offspring
        for _ in range(population_size - elite_size):
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = crossover(parent1, parent2)
            mutate(child, mutation_rate)
            child.calculate_fitness(chessboard_size)
            new_population.append(child)
        # Replace population
        population = new_population

        # Get best individual
        best_individual = max(population, key=lambda x: x.fitness)
        # print(f"Best Fitness: {best_individual.fitness}, Start Pos: {best_individual.start_pos}, Start Angle: {best_individual.start_angle}")
        if best_individual.fitness > best_fitness:
            best_fitness = best_individual.fitness
            best_Gen = generation

    print(f"Best Fitness: {best_fitness}, Generation: {best_Gen} / {max_generations}, population size: {population_size}")
    return max(population, key=lambda x: x.fitness)

if __name__ == '__main__':
    import logging

    file_path = "./best.txt"
    best_fitness = 0
    # best, index = GeneticAlgorithm(100, 1000)
    # print(f"best fitness: {best.fitness}, index: {index} / 1000 \n {best.board}")
    for population_size in range(1000, 5000, 500):
        for max_generations in range(1500, 5000, 200):
            best = genetic_algorithm(population_size, max_generations)
            if best.fitness > best_fitness:
                best_fitness = best.fitness
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(str(best.board) + "\n")
                    f.write(str(best.fitness) +" \n\n")

