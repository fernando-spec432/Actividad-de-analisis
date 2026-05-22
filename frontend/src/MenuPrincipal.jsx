function MenuPrincipal({ onIrProductos, onCerrarSesion }) {
  return (
    <div style={styles.contenedor}>
      <header style={styles.header}>
        <h1>Sistema de Control de Inventario</h1>
        <button onClick={onCerrarSesion} style={styles.botonSalir}>
          Cerrar sesión
        </button>
      </header>

      <main style={styles.contenido}>
        <h2>Menú principal</h2>
        <p>Seleccione una opción del sistema.</p>

        <div style={styles.grid}>
          <button onClick={onIrProductos} style={styles.tarjeta}>
            <h3>Productos</h3>
            <p>Crear, listar, editar y eliminar productos.</p>
          </button>

          <button style={styles.tarjetaDeshabilitada} disabled>
            <h3>Proveedores</h3>
            <p>Pendiente de implementación.</p>
          </button>

          <button style={styles.tarjetaDeshabilitada} disabled>
            <h3>Movimientos</h3>
            <p>Pendiente de implementación.</p>
          </button>

          <button style={styles.tarjetaDeshabilitada} disabled>
            <h3>Alertas de stock</h3>
            <p>Pendiente de implementación.</p>
          </button>
        </div>
      </main>
    </div>
  );
}

const styles = {
  contenedor: {
    minHeight: "100vh",
    backgroundColor: "#f4f6f8",
    fontFamily: "Arial, sans-serif",
  },
  header: {
    backgroundColor: "#749acf",
    color: "white",
    padding: "20px 30px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  botonSalir: {
    backgroundColor: "#dc2626",
    color: "white",
    border: "none",
    padding: "10px 15px",
    borderRadius: "6px",
    cursor: "pointer",
  },
  contenido: {
    padding: "30px",
    textAlign: "center",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "20px",
    marginTop: "30px",
  },
  tarjeta: {
    backgroundColor: "white",
    padding: "25px",
    borderRadius: "12px",
    border: "none",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
    cursor: "pointer",
  },
  tarjetaDeshabilitada: {
    backgroundColor: "#e5e7eb",
    padding: "25px",
    borderRadius: "12px",
    border: "none",
    color: "#6b7280",
    cursor: "not-allowed",
  },
};

export default MenuPrincipal;