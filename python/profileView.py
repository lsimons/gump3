import pstats
p = pstats.Stats('iprof')

p.sort_stats('cumulative').print_stats()


