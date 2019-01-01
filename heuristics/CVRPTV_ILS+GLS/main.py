import cvrptw

problems = ['instances/C108.txt', 'instances/C203.txt', 'instances/C249.TXT', 'instances/C266.TXT', 'instances/R146.TXT',
            'instances/R168.TXT', 'instances/R202.txt', 'instances/RC105.txt', 'instances/RC148.TXT', 'instances/RC207.txt']
for problem in problems:
    cvrptw.solve(problem, 3*60*60)
