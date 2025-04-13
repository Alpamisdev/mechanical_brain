def split_long_message(message, max_length=4000):
    """
    Split a long message into multiple parts that are within Telegram's character limit.
    
    Args:
        message (str): The message to split
        max_length (int): Maximum length of each part (default: 4000, slightly below Telegram's 4096 limit)
        
    Returns:
        list: List of message parts
    """
    if len(message) <= max_length:
        return [message]
        
    parts = []
    lines = message.split('\n')
    current_part = ""
    
    for line in lines:
        # If adding this line would exceed the limit, start a new part
        if len(current_part) + len(line) + 1 > max_length:
            parts.append(current_part)
            current_part = line
        else:
            if current_part:
                current_part += '\n' + line
            else:
                current_part = line
    
    # Add the last part if it's not empty
    if current_part:
        parts.append(current_part)
        
    return parts
