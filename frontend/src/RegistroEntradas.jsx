import React, { useState, useEffect } from 'react';

export default function RegistroEntradas({ onVolverMenu }) {
  // Estado original vacío para recibir los productos de la BD
  const [productos, setProductos] = useState([]);
  
  // Estado para capturar los datos del formulario
  const [formData, setFormData] = useState({
    id_producto: '',
    cantidad: '',
    fecha: new Date().toISOString().split('T')[0] // Fecha de hoy por defecto
  });

  const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
  const [cargando, setCargando] = useState(false);

  // EFECTO ACTIVO: Carga los productos reales desde el backend
  useEffect(() => {
    fetch('http://localhost:8000/api/productos') 
      .then((res) => {
        if (!res.ok) throw new Error('Error al conectar con el servidor');
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          setProductos(data);
        }
      })
      .catch((err) => {
        console.error('Error al cargar productos:', err);
        setMensaje({ texto: '❌ No se pudo conectar con el catálogo de productos.', tipo: 'error' });
      });
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMensaje({ texto: '', tipo: '' });

    // Validación de cantidad positiva (Criterio de aceptación)
    const cantidadNumerica = parseInt(formData.cantidad);
    if (isNaN(cantidadNumerica) || cantidadNumerica <= 0) {
      setMensaje({ 
        texto: '⚠️ La cantidad debe ser un número positivo mayor a cero.', 
        tipo: 'error' 
      });
      return;
    }

    if (!formData.id_producto) {
      setMensaje({ texto: '⚠️ Por favor, selecciona un producto.', tipo: 'error' });
      return;
    }

    setCargando(true);

    try {
      // Petición POST real para registrar la entrada en la base de datos
      const respuesta = await fetch('http://localhost:8000/api/entradas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_producto: parseInt(formData.id_producto),
          cantidad: cantidadNumerica,
          fecha: formData.fecha
        })
      });

      const resultado = await respuesta.json();

      if (respuesta.ok) {
        setMensaje({ texto: '✅ Entrada registrada y stock actualizado en la base de datos.', tipo: 'exito' });
        setFormData({
          id_producto: '',
          cantidad: '',
          fecha: new Date().toISOString().split('T')[0]
        });
      } else {
        setMensaje({ texto: `❌ Error backend: ${resultado.detail || 'No se pudo registrar'}`, tipo: 'error' });
      }
    } catch (error) {
      setMensaje({ texto: '❌ Error de red. Asegúrate de que el backend esté encendido.', tipo: 'error' });
    } finally {
      setCargando(false);
    }
  };

  return (
    <div style={styles.contenedor}>
      <button onClick={onVolverMenu} style={styles.botonVolver}>
        ← Volver al Menú Principal
      </button>

      <div style={styles.tarjetaFormulario}>
        <h2 style={styles.titulo}>📥 Registro de Entradas</h2>
        <p style={styles.subtitulo}>HU-03: Rol Bodeguero</p>

        {mensaje.texto && (
          <div style={{
            ...styles.alerta,
            backgroundColor: mensaje.tipo === 'error' ? '#fee2e2' : '#dcfce7',
            color: mensaje.tipo === 'error' ? '#b91c1c' : '#15803d'
          }}>
            {mensaje.texto}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={styles.campo}>
            <label style={styles.label}>Seleccionar Producto</label>
            <select
              name="id_producto"
              value={formData.id_producto}
              onChange={handleChange}
              style={styles.input}
            >
              <option value="">-- Elija un producto --</option>
              {productos.map((prod) => (
                <option key={prod.id_producto} value={prod.id_producto}>
                  {prod.nombre || `Producto #${prod.id_producto}`}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.campo}>
            <label style={styles.label}>Cantidad a Ingresar</label>
            <input
              type="number"
              name="cantidad"
              value={formData.cantidad}
              onChange={handleChange}
              placeholder="Ej. 50"
              style={styles.input}
            />
          </div>

          <div style={styles.campo}>
            <label style={styles.label}>Fecha de Registro</label>
            <input
              type="date"
              name="fecha"
              value={formData.fecha}
              onChange={handleChange}
              style={styles.input}
            />
          </div>

          <button
            type="submit"
            disabled={cargando}
            style={{
              ...styles.botonGuardar,
              backgroundColor: cargando ? '#9ca3af' : '#749acf',
              cursor: cargando ? 'not-allowed' : 'pointer'
            }}
          >
            {cargando ? 'Guardando...' : 'Registrar Entrada'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  contenedor: { minHeight: "100vh", backgroundColor: "#f4f6f8", fontFamily: "Arial, sans-serif", padding: "30px" },
  botonVolver: { backgroundColor: "transparent", color: "#4b5563", border: "none", fontSize: "1rem", cursor: "pointer", marginBottom: "20px", fontWeight: "bold" },
  tarjetaFormulario: { backgroundColor: "white", maxWidth: "450px", margin: "0 auto", padding: "30px", borderRadius: "12px", boxShadow: "0 4px 12px rgba(0,0,0,0.1)" },
  titulo: { margin: "0 0 5px 0", color: "#1f2937", textAlign: "center" },
  subtitulo: { margin: "0 0 20px 0", color: "#6b7280", textAlign: "center", fontSize: "0.9rem" },
  alerta: { padding: "12px", borderRadius: "6px", marginBottom: "20px", fontSize: "0.9rem", fontWeight: "500", textAlign: "center" },
  campo: { marginBottom: "20px" },
  label: { display: "block", marginBottom: "6px", color: "#374151", fontWeight: "bold", fontSize: "0.9rem", textAlign: "left" },
  input: { width: "100%", padding: "10px", borderRadius: "6px", border: "1px solid #d1d5db", boxSizing: "border-box", fontSize: "1rem" },
  botonGuardar: { width: "100%", color: "white", border: "none", padding: "12px", borderRadius: "6px", fontSize: "1rem", fontWeight: "bold", marginTop: "10px" }
};