# Bubble Sort Implementation


def bubble_sort(arr):
    """
    Sorts an array using the bubble sort algorithm.

    Args:
        arr (list): The list to be sorted.

    Returns:
        list: The sorted list.
    """
    n = len(arr)

    # Traverse through all array elements
    for i in range(n):
        # Flag to check if any swapping occurred in this pass
        swapped = False

        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # If no two elements were swapped in inner loop, break
        if not swapped:
            break

    return arr


# Example usage
if __name__ == "__main__":
    # Test array
    test_arr = [64, 34, 25, 12, 22, 11, 90]
    print("Original array:", test_arr)

    # Sort the array
    sorted_arr = bubble_sort(test_arr.copy())
    print("Sorted array:", sorted_arr)

    # Additional test with different types of input
    test_arr2 = [5, 1, 4, 2, 8]
    print("\nOriginal array:", test_arr2)
    sorted_arr2 = bubble_sort(test_arr2)
    print("Sorted array:", sorted_arr2)
