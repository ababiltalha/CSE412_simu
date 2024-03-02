import numpy as np
np.random.seed(77)

num_trials = 10000
num_generations = 10

def probability():
    p = []
    p.append(0)
    sum = 0
    for i in range(1, 4):
        p.append(0.2126 * 0.5893 ** (i - 1))
        sum += p[i]
    p[0] = 1 - sum
    return p

def simulate(num_generations, num_trials, p):    
    neutrons = np.zeros((num_generations + 1, num_trials))

    for trial in range(num_trials):
        neutrons[0, trial] = 1
        for generation in range(1, num_generations + 1):
            for _ in range(int(neutrons[generation - 1, trial])):
                neutrons[generation, trial] += np.random.choice([0, 1, 2, 3], p=p)

    probabilities = np.zeros((num_generations + 1, 5))
    for generation in range(num_generations + 1):
        for j in range(5):
            probabilities[generation, j] = np.sum(neutrons[generation, :] == j) / num_trials
    
    return probabilities

def generate_results(probabilities):
    result = ''
    for i in range(1, probabilities.shape[0]):
        result += f'Generation-{i}:\n'
        for j in range(probabilities.shape[1]):
            result += f'p[{j}] = {probabilities[i][j]}\n'
        result += '\n'
    
    return result

if __name__ == '__main__':
    p = probability()
    probabilities = simulate(num_generations, num_trials, p)
    results = generate_results(probabilities)
    with open('1805077_Problem_1_Output.txt', 'w') as file:
        file.write(results)
    # print(results)
    
    
    