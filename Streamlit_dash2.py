import streamlit as st

st.title("Optimal Combinations")

graph_code = """
digraph G {
    P [label="Pamo (Mid)"]
    R [label="Raco (Mid)"]
    Z [label="Zaco (Fwd)"]

    P -> Z
    R -> Z
    P -> R
}
"""

st.graphviz_chart(graph_code)
