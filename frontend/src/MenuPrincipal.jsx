function MenuPrincipal({ onIrProductos, onIrEntradas, onCerrarSesion }) {
  return (
    <div style={styles.contenedor}>
      <header style={styles.header}>
        <h1 style={styles.textoHeader}>Sistema de Control de Inventario</h1>
        <button onClick={onCerrarSesion} style={styles.botonSalir}>
          Cerrar sesión
        </button>
      </header>

      <main style={styles.contenido}>
        <h2 style={styles.tituloSeccion}>Menú principal</h2>
        <p style={styles.subtituloSeccion}>Seleccione una opción del sistema.</p>

        <div style={styles.grid}>
          {/* Tarjeta 1: Productos */}
          <button onClick={onIrProductos} style={styles.tarjeta}>
            <h3 style={styles.tituloTarjeta}>Productos</h3>
            <p style={styles.descripcionTarjeta}>Crear, listar, editar y eliminar productos.</p>
          </button>

          {/* Tarjeta 2: Proveedores */}
          <button style={styles.tarjetaDeshabilitada} disabled>
            <h3 style={styles.tituloTarjetaDeshabilitada}>Proveedores</h3>
            <p style={styles.descripcionTarjetaDeshabilitada}>Pendiente de implementación.</p>
          </button>

          {/* Tarjeta 3: Registrar Entradas (HU-03 de Miércoles) */}
          <button onClick={onIrEntradas} style={styles.tarjeta}>
            <h3 style={styles.tituloTarjeta}>Registrar Entradas</h3>
            <p style={styles.descripcionTarjeta}>Ingresar cantidad y actualizar stock en bodega.</p>
          </button>

          {/* Tarjeta 4: Alertas de stock */}
          <button style={styles.tarjetaDeshabilitada} disabled>
            <h3 style={styles.tituloTarjetaDeshabilitada}>Alertas de stock</h3>
            <p style={styles.descripcionTarjetaDeshabilitada}>Pendiente de implementación.</p>
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
  textoHeader: {
    margin: 0,
    color: "#ffffff",
  },
  botonSalir: {
    backgroundColor: "#dc2626",
    color: "white",
    border: "none",
    padding: "10px 15px",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
  },
  contenido: {
    padding: "30px",
    textAlign: "center",
  },
  tituloSeccion: {
    color: "#1f2937",
    margin: "0 0 10px 0",
  },
  subtituloSeccion: {
    color: "#4b5563",
    margin: 0,
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
    gap: "20px",
    marginTop: "30px",
  },
  tarjeta: {
    backgroundColor: "#ffffff",
    padding: "25px",
    borderRadius: "12px",
    border: "none",
    boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
    cursor: "pointer",
    textAlign: "center",
  },
  tarjetaDeshabilitada: {
    backgroundColor: "#e5e7eb",
    padding: "25px",
    borderRadius: "12px",
    border: "none",
    cursor: "not-allowed",
    textAlign: "center",
  },
  // --- ESTILOS CONTROLADOS PARA EL TEXTO ---
  tituloTarjeta: {
    color: "#111827", // Negro intenso
    fontSize: "1.2rem",
    margin: "0 0 8px 0",
    fontWeight: "bold",
  },
  descripcionTarjeta: {
    color: "#374151", // Gris oscuro legible
    fontSize: "0.95rem",
    margin: 0,
  },
  tituloTarjetaDeshabilitada: {
    color: "#6b7280", // Gris apagado
    fontSize: "1.2rem",
    margin: "0 0 8px 0",
    fontWeight: "bold",
  },
  descripcionTarjetaDeshabilitada: {
    color: "#9ca3af", // Gris muy claro
    fontSize: "0.95rem",
    margin: 0,
  },
};

export default MenuPrincipal;