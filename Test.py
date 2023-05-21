# Define a dictionary to store the values
d = {}
demandl = [40,30,10,20,42]
nodes = [1,2,3]
# Iterate through each number from 1 to 9

def demand(node, demandlist):
    d = {}
    for i in range(1,len(nodes)+1)
        for j in range(1, len(demandlist)+1): #times
            # Create a tuple for each possible combination
            pair = (node, j)
            
            # Determine the value for the combination using conditional statements
            value = demandlist[j-1]
                
            d[pair] = value
    
    return d

print(demand(1, demandl))



#Generate 5 random numbers between 10 and 30
print(randomlist)
