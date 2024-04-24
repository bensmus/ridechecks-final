from typing import List, Dict, Tuple, Set, Literal, Any
import random
import yaml
from csp import csp_solution, to_ride_assignment

def generate_day_assignment(worker_time: int, rides_time: Dict[str, int], workers_can_check: Dict[str, Set[str]]) -> Dict[str, str] | None:
    """
    Find a complete assignment using python-constraints library MinConflictsSolver, then improve the complete assignment using hillclimbing.
    Returns a random locally optimal assignment {ride: worker...} and the remaining times of the workers {worker: time...}.
    """

    solution = csp_solution(worker_time, rides_time, workers_can_check)
    if solution == None:
        print(f"No assignment exists for worker_time={worker_time}, ride_times={rides_time}, can_check={workers_can_check}")
        return None
    
    complete_assignment = to_ride_assignment(solution)

    complete_worker_times_remaining = {worker: worker_time for worker in workers_can_check}
    for ride, worker in complete_assignment.items():
        time = ride_times[ride]
        complete_worker_times_remaining[worker] -= time

    # SECTION - HILLCLIMB

    def hillclimb(complete_assignment: Dict[str, str], complete_worker_times_remaining: Dict[str, int]) -> bool:
        """
        Modifies `complete_assignment` in place. 
        Try to hillclimb (improve the assignment). Randomized to find different local optimums.
        Return whether further hillclimbing is possible.
        """
        
        def try_transfer_ride(transferring_worker: str) -> Tuple[str, str] | None:
            """
            Transfer rides from transferring_worker to another if it results in a better 
            balance of remaining time among the workers.

            A: accepting_worker time remaining.
            T: transferring_worker time remaining.
            |(A - delta) - (T + delta)| < |A - T| <=> Should transfer.

            Returns ride, accepting_worker if transfer occurs, otherwise returns None.
            """

            def should_transfer(accepting_worker_time_remaining: int, transferring_worker_time_remaining: int, ride_time: int) -> bool:
                new_diff = abs(accepting_worker_time_remaining - transferring_worker_time_remaining - 2 * ride_time)
                old_diff = abs(accepting_worker_time_remaining - transferring_worker_time_remaining)
                return new_diff < old_diff and accepting_worker_time_remaining > transferring_worker_time_remaining      
            
            transferring_worker_time_remaining = complete_worker_times_remaining[transferring_worker]
            rides_to_transfer = [ride for ride in complete_assignment if complete_assignment[ride] == transferring_worker]
            random.shuffle(rides_to_transfer)
            
            for ride in rides_to_transfer:
                ride_time = rides_time[ride]
                accepting_workers = filter(lambda worker: worker != transferring_worker and ride in workers_can_check[worker], workers_can_check.keys())
                for accepting_worker in accepting_workers:
                    accepting_worker_time_remaining = complete_worker_times_remaining[accepting_worker]
                    if should_transfer(accepting_worker_time_remaining, transferring_worker_time_remaining, ride_time):
                        return ride, accepting_worker
            return None
        
        transferring_workers = list(workers_can_check.keys()) # All workers.
        random.shuffle(transferring_workers)
        for transferring_worker in transferring_workers:
            # Choose random worker that will try to give one of its rides to a worker.
            if (res := try_transfer_ride(transferring_worker)):
                ride_transferred = res[0]
                accepting_worker = res[1]
                complete_assignment[ride_transferred] = accepting_worker
                complete_worker_times_remaining[transferring_worker] += rides_time[ride_transferred]
                complete_worker_times_remaining[accepting_worker] -= rides_time[ride_transferred]
                return True
        return False

    while hillclimb(complete_assignment, complete_worker_times_remaining): # Hillclimb until local optimum.
        pass

    return complete_assignment


def without_keys(d: Dict, keys_to_exclude: List) -> Dict:
    return {k: v for k, v in d.items() if k not in keys_to_exclude}


DayInfoKey = Literal['time', 'uaworkers', 'uarides']
DayInfo = Dict[DayInfoKey, Any]
Day = str
Ride = str
Worker = str


def generate_multiple_day_assignments(
        days_info: Dict[Day, DayInfo], 
        all_rides_time: Dict[Ride, int], 
        all_workers_can_check: Dict[Worker, Set[Ride]]    
    ) -> Tuple[Dict[Day, Dict[Ride, Worker]] | None, str]:
    """
    First elem of tuple return value:
        Dict of {day: {ride: worker...}, ...} if an assignment can be found for all days,
        otherwise None.
    Second elem of tuple:
        Status string. If successful says for which days generated, which days closed.
        Otherwise, says which for which days it could not find an assignment. 
    """
    multiple_day_assignments = {}
    string_success = "Generated worker schedule for "
    string_failure = "Could not find a worker schedule for "
    status_string = string_success
    success = True # Does this function return a schedule or None?

    print("---")

    for day, day_info in days_info.items():
        worker_time = day_info['time']

        if worker_time == 0: # Closed on that day
            multiple_day_assignments[day] = {}
            continue

        # Not closed on that day
        day_ride_times = without_keys(all_rides_time, day_info['rides_ua'])
        day_can_check = without_keys(all_workers_can_check, day_info['workers_ua'])
        day_assignment = generate_day_assignment(worker_time, day_ride_times, day_can_check)

        if day_assignment == None: # Cannot find assignment for that day
            if success:
                multiple_day_assignments = None
                success = False
                status_string = string_failure
            status_string += day + ", "
        
        # Found assignment for that day
        if success:
            multiple_day_assignments[day] = day_assignment
            status_string += day + ", "
    
    # Remove last trailing comma and space
    status_string = status_string[:-2]
    
    return multiple_day_assignments, status_string


if __name__ == '__main__':
    # week_info: Dict[Day, DayInfo] = {
    #     'mon': {
    #         'time': 20,
    #         'workers_ua': [],
    #         'rides_ua': []
    #     },
    #     'wed': {
    #         'time': 20,
    #         'workers_ua': [],
    #         'rides_ua': []
    #     }
    # }
    # all_ride_times = {
    #     'wooden': 10,
    #     'scary': 1,
    #     'slow': 1,
    #     'fast': 5
    # }
    # all_can_check = {
    #     'john': {'wooden', 'fast'},
    #     'bob': {'scary', 'slow'},
    # }

    with open('realistic_state.yaml') as f:
            yaml_data = yaml.safe_load(f)
    
    ride_times: Dict[str, int] = yaml_data['Ride Times']
    worker_permissions: Dict[str, List[str]] = yaml_data['Worker Permissions']
    week_info = yaml_data['Weekly Info']
    
    assignments, status = generate_multiple_day_assignments(week_info, ride_times, worker_permissions)
    print(assignments, status)
