import { useEffect, useState } from "react";

function App() {
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/roles")
      .then((response) => response.json())
      .then((data) => setRoles(data))
      .catch((error) => console.error("Error al conectar con la API:", error));
  }, []);

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>Sistema de Control de Inventario</h1>
      <h2>Roles desde PostgreSQL</h2>

      {roles.length === 0 ? (
        <p>No hay roles cargados o no se pudo conectar con la API.</p>
      ) : (
        <ul>
          {roles.map((rol) => (
            <li key={rol.id_col}>
              {rol.id_col} - {rol.nombre_rol}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;