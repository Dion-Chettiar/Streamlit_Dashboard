import streamlit as st



st.title("Optimal Combinations")

st.markdown("### Zaco (Fwd), Pamo (Mid), Raco (Mid)")

# Create a directed graph
dot = graphviz.Digraph()

# Add nodes
dot.node("Z", "Zaco (Fwd)")
dot.node("P", "Pamo (Mid)")
dot.node("R", "Raco (Mid)")

# Add edges
dot.edge("P", "Z")
dot.edge("R", "Z")
dot.edge("P", "R")

# Display in Streamlit
st.graphviz_chart(dot)
