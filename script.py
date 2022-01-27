import pickle
import time

import ray
from pyscipopt import Model, quicksum

start_time = time.time()

ray.init(address="auto")


@ray.remote
def solve_instance(data):
    model = Model("CLSP")

    ######### define decision variables #########
    X, Y, I = {}, {}, {}

    # lot size of product j in period t
    for j in data["products"]:
        for t in data["periods"]:
            X[j, t] = model.addVar(vtype="C", name=f"X_{j,t}")

    # 1, if a setup for product j takes place in period t, 0 otherwise
    for j in data["products"]:
        for t in data["periods"]:
            Y[j, t] = model.addVar(vtype="B", name=f"B_{j,t}")

    # inventory of product j at the end of period t
    for j in data["products"]:
        for t in data["periods"]:
            I[j, t] = model.addVar(vtype="C", name=f"I_{j,t}")

    ######### define constraints #########

    # inventory balance
    for j in data["products"]:
        for t in data["periods"]:
            if t == 0:
                model.addCons(I[j, t] == X[j, t] - data["demand"][j, t])
            else:
                model.addCons(I[j, t] == I[j, t - 1] + X[j, t] - data["demand"][j, t])

    # machine setups
    for j in data["products"]:
        for t in data["periods"]:
            model.addCons(X[j, t] <= data["capacity"] * Y[j, t])

    # machine capacity
    for t in data["periods"]:
        model.addCons(
            quicksum(
                data["production_coefficient"][j] * X[j, t] for j in data["products"]
            )
            <= data["capacity"]
        )

    ######### objective function #########
    model.setObjective(
        quicksum(
            data["holding_cost"][j] * I[j, t] + data["setup_cost"][j] * Y[j, t]
            for j in data["products"]
            for t in data["periods"]
        ),
        "minimize",
    )

    model.optimize()
    total_time = model.getTotalTime()
    gap = model.getGap()
    return total_time, gap


with open("data/data.p", "rb") as fp:
    data = pickle.load(fp)


obj_refs = [solve_instance.remote(data) for i in range(100)]
results = ray.get(obj_refs)

time.sleep(0.1)

print("\n")
for i, result in enumerate(results):
    print(f"EXPERIMENT {i}: total time = {result[0]} seconds, gap = {result[1]*100}%")

print("\n")
print(f"Runtime parallel execution= {time.time() - start_time} seconds \n")
print(
    f"Runtime sequential execution  = {sum(result[0] for result in results)} seconds \n"
)
