import json

#Some functions for loading description information from the WATCHMVAKERS
#database for running

def loadPairVariableDescriptions(variable_dict,variable_db):
    loaded_variables = {"variables": {"prompt": {}, "delayed":{},"interevent": {}},
            "spectators": {"prompt": {}, "delayed": {},"interevent": {}}}
    for specorvar in variable_dict:
        for vartype in variable_dict[specorvar]:
            for var in variable_dict[specorvar][vartype]:
                if var in variable_db:
                    print(var)
                    print(loaded_variables)
                    loaded_variables[specorvar][vartype][var] = variable_db[var]
                else:
                    print("A variable chosen in variables config is not supported. exiting")
                    sys.exit(0)
    return loaded_variables

def loadSinglesVariableDescriptions(variable_dict,variable_db):
    loaded_variables = {"variables": {},
            "spectators": {}}
    for specorvar in variable_dict:
        for var in variable_dict[specorvar]:
            print(var)
            if var in variable_db:
                loaded_variables[specorvar][var] = variable_db[var]
            else:
                print("A variable chosen in variables config is not supported. exiting")
                sys.exit(0)
    return loaded_variables
