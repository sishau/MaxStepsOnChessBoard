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

def repair_chess_seq(chess_seq):
    actual_A = chess_seq.count("A")
    actual_B = chess_seq.count("B")
    actual_C = chess_seq.count("C")
    num_A_to_replace, num_B_to_replace, num_C_to_replace = 0, 0, 0
    replacements = []
    if actual_A < chess_countr["A"]:
        replacements.extend(["A"] * (chess_countr["A"] - actual_A))
    elif actual_A > chess_countr["A"]:
        num_A_to_replace = actual_A - chess_countr["A"]
    if actual_B < chess_countr["B"]:
        replacements.extend(["B"] * (chess_countr["B"] - actual_B))
    elif actual_B > chess_countr["B"]:
        num_B_to_replace = actual_B - chess_countr["B"]
    if actual_C < chess_countr["C"]:
        replacements.extend(["C"] * (chess_countr["C"] - actual_C))
    elif actual_C > chess_countr["C"]:
        num_C_to_replace = actual_C - chess_countr["C"]
    if replacements:
        random.shuffle(replacements)

    for idx in reversed(range(len(chess_seq))):
        if chess_seq[idx] == "A" and num_A_to_replace > 0:
            chess_seq[idx] = replacements.pop()
            num_A_to_replace -= 1
        elif chess_seq[idx] == "B" and num_B_to_replace > 0:
            chess_seq[idx] = replacements.pop()
            num_B_to_replace -= 1
        elif chess_seq[idx] == "C" and num_C_to_replace > 0:
            chess_seq[idx] = replacements.pop()
            num_C_to_replace -= 1
        if num_A_to_replace == 0 and num_B_to_replace == 0 and num_C_to_replace == 0:
            break
    if replacements:
        chess_seq.extend(replacements)
    return chess_seq

def crossover(parent1, parent2, chessboard_size):
    # Crossover start position and angle
    child_start_pos = (
        random.choice([parent1.start_pos[0], parent2.start_pos[0]]),
        random.choice([parent1.start_pos[1], parent2.start_pos[1]])
    )
    child_start_angle = random.choice([parent1.start_angle, parent2.start_angle])

    # Partial chess sequence crossover (swap middle section)
    # Ensure chess sequence constraints are maintained
    max_length = len(parent1.chess_seq)
    parent1_end_index = min(parent1.fitness, max_length)
    parent2_end_index = min(parent2.fitness, max_length)
    delta = 0
    if parent1_end_index + parent2_end_index > max_length:
        delta = (parent1_end_index + parent2_end_index - max_length + 1 ) // 2
    # print(f"Parent 1: {parent1_end_index}, Parent 2: {parent2_end_index}, delta: {delta}, Parent length: {max_length}")
    child_chess_seq = parent1.chess_seq[:parent1_end_index-delta] + parent2.chess_seq[delta:parent2_end_index]

    # Repair the chess sequence to maintain counts (this is a placeholder for actual repair logic)
    repair_chess_seq(child_chess_seq)
    # Flip sequence crossover
    child_flip_seq = parent1.flip_seq[:parent1_end_index] + parent2.flip_seq[delta:parent2_end_index]
    # Repair the flip sequence
    if len(child_flip_seq) < len(parent1.flip_seq):
        child_flip_seq.extend([random.getrandbits(1) for _ in range(len(parent1.flip_seq) - len(child_flip_seq))])
    elif len(child_flip_seq) > len(parent1.flip_seq):
        child_flip_seq = child_flip_seq[:len(parent1.flip_seq)]
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
    elite_size = 20  # Number of elite individuals to carry over

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
            child = crossover(parent1, parent2, chessboard_size)
            mutate(child, mutation_rate)
            child.calculate_fitness(chessboard_size)
            new_population.append(child)
        # Replace population
        population = new_population

        # Get best individual
        best_individual = max(population, key=lambda x: x.fitness)
        # print(f"Best Fitness: {best_individual.fitness}, Start Pos: {best_individual.start_pos}, Start Angle: {best_individual.start_angle}")

    return max(population, key=lambda x: x.fitness)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    def GeneticAlgorithm(population_size, max_generations):
        best = genetic_algorithm(population_size, max_generations)
        logging.info(f"Start Position: {best.start_pos}, Start Angle: {best.start_angle}")
        # Optionally print chess sequence and flip sequence
        logging.info(f"Chess Sequence: {best.chess_seq}, Flip Sequence: {best.flip_seq}")
        logging.info(best.board)
        logging.info(f"Steps: {best.fitness}, population_size: {population_size}, max_generations: {max_generations}")


    for polulation_size in range(500, 800, 100):
        for max_generations in range(500, 800, 100):
            GeneticAlgorithm(polulation_size, max_generations)
