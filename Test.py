# Define a dictionary to store the values
d = {}

# Iterate through each number from 1 to 9
for i in range(1, 3):
    for j in range(1, 8):
        # Create a tuple for each possible combination
        pair = (i, j)
        
        # Determine the value for the combination using conditional statements
        if i == j:
            value = 0
        else:
            value=50
        
        d[pair] = value
print(d)


