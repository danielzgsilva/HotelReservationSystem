def get_int_date(date):

    # dates are inputted in this format: 2019-09-17
    data = date.split('-')

    # need to put in int format: 09170219
    int_date = int(data[1] + data[2] + data[0])

    return int_date