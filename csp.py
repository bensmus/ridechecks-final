from typing import Dict, List, Tuple
from constraint import *
from itertools import combinations
import yaml


def all_subsets(lst):
    subsets = []
    for i in range(len(lst) + 1):
        subsets.extend(combinations(lst, i))
    return subsets


def total_ride_times(rides: List[str], rides_time: Dict[str, int]):
    total = 0
    for ride in rides:
        total += rides_time[ride]
    return total


def csp_solution(worker_time: int, rides_time: Dict[str, int], workers_can_check: Dict[str, List[str]]) -> Dict[str, Tuple[str, ...]] | None:
    problem = Problem(MinConflictsSolver())
    for worker in workers_can_check:
        problem.addVariable(worker, all_subsets(workers_can_check[worker]))
        problem.addConstraint(lambda rides: total_ride_times(rides, rides_time) <= worker_time, [worker])
    
    def union_constraint(*many_rides):
        assigned_rides = set()
        for rides in many_rides:
            assigned_rides.update(rides)
        return assigned_rides == set(rides_time.keys())
    
    problem.addConstraint(union_constraint, workers_can_check.keys())
    solution = problem.getSolution()
    return solution


def to_ride_assignment(solution: Dict[str, Tuple[str, ...]]):
    # Removes duplicate ridechecks as well,
    # since solution produced:
    # {'Alan': ('Breakdance', 'Dizzy drop', 'Flutterbye'), 'Bill': ('Breakdance',) ...}

    # Sort solution to put people with many assignments first: (this will distribute work more evenly)
    solution = dict(sorted(solution.items(), key=lambda item: len(item[1]), reverse=True))

    ride_assignment = {}
    for worker, rides in solution.items():
        for ride in rides:
            ride_assignment[ride] = worker
    return dict(sorted(ride_assignment.items()))


if __name__ == '__main__':
    # worker_time = 20
    # rides_time = {
    #     'wooden': 10,
    #     'scary': 20,
    #     'slow': 1,
    #     'fast': 5
    # }
    # workers_can_check = {
    #     'john': ['wooden', 'fast', 'scary', 'slow'],
    #     'bob': ['scary', 'slow'],
    # }
    with open('realistic_state.yaml') as f:
            yaml_data = yaml.safe_load(f)
    
    rides_time: Dict[str, int] = yaml_data['Ride Times']
    workers_can_check: Dict[str, List[str]] = yaml_data['Worker Permissions']
    # week_info = yaml_data['Weekly Info']

    # print(rides_time)
    # print(workers_can_check)
    
    solution = csp_solution(240, rides_time, workers_can_check)
    ride_assignment = to_ride_assignment(solution)
    print(solution)
    print('---')
    print(ride_assignment)
