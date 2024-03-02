import numpy as np
import matplotlib.pyplot as plt
np.random.seed(77)

num_trials = 10000
criteria = [1, 3, 5, 10]

def simulate(n, m, s):
    candidates = np.random.permutation(n) + 1
    # print(candidates)
    standard = np.min(candidates[:m]) if m > 0 else 0
    for candidate in candidates[m:]:
        if candidate < standard:
            return candidate <= s
    return candidates[-1] <= s

def success_rate(n, m, s, num_trials=num_trials):
    return np.mean([simulate(n, m, s) for _ in range(num_trials)])

if __name__ == "__main__":
    n = 100
    for s in criteria:
        success_rates = [success_rate(n, m, s) for m in range(n)]
        plt.plot(success_rates, label=f's={s}')
    plt.xlabel('Sample size, m')
    plt.ylabel('Success rate')
    plt.legend()
    plt.savefig("1805077_Problem_2_Output.png")
    plt.close()