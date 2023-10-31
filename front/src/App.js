import { createBrowserRouter, RouterProvider } from "react-router-dom";

// import NotFound from "./routes/NotFound";
// import Root from "./routes/root";
// import Players from "./routes/players";
// import Teams from "./routes/teams";
import Inventory from "./Inventory";

let router = createBrowserRouter([
  {
    path: "/inventory",
    element: <Inventory />,
  },
]);

if (import.meta.hot) {
  import.meta.hot.dispose(() => router.dispose());
}

export default function App() {
  return <RouterProvider router={router} />;
}
