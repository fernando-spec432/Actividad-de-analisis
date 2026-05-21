import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Login({ onLogin }) {
  const [credenciales, setCredenciales] = useState({
    username: "",
    password: "",
  });

  const [mensaje, setMensaje] = useState("");

  const manejarCambio = (e) => {
    const { name, value } = e.target;

    setCredenciales({
      ...credenciales,
      [name]: value,
    });
  };

  const iniciarSesion = async (e) => {
    e.preventDefault();
    setMensaje("");

    try {
      const respuesta = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credenciales),
      });

      if (!respuesta.ok) {
        const error = await respuesta.json();
        setMensaje(error.detail || "Usuario o contraseña incorrectos.");
        return;
      }

      const datos = await respuesta.json();

      if (!datos.access_token) {
        setMensaje("No se recibió token desde el servidor.");
        return;
      }

      onLogin(datos.access_token);
    } catch (error) {
      setMensaje("Error de conexión con el backend.");
      console.error(error);
    }
  };

  return (
    <div style={styles.contenedor}>
      <form onSubmit={iniciarSesion} style={styles.tarjeta}>
        <h1 style={styles.titulo}>Sistema de Control de Inventario</h1>
        <h2 style={styles.subtitulo}>Inicio de sesión</h2>

        {mensaje && <p style={styles.mensaje}>{mensaje}</p>}

        <label>Usuario</label>
        <input
          type="text"
          name="username"
          value={credenciales.username}
          onChange={manejarCambio}
          placeholder="Ingrese su usuario"
          style={styles.input}
          required
        />

        <label>Contraseña</label>
        <input
          type="password"
          name="password"
          value={credenciales.password}
          onChange={manejarCambio}
          placeholder="Ingrese su contraseña"
          style={styles.input}
          required
        />

        <button type="submit" style={styles.boton}>
          Iniciar sesión
        </button>
      </form>
    </div>
  );
}

const styles = {
  contenedor: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f4f6f8",
    fontFamily: "Arial, sans-serif",
  },
  tarjeta: {
    width: "400px",
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 2px 10px rgba(0,0,0,0.15)",
  },
  titulo: {
    textAlign: "center",
    fontSize: "25px",
  },
  subtitulo: {
    textAlign: "center",
    color: "#4b5563",
  },
  input: {
    width: "100%",
    padding: "10px",
    marginTop: "6px",
    marginBottom: "15px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    boxSizing: "border-box",
  },
  boton: {
    width: "100%",
    padding: "12px",
    backgroundColor: "#2563eb",
    color: "white",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  mensaje: {
    backgroundColor: "#fee2e2",
    color: "#991b1b",
    padding: "10px",
    borderRadius: "6px",
    textAlign: "center",
  },
};

export default Login;