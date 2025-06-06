
import streamlit as st

# Título de la página
st.title("Clase: ")

if st.button("Haz click"):
    st.success("clickeaste")
    
nombre = st.text_input("Escribe tu nombre:")
if nombre:
    st.write(f"¡Hola, {nombre}!")
    
    
v= st.checkbox("Activar internet")

if v:
    st.success("internet activado")