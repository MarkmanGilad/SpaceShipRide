import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

def plot_normal_distribution(mu, sigma, label):
    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 100)
    y = norm.pdf(x, mu, sigma)
    plt.plot(x, y, label=label)

# Plot multiple distributions
plt.figure(figsize=(8, 6))
plot_normal_distribution(0, 1, 'Mean=0, Std=1')
plot_normal_distribution(2, 1, 'Mean=2, Std=1')
plot_normal_distribution(0, 2, 'Mean=0, Std=2')

plt.xlabel('x')
plt.ylabel('Probability Density')
plt.title('Comparison of Normal Distributions')
plt.legend()
plt.grid()
plt.show()