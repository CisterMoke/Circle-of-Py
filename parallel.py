import physics as ph
from concurrent.futures import ProcessPoolExecutor, as_completed


def init_pool(pool: ProcessPoolExecutor):
    verts = [(0, 0)] * 50
    pool.map(ph.bigger_norm, zip(verts, verts))
    return


def interact(pair_list, pool: ProcessPoolExecutor):
    futures = [pool.submit(ph.interact, *pair) for pair in pair_list]
    results = as_completed(futures)
    return results
