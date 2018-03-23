import json

#Some functions for loading description information from the WATCHMVAKERS
#database for running

def loadVariableDescriptions(variable_array,variable_db):
    loaded_variables = {} 
    for var in variables:
        if variables[var] in variable_db:
            loaded_variables[var] = variable_db[var]
    return loaded_variables
