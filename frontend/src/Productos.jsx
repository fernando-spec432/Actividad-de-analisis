import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

function Productos({ onVolverMenu, onCerrarSesion }) {
  const [productos, setProductos] = useState([]);
  const [mensaje, setMensaje] = useState("");
  const [editandoId, setEditandoId] = useState(null);

  const [formulario, setFormulario] = useState({
    codigo_unico: "",
    nombre: "",
    descripcion: "",
    stock_minimo_alerta: 5,
  });

  const obtenerToken = () => localStorage.getItem("token");

  const cargarProductos = async () => {
    const token = obtenerToken();

    if (!token) {
      setMensaje("No hay sesión activa.");
      return;
    }

    try {
      const respuesta = await fetch(`${API_URL}/productos/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!respuesta.ok) {
        setMensaje("No se pudieron cargar los productos.");
        return;
      }

      const datos = await respuesta.json();
      setProductos(datos);
      setMensaje("Productos cargados correctamente.");
    } catch (error) {
      setMensaje("Error de conexión con el backend.");
      console.error(error);
    }
  };

  const manejarCambio = (e) => {
    const { name, value } = e.target;

    setFormulario({
      ...formulario,
      [name]: name === "stock_minimo_alerta" ? Number(value) : value,
    });
  };

  const limpiarFormulario = () => {
    setFormulario({
      codigo_unico: "",
      nombre: "",
      descripcion: "",
      stock_minimo_alerta: 5,
    });
    setEditandoId(null);
  };

  const guardarProducto = async (e) => {
    e.preventDefault();

    const token = obtenerToken();

    const url = editandoId
      ? `${API_URL}/productos/${editandoId}`
      : `${API_URL}/productos/`;

    const metodo = editandoId ? "PUT" : "POST";

    const datosEnviar = editandoId
      ? {
          nombre: formulario.nombre,
          descripcion: formulario.descripcion,
          stock_minimo_alerta: formulario.stock_minimo_alerta,
        }
      : formulario;

    try {
      const respuesta = await fetch(url, {
        method: metodo,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(datosEnviar),
      });

      if (!respuesta.ok) {
        const error = await respuesta.json();
        setMensaje(error.detail || "No se pudo guardar el producto.");
        return;
      }

      setMensaje(editandoId ? "Producto actualizado correctamente." : "Producto creado correctamente.");
      limpiarFormulario();
      cargarProductos();
    } catch (error) {
      setMensaje("Error al guardar el producto.");
      console.error(error);
    }
  };

  const prepararEdicion = (producto) => {
    setEditandoId(producto.id_producto);

    setFormulario({
      codigo_unico: producto.codigo_unico,
      nombre: producto.nombre,
      descripcion: producto.descripcion || "",
      stock_minimo_alerta: producto.stock_minimo_alerta,
    });

    setMensaje(`Editando producto: ${producto.nombre}`);
  };

  const eliminarProducto = async (idProducto) => {
    const confirmar = window.confirm("¿Seguro que deseas eliminar este producto?");
    if (!confirmar) return;

    const token = obtenerToken();

    try {
      const respuesta = await fetch(`${API_URL}/productos/${idProducto}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!respuesta.ok) {
        setMensaje("No se pudo eliminar el producto.");
        return;
      }

      setMensaje("Producto eliminado correctamente.");
      cargarProductos();
    } catch (error) {
      setMensaje("Error al eliminar el producto.");
      console.error(error);
    }
  };

  useEffect(() => {
    cargarProductos();
  }, []);

  return (
    <div style={styles.contenedor}>
      <header style={styles.header}>
        <h1>Productos</h1>

        <div>
          <button onClick={onVolverMenu} style={styles.botonSecundario}>
            Volver al menú
          </button>

          <button onClick={onCerrarSesion} style={styles.botonSalir}>
            Cerrar sesión
          </button>
        </div>
      </header>

      {mensaje && <p style={styles.mensaje}>{mensaje}</p>}

      <section style={styles.tarjeta}>
        <h3>{editandoId ? "Editar producto" : "Crear producto"}</h3>

        <form onSubmit={guardarProducto} style={styles.formulario}>
          <label>Código único</label>
          <input
            type="text"
            name="codigo_unico"
            value={formulario.codigo_unico}
            onChange={manejarCambio}
            disabled={editandoId !== null}
            required={!editandoId}
            style={styles.input}
          />

          <label>Nombre</label>
          <input
            type="text"
            name="nombre"
            value={formulario.nombre}
            onChange={manejarCambio}
            required
            style={styles.input}
          />

          <label>Descripción</label>
          <textarea
            name="descripcion"
            value={formulario.descripcion}
            onChange={manejarCambio}
            style={styles.textarea}
          />

          <label>Stock mínimo de alerta</label>
          <input
            type="number"
            name="stock_minimo_alerta"
            value={formulario.stock_minimo_alerta}
            onChange={manejarCambio}
            min="0"
            style={styles.input}
          />

          <div>
            <button type="submit" style={styles.botonPrincipal}>
              {editandoId ? "Actualizar producto" : "Crear producto"}
            </button>

            {editandoId && (
              <button type="button" onClick={limpiarFormulario} style={styles.botonSecundario}>
                Cancelar edición
              </button>
            )}
          </div>
        </form>
      </section>

      <section style={styles.tarjeta}>
        <h3>Listado de productos</h3>

        {productos.length === 0 ? (
          <p>No hay productos registrados.</p>
        ) : (
          <table style={styles.tabla}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Código</th>
                <th style={styles.th}>Nombre</th>
                <th style={styles.th}>Descripción</th>
                <th style={styles.th}>Stock actual</th>
                <th style={styles.th}>Stock mínimo</th>
                <th style={styles.th}>Fecha creación</th>
                <th style={styles.th}>Acciones</th>
              </tr>
            </thead>

            <tbody>
              {productos.map((producto) => (
                <tr key={producto.id_producto}>
                  <td style={styles.td}>{producto.id_producto}</td>
                  <td style={styles.td}>{producto.codigo_unico}</td>
                  <td style={styles.td}>{producto.nombre}</td>
                  <td style={styles.td}>{producto.descripcion || "Sin descripción"}</td>
                  <td style={styles.td}>{producto.stock_actual}</td>
                  <td style={styles.td}>{producto.stock_minimo_alerta}</td>
                  <td style={styles.td}>{producto.fecha_creacion}</td>
                  <td style={styles.td}>
                    <button onClick={() => prepararEdicion(producto)} style={styles.botonEditar}>
                      Editar
                    </button>

                    <button onClick={() => eliminarProducto(producto.id_producto)} style={styles.botonEliminar}>
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

const styles = {
  contenedor: {
    padding: "30px",
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f4f6f8",
    minHeight: "100vh",
  },
  header: {
    backgroundColor: "#749acf",
    color: "white",
    padding: "20px",
    borderRadius: "10px",
    marginBottom: "20px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  tarjeta: {
    backgroundColor: "white",
    padding: "20px",
    borderRadius: "10px",
    marginBottom: "20px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },
  formulario: {
    display: "grid",
    gap: "10px",
  },
  input: {
    width: "100%",
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    boxSizing: "border-box",
  },
  textarea: {
    width: "100%",
    height: "60px",
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    boxSizing: "border-box",
  },
  botonPrincipal: {
    padding: "10px 15px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#2563eb",
    color: "white",
    cursor: "pointer",
    marginRight: "10px",
  },
  botonSecundario: {
    padding: "10px 15px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#6b7280",
    color: "white",
    cursor: "pointer",
    marginRight: "10px",
  },
  botonSalir: {
    padding: "10px 15px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#dc2626",
    color: "white",
    cursor: "pointer",
  },
  botonEditar: {
    padding: "7px 10px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#f59e0b",
    color: "white",
    cursor: "pointer",
    marginRight: "5px",
  },
  botonEliminar: {
    padding: "7px 10px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#dc2626",
    color: "white",
    cursor: "pointer",
  },
  mensaje: {
    padding: "10px",
    backgroundColor: "#e0f2fe",
    borderRadius: "5px",
    color: "#075985",
  },
  tabla: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "15px",
  },
  th: {
    border: "1px solid #ddd",
    padding: "10px",
    backgroundColor: "#1f2937",
    color: "white",
  },
  td: {
    border: "1px solid #ddd",
    padding: "10px",
    textAlign: "center",
  },
};

export default Productos;