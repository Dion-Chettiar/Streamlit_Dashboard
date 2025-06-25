import streamlit as st
import graphviz

try:
    import graphviz
    st.success("Graphviz imported successfully!")
except ModuleNotFoundError as e:
    st.error(f"Graphviz not found: {e}")


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
