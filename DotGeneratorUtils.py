from sympy import Point, Line, symbols


def generate_dots(start: Point, end: Point, interval: float):
    """
    Generate a series of dots between the start and end point with a given interval.
    
    Parameters:
        - start (Point): The starting point.
        - end (Point): The ending point.
        - interval (float): Distance between adjacent points.
        
    Returns:
        - List[Point]: A list of sympy Points evenly spaced between start and end.
    """
    # Step 1: Calculate the total distance between start and end
    total_distance = start.distance(end)

    # Step 2: Calculate the unit vector in the direction from start to end
    direction_vector = (end - start).unit

    # Step 3: Determine the number of dots based on the interval
    n_points = int(total_distance / interval)  # Number of steps (floor division)

    # Step 4: Generate the points
    dots = [start + (interval * i) * direction_vector for i in range(n_points + 1)]

    return dots


# Example usage
start = Point(0, 0)
end = Point(10, 10)
interval = 2

dots = generate_dots(start, end, interval)
for dot in dots:
    print(dot)