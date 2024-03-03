from typing import List, Dict, Tuple, Set, Literal, Any
import time
import random


def generate_day_assignment(worker_time: int, rides_time: Dict[str, int], workers_can_check: Dict[str, Set[str]]) -> Dict[str, str] | None:
    """
    Find a complete assignment using dfs (backtracking), then improve the complete assignment using hillclimbing.
    Returns a random locally optimal assignment {ride: worker...} and the remaining times of the workers {worker: time...}.
    """

    # SECTION - DFS

    # FIXME - Takes a long time if a complete assignment is impossible.

    def dfs(partial_assignment: Dict[str, str], partial_worker_times_remaining: Dict[str, int]) -> Tuple[Dict[str, str], Dict[str, int]]:
        """
        Recursive function.
        partial_assignment: Dictionary of {ride: worker...} containing a subset of rides.
        worker_times: How much time does every worker have remaining.
        Randomized dfs: find a random solution to CSP that is not even locally optimal.
        """

        # NOTE - This function could be faster if workers were chosen from a list sorted based on time remaining. (Kind of A star-y?)
        # Randomize the next ride instead. 
        # Add a line to check if a complete assignment is possible: set of values of workers_can_check cardinality equal to rides_time length.

        # Base case: 
        if len(partial_assignment) == len(rides_time):
            return partial_assignment, partial_worker_times_remaining
        
        # Recursive case:
        ride = next(ride for ride in rides_time if ride not in partial_assignment)
        workers = list(workers_can_check.keys())
        random.shuffle(workers)
        for worker in workers: # Try to assign every worker to the ride in a random order.
            if ride in workers_can_check[worker] and rides_time[ride] <= partial_worker_times_remaining[worker]:
                # Recursive call, adding ride and worker to partial_assignment, worker_times reflect remaining time.
                complete_assignment, complete_worker_times_remaining = dfs(
                    partial_assignment | {ride: worker}, 
                    partial_worker_times_remaining | {worker: partial_worker_times_remaining[worker] - rides_time[ride]}
                )
                if complete_assignment != {}:
                    return complete_assignment, complete_worker_times_remaining
        # Could not find a complete assignment based on the partial_assignment and worker_times_remaining.
        return {}, partial_worker_times_remaining

    start_dfs_time = time.time()

    complete_assignment, complete_worker_times_remaining = dfs({}, {worker: worker_time for worker in workers_can_check})
    if complete_assignment == {}:
        print(f"No assignment exists for worker_time={worker_time}, ride_times={rides_time}, can_check={workers_can_check}")
        return None
    
    end_dfs_time = time.time()
    print('dfs time', end_dfs_time - start_dfs_time)

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
    
    start_hillclimb_time = time.time()

    while hillclimb(complete_assignment, complete_worker_times_remaining): # Hillclimb until local optimum.
        pass
    
    end_hillclimb_time = time.time()
    print('hillclimb time', end_hillclimb_time - start_hillclimb_time)

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
    week_info: Dict[Day, DayInfo] = {
        'mon': {
            'time': 20,
            'workers_ua': [],
            'rides_ua': []
        },
        'wed': {
            'time': 20,
            'workers_ua': [],
            'rides_ua': []
        }
    }
    all_ride_times = {
        'wooden': 10,
        'scary': 1,
        'slow': 1,
        'fast': 5
    }
    all_can_check = {
        'john': {'wooden', 'fast'},
        'bob': {'scary', 'slow'},
    }
    assignments, status = generate_multiple_day_assignments(week_info, all_ride_times, all_can_check)
    print(assignments, status)
