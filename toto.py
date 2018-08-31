def carre(num):
    for k in num:
        yield (k**2)

num=carre([1,2,3,4,5,6])

for i in num:
    print(i)
