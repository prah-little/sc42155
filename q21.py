#Q2.1
#on1 eqv 1, on2 eqv 2, on3 eqv 3, off1 eqv 4, off2 eqv 5, off3 eqv 6
tq21 = {
    0:{'1':1, '2':4, '3':4, '4':4, '5':4, '6':4,},
    1:{'1':4, '2':2, '3':4, '4':0, '5':4, '6':4,},
    2:{'1':4, '2':4, '3':3, '4':4, '5':1, '6':4,},
    3:{'1':4, '2':4, '3':4, '4':4, '5':4, '6':2,},
    4:{'1':4, '2':4, '3':4, '4':4, '5':4, '6':4,}
    }

def accepts(transitions,initial,s):
    state = initial
    for c in s:
        state = transitions[state][c]
    return state

test = '1236'

print(accepts(tq21,0,test))


