





a = [1,2,3,4]
b = [4,5,6,7]



if __name__=="__main__":

    sum = sum([x+y for x,y in zip(a,b)])
    print(sum)
