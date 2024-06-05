"""
SOD
type=library
name=random
needsinit=false
EOD
"""
state = realtime()

def seed(sed):
    global state
    state = sed

def random(min_, max_):
    global state
    rnd = state * 58375838583 / 483867375 // 1 % (2**32-1)
    state = rnd
    rnd /= (2**32-1)
    rnd *= (max_ - min_)
    rnd += min_
    return int(rnd)
