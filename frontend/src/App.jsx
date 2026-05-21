import { useState } from "react";
import Login from "./Login";
import MenuPrincipal from "./MenuPrincipal";
import Productos from "./Productos";

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

  if (!token) {
    return <Login onLogin={manejarLogin} />;
  }

  if (vista === "productos") {
    return (
      <Productos
        onVolverMenu={() => setVista("menu")}
        onCerrarSesion={cerrarSesion}
      />
    );
  }

  return (
    <MenuPrincipal
      onIrProductos={() => setVista("productos")}
      onCerrarSesion={cerrarSesion}
    />
  );
}

export default App;