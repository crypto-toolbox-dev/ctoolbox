def get_indicator_descriptions(indicator):
    if indicator is None:
        # Get descriptions of the indicators from text files
        description = '"None" is simply "None", and nothing can change "None" \n' \
                      'for it is simply nothing. :)'

    else:
        # Get descriptions of the indicators from text files
        try:
            description_file = open(f'descriptions/{indicator.lower()}.txt', 'r')
            line_strip = [line.strip() + '\n' for line in description_file]
            description = " ".join(line_strip)
            description = description.replace('\n', '<br>')
            description_file.close()

        except FileNotFoundError:
            description = "No indicator has been selected, please choose one."

    # In case no indicator was selected (like when you hit the scan button with nothing selected)
    try:
        description_file.close()
    except UnboundLocalError:
        print("Nothing to close")

    return description


def get_pattern_descriptions(pattern):
    if pattern is None:
        # Get descriptions of the indicators from text files
        description = '"None" is simply "None", and nothing can change "None" \n' \
                      'for it is simply nothing. :)'

    else:
        # Get descriptions of the indicators from text files
        try:
            description_file = open(f'descriptions/{pattern.lower()}.txt', 'r')
            line_strip = [line.strip() + '\n' for line in description_file]
            description = " ".join(line_strip)
            description = description.replace('\n', '<br>')
            description_file.close()

        except FileNotFoundError:
            description = "No Description Available."

    # In case no indicator was selected (like when you hit the scan button with nothing selected)
    try:
        description_file.close()
    except UnboundLocalError:
        print("Nothing to close")

    return description

