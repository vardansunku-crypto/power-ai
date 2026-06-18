import streamlit as st
import plotly.express as px

from utils.cleaner import clean_dataframe_columns


def show_kpi_and_charts(dataframe, title):

    dataframe = clean_dataframe_columns(dataframe)

    numeric_columns = dataframe.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    categorical_columns = dataframe.select_dtypes(
        include=["object"]
    ).columns.tolist()

    all_columns = dataframe.columns.tolist()

    # -------------------------------------------------
    # KPI SECTION
    # -------------------------------------------------

    st.subheader(f"{title} KPI Insights")

    total_rows = len(dataframe)
    total_columns = len(dataframe.columns)
    numeric_count = len(numeric_columns)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", total_rows)

    with col2:
        st.metric("Total Columns", total_columns)

    with col3:
        st.metric("Numeric Columns", numeric_count)

    if len(numeric_columns) > 0:

        st.markdown("### Numeric Totals")

        metric_columns = st.columns(3)

        for index, column in enumerate(numeric_columns):

            total_value = dataframe[column].sum()

            with metric_columns[index % 3]:

                st.metric(
                    label=f"Total {column}",
                    value=round(total_value, 2)
                )

    # -------------------------------------------------
    # DYNAMIC CHART BUILDER
    # -------------------------------------------------

    st.subheader(f"{title} Dynamic Chart Builder")

    if len(all_columns) == 0:

        st.warning("No columns available for charting.")
        return

    chart_type = st.selectbox(
        "Select Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Pie Chart",
            "Scatter Chart",
            "Area Chart"
        ],
        key=f"{title}_chart_type"
    )

    x_column = st.selectbox(
        "Select X-axis / Category Column",
        all_columns,
        key=f"{title}_x_column"
    )

    y_column = None

    if chart_type != "Pie Chart":

        if len(numeric_columns) == 0:

            st.warning("No numeric columns available for Y-axis.")
            return

        y_column = st.selectbox(
            "Select Y-axis / Numeric Column",
            numeric_columns,
            key=f"{title}_y_column"
        )

    else:

        if len(numeric_columns) == 0:

            st.warning("No numeric columns available for Pie values.")
            return

        y_column = st.selectbox(
            "Select Values Column",
            numeric_columns,
            key=f"{title}_pie_values"
        )

    try:

        if chart_type == "Bar Chart":

            fig = px.bar(
                dataframe,
                x=x_column,
                y=y_column,
                title=f"{title} Bar Chart"
            )

        elif chart_type == "Line Chart":

            fig = px.line(
                dataframe,
                x=x_column,
                y=y_column,
                title=f"{title} Line Chart"
            )

        elif chart_type == "Pie Chart":

            fig = px.pie(
                dataframe,
                names=x_column,
                values=y_column,
                title=f"{title} Pie Chart"
            )

        elif chart_type == "Scatter Chart":

            fig = px.scatter(
                dataframe,
                x=x_column,
                y=y_column,
                title=f"{title} Scatter Chart"
            )

        elif chart_type == "Area Chart":

            fig = px.area(
                dataframe,
                x=x_column,
                y=y_column,
                title=f"{title} Area Chart"
            )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Chart Error: {e}"
        )