from datetime import datetime

def get_valid_date(prompt, max_date=None, min_date=None):
    """
    Prompts user for a date input and validates it against optional min/max constraints.
    
    Args:
        prompt (str): The prompt message to display to the user
        max_date (datetime, optional): Maximum allowed date
        min_date (datetime, optional): Minimum allowed date
        
    Returns:
        datetime: Valid datetime object
    """
    while True:
        try:
            date_str = input(prompt)
            date = datetime.strptime(date_str, '%b %d, %Y')
            if max_date and date > max_date:
                print(f"Date cannot be later than {max_date.strftime('%b %d, %Y')}.")
            elif min_date and date < min_date:
                print(f"Date cannot be earlier than {min_date.strftime('%b %d, %Y')}.")
            else:
                return date
        except ValueError:
            print("Invalid date format. Please use 'MMM DD, YYYY' format (e.g., 'Sep 30, 2024').")

def date_to_unix(date):
    """
    Converts a datetime object to Unix timestamp.
    
    Args:
        date (datetime): The datetime object to convert
        
    Returns:
        int: Unix timestamp (seconds since epoch)
    """
    return int(date.timestamp())

def parse_date_string(date_str):
    """Convert date string from Yahoo Finance to datetime object"""
    try:
        return datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%B %d, %Y')
        except ValueError:
            print(f"Could not parse date: {date_str}")
            return None