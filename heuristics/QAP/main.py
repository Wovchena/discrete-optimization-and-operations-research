import qap
probs = ["tai20a", "tai40a", "tai60a", "tai80a", "tai100a"]
for p in probs:
    qap.evolve(p, 60 * 30)
