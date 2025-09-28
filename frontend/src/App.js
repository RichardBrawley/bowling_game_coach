// src/App.js
import React, { useState } from "react";
import Auth from "./pages/Auth";
import Board from "./pages/Board";

function App() {
  const [user, setUser] = useState(null);

  return user ? (
    <Board username={user} />
  ) : (
    <Auth onAuthSuccess={(username) => setUser(username)} />
  );
}

export default App;
