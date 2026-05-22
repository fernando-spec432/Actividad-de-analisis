import { useState } from "react";
import Login from "./Login";
import MenuPrincipal from "./MenuPrincipal";
import Productos from "./Productos";
import RegistroEntradas from './RegistroEntradas'; // Componente importado

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [vista, setVista] = useState("menu");

  const manejarLogin = (nuevoToken) => {
    localStorage.setItem("token", nuevoToken);
    setToken(nuevoToken);
    setVista("menu");
  };

  const cerrarSesion = () => {
    localStorage.removeItem("token");
    setToken("");
    setVista("menu");
  };

  // 1. Si no hay sesión iniciada, obligar a ir al Login
  if (!token) {
    return <Login onLogin={manejarLogin} />;
  }

  // 2. Pantalla de Gestión de Productos
  if (vista === "productos") {
    return (
      <Productos
        onVolverMenu={() => setVista("menu")}
        onCerrarSesion={cerrarSesion}
      />
    );
  }

  // 3. Pantalla de Registro de Entradas (HU-03)
  if (vista === "entradas") {
    return (
      <RegistroEntradas 
        onVolverMenu={() => setVista("menu")} 
      />
    );
  }

  // 4. Pantalla del Menú Principal (por defecto al estar logueado)
  return (
    <MenuPrincipal
      onIrProductos={() => setVista("productos")}
      onIrEntradas={() => setVista("entradas")}
      onCerrarSesion={cerrarSesion}
    />
  );
}

export default App;