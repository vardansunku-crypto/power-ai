def generate_sql(user_query):

    user_query = user_query.lower()

    # SHOW SALES
    if "sales" in user_query:

        return "SELECT * FROM sales"

    # SHOW REVENUE
    elif "revenue" in user_query:

        return """
        SELECT product_name, revenue
        FROM sales
        """

    # HIGHEST REVENUE
    elif "highest revenue" in user_query:

        return """
        SELECT product_name, revenue
        FROM sales
        ORDER BY revenue DESC
        LIMIT 1
        """

    # SHOW QUANTITY
    elif "quantity" in user_query:

        return """
        SELECT product_name, quantity
        FROM sales
        """

    else:

        return None